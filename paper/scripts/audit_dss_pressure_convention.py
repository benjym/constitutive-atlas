"""Check a channel identity in the 17 pinned DSS CSVs; no model scores or splits.

This intentionally reads response columns for source-integrity review. It makes
no saturated-pore-pressure interpretation and does not release benchmark data.
"""
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inventory_path = ROOT / 'paper/study/ottawa_cyclic_inventory.json'
    inventory_sha = sha(inventory_path)
    inventory = json.loads(inventory_path.read_text())
    records = [r for r in inventory['records'] if r['source_id'] == 'leap-2018-dss']
    if len(records) != 17:
        raise ValueError('Review scope changed: expected the pinned 17 DSS files')
    results = []
    for record in records:
        path = ROOT / 'tmp/dataset-survey' / record['source_file']
        if sha(path) != record['source_file_sha256']:
            raise ValueError(f'Source changed: {path}')
        sums, lows, highs = [], [], []
        blank_rows = 0
        with path.open(newline='') as stream:
            reader = csv.reader(stream)
            header = [' '.join(x.split()) for x in next(reader)]
            if header != ['Cycle', 'Shear Strain', 'Shear Stress',
                          'Axial Strain', 'Axial Stress', 'Excess Pressure']:
                raise ValueError('Unexpected CSV convention')
            for row in reader:
                if not row or not any(x.strip() for x in row):
                    blank_rows += 1
                    continue
                if len(row) != 6:
                    raise ValueError('Unexpected row width')
                # Only these two channels are parsed. Preserve reported decimal
                # precision; rounding intervals are not sensor uncertainty.
                stress, pressure = Decimal(row[4]), Decimal(row[5])
                if not stress.is_finite() or not pressure.is_finite():
                    raise ValueError('Nonfinite channel value')
                total = stress + pressure
                half_width = (Decimal(10) ** stress.as_tuple().exponent
                              + Decimal(10) ** pressure.as_tuple().exponent) / 2
                sums.append(total)
                lows.append(total - half_width)
                highs.append(total + half_width)
        if not sums:
            raise ValueError('No rows')
        if sha(path) != record['source_file_sha256']:
            raise ValueError('Source changed during review')
        lower, upper = max(lows), min(highs)
        results.append({
            'id': record['id'], 'source_file': record['source_file'],
            'source_file_sha256': record['source_file_sha256'],
            'rows_checked': len(sums),
            'blank_rows_ignored': blank_rows,
            'median_stress_plus_pressure_kpa': str(statistics.median(sums)),
            'range_of_stress_plus_pressure_kpa': str(max(sums) - min(sums)),
            'common_reference_interval_kpa': [str(lower), str(upper)],
            'constant_reference_compatible_with_printed_rounding': lower <= upper,
        })
    if sha(inventory_path) != inventory_sha:
        raise ValueError('Inventory changed during review')
    report = {
        'paper_record_version': 1,
        'status': 'source_channel_identity_audit_not_benchmark_admission',
        'date': '2026-10-31',
        'exposure': 'All 17 DSS CSV files traversed; vertical-stress and excess-pressure '
                    'columns parsed. No response plotting, scoring, fitting or split selection.',
        'hypothesis': 'Axial Stress + Excess Pressure is a specimen-specific constant.',
        'rounding_qualification': 'Half a last printed decimal unit per channel; '
                                  'these bounds are format precision, not sensor accuracy.',
        'physical_limit': 'An algebraic identity cannot establish saturation, measured '
                          'pore-water pressure, lateral stress or apparatus correction validity.',
        'inputs_sha256': {
            'paper/study/ottawa_cyclic_inventory.json': inventory_sha,
            'paper/scripts/audit_dss_pressure_convention.py': sha(Path(__file__)),
        },
        'results': results,
    }
    output = ROOT / 'paper/study/dss_pressure_identity_audit.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    passed = sum(r['constant_reference_compatible_with_printed_rounding'] for r in results)
    print(f'Constant-reference rounding compatibility: {passed}/{len(results)} files')
    for result in results:
        print(result['id'], result['range_of_stress_plus_pressure_kpa'],
              result['common_reference_interval_kpa'])


if __name__ == '__main__':
    main()
