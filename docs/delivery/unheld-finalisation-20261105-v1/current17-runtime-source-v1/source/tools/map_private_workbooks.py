"""Extract explicitly labelled worksheet channels for local admission review.

Source rows remain authoritative. Candidate axes describe source quantities;
they do not establish model compatibility, compression sign or initial state.
No permission-held measurements or workbook notes are written outside tmp.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.measurement_units import UNITS


# Exact labels observed in the standard workbooks. Missing units and ambiguous
# labels are deliberately absent; stress p without a prime is not effective p.
QUANTITIES = {
    'epax=dh/h0': 'axial_strain', 'epax = dh/h0': 'axial_strain',
    'eps = dh/h0': 'axial_strain', 'epv=dV/V0': 'volumetric_strain',
    'epv': 'volumetric_strain', "p'": 'effective_mean_stress',
    'q': 'deviatoric_stress', 'sig': 'axial_stress',
    "sigrad'": 'effective_radial_stress', 'sigrad': 'radial_stress',
    'mean stress p': 'mean_stress_unspecified', 'p': 'mean_stress_unspecified',
    'G': 'shear_modulus', 'G smallstrain': 'shear_modulus',
    'epsh smallstrain': 'source_small_strain', 'e': 'void_ratio',
    'sieve size': 'grain_size', 'passing': 'percent_passing',
}
PAIRS = [
    ('axial_strain', 'deviatoric_stress'),
    ('effective_mean_stress', 'deviatoric_stress'),
    ('axial_strain', 'volumetric_strain'),
    ('axial_stress', 'axial_strain'),
    ('mean_stress_unspecified', 'volumetric_strain'),
    ('mean_stress_unspecified', 'shear_modulus'),
    ('grain_size', 'percent_passing'),
]


def channel(index, label):
    if not isinstance(label, str):
        return None
    match = re.fullmatch(r'\s*(.*?)\s*\[([^\]]+)\]\s*', label)
    if not match:
        return None
    name, unit = match.groups()
    conversion = UNITS.get(unit)
    quantity = QUANTITIES.get(name)
    return dict(index=index, label=label, quantity=quantity,
                source_unit=unit, unit=conversion[0] if conversion else unit,
                conversion=dict(scale=conversion[1], offset=conversion[2]) if conversion else None)


def extract(rows):
    """Keep independent labelled blocks separate; never join by row proximity."""
    blocks = []
    for offset, row in enumerate(rows):
        cells = row['cells']
        columns = [c for i, label in enumerate(cells) if (c := channel(i, label))]
        if len(columns) < 2:
            continue
        labels = [c['label'] for c in columns]
        duplicate = len(labels) != len(set(labels))
        block = dict(header_excel_row=row['excel_row'], columns=columns,
                     candidate_axes=[], rows=[], warnings=[])
        if duplicate:
            block['warnings'].append('Duplicate source header labels; candidate axes withheld.')
        known = Counter(c['quantity'] for c in columns if c['quantity'])
        converted = {c['quantity'] for c in columns if c['conversion']}
        for x, y in PAIRS:
            if not duplicate and known[x] == known[y] == 1 and x in converted and y in converted:
                block['candidate_axes'].append(dict(x=x, y=y))
        for source in rows[offset+1:]:
            values = source['cells']
            # A new label row terminates this block, including malformed headers.
            if sum(isinstance(v, str) for v in values) >= 2:
                break
            native = {}; standardized = {}
            for c in columns:
                i = c['index']
                value = values[i] if i < len(values) else None
                if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
                    native[str(i)] = value
                    if c['conversion']:
                        standardized[str(i)] = value*c['conversion']['scale']+c['conversion']['offset']
            if native:
                block['rows'].append(dict(excel_row=source['excel_row'], native=native, values=standardized))
        if block['rows']:
            # A labelled pair must have at least one co-observed numeric row.
            keys = {c['quantity']: str(c['index']) for c in columns if c['quantity'] and c['conversion']}
            block['candidate_axes'] = [p for p in block['candidate_axes'] if any(
                keys[p['x']] in r['values'] and keys[p['y']] in r['values'] for r in block['rows'])]
            blocks.append(block)
    return blocks


def read_table(path, expected):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('Private source checksum mismatch: '+path.name)
    with gzip.open(path, 'rt') as stream:
        metadata = json.loads(next(stream))['metadata']
        rows = [json.loads(line) for line in stream]
    return metadata, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'tmp/private-measurements')
    parser.add_argument('--output', type=Path, default=ROOT/'tmp/private-workbook-mappings')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT/'tmp').resolve()):
        parser.error('Permission-held output must remain under ignored tmp')
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((args.input/'index.json').read_text())
    sources = [e for e in manifest['entries'] if e['source_id'] == 'soilmodels-standard']
    notes = {}
    for e in sources:
        if e['sheet'] == 'NOTES':
            _, rows = read_table(args.input/e['path'], e['sha256'])
            notes[e['member']] = rows
    entries = []
    for e in sources:
        metadata, rows = read_table(args.input/e['path'], e['sha256'])
        blocks = extract(rows) if e['sheet'] != 'NOTES' else []
        record = dict(source_id=e['source_id'], member=e['member'], sheet=e['sheet'],
                      source_table=e['path'], source_table_sha256=e['sha256'],
                      public_hosting=False, model_overlay_eligible=False,
                      source_metadata=metadata, workbook_notes=notes.get(e['member'], []),
                      source_context=[r for r in rows[:12] if any(isinstance(v,str) for v in r['cells'])],
                      blocks=blocks, warnings=[
                          'Dataset redistribution permission unresolved.',
                          'Source-labelled axes only; sign, protocol and initial-state admission remain unverified.',
                          'Original table retains omitted, unlabelled and nonnumeric cells.'])
        path = e['path'].replace('.jsonl.gz', '.json.gz')
        with gzip.open(output/path, 'wt') as stream:
            json.dump(record, stream, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
        entries.append(dict(member=e['member'], sheet=e['sheet'], path=path,
                            sha256=hashlib.sha256((output/path).read_bytes()).hexdigest(),
                            blocks=len(blocks), mapped_rows=sum(len(b['rows']) for b in blocks),
                            candidate_axis_pairs=sum(len(b['candidate_axes']) for b in blocks),
                            duplicate_header_blocks=sum(bool(b['warnings']) for b in blocks)))
    result = dict(format='atlas-private-workbook-mappings-v1', public_hosting=False,
                  model_overlay_eligible=False, entries=entries)
    (output/'index.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(workbooks=len({e['member'] for e in entries}), sheets=len(entries),
                         sheets_with_blocks=sum(bool(e['blocks']) for e in entries),
                         mapped_rows=sum(e['mapped_rows'] for e in entries),
                         candidate_axis_pairs=sum(e['candidate_axis_pairs'] for e in entries),
                         duplicate_header_blocks=sum(e['duplicate_header_blocks'] for e in entries))))


if __name__ == '__main__':
    main()
