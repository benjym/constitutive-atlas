"""One serial metadata-only build from the pinned Git source; no material calls.

Run from this checkout with a NEW absolute output directory outside the repo.
All subprocess output is retained by the existing TMD2 command journal helper.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.benchmark_tmd2 import command

PACKET = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    out = args.output
    if not out.is_absolute() or out.exists() or ROOT == out or ROOT in out.parents:
        parser.error('output must be a new absolute directory outside the repository')
    policy = json.loads((PACKET/'protocol.json').read_text())
    assert sha(PACKET/'source-manifest.json') == policy['source_manifest_sha256']
    manifest = json.loads((PACKET/'source-manifest.json').read_text())
    assert manifest['source_commit'] == policy['source_commit']
    out.mkdir(parents=True)
    source = out/'source'
    source.mkdir()
    for name, digest in manifest['files'].items():
        path = Path(name)
        assert not path.is_absolute() and '..' not in path.parts
        content = subprocess.check_output(['git', '-C', str(ROOT), 'show', f"{policy['source_commit']}:{name}"])
        assert hashlib.sha256(content).hexdigest() == digest
        target = source/path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    # Generate the expected bytes BEFORE any CMake or native execution.
    command([sys.executable, '-c',
             'import os,runpy,sys; os.chdir(sys.argv[1]); sys.path.insert(0,sys.argv[1]); sys.argv=["atlas.compiler",sys.argv[2]]; runpy.run_module("atlas.compiler",run_name="__main__")',
             str(source), str(out/'expected')], out, '01-expected')
    expected = json.loads((out/'expected/models.json').read_text())
    assert expected['sha256'] == '0d2e46841e859ca94bd69fff91020a4516b24f2c50c139f61ece5748b00b3fe7'
    assert len(expected['models']) == 9
    freeze = {'protocol_sha256':sha(PACKET/'protocol.json'),
              'source_manifest_sha256':sha(PACKET/'source-manifest.json'),
              'runner_sha256':sha(Path(__file__)),
              'journal_helper_sha256':sha(ROOT/'tools/benchmark_tmd2.py'),
              'python':sys.executable, 'python_version':sys.version,
              'expected':{name:sha(out/'expected'/name) for name in ['models.json','models.hpp']},
              'catalogue_identity':expected['sha256'], 'model_count':len(expected['models'])}
    write(out/'freeze.json', freeze)
    command(['cmake','--version'], out, '02-cmake-version')
    command(['cmake','-S',str(source),'-B',str(out/'build'),'-DCMAKE_BUILD_TYPE=Release',
             '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON',f'-DPython3_EXECUTABLE={sys.executable}'], out, '03-configure')
    cache = (out/'build/CMakeCache.txt').read_text().splitlines()
    compiler = next(line.split('=',1)[1] for line in cache if line.startswith('CMAKE_CXX_COMPILER:FILEPATH='))
    command([compiler,'--version'], out, '04-compiler-version')
    command(['cmake','--build',str(out/'build'),'--target','atlas_solver','--parallel','1'], out, '05-build')
    for name,digest in freeze['expected'].items():
        assert sha(out/'build/generated'/name) == digest, f'generated {name} changed'
    solver = out/'build/atlas_solver'
    command([str(solver),'--describe'], out, '06-describe')
    assert json.loads((out/'06-describe.stdout').read_text()) == expected
    for name,digest in manifest['files'].items():
        assert sha(source/name) == digest, f'source changed: {name}'
    commands = [json.loads(path.read_text()) for path in sorted(out.glob('0*.json'))]
    assert len(commands) == 6 and all(type(row['returncode']) is int and row['returncode'] == 0 for row in commands)
    files = sorted(path for path in out.iterdir() if path.is_file())
    result = {'status':'pass','source_commit':policy['source_commit'],
              'source_files_checked':len(manifest['files']), 'freeze_sha256':sha(out/'freeze.json'),
              'artifact_sha256':sha(solver), 'artifact_path':str(solver),
              'catalogue_identity':expected['sha256'], 'model_count':len(expected['models']),
              'material_calls':0, 'native_metadata_calls':1, 'build_target':'atlas_solver','parallel':1,
              'build_files':{name:sha(out/'build'/name) for name in ['CMakeCache.txt','compile_commands.json']},
              'evidence_files':{path.name:sha(path) for path in files},
              'limits':policy['limits']}
    write(out/'result.json', result)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
