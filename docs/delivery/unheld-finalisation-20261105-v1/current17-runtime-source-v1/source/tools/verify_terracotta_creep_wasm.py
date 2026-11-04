"""Assess both C-ABI backends against the frozen scalar creep reference."""
import argparse
import hashlib
import json
import math
from pathlib import Path

from atlas.model import ROOT
from tools.terracotta_creep_study import assess_study, compare_response


TOLERANCE = 1e-7


def assess(report, reference, catalogue_hash):
    if (report.get('version') != 'terracotta-creep-wasm-parity-0.1'
            or report.get('relative_parity_tolerance') != TOLERANCE):
        raise ValueError('unexpected creep parity protocol')
    records = report.get('records', [])
    cases = {case['id']: case for case in reference['cases']}
    backends = {name: [] for name in ('native', 'wasm')}
    for record in records:
        if record.get('case') not in cases:
            raise ValueError('unexpected creep case')
        request = record['request']
        for name in backends:
            response = record[name]
            backends[name].append({
                'case': record['case'], 'relative_tolerance': record['relative_tolerance'],
                'request': request, 'response': response,
                'maximum_errors': compare_response(request, response, cases[record['case']]),
            })
        native, wasm = record['native'], record['wasm']
        errors = {key: 0 for key in ('state', 'strain', 'strain_rate', 'observables')}
        if len(native['points']) != len(wasm['points']):
            raise ValueError('creep backend point count differs')
        for left, right in zip(native['points'], wasm['points']):
            for key in errors:
                if len(left[key]) != len(right[key]):
                    raise ValueError('creep backend channel size differs')
                for a, b in zip(left[key], right[key]):
                    if a is None or b is None:
                        if a != b:
                            raise ValueError('creep backend masks differ')
                        continue
                    error = abs(a-b)/max(1, abs(a))
                    if not math.isfinite(error) or error > TOLERANCE:
                        raise ValueError('creep backend parity bound exceeded')
                    errors[key] = max(errors[key], error)
        if record.get('maximum_scaled_parity_errors') != errors:
            raise ValueError('creep parity metrics differ from retained responses')
    return {name: assess_study(rows, reference, catalogue_hash)
            for name, rows in backends.items()}


def verify_artifacts(report, paths):
    expected = {'request_matrix_sha256', 'wasm_loader_sha256',
                'wasm_binary_sha256', 'native_binary_sha256'}
    if set(paths) != expected or set(report.get('artifacts', {})) != expected:
        raise ValueError('incomplete creep artifact bindings')
    for key, path in paths.items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != report['artifacts'][key]:
            raise ValueError('creep artifact hash mismatch: '+key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--native', type=Path, default=ROOT/'build/atlas_research_solver')
    parser.add_argument('--wasm', type=Path, default=ROOT/'build-wasm/research.js')
    parser.add_argument('--catalogue', type=Path, default=ROOT/'build/research-generated/models.json')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_bytes())
    verify_artifacts(report, {
        'request_matrix_sha256': ROOT/'catalogue/investigations/terracotta-creep-v1/native.json',
        'wasm_loader_sha256': args.wasm, 'wasm_binary_sha256': args.wasm.with_suffix('.wasm'),
        'native_binary_sha256': args.native,
    })
    reference = json.loads((ROOT/'tests/reference/terracotta-2024-scalar-creep.json').read_bytes())
    summary = assess(report, reference, json.loads(args.catalogue.read_bytes())['sha256'])
    if args.output:
        args.output.write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    print('Prepared creep: both complete nine-case backends passed scalar-reference bounds and refinement.')


if __name__ == '__main__':
    main()
