"""Audit only extracted development compression records and their source pins."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from analysis.compression_data import audit_oedometer
from analysis.reservations import POLICY_PATH, assert_development_ids


def audit(directory, manifest_path):
    manifest = read_json(manifest_path)
    expected = [identifier for s in manifest['sources'] for identifier in s['development_ids']]
    assert_development_ids(expected)
    ledger = read_json(directory/'extraction.json')
    if (ledger['manifest_sha256'] != digest(manifest_path) or
            ledger['reservation_sha256'] != digest(POLICY_PATH) or
            sorted(ledger['read_member_ids']) != sorted(expected)):
        raise ValueError('extraction inputs or expected member coverage differ')
    entries = {r['id']: r for r in ledger['experiments']}
    if len(entries) != len(expected) or set(entries) != set(expected):
        raise ValueError('extraction ledger has duplicate or missing IDs')
    tabulated = {r['id']: r for r in read_json(POLICY_PATH)['experiments']}
    results = []
    for identifier in expected:
        path = directory/'normalized'/f'{identifier}.json'
        if digest(path) != entries[identifier]['normalized_sha256']:
            raise ValueError('normalized compression record changed')
        record = read_json(path)
        if record['id'] != identifier or record['protocol'] != 'oedometer':
            raise ValueError('unexpected compression record identity or protocol')
        result = audit_oedometer(record)
        table_e = tabulated[identifier]['tabulated_void_ratio_at_zero_axial_stress']
        result.update(normalized_sha256=digest(path), member_sha256=entries[identifier]['member_sha256'],
                      tabulated_e0=table_e, file_initial_void_ratio=record['initial']['void_ratio'],
                      initial_e0_agrees_at_table_print_precision=abs(record['initial']['void_ratio']-table_e) <= .0005)
        results.append(result)
    return dict(paper_record_version=1, status='development_compression_audit_not_calibration_admission',
                extraction_sha256=digest(directory/'extraction.json'),
                manifest_sha256=digest(manifest_path), reservation_sha256=digest(POLICY_PATH),
                script_sha256=digest(__file__), analysis_sha256=digest(ROOT/'paper/analysis/compression_data.py'),
                read_member_ids=expected, experiments=results,
                limits=['No full initial effective stress is inferred from axial stress.',
                        'Zero-stress observations are retained, not passed to a positive-pressure constitutive law.',
                        'Printing precision is not measurement uncertainty.',
                        'Void ratio and axial strain are linked by oedometer kinematics; do not double-count information.',
                        'Positive-stress initialization, K0/history, model scope and the replay/objective protocol remain open.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=ROOT/'paper/results/compression-development-v1')
    parser.add_argument('--manifest', type=Path, default=ROOT/'paper/study/compression_sources.json')
    args = parser.parse_args()
    result = audit(args.data, args.manifest)
    write_json(args.data/'audit.json', result)
    lines = ['# Development compression audit', '',
             '| Test | Rows | Zero-stress rows | Stress reversals | Kinematic rounding ratio | Table e0 agrees |',
             '| --- | ---: | ---: | ---: | ---: | --- |']
    for r in result['experiments']:
        lines.append(f"| {r['id']} | {r['rows']} | {r['zero_axial_stress_rows']} | {r['stress_direction_changes']} | {r['maximum_print_rounding_ratio']:.3f} | {r['initial_e0_agrees_at_table_print_precision']} |")
    lines += ['', 'A kinematic rounding ratio below one means consistency within a bound derived from printed decimal precision, not a measurement-noise estimate.', '']
    lines += ['- '+s for s in result['limits']]
    (args.data/'audit.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))
