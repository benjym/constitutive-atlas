"""Run the unchanged saved DP assessor in its exact original source context.

Only Node's saved-JSON assessment branch executes. No Wasm/native artifact is
loaded, no constitutive request is made and no historical file is overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from check import HERE, ROOT, assess, read_json, require, within


def replay():
    work = read_json(HERE / 'work-packages.json')
    assess(ROOT, work, read_json(HERE / 'decisions-template.json'))
    bindings = read_json(HERE / 'dp-replay-bindings.json')
    freeze_path = bindings['original_freeze']
    freeze_bytes = within(ROOT, freeze_path).read_bytes()
    require(hashlib.sha256(freeze_bytes).hexdigest() == bindings['original_freeze_sha256'],
            'original freeze changed')
    freeze = read_json(ROOT / freeze_path)
    selected = {entry['path']: entry for entry in bindings['changed_live_dependencies']}
    require(len(selected) == len(bindings['changed_live_dependencies']), 'duplicate replay binding')
    require(len(freeze['files']) == bindings['original_dependencies'], 'original dependency count changed')
    with tempfile.TemporaryDirectory(prefix='atlas-dp-saved-closure-') as temporary:
        context = Path(temporary) / 'source'
        context.mkdir()
        for name, expected in freeze['files'].items():
            entry = selected.get(name)
            if entry:
                require(entry['sha256'] == expected, 'binding is not in original freeze')
            source = within(ROOT, entry['selected'] if entry else name)
            require(hashlib.sha256(source.read_bytes()).hexdigest() == expected,
                    'original replay input missing or changed: ' + name)
            destination = within(context, name)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        destination = within(context, freeze_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(freeze_bytes)
        base = 'docs/reviews/dp-dilatancy-web-v1/'
        output = Path(temporary) / 'assessment'
        command = ['node', str(context / base / 'check.mjs'), str(context),
                   'UNUSED-SAVED-REPLAY-ONLY', str(output), str(ROOT / base / 'results/raw.json')]
        process = subprocess.run(command, capture_output=True, text=True, check=True)
        expected = (ROOT / base / 'results/report.json').read_bytes()
        require((output / 'report.json').read_bytes() == expected,
                'original saved assessment did not reproduce exactly')
        report = read_json(output / 'report.json')
        return {'kind': 'dp-original-saved-replay-restored-v1', 'passed': True,
                'original_context_files': len(freeze['files']),
                'restored_historical_bindings': len(selected),
                'case_count': report['count'], 'report_byte_identical': True,
                'report_sha256': hashlib.sha256(expected).hexdigest(),
                'assessor_modified': False, 'acceptance_bounds_changed': False,
                'compiled_calls': 0, 'stdout': process.stdout.strip()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = json.dumps(replay(), indent=2) + '\n'
    if args.output:
        with args.output.open('x') as stream:
            stream.write(output)
    else:
        print(output, end='')


if __name__ == '__main__':
    main()
