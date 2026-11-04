"""Prospective controlled-path regression receipts; execution is coordinator-only.

Importing this module reads no artifacts and executes no numerical code.  The
explicit `run` command is the only operation that executes build/test commands.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PACKET = Path('docs/ingestion/vibe-2026/controlled-path-refresh-v1')
PLAN = PACKET/'plan-v5.json'
CURRENT_PACKET = Path('docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1')
CURRENT_PLAN = CURRENT_PACKET/'plan-v1.json'
MODEL_PATHS = {
    'norsand': ['models/research/norsand/norsand-jefferies-1993-active-axial.json',
                'tests/fixtures/controlled-path/synthetic-curved.json',
                'tests/fixtures/controlled-path/synthetic-model.json'],
    'interface2016': ['models/research/interface2016/hvwe2016-reconciled-fixed-local.json'],
}
MODELS = {'norsand': 'norsand-jefferies-1993-active-axial',
          'interface2016': 'hvwe2016-reconciled-fixed-local'}
GENERATED = ('path_catalogue.json', 'path_models.hpp', 'path_api.cpp')
NORSAND = 'docs/ingestion/norsand-1993/e2-v3/'
INTERFACE = 'docs/ingestion/hypoplastic-interface-2016/'
GATES = {
    'norsand': dict(native_requests=58, wasm_requests=58, native_successes=40,
                    native_rejections=18, wasm_successes=40, wasm_rejections=18,
                    source_analytical=True, parity=True),
    'interface2016': dict(native_requests=59, wasm_requests=59,
                         full_finite_state_stress_and_bindings=True,
                         rollback_sentinels_and_recovery=True, parity=True),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(name):
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('Expected safe repository-relative path: '+str(name))
    resolved = (ROOT/path).resolve()
    if not resolved.is_relative_to(ROOT.resolve()):
        raise ValueError('Path escapes repository: '+str(name))
    return resolved


def plan_layout(plan_path=PLAN):
    plan_path = Path(plan_path)
    if plan_path == PLAN:
        return PACKET, '.local/controlled-path-refresh-v2'
    if plan_path != CURRENT_PLAN:
        raise ValueError('Unknown controlled-path plan selection')
    # Fixed allowlist plus lexical and no-symlink validation, before reading.
    relative(plan_path)
    current = ROOT
    for part in plan_path.parts:
        current = current/part
        if current.is_symlink():
            raise ValueError('Symlink controlled-path plan selection')
    return CURRENT_PACKET, '.local/controlled-path-refresh-20261105-v1'


def write_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as output:
        json.dump(data, output, indent=2, allow_nan=False)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())


def closure():
    names = set()
    for directory, pattern in [('atlas', '*.py'), ('schemas', '*.json'),
                               ('cpp/include/atlas', '*.hpp'), ('cpp/scalar-functions', '*'),
                               ('models', '*.json'), ('tests/fixtures', '*.json'),
                               ('initialization', '*.json'), ('catalogue/path-examples', '*.json')]:
        names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/directory).rglob(pattern)
                     if p.is_file() and '__pycache__' not in p.parts)
    names.update(['cmake/controlled-path/CMakeLists.txt', 'cmake/AtlasScalarFunctions.cmake',
                  'tools/generate_controlled_path.py', 'tools/qualify_controlled_path_refresh.py',
                  'tools/build_controlled_path_web.py', 'tools/build_interface2016_web.py',
                  'tools/test_interface2016_package.mjs',
                  'tests/test_controlled_path.py', 'tests/test_formulation.py', 'tests/test_state_contract.py',
                  'tests/test_stress_scope.py', 'tests/historical_generation.py',
                  NORSAND+'run_native_requests_v2.py', NORSAND+'run_wasm_requests_v2.mjs',
                  NORSAND+'backend-requests-v2.json', NORSAND+'check_backend_results_v3.py',
                  INTERFACE+'implementation-v1/check_backend_results_v2.py',
                  INTERFACE+'implementation-v1/backend-requests.json',
                  INTERFACE+'implementation-v1/backend-expectations.json',
                  INTERFACE+'implementation-v1/references.json',
                  INTERFACE+'execution-v1/check_parity_v2.py',
                  INTERFACE+'execution-v1/source-freeze-v2.json'])
    for paths in MODEL_PATHS.values():
        names.update(paths)
    return {name: sha(relative(name)) for name in sorted(names)}


def commands(library, plan_path=PLAN):
    """Exact original CI gates, sequential explicit-target builds and durable logs."""
    packet, build_prefix = plan_layout(plan_path)
    rows = []
    def add(identity, argv):
        rows.append(dict(id=identity, argv=argv))
    for name, argv in [('cmake-version',['cmake','--version']), ('node-version',['node','--version']),
                       ('python-version',['python3','--version']), ('emscripten-version',['emcc','--version'])]:
        add(name, argv)
    add('contracts', ['python3', '-B', '-m', 'unittest', 'tests.test_controlled_path',
                     'tests.test_formulation', 'tests.test_state_contract', '-q'])
    for backend in ('native', 'wasm'):
        for key in MODEL_PATHS:
            build = build_prefix+'/'+key+'-'+backend
            out = str(packet/'execution-v2'/key)
            # Source paths use $ROOT substitution resolved by run, rather than
            # freezing local-only checkout paths into durable evidence.
            model_list = ';'.join('$ROOT/'+p for p in MODEL_PATHS[key])
            configure = ['cmake', '-S', 'cmake/controlled-path', '-B', build,
                         '-DCMAKE_BUILD_TYPE='+('Debug' if key == 'norsand' else 'Release'),
                         '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON', '-DATLAS_PATH_MODELS='+model_list]
            add(key+'-'+backend+'-configure', (['emcmake'] if backend == 'wasm' else [])+configure)
            add(key+'-'+backend+'-build', ['cmake', '--build', build, '--target',
                                         'atlas_path_capability', '--parallel', '1'])
            req = (NORSAND+'backend-requests-v2.json' if key == 'norsand' else
                   INTERFACE+'implementation-v1/backend-requests.json')
            result = out+'/'+backend+'.json'
            if backend == 'native':
                argv = ['python3', '-B', NORSAND+'run_native_requests_v2.py', build+'/'+library, req, result]
            else:
                argv = ['node', NORSAND+'run_wasm_requests_v2.mjs', build+'/atlas_path_capability.mjs',
                        build+'/atlas_path_capability.wasm', req, result]
            add(key+'-'+backend+'-requests', argv)
            if key == 'norsand':
                results = [out+'/native.json', result] if backend == 'wasm' else [result]
                add(key+'-'+backend+'-checks', ['python3', '-B', NORSAND+'check_backend_results_v3.py', req]+results)
            else:
                add(key+'-'+backend+'-checks', ['python3', '-B', INTERFACE+'implementation-v1/check_backend_results_v2.py',
                                              result, '--output', out+'/'+backend+'-check.json'])
                if backend == 'wasm':
                    add(key+'-parity', ['python3', '-B', INTERFACE+'execution-v1/check_parity_v2.py',
                                      out+'/native.json', result, out+'/parity.json'])
    return rows


def prepare(plan_path=PLAN):
    library = 'libatlas_path_capability.dylib' if sys.platform == 'darwin' else 'libatlas_path_capability.so'
    plan_layout(plan_path)
    data = dict(identity=('controlled-path-refresh-plan-v5' if Path(plan_path) == PLAN else 'controlled-path-refresh-plan-20261105-v1'), schema_version=1,
                source_closure=closure(), models=MODELS, definitions=MODEL_PATHS,
                gates=GATES, native_library=library, commands=commands(library, plan_path),
                policy='Original cases/checkers/bounds unchanged; actual native and Wasm gates plus separate exact build review required.')
    write_new(relative(plan_path), data)
    return data


def load_plan(plan_path=PLAN, expected_sha256=None):
    plan_layout(plan_path)
    if Path(plan_path) != PLAN and (not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or any(c not in '0123456789abcdef' for c in expected_sha256)):
        raise ValueError('Explicit selected plan SHA256 required')
    if expected_sha256 is not None and sha(relative(plan_path)) != expected_sha256:
        raise ValueError('Selected controlled-path plan hash changed')
    plan = json.loads(relative(plan_path).read_text())
    if Path(plan_path) != PLAN and plan.get('identity') != 'controlled-path-refresh-plan-20261105-v1':
        raise ValueError('Wrong selected controlled-path plan identity')
    if plan['source_closure'] != closure() or plan['gates'] != GATES or plan['models'] != MODELS or plan['definitions'] != MODEL_PATHS:
        raise ValueError('Current controlled-path source closure/contract changed')
    if plan['commands'] != commands(plan['native_library'], plan_path):
        raise ValueError('Frozen controlled-path command corpus changed')
    return plan


def run(implementation_run, plan_path=PLAN, expected_sha256=None):
    if not implementation_run.strip():
        raise ValueError('Implementation run identity required')
    plan = load_plan(plan_path, expected_sha256)
    packet, build_prefix = plan_layout(plan_path)
    base = relative(packet/'execution-v2')
    base.mkdir(parents=True, exist_ok=False)
    for key in MODEL_PATHS:
        (base/key).mkdir()
    write_new(base/'run.json', dict(implementation_run=implementation_run, plan_sha256=sha(relative(plan_path)),
                                  platform=platform.platform(), python=sys.version))
    for row in plan['commands']:
        load_plan(plan_path, expected_sha256)
        argv = [arg.replace('$ROOT', str(ROOT)) for arg in row['argv']]
        logfile = base/(row['id']+'.log')
        started = time.time()
        with logfile.open('xb') as output:
            result = subprocess.run(argv, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
            output.flush()
            os.fsync(output.fileno())
        receipt = dict(id=row['id'], argv=argv, cwd='repository-root', repository_root=str(ROOT),
                       started_unix=started, finished_unix=time.time(), returncode=result.returncode,
                       log=dict(path=logfile.relative_to(ROOT).as_posix(), sha256=sha(logfile)),
                       plan_sha256=sha(relative(plan_path)))
        write_new(base/(row['id']+'.receipt.json'), receipt)
        if result.returncode:
            raise RuntimeError('Frozen command failed; evidence retained: '+row['id'])
    load_plan(plan_path, expected_sha256)
    return collect(plan_path, expected_sha256)


def check_backend_identity(key, artifacts, results):
    names = {Path(name).name:name for name in results}
    native = json.loads(relative(names['native.json']).read_text())
    wasm = json.loads(relative(names['wasm.json']).read_text())
    library = next(value for name,value in artifacts.items() if name.startswith('native/'))
    request = NORSAND+'backend-requests-v2.json' if key == 'norsand' else INTERFACE+'implementation-v1/backend-requests.json'
    if (native.get('library_sha256') != library
            or wasm.get('module_sha256') != artifacts['atlas_path_capability.mjs']
            or wasm.get('wasm_sha256') != artifacts['atlas_path_capability.wasm']
            or native.get('request_sha256') != sha(relative(request))
            or wasm.get('request_sha256') != sha(relative(request))):
        raise ValueError('Backend report does not bind actual qualified artifacts/requests')


def collect(plan_path=PLAN, expected_sha256=None):
    plan = load_plan(plan_path, expected_sha256)
    packet, build_prefix = plan_layout(plan_path)
    base = relative(packet/'execution-v2')
    run_info = json.loads((base/'run.json').read_text())
    if run_info['plan_sha256'] != sha(relative(plan_path)):
        raise ValueError('Run plan changed')
    receipts = {}
    for row in plan['commands']:
        path = base/(row['id']+'.receipt.json')
        receipt = json.loads(path.read_text())
        if receipt['returncode'] != 0 or receipt['plan_sha256'] != sha(relative(plan_path)) or receipt['argv'] != [a.replace('$ROOT', str(ROOT)) for a in row['argv']]:
            raise ValueError('Missing/failed exact command: '+row['id'])
        if sha(relative(receipt['log']['path'])) != receipt['log']['sha256']:
            raise ValueError('Command log changed')
        receipts[path.relative_to(ROOT).as_posix()] = sha(path)
        receipts[receipt['log']['path']] = receipt['log']['sha256']
    for key in MODEL_PATHS:
        output = base/key/'engine'
        output.mkdir(exist_ok=False)
        native = relative(build_prefix+'/'+key+'-native')
        wasm = relative(build_prefix+'/'+key+'-wasm')
        artifacts = {}
        for name, original in [('native/'+plan['native_library'], native/plan['native_library']),
                               ('atlas_path_capability.mjs', wasm/'atlas_path_capability.mjs'),
                               ('atlas_path_capability.wasm', wasm/'atlas_path_capability.wasm')]:
            target = output/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, target)
            artifacts[name] = sha(target)
        generated = {}
        native_generated = {}
        for name in GENERATED:
            target = output/'generated'/name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(wasm/'generated'/name, target)
            generated[name] = sha(target)
            native_generated[name] = sha(native/'generated'/name)
            if generated[name] != native_generated[name]:
                raise ValueError('Native/Wasm generated source mismatch: '+name)
        results = {p.relative_to(ROOT).as_posix():sha(p) for p in sorted((base/key).glob('*.json'))}
        metadata = {}
        for backend, build in [('native', native), ('wasm', wasm)]:
            for name in ['CMakeCache.txt', 'compile_commands.json']:
                target = output/'build-metadata'/backend/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(build/name, target)
                metadata[target.relative_to(output).as_posix()] = sha(target)
        check_backend_identity(key, artifacts, results)
        binding = dict(model=MODELS[key], model_sha256=sha(relative(MODEL_PATHS[key][0])),
                       plan=dict(path=Path(plan_path).as_posix(), sha256=sha(relative(plan_path))),
                       source_closure=plan['source_closure'], artifacts=artifacts,
                       generated=generated, native_generated=native_generated,
                       commands=receipts, results=results, build_metadata=metadata)
        write_new(output/'qualification-pending.json', dict(schema_version='controlled-path-refresh-1',
                  status='passed-original-backend-gates-pending-independent-review', model=MODELS[key],
                  implementation_run=run_info['implementation_run'], binding=binding, gates=GATES[key]))
    return dict(status='pending-independent-build-review', compiled_gate_commands=len(plan['commands']))


def finalize(build):
    build = Path(build)
    pending = json.loads((build/'qualification-pending.json').read_text())
    accepted = json.loads((build/'build-review.json').read_text())
    if (accepted.get('schema_version') != 'controlled-path-refresh-review-1' or accepted.get('status') != 'accepted'
            or accepted.get('binding') != pending['binding'] or accepted.get('gates') != pending['gates']
            or not accepted.get('reviewer_run', '').strip() or accepted['reviewer_run'] == pending['implementation_run']
            or accepted.get('blocking_findings') != []
            or accepted.get('qualification_pending_sha256') != sha(build/'qualification-pending.json')):
        raise ValueError('Separate exact independent build acceptance required')
    pending['status'] = 'passed'
    pending['independent_review'] = dict(path='build-review.json', sha256=sha(build/'build-review.json'))
    write_new(build/'refresh-qualification.json', pending)
    return dict(status='finalized', path=str(build/'refresh-qualification.json'))


def validate_refresh(build, model):
    """Optional additive packaging branch. Historical branches stay unchanged."""
    build = Path(build)
    path = build/'refresh-qualification.json'
    if not path.is_file():
        return None
    data = json.loads(path.read_text())
    binding = data.get('binding', {})
    plan_pin = binding.get('plan', {})
    plan_path = Path(plan_pin.get('path', ''))
    plan = load_plan(plan_path, plan_pin.get('sha256'))
    packet, _ = plan_layout(plan_path)
    key = next(k for k, value in MODELS.items() if value == model)
    if (data.get('schema_version') != 'controlled-path-refresh-1' or data.get('status') != 'passed'
            or data.get('model') != model or data.get('gates') != GATES[key]
            or not data.get('implementation_run', '').strip()
            or binding.get('model') != model or binding.get('model_sha256') != sha(relative(MODEL_PATHS[key][0]))
            or binding.get('source_closure') != plan['source_closure']
            or binding.get('plan') != dict(path=Path(plan_path).as_posix(), sha256=sha(relative(plan_path)))):
        raise ValueError('Fresh controlled-path qualification is stale/incomplete')
    if binding.get('generated') != {name:sha(build/'generated'/name) for name in GENERATED} or binding.get('native_generated') != binding['generated']:
        raise ValueError('Fresh generated source changed')
    artifact_names = {'native/'+plan['native_library'], 'atlas_path_capability.mjs', 'atlas_path_capability.wasm'}
    if set(binding.get('artifacts', {})) != artifact_names:
        raise ValueError('Native and Wasm artifacts required')
    for group, directory in [('artifacts', build), ('build_metadata', build), ('commands', ROOT), ('results', ROOT)]:
        if not binding.get(group):
            raise ValueError('Fresh qualification omits '+group)
        for name, digest in binding[group].items():
            target = relative(name) if directory == ROOT else directory/Path(name)
            if Path(name).is_absolute() or '..' in Path(name).parts or sha(target) != digest:
                raise ValueError('Fresh qualification evidence changed: '+name)
    if set(binding['commands']) != {str(packet/'execution-v2'/(r['id']+ext)) for r in plan['commands'] for ext in ('.receipt.json', '.log')}:
        raise ValueError('Fresh qualification omits exact commands/logs')
    for row in plan['commands']:
        receipt = json.loads(relative(str(packet/'execution-v2'/(row['id']+'.receipt.json'))).read_text())
        if (receipt.get('returncode') != 0 or receipt.get('plan_sha256') != sha(relative(plan_path))
                or not Path(receipt.get('repository_root', '')).is_absolute()
                or receipt.get('argv') != [arg.replace('$ROOT', receipt['repository_root']) for arg in row['argv']]):
            raise ValueError('Fresh command receipt differs: '+row['id'])
    result_names = ('native.json', 'wasm.json') if key == 'norsand' else ('native.json','wasm.json','native-check.json','wasm-check.json','parity.json')
    if set(binding['results']) != {str(packet/'execution-v2'/key/name) for name in result_names}:
        raise ValueError('Fresh qualification omits original backend results')
    check_backend_identity(key, binding['artifacts'], binding['results'])
    if set(binding['build_metadata']) != {'build-metadata/'+backend+'/'+name for backend in ('native','wasm') for name in ('CMakeCache.txt','compile_commands.json')}:
        raise ValueError('Fresh qualification omits compiler metadata')
    pin = data.get('independent_review', {})
    if pin.get('path') != 'build-review.json' or pin.get('sha256') != sha(build/'build-review.json'):
        raise ValueError('Fresh independent review pin changed')
    accepted = json.loads((build/'build-review.json').read_text())
    if (accepted.get('schema_version') != 'controlled-path-refresh-review-1' or accepted.get('status') != 'accepted'
            or accepted.get('binding') != binding or accepted.get('gates') != GATES[key]
            or not accepted.get('reviewer_run', '').strip() or accepted['reviewer_run'] == data['implementation_run']
            or accepted.get('blocking_findings') != []):
        raise ValueError('Separate fresh build review required')
    pending = json.loads((build/'qualification-pending.json').read_text())
    if (accepted.get('qualification_pending_sha256') != sha(build/'qualification-pending.json')
            or pending.get('binding') != binding or pending.get('gates') != data['gates']
            or pending.get('implementation_run') != data['implementation_run']
            or pending.get('status') != 'passed-original-backend-gates-pending-independent-review'):
        raise ValueError('Fresh review does not bind exact observed pending receipt')
    return dict(qualification=data, qualification_bytes=path.read_bytes(), review_bytes=(build/'build-review.json').read_bytes(),
                artifacts={name:(build/name).read_bytes() for name in ('atlas_path_capability.mjs', 'atlas_path_capability.wasm')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=PLAN)
    parser.add_argument('--plan-sha256')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('prepare')
    sub.add_parser('verify')
    run_parser = sub.add_parser('run')
    run_parser.add_argument('--implementation-run', required=True)
    sub.add_parser('collect')
    final = sub.add_parser('finalize')
    final.add_argument('build', type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        result = prepare(args.plan)
    elif args.command == 'verify':
        result = dict(status='source-plan-verified-no-execution', files=len(load_plan(args.plan, args.plan_sha256)['source_closure']))
    elif args.command == 'run':
        result = run(args.implementation_run, args.plan, args.plan_sha256)
    elif args.command == 'collect':
        result = collect(args.plan, args.plan_sha256)
    else:
        result = finalize(args.build)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
