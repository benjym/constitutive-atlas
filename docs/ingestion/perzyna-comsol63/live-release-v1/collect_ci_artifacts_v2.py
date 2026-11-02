"""Retain authenticated CI uploads and assess their genuine numerical receipts.

No compiled artifact is executed by this collector. Original ZIP bytes stay private.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RELEASE = '106a9cf8c327c9c262a97eb86aa04dae3f6cadb8'
RUN = 41415383260
NAMES = ('perzyna-native-macos-26', 'perzyna-native-ubuntu-latest',
         'perzyna-paired-Linux', 'perzyna-paired-macOS')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def api(path):
    return json.loads(subprocess.check_output(['gh', 'api', 'repos/benjym/constitutive-atlas/' + path]))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private', required=True, type=Path)
    args = parser.parse_args()
    inventory = api('actions/runs/' + str(RUN) + '/artifacts?per_page=100')
    artifacts = inventory['artifacts']
    assert len(artifacts) == inventory['total_count']
    found = []
    for metadata in artifacts:
        name = metadata['name']
        if name not in NAMES:
            continue
        found.append(name)
        assert not metadata['expired']
        assert metadata['workflow_run']['head_sha'] == RELEASE
        archive = args.private / (name + '.zip')
        if not archive.exists():
            with archive.open('xb') as stream:
                subprocess.run(['gh', 'api', 'repos/benjym/constitutive-atlas/actions/artifacts/' + str(metadata['id']) + '/zip'], stdout=stream, check=True)
        assert metadata['digest'] == 'sha256:' + digest(archive.read_bytes())
        out = HERE / 'ci-artifacts-v2' / name
        if out.exists():
            assert json.loads((out / 'RESULT.json').read_text())['passed']
            continue
        out.mkdir(parents=True)
        result = dict(passed=False, name=name, release=RELEASE, run=RUN,
                      private_archive=str(archive), artifact=metadata)
        try:
            with zipfile.ZipFile(archive) as zipped:
                members = zipped.namelist()
                assert len(members) == len(set(members))
                summary = json.loads(zipped.read('summary.json'))
                paired = name.startswith('perzyna-paired-')
                assert summary['passed'] and summary['paired'] == paired
                expected = [k + '-' + op for k in (('native', 'wasm') if paired else ('native',)) for op in ('configure', 'build', 'capture', 'consumer', 'verify')]
                if paired:
                    expected += ['wasm-assessment', 'physical-parity']
                assert [x['name'] for x in summary['operations']] == expected
                for operation in summary['operations']:
                    assert operation['returncode'] == 0
                    assert digest(zipped.read(operation['name'] + '.log')) == operation['log_sha256']
                    if operation['name'].endswith('-build'):
                        assert operation['argv'][-2:] == ['--parallel', '1']
                selected = {'summary.json'}
                backends = {}
                for kind in (('native', 'wasm') if paired else ('native',)):
                    pre_bytes = zipped.read(kind + '-pre.json')
                    pre = json.loads(pre_bytes)
                    post = json.loads(zipped.read(kind + '-post.json'))
                    report_member = kind + '-raw-report.json' if kind == 'native' else 'wasm-assessment.log'
                    report = json.loads(zipped.read(report_member))
                    assert post['pre_receipt_sha256'] == digest(pre_bytes)
                    assert post['all_records_unchanged']
                    assert pre['snapshot']['current_release_source_not_historical_substitution']
                    assert pre['request']['target'] == 'atlas_perzyna_solver'
                    assert pre['request']['entrypoint'] == 'cpp/main.cpp'
                    assert report['passed'] and report['cases'] == 107 and report['raw_calls'] == 214 and report['numeric_comparisons'] == 6574
                    selected.update((report_member, kind + '-post.json'))
                    backends[kind] = dict(cases=report['cases'], raw_calls=report['raw_calls'], numeric_comparisons=report['numeric_comparisons'], source_and_build_records_unchanged=True, pre_receipt_sha256=digest(pre_bytes))
                if paired:
                    parity = json.loads(zipped.read('physical-parity.log'))
                    assert parity['passed'] and parity['cases'] == 107
                    assert parity['physical_numeric_comparisons'] == 15667
                    assert parity['relative_budget'] == 2e-10
                    assert parity['worst_scaled_difference'] <= 2e-10
                    selected.add('physical-parity.log')
                    result['physical_parity'] = parity
                for member in sorted(selected):
                    (out / member).write_bytes(zipped.read(member))
                (out / 'MEMBERS.json').write_text(json.dumps({n: dict(sha256=digest(zipped.read(n)), bytes=zipped.getinfo(n).file_size) for n in members if not n.endswith('/')}, indent=2) + '\n')
                result.update(passed=True, backends=backends, all_operation_exits_zero=True, operations=len(summary['operations']), zip_members=len(members))
        except Exception as error:
            result['error'] = repr(error)
            raise
        finally:
            (out / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
        print(name + ': PASS', flush=True)
    print(json.dumps({'available': sorted(found), 'pending': sorted(set(NAMES) - set(found))}))

if __name__ == '__main__':
    main()
