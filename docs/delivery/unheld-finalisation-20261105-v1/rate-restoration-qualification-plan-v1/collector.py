"""Thin fresh-build17 provenance adapter; original scientific collector untouched."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
OLD=HERE.parents[1]/'unheld-finalisation-20261102-v1/baseline-qualification-plan-v5'
spec=importlib.util.spec_from_file_location('_original_v5_qualification',OLD/'collector.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
pin=M.pin;sha=M.sha;verify=M.verify;write=M.write;source_files=M.source_files
PLAN=json.loads((HERE/'plan.json').read_text());ACTUAL=Path(PLAN['actual']);WORK=Path(PLAN['work']);SOURCE=Path(PLAN['source'])
def verify_plan(expected):
 assert not sys.flags.optimize,'assertions must be enabled'
 assert sha(HERE/'manifest.json')==expected,'wrong frozen plan manifest'
 for row in json.loads((HERE/'manifest.json').read_text())['files']:
  p=Path(row['path']);assert not p.is_absolute()and'..'not in p.parts
  q=HERE/p;assert sha(q)==row['sha256']and q.stat().st_size==row['size_bytes']
 for row in json.loads((HERE/'external-pins.json').read_text()):verify(row)
def verify_cache(path):
 receipt=json.loads((HERE.parent/'rate-restoration-cache-copy-v1.json').read_text())
 assert path.resolve()==path and str(path)==receipt['destination'] and receipt['source_owner_untouched'] is True
 expected={r['path']:r for r in receipt['files']}
 actual={str(p.relative_to(path))for p in path.rglob('*')if p.is_file()}
 assert actual==set(expected),'cache namespace differs from exact parent-owned copy receipt'
 for name,row in expected.items():
  p=path/name;assert not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
def assert_source(repo):
 assert repo.resolve()==SOURCE
 assert sha(repo/'cpp/include/atlas/solver.hpp')=='0292c075b7a81ce946adf3199e8f729102815ce427c71a16aea4db20932c99fc'
 assert sha(repo/'tests/test_solver.cpp')=='da2b0ed473cdb186fafac04033350b17ff25d287a804abb1c63cb46addd88b90'
 assert sha(repo/'tests/test_ensemble.mjs')=='4c64a92d07675209c3b8b0030cd286841953ff7b11253ea376828d6452d2563d'
 policy=json.loads((OLD/'policy.json').read_text())
 for name,h in policy['unchanged_gate_sha256'].items():assert sha(repo/name)==h
 for model,h in policy['candidate_sha256'].items():assert sha(repo/'models'/f'{model}.json')==h
 expected=json.loads((HERE.parent/'current17-browser-plan-v1/catalogue17.json').read_text())
 actual=[json.loads(p.read_text())for p in sorted((repo/'models').glob('*.json'))]
 assert len(actual)==17 and actual==expected['models'],'exact17 source definitions/order'
def assert_generated(build):
 defs=[];headers=[]
 for backend in('native','wasm'):
  directory=WORK/backend
  data=json.loads((directory/'generated/models.json').read_text());defs.append(data);headers.append(sha(directory/'generated/models.hpp'))
  assert len(data['models'])==17 and data==json.loads((HERE.parent/'current17-browser-plan-v1/catalogue17.json').read_text())
 assert defs[0]==defs[1]and headers[0]==headers[1]
OriginalValidate=M.validate_execution_freeze
def validate_execution_freeze(f):
 OriginalValidate(f);assert_source(Path(f['repo']));b=json.loads(Path(f['build_receipt']['path']).read_text());verify(b['execution_script']);assert_generated(b)
M.validate_execution_freeze=validate_execution_freeze
# Same actual per-call binding adapter already source-reviewed for current17 reuse.
OriginalTransport=M.Transport
class GuardedTransport(OriginalTransport):
 def run(self,command,**kwargs):
  def bound():
   for item in [*self.freeze['artifacts'].values(),self.freeze['python']]:verify(item)
  bound();primary=None
  try:return super().run(command,**kwargs)
  except BaseException as error:primary=error;raise
  finally:
   try:bound()
   except BaseException as error:
    if self.calls:self.calls[-1]['post_artifact_binding_error']=repr(error)
    write(self.out/'raw-calls.json',self.calls)
    if primary is None:raise
    primary.artifact_post_errors=[*getattr(primary,'artifact_post_errors',[]),repr(error)]
M.Transport=GuardedTransport

def main():
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['source-freeze','freeze','native','wasm','pair']);p.add_argument('--plan-manifest-sha256',required=True);p.add_argument('--node',type=Path);p.add_argument('--tool',action='append');a=p.parse_args();verify_plan(a.plan_manifest_sha256);assert_source(SOURCE)
 if a.phase=='source-freeze':
  assert not ACTUAL.exists(),'distinct never-used actual directory required';ACTUAL.mkdir()
  assert a.node and a.tool
  M.source_freeze(argparse.Namespace(repo=SOURCE,node=a.node,tool=a.tool,output=ACTUAL/'source-freeze.json'))
  write(ACTUAL/'plan-binding.json',{'identity':'rate-restoration-plan-before-new-build-v1','plan_manifest':pin(HERE/'manifest.json'),'source_freeze':pin(ACTUAL/'source-freeze.json'),'requests':pin(HERE/'requests.json'),'supplemental_regression_test':pin(SOURCE/'tests/test_solver.cpp'),'supplemental_ensemble_test':pin(SOURCE/'tests/test_ensemble.mjs'),'launch_review_required':'separate accepted independent regression-test review before source-freeze/build; parent launch receipt binds its genuine decision','new_build_required':True})
 else:
  binding=json.loads((ACTUAL/'plan-binding.json').read_text());verify(binding['plan_manifest']);verify(binding['source_freeze']);verify(binding['supplemental_regression_test']);verify(binding['supplemental_ensemble_test']);assert binding['plan_manifest']['sha256']==a.plan_manifest_sha256
  if a.phase=='freeze':
   M.freeze(argparse.Namespace(repo=SOURCE,native=WORK/'native/atlas_solver',module=WORK/'wasm/atlas.js',wasm=WORK/'wasm/atlas.wasm',node=Path(json.loads((ACTUAL/'source-freeze.json').read_text())['node']['path']),source_freeze=ACTUAL/'source-freeze.json',build_receipt=ACTUAL/'build/receipt.json',output=ACTUAL/'execution-freeze.json'))
   validate_execution_freeze(json.loads((ACTUAL/'execution-freeze.json').read_text()))
  elif a.phase in('native','wasm'):M.collect(argparse.Namespace(freeze=ACTUAL/'execution-freeze.json',backend=a.phase,output=ACTUAL/a.phase))
  else:M.assess_pair(argparse.Namespace(native=ACTUAL/'native',wasm=ACTUAL/'wasm',output=ACTUAL/'pair.json'))
 verify_plan(a.plan_manifest_sha256);assert_source(SOURCE)
if __name__=='__main__':main()
