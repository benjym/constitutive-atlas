"""Qualify the generated native catalogue and its model-specific numerical references."""
import argparse
from decimal import Decimal
import json
import os
from pathlib import Path
import sys

from check_md1997_numerical_ci import (
    MD, NATIVE, REFERENCE_FILES, ROOT, canonical, digest, json_read,
    record, require, run_process, write,
)

REFERENCE = ROOT / 'tools/md1997_decimal_reference_current17_v1'
SELECTOR = 'current-catalogue-v1'
sys.path.insert(0, str(REFERENCE))
from assess_saved import context, hexfloat, read, same_metadata


def current_catalogue(build):
    sources = {}
    for path in sorted((ROOT / 'models').glob('*.json')):
        model = json_read(path)
        require(model['id'] == path.stem, f'model ID does not match filename: {path}')
        sources[path.stem] = model
    generated = json_read(build / 'generated/models.json')
    require(set(generated) == {'schema_version', 'sha256', 'models'} and
            generated['schema_version'] == '0.1', 'generated catalogue schema')
    require(sources and generated['models'] == list(sources.values()),
            'generated catalogue differs from current model definitions; rebuild the solver')
    require(generated['sha256'] == digest(canonical(generated['models'])),
            'generated catalogue canonical hash mismatch')
    return sources, generated['sha256']


def assess_md(stdout, count, binding_hash):
    requests = read(REFERENCE / 'requests.json')
    reference = read(REFERENCE / 'reference.json')
    export = read(stdout)
    same_metadata({k: export[k] for k in ('identity', 'selector', 'status', 'models')}, {
        'identity': 'md1997-decimal-ad-export-current-catalogue-v1',
        'selector': SELECTOR, 'status': 'exported-unassessed', 'models': count,
    })
    bindings = {k: reference[k] for k in (
        'evaluator_sha256', 'policy_sha256', 'base_source_freeze_sha256', 'model_sha256')}
    bindings.update(request_sha256=REFERENCE_FILES['requests.json'],
                    reference_sha256=REFERENCE_FILES['reference.json'],
                    build_binding_sha256=binding_hash)
    same_metadata(export['bindings'], bindings)
    same_metadata(export['base'], {k: requests[k] for k in (
        'layout', 'state_hex', 'previous_hex', 'loading_hex', 'parameters_hex', 'scales_hex')})
    same_metadata(export['endpoints'], [
        {**row, 'domain': True, 'branch': True} for row in requests['endpoints']])
    same_metadata(export['cpp_checks'], {'rank13': True, 'rotation': True, 'other_models': True})
    ad = export['ad_hex']
    require(len(ad) == 14 and all(len(row) == 14 for row in ad), 'AD14x14 shape')
    ad = [[Decimal.from_float(hexfloat(x)) for x in row] for row in ad]
    secants = reference['data']['120']['secants']
    require(len(secants) == 28 and all(len(row) == 14 for row in secants), 'reference shape')
    failures = []
    comparisons = 0

    def compare(gate, col, row, x, y, tolerance):
        nonlocal comparisons
        comparisons += 1
        error = abs(x - y)
        budget = tolerance * max(1, abs(x), abs(y))
        if error >= budget:
            failures.append(dict(gate=gate, column=col, row=row, x=str(x), y=str(y),
                                 error=str(error), budget=str(budget)))

    with context(120):
        for col in range(14):
            for row in range(14):
                fd, half = (Decimal(secants[2 * col + level][row]) for level in (0, 1))
                require(fd.is_finite() and half.is_finite(), 'nonfinite reference secant')
                compare('AD/FD h', col, row, fd, ad[row][col], Decimal('3e-5'))
                compare('AD/FD h/2', col, row, half, ad[row][col], Decimal('3e-5'))
                compare('h/h2', col, row, fd, half, Decimal('1.5e-5'))
    return dict(comparisons=comparisons, failures=failures)


def run(build, output):
    build = build.resolve()
    output.mkdir(parents=True)
    report = {'identity': 'current-catalogue-numerical-v1', 'passed': False}
    try:
        models, catalogue_hash = current_catalogue(build)
        executable = build / 'atlas_numerical_tests'
        report.update(models=list(models), catalogue_sha256=catalogue_hash,
                      executable_sha256=record(executable)['sha256'])
        hash_stdout, hash_stderr = output / 'catalogue.stdout', output / 'catalogue.stderr'
        code = run_process([str(executable), '--catalogue-hash'], build, os.environ,
                           hash_stdout, hash_stderr, 30)
        require(code == 0 and hash_stdout.read_text().strip() == catalogue_hash,
                'native numerical executable was compiled from a different catalogue; rebuild it')
        env = dict(os.environ, ATLAS_NATIVE_FIXTURES=NATIVE, ATLAS_NUMERICAL_FIXTURES=SELECTOR)
        env.pop('ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256', None)
        if MD in models:
            for name, expected in REFERENCE_FILES.items():
                require(record(REFERENCE / name)['sha256'] == expected, f'MD1997 reference input: {name}')
            requests = read(REFERENCE / 'requests.json')
            model_hash = record(ROOT / 'models' / f'{MD}.json')['sha256']
            require(model_hash == requests['model_sha256'], 'MD1997 definition no longer matches its independent reference')
            binding = dict(identity='current-catalogue-md1997-binding-v1', model_sha256=model_hash,
                           catalogue_sha256=catalogue_hash, executable_sha256=report['executable_sha256'])
            write(output / 'build-binding.json', binding)
            binding_hash = record(output / 'build-binding.json')['sha256']
            env['ATLAS_MD1997_DECIMAL_BUILD_BINDING_SHA256'] = binding_hash

        stdout, stderr = output / 'native.stdout', output / 'native.stderr'
        report['returncode'] = run_process([str(executable)], build, env, stdout, stderr, 600)
        require(report['returncode'] == 0, f'native numerical checks failed: {stderr.read_text().strip()}')
        require(current_catalogue(build) == (models, catalogue_hash) and
                record(executable)['sha256'] == report['executable_sha256'],
                'catalogue or executable changed while running numerical checks')
        if MD in models:
            report['md1997'] = assess_md(stdout, len(models), binding_hash)
            require(not report['md1997']['failures'], 'MD1997 Decimal comparison failed; see result.json')
        report['passed'] = True
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        write(output / 'result.json', report)
    print(f"Native numerical checks passed for {len(models)} models"
          + (f"; {report['md1997']['comparisons']} MD1997 Decimal comparisons passed" if MD in models else ""))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, default=ROOT / 'build')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.build, args.output)
