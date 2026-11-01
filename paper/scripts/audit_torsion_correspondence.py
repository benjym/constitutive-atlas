"""Exact acquisition-content fingerprints; no curve similarity or fitted alignment."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'paper/results/dependencies'))
import xlrd


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(rows):
    digest = hashlib.sha256()
    count = 0
    width = None
    for expected, row in enumerate(rows, 1):
        if width is None:
            width = len(row)
        if width not in (3, 5) or len(row) != width:
            raise ValueError('Expected sample number and two/four acquisition channels')
        values = [float(v) for v in row]
        if values[0] != expected or not all(math.isfinite(v) for v in values):
            raise ValueError('Nonsequential acquisition or nonfinite channel')
        digest.update(struct.pack(f'<{width}d', *(0.0 if v == 0 else v for v in values)))
        count += 1
    if not count:
        raise ValueError('Empty acquisition')
    return {'rows': count, 'columns': width, 'sha256_ieee754_binary64_columns': digest.hexdigest()}


def main():
    inventory_path = ROOT / 'paper/study/ottawa_cyclic_inventory.json'
    inventory_sha = sha(inventory_path)
    records = json.loads(inventory_path.read_text())['records']
    raw_records = [r for r in records if r['protocol'] in
                   ('torsion-apparatus-source', 'consolidation-apparatus-source')]
    processed = [r for r in records if r['protocol'] in
                 ('cyclic-torsional-shear-source', 'torsion-consolidation-source',
                  'post-torsion-reconsolidation-source')]
    if len(raw_records) != 27 or len(processed) != 27:
        raise ValueError('Expected27acquisitions and27workbook phases')
    raw_results = []
    raw_content = {}
    for r in raw_records:
        path = ROOT / 'tmp/dataset-survey' / r['source_file']
        if sha(path) != r['source_file_sha256']:
            raise ValueError('Raw source hash mismatch')
        reader = csv.reader(io.StringIO(path.read_bytes().decode('cp932')))
        metadata = {}
        header = [''] + [f'CH_{i}' for i in range(1, len(r['source_columns']))]
        for row in reader:
            if row == header:
                break
            metadata[row[0]] = row[1:]
        else:
            raise ValueError('Missing acquisition header')
        raw_rows = [row for row in reader if any(v.strip() for v in row)]
        fp = fingerprint(raw_rows)
        raw_content[r['id']] = raw_rows
        if fp['rows'] != int(metadata['NUM_SAMPS'][0]):
            raise ValueError('NUM_SAMPS mismatch')
        aliases = []
        for alias in r['source_aliases']:
            alias_path = ROOT / 'tmp/dataset-survey' / alias
            if sha(alias_path) != r['source_file_sha256']:
                raise ValueError('Alias bytes differ')
            aliases.append(alias)
        raw_results.append({'id': r['id'], 'source_file': r['source_file'],
                            'source_file_sha256': r['source_file_sha256'],
                            'verified_byte_identical_aliases': aliases,
                            'acquisition_metadata': {k: metadata[k] for k in
                                                     ('DATASET', 'DATE', 'TIME', 'RATE', 'VERT_UNITS', 'NUM_SAMPS')},
                            'fingerprint': fp})
    matches = []
    for r in processed:
        path = ROOT / 'tmp/dataset-survey' / r['source_file']
        if sha(path) != r['source_file_sha256']:
            raise ValueError('Workbook source hash mismatch')
        book = xlrd.open_workbook(path, on_demand=True)
        try:
            sheet = book.sheet_by_name(r['source_member'])
            width = 5 if r['protocol'] == 'cyclic-torsional-shear-source' else 3
            def rows():
                ended = False
                for row in range(21, sheet.nrows):
                    values = sheet.row_values(row, 1, 1 + width)
                    if all(v in ('', None) for v in values):
                        ended = True
                    elif ended:
                        raise ValueError('Acquisition resumes after blank row')
                    else:
                        yield values
            workbook_rows = list(rows())
            fp = fingerprint(workbook_rows)
        finally:
            book.release_resources()
        if sha(path) != r['source_file_sha256']:
            raise ValueError('Workbook changed during audit')
        exact = [v['id'] for v in raw_results if v['fingerprint'] == fp]
        prefixes = []
        for raw_id, raw_rows in raw_content.items():
            if len(raw_rows) < len(workbook_rows) or len(raw_rows[0]) != width:
                continue
            if fingerprint(raw_rows[:len(workbook_rows)]) == fp:
                prefixes.append({'raw_acquisition_id': raw_id,
                                 'raw_first_sample': 1, 'raw_last_sample': len(workbook_rows),
                                 'omitted_trailing_rows': len(raw_rows) - len(workbook_rows)})
        matches.append({'curated_phase_id': r['id'], 'source_file': r['source_file'],
                        'source_file_sha256': r['source_file_sha256'], 'sheet': r['source_member'],
                        'fingerprint': fp, 'exact_raw_content_matches': exact,
                        'exact_acquisition_prefix_matches': prefixes,
                        'status': 'unique_exact_match' if len(exact) == 1 else
                                  'unique_exact_prefix' if len(prefixes) == 1 else 'unresolved'})
    if sha(inventory_path) != inventory_sha:
        raise ValueError('Inventory changed during audit')
    result = {'paper_record_version': 1, 'date': '2026-10-31',
              'status': 'exact_three_phase_acquisition_correspondence_not_admission',
              'inputs_sha256': {'paper/study/ottawa_cyclic_inventory.json': inventory_sha,
                               'paper/scripts/audit_torsion_correspondence.py': sha(Path(__file__))},
              'method': 'SHA256 of sequential sample number plus all two/four acquisition '
                        'channels, parsed as finite binary64 numbers and packed little-endian; '
                        'signed zero canonicalized. Compare complete sequences and exact prefixes '
                        'of the raw acquisitions with the same length as each workbook phase. '
                        'No tolerance, decimal rounding, time shift, scaling, curve-shape matching '
                        'or model fitting. An initial exploratory source-precision segment search '
                        'showed loading matches were exact binary64 prefixes; final audit uses '
                        'the stronger prefix identity, including sample numbers.',
              'exposure': 'Entire raw acquisitions and pasted workbook phase channels '
                          'channels traversed for fingerprints. No numeric histories retained '
                          'in this record, plotting/scoring/threshold analysis or split assignment. '
                          'A preliminary raw-file header inspection also displayed initial rows.',
              'limits': 'Identity of pasted acquisition content does not validate calibration, '
                        'processing, physical specimen independence or cross-campaign reuse. '
                        'Channel names/units are not inferred from numerical identity.',
              'raw_acquisitions': raw_results, 'workbook_matches': matches}
    (ROOT / 'paper/study/torsion_acquisition_correspondence.json').write_text(
        json.dumps(result, indent=2) + '\n')
    for row in matches:
        print(row['curated_phase_id'], row['status'], row['exact_acquisition_prefix_matches'])


if __name__ == '__main__':
    main()
