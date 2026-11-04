"""Validate three retained current engines through pure package guards.

No provisioning, compilation, compiled-module loading or material execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ENGINES = {
    'norsand': 'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/norsand/engine',
    'interface2016': 'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine',
    'maxwell': 'docs/ingestion/vibe-2026/maxwell-refresh-v1/execution-v1/engine',
}

REQUIRED = {key: ('refresh-qualification.json', 'qualification-pending.json', 'build-review.json',
                  'atlas_path_capability.mjs', 'atlas_path_capability.wasm',
                  'generated/path_catalogue.json', 'generated/path_models.hpp', 'generated/path_api.cpp')
            for key in ('norsand', 'interface2016')}
REQUIRED['maxwell'] = ('maxwell.js', 'maxwell.wasm', 'generated/models.json',
                       'maxwell-qualification.json', 'build-review.json')


def selected_engines(plan_path=None, plan_sha256=None):
    if plan_path is None:
        if plan_sha256 is not None:
            raise ValueError('Plan hash requires explicit selection')
        return dict(ENGINES)
    from tools.qualify_controlled_path_refresh import load_plan, plan_layout
    load_plan(plan_path, plan_sha256)
    packet, _ = plan_layout(plan_path)
    result = dict(ENGINES)
    for key in ('norsand', 'interface2016'):
        result[key] = str(packet/'execution-v2'/key/'engine')
    return result


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def repo_path(name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('Expected repository-relative asset path: '+str(name))
    current = ROOT
    for part in path.parts:
        current = current/part
        if current.is_symlink():
            raise ValueError('Symlink dependency path: '+str(name))
    if not current.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Dependency path escapes repository: '+str(name))
    return current


def tree_snapshot(directory):
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('Missing or nonregular dependency directory: '+str(directory))
    files = {}
    for path in sorted(directory.rglob('*')):
        mode = path.lstat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise ValueError('Nonregular dependency member: '+str(path))
        files[path.relative_to(directory).as_posix()] = sha(path)
    if not files:
        raise ValueError('Empty dependency directory: '+str(directory))
    return files


def engine_snapshot(engines=ENGINES):
    result = {}
    for key,name in engines.items():
        files = tree_snapshot(repo_path(name))
        if not set(REQUIRED[key]).issubset(files):
            raise ValueError('Required current qualification/artifacts missing: '+key)
        result[key] = dict(path=name, files=files)
    return result


def source_snapshot(plan_path=None, plan_sha256=None):
    from tools.qualify_controlled_path_refresh import load_plan, PLAN
    from tools.build_maxwell_laboratory import source_manifest
    selected = PLAN if plan_path is None else Path(plan_path)
    files = dict(load_plan(selected, plan_sha256)['source_closure'])
    for name,digest in source_manifest()['files'].items():
        if name in files and files[name] != digest:
            raise ValueError('Current source manifests disagree: '+name)
        files[name] = digest
    names = [selected.as_posix(), 'catalogue/approved-models.json', 'catalogue/source-archive-map.json',
             'tools/check_current_dependency_assets.py', 'tools/build_controlled_path_web.py',
             'tools/build_interface2016_web.py', 'tools/build_maxwell_laboratory.py']
    for name in names:
        path = repo_path(name)
        if not stat.S_ISREG(path.stat().st_mode):
            raise ValueError('Nonregular source receipt: '+name)
        files[name] = sha(path)
    # Review/approval/source receipt integrity is checked by each bundler, then
    # their exact consumed scientific assets are hashed in its temporary package.
    return dict(sorted(files.items()))


def bundlers():
    from tools.build_controlled_path_web import bundle as norsand
    from tools.build_interface2016_web import bundle as interface2016
    from tools.build_maxwell_laboratory import bundle as maxwell
    return dict(norsand=norsand, interface2016=interface2016, maxwell=maxwell)


def output_directory(value, engines=ENGINES):
    path = Path(value).absolute()
    if '..' in path.parts or path.exists() or path.is_symlink() or any(p.is_symlink() for p in path.parents):
        raise ValueError('Refusing existing or unsafe guard evidence directory: '+str(value))
    for name in engines.values():
        if path.resolve().is_relative_to((ROOT/name).resolve()):
            raise ValueError('Guard output must not modify retained engine inputs')
    path.mkdir(parents=True, exist_ok=False)
    return path


def check(output, plan_path=None, plan_sha256=None):
    engines = selected_engines(plan_path, plan_sha256)
    output = output_directory(output, engines)
    report = dict(kind='current-dependency-package-guards-v1', status='failed', compiled_calls=0,
                  scope='Current retained assets, scientific approvals and exact pure package guards; no new numerical/browser/live qualification.',
                  packages={})
    try:
        report['before'] = dict(engines=engine_snapshot(engines), sources=source_snapshot(plan_path, plan_sha256))
        with tempfile.TemporaryDirectory(prefix='atlas-current-dependency-guards-') as temporary:
            actions = bundlers()
            if set(actions) != set(engines):
                raise ValueError('All three fixed dependency guards are required')
            for key,name in engines.items():
                destination = Path(temporary)/key
                identity = actions[key](destination, repo_path(name))
                report['packages'][key] = dict(identity=identity, files=tree_snapshot(destination))
        report['after'] = dict(engines=engine_snapshot(engines), sources=source_snapshot(plan_path, plan_sha256))
        if report['before'] != report['after']:
            raise ValueError('Dependency/source changed during package guards')
        report['status'] = 'passed-source-and-retained-asset-guards'
    except BaseException as error:
        report['failure'] = dict(type=type(error).__name__, message=str(error))
        try:
            report['after'] = dict(engines=engine_snapshot(engines), sources=source_snapshot(plan_path, plan_sha256))
        except BaseException as after_error:
            report['after_capture_failure'] = dict(type=type(after_error).__name__,message=str(after_error))
        raise
    finally:
        with (output/'report.json').open('x') as receipt:
            json.dump(report, receipt, indent=2, allow_nan=False)
            receipt.write('\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--controlled-plan', type=Path)
    parser.add_argument('--controlled-plan-sha256')
    args=parser.parse_args()
    result=check(args.output, args.controlled_plan, args.controlled_plan_sha256)
    print(json.dumps(dict(status=result['status'], compiled_calls=0, report=str(args.output/'report.json'))))


if __name__ == '__main__':
    main()
