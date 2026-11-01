"""Extract only printed test-state metadata; do not open experiment response files."""
import hashlib
import json
import re
import subprocess
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / 'paper/study'
MANIFEST = STUDY / 'dataset_methods_downloads.json'
LISTING = ROOT / 'tmp/dataset-survey/PRJ-3484-files.json'
OUTPUT = STUDY / 'leap2022_specimen_metadata.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads(MANIFEST.read_text())
    source = next(x for x in manifest['assets'] if x['name'].startswith('Summary Report'))
    pdf = ROOT / source['local_copy']
    if sha(pdf) != source['sha256'] or sha(LISTING) != manifest['inputs_sha256'][str(LISTING.relative_to(ROOT))]:
        raise ValueError('Pinned report or provider listing changed')
    # Read only report front matter/methods/tables, PDF pages 1-13, not appendix curves.
    text = subprocess.check_output(['pdftotext', '-f', '1', '-l', '13', '-layout', str(pdf), '-'], text=True)
    pages = text.split('\f')
    configs = {6: [(2, 7, 100, '0.600'), (3, 7, 40, '0.601')],
               8: [(4, 7, 40, '0.631'), (5, 4, 40, '0.588'), (6, 7, 40, '0.576')],
               10: [(7, 8, 100, '0.601'), (8, 7, 40, '0.601'), (9, 7, 40, '0.601')]}
    files = []
    pattern = re.compile(r'eo_0_(\d+)_sigv_(\d+)_CSR_0_(\d+)_Tau_(\d+)_\.csv')
    for item in json.loads(LISTING.read_text()):
        m = pattern.fullmatch(item['name'])
        if m:
            e, stress, csr, tau = m.groups()
            files.append({'path': item['path'], 'e_label': D(e) / 1000,
                          'stress': D(stress), 'csr': D(csr) / 1000, 'tau': D(tau)})
    records = []
    for page, tables in configs.items():
        lines = [line.split() for line in pages[page - 1].splitlines()
                 if re.match(r'^\s*\d+\s+\d{4}\s+0\.\d+\s+', line)]
        offset = 0
        for table, count, stress, group_e in tables:
            rows = lines[offset:offset + count]
            if len(rows) != count or [int(x[0]) for x in rows] != list(range(1, count + 1)):
                raise ValueError('Unexpected table layout or specimen numbering')
            for row in rows:
                no, rho, e, dr, csr = row[:5]
                alpha = D(row[5]) if table == 7 else D('0.25') if table == 8 else D('0.375') if table == 9 else D(0)
                candidates = [f for f in files if f['e_label'] == D(group_e)
                              and f['stress'] == stress and f['csr'] == D(csr)
                              and f['tau'] == alpha * stress]
                if len(candidates) != 1:
                    raise ValueError('Expected one nominal-condition filename candidate')
                # Conservative rounding interval diagnostic: permit half a final
                # digit for e (.001), Dr (.1%) AND both index limits (.01).
                e_val = D(e)
                dr_low = 100 * (D('.775') - (e_val + D('.0005'))) / (D('.775') - D('.505'))
                dr_high = 100 * (D('.785') - (e_val - D('.0005'))) / (D('.785') - D('.515'))
                compatible = dr_low <= D(dr) + D('.05') and dr_high >= D(dr) - D('.05')
                records.append({
                    'id': f'LEAP2022-report-table{table}-test{no}', 'pdf_page': page,
                    'table': table, 'test_number': int(no), 'reported_dry_density_kg_m3': int(rho),
                    'reported_void_ratio_eac': e, 'reported_relative_density_percent': dr,
                    'vertical_consolidation_stress_kpa': stress, 'csr': csr,
                    'static_shear_ratio': str(alpha), 'static_shear_stress_kpa': str(alpha * stress),
                    'relative_density_state': 'after_consolidation_and_static_shear' if alpha else 'after_consolidation',
                    'filename_candidate': candidates[0]['path'], 'filename_void_ratio_label': group_e,
                    'filename_void_ratio_equals_table_value': D(group_e) == e_val,
                    'correspondence_status': 'unique_nominal_condition_candidate_not_verified_raw_specimen_identity',
                    'relative_density_rounding_check': {
                        'compatible_with_printed_index_limits_allowing_rounding': compatible,
                        'possible_dr_percent_range': [str(dr_low), str(dr_high)],
                    },
                    'role': 'unassigned', 'scientific_admission': 'not_assessed',
                })
            offset += count
        if offset != len(lines):
            raise ValueError('Unparsed test-state row')
    if len(records) != 54 or len({r['filename_candidate'] for r in records}) != 54 or len(files) != 54:
        raise ValueError('Report/listing coverage is not 54 unique candidates')
    OUTPUT.write_text(json.dumps({
        'paper_record_version': 1, 'date': '2026-10-31',
        'status': 'assisted_printed_metadata_transcription_not_admission',
        'inputs_sha256': {str(p.relative_to(ROOT)): sha(p) for p in [MANIFEST, LISTING, Path(__file__).resolve()]},
        'source_sha256': source['sha256'], 'source_local_copy': source['local_copy'],
        'method': 'pdftotext -layout fixed-page table rows, source pages visually checked; retain state fields only, no threshold outcome values. Match candidates using filename group e, vertical stress, CSR and static shear stress; never curve similarity.',
        'rounding_diagnostic': 'Dr=100*(emax-e)/(emax-emin); emax=.78 and emin=.51 each allowed +/-.005, tabulated e +/-.0005 and Dr +/-.05 percentage point. Disjoint intervals identify internal incompatibility even under these allowances; overlapping intervals do not validate state or index measurements.',
        'coverage': {'test_state_rows': len(records), 'unique_filename_candidates': 54,
                     'filename_e_differs_from_individual_table_e': sum(not r['filename_void_ratio_equals_table_value'] for r in records),
                     'incompatible_dr_rows': [r['id'] for r in records if not r['relative_density_rounding_check']['compatible_with_printed_index_limits_allowing_rounding']]},
        'limits': ['Filename matching establishes nominal-condition correspondence only; no CSV contents read.',
                   'State timing for reported dry density is not explicitly reconciled with post-consolidation e.',
                   'Published threshold outcomes were exposed on the same report pages but not retained as calibration data.',
                   'No state correction, fit, split assignment or shared atlas edit. Independent review pending.'],
        'records': records,
    }, indent=2) + '\n')
    print(json.loads(OUTPUT.read_text())['coverage'])


if __name__ == '__main__':
    main()
