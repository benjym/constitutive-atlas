"""Build and assess the frozen barodesy source context, never the live engine.

The original scripts, references, policies and model are unchanged. This is
historical regression qualification; current-engine checks remain separate.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CAPSULE_SHA256 = 'dc8a2ad8e13c584b5e3f15a71f282bc0f39c01cc9a6e5750a345b20e29530cbd'
CAPSULE = 'catalogue/source-replays/finite-tensor-v1/capsule.json.gz'

# A minimal, separately identified build driver avoids adding live source files
# just to satisfy unrelated targets in the archived full-project CMakeLists.
CMAKE = '''cmake_minimum_required(VERSION 3.20)
project(HistoricalBarodesy LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
find_package(Python3 REQUIRED COMPONENTS Interpreter)
add_custom_command(
  OUTPUT "${CMAKE_BINARY_DIR}/generated/models.hpp"
  COMMAND "${Python3_EXECUTABLE}" -m atlas.compiler "${CMAKE_BINARY_DIR}/generated" "${ARCHIVE_ROOT}/models/research/barodesy2017"
  WORKING_DIRECTORY "${ARCHIVE_ROOT}")
add_custom_target(historical_models DEPENDS "${CMAKE_BINARY_DIR}/generated/models.hpp")
add_executable(atlas_barodesy_solver "${ARCHIVE_ROOT}/cpp/main.cpp")
add_dependencies(atlas_barodesy_solver historical_models)
target_include_directories(atlas_barodesy_solver PRIVATE "${ARCHIVE_ROOT}/cpp/include" "${CMAKE_BINARY_DIR}/generated")
if(EMSCRIPTEN)
  target_compile_options(atlas_barodesy_solver PRIVATE -fexceptions)
  set_target_properties(atlas_barodesy_solver PROPERTIES OUTPUT_NAME "barodesy-isotropic" SUFFIX ".js")
  target_link_options(atlas_barodesy_solver PRIVATE
    "-sMODULARIZE=1" "-sEXPORT_ES6=1" "-sEXPORT_NAME=createAtlas"
    "-sENVIRONMENT=web,worker,node" "-sALLOW_MEMORY_GROWTH=1"
    "-sMAXIMUM_MEMORY=268435456" "-sSTACK_SIZE=1048576"
    "-sEXPORTED_RUNTIME_METHODS=['ccall']" "-fexceptions"
    "-sFILESYSTEM=0" "--no-entry")
endif()
'''


def prepare(directory, root=ROOT):
    # Decode only the explicitly pinned trusted project capsule. Materialization
    # validates all internal blobs and paths before any archived code executes.
    from atlas.source_replay import materialize, strict_json
    blob = (root / CAPSULE).read_bytes()
    if hashlib.sha256(blob).hexdigest() != CAPSULE_SHA256:
        raise ValueError('historical capsule changed')
    capsule = strict_json(gzip.decompress(blob))
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    archive = materialize(capsule, directory / 'source')
    project = directory / 'build-project'
    project.mkdir()
    (project / 'CMakeLists.txt').write_text(CMAKE)
    result = {'version': 'historical-barodesy-ci-v1',
              'scope': 'frozen-source historical regression, not current-engine qualification',
              'capsule_sha256': CAPSULE_SHA256,
              'build_driver_sha256': hashlib.sha256(CMAKE.encode()).hexdigest(),
              'source_files': {p: v['sha256'] for p, v in capsule['files'].items()},
              'python': sys.version, 'compiled_execution': False,
              'current_engine_qualified': False, 'admission': False, 'completed': False}
    (directory / 'freeze.json').write_text(json.dumps(result, indent=2) + '\n')
    return archive, project, result


def commands(directory, archive, project):
    directory, archive, project = map(Path, (directory, archive, project))
    native, wasm = directory / 'native', directory / 'wasm'
    common = ['-DCMAKE_BUILD_TYPE=Release', '-DARCHIVE_ROOT=' + str(archive),
              '-DPython3_EXECUTABLE=' + sys.executable]
    yield ['cmake', '-S', str(project), '-B', str(native), *common]
    yield ['cmake', '--build', str(native), '--target', 'atlas_barodesy_solver', '--parallel', '1']
    yield ['emcmake', 'cmake', '-S', str(project), '-B', str(wasm), *common]
    yield ['cmake', '--build', str(wasm), '--target', 'atlas_barodesy_solver', '--parallel', '1']
    for name, study, collector in (
        ('isotropic', 'tools.barodesy2017_integration_study', 'test_barodesy2017_paths_wasm.mjs'),
        ('wider', 'tools.barodesy2017_wider_study', 'test_barodesy2017_wider_wasm.mjs'),
    ):
        n, w = directory / (name + '-native.json'), directory / (name + '-wasm.json')
        yield [sys.executable, '-B', '-m', study, '--solver', str(native / 'atlas_barodesy_solver'), '--output', str(n)]
        yield ['node', str(archive / 'tools' / collector), '--native-report', str(n),
               '--wasm', str(wasm / 'barodesy-isotropic.js'), '--output', str(w)]
        extra = [] if name == 'isotropic' else [
            '--transport', str(w.with_suffix('.transport.jsonl')),
            '--native-transport', str(n.with_suffix('.transport.jsonl'))]
        yield [sys.executable, '-B', '-m', study, '--report', str(w), '--native-report', str(n),
               *extra, '--output', str(directory / (name + '-assessment.json'))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', required=True, type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    directory = args.directory.resolve()
    archive, project, result = prepare(directory)
    if args.prepare_only:
        print(json.dumps(result, indent=2))
        return
    env = {k: v for k, v in os.environ.items() if not k.startswith(('PYTHON', 'ATLAS_'))}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    for index, command in enumerate(commands(directory, archive, project), 1):
        print('Historical barodesy:', command, flush=True)
        process = subprocess.run(command, cwd=archive, env=env, capture_output=True, text=True)
        record = dict(args=command, returncode=process.returncode,
                      stdout=process.stdout, stderr=process.stderr)
        (directory / f'command-{index:02}.json').write_text(json.dumps(record, indent=2) + '\n')
        if process.returncode:
            print(process.stdout, end='')
            print(process.stderr, end='', file=sys.stderr)
            raise SystemExit(process.returncode)
    for name, pin in result['source_files'].items():
        if hashlib.sha256((archive / name).read_bytes()).hexdigest() != pin:
            raise ValueError('archived input changed during study: ' + name)
    result.update(compiled_execution=True, completed=True)
    result['outputs'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in directory.glob('*.json') if p.name != 'freeze.json'}
    (directory / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Historical barodesy: original isotropic and wider native/Wasm policies passed; current engine remains separately qualified.')


if __name__ == '__main__':
    # Direct script invocation must resolve the checkout's trusted helper package.
    sys.path.insert(0, str(ROOT))
    main()
