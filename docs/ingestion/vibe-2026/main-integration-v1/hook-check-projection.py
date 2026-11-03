"""Pure exact-byte reversal proof for the narrowly approved release hook patch."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess

def parse_yaml(path):
    return json.loads(subprocess.check_output(['ruby','-rjson','-ryaml','-e','puts JSON.generate(YAML.safe_load(File.read(ARGV.fetch(0)), aliases: false))',str(path)]))
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
N='docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/norsand/engine'
I='docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine'
M='docs/ingestion/vibe-2026/maxwell-refresh-v1/execution-v1/engine'
files=[]
for name in ['tools/build_web.py','.github/workflows/qualification.yml','.github/workflows/pages.yml']:
 old=(HERE/'hook-preimages'/name).read_text();new=(ROOT/name).read_text();reverse=new
 if name.endswith('.py'):
  ast.parse(new)
  for after,before in [(f"default=ROOT/'{N}'","default=ROOT/'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v1/norsand/engine'"),(f"default=ROOT/'{I}'","default=ROOT/'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v1/interface2016/engine'"),(f"default=ROOT/'{M}'","default=ROOT/'build-maxwell-wasm'")]:
   assert reverse.count(after)==1;reverse=reverse.replace(after,before)
 else:
  parsed=parse_yaml(ROOT/name);original=parse_yaml(HERE/'hook-preimages'/name)
  assert parsed.get('on',parsed.get('true'))==original.get('on',original.get('true')) and parsed['permissions']==original['permissions']
  runs=[step['run'] for job in parsed['jobs'].values() for step in job.get('steps',[]) if 'run' in step]
  assert not any('tools/provision_bingham_dependency_assets.py' in r for r in runs)
  guarded=[r for r in runs if 'tools/check_current_dependency_assets.py' in r]
  packaged=[r for r in runs if 'tools/build_web.py' in r]
  assert len(guarded)==len(packaged)==(2 if 'qualification' in name else 1)
  for run in packaged:assert all(flag+' '+path in run for flag,path in [('--controlled-path-wasm-dir',N),('--interface2016-wasm-dir',I),('--maxwell-wasm-dir',M)])
  reverse=reverse.replace('tools/check_current_dependency_assets.py --output "$RUNNER_TEMP/current-dependency-guards"','tools/provision_bingham_dependency_assets.py')
  reverse=reverse.replace(f'--controlled-path-wasm-dir {N} --interface2016-wasm-dir {I} --maxwell-wasm-dir {M}','--controlled-path-wasm-dir docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v1/norsand/engine')
  if 'qualification' in name:
   maxwell=[r for r in runs if 'tools/check_maxwell_ci.py' in r]
   assert len(maxwell)==2 and all('--build '+M in r for r in maxwell)
   reverse=reverse.replace(f'tools/check_maxwell_ci.py --build {M} --output','tools/check_maxwell_ci.py --output')
   addition='''    - name: Retain current dependency guards and Maxwell regression
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: current-dependency-guards-${{ runner.os }}
        path: |-
          ${{ runner.temp }}/current-dependency-guards/
          ${{ runner.temp }}/maxwell-ci-regression/
'''
   assert reverse.count(addition)==2;reverse=reverse.replace(addition,'')
  else:
   before='        path: "${{ runner.temp }}/packaged-laboratory.json"'
   after='        path: |-\n          ${{ runner.temp }}/packaged-laboratory.json\n          ${{ runner.temp }}/current-dependency-guards/'
   assert reverse.count(after)==1;reverse=reverse.replace(after,before)
 assert reverse.encode()==old.encode(),name
 files.append(dict(path=name,original_sha256=hashlib.sha256(old.encode()).hexdigest(),current_sha256=hashlib.sha256(new.encode()).hexdigest(),exact_reverse_bytes=True))
for name in ['tools/provision_bingham_dependency_assets.py','tools/provision_maxwell_assets.py','tests/test_provision_maxwell_assets.py']:
 assert (ROOT/name).read_bytes()==(HERE/'hook-preimages'/name).read_bytes()
for name in ['tools/check_current_dependency_assets.py','tests/test_current_dependency_assets.py']:ast.parse((ROOT/name).read_text())
print(json.dumps(dict(status='pass-exact-hook-source-reversal',files=files,obsolete_actual_invocations_replaced=3,explicit_maxwell_build_calls=2,explicit_three_engine_package_calls=3,historical_files_byte_identical=3,python_ast_and_workflow_yaml_parsed=True,all_other_commands_and_workflow_fields_byte_identical=True,compiled_calls=0),indent=2))
