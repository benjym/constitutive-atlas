"""Saved-only exact-source and diagnostic replay; no material execution."""
from pathlib import Path
import hashlib,json,importlib.util,sys
P=Path(__file__).parent;ROOT=P.parents[2]
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify():
 for n,h in json.loads((P/'prospective-freeze.json').read_text())['files'].items():assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
 sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
 for n,h in json.loads((P/'source-pins.json').read_text()).items():checked_receipt(ROOT,str((P/'source-pins.json').relative_to(ROOT)),n,h)
 original=module('trace_source_recovery',P/'check_instrumentation.py').check();assert len(original)==22
 inputs=json.loads((P/'inputs.json').read_text());assert module('trace_float_reference',P/'reference.py').run(inputs)==json.loads((P/'rounded-reference.json').read_text())
 for b in ['native','wasm']:
  for phase in ['configure','build','execution']:assert json.loads((P/(b+'-'+phase+'-process.json')).read_text())['returncode']==0
  assert json.loads((P/(b+'-build-process.json')).read_text())['command'][-4:]==['--target','atlas_tresca_reversal_diagnostic','--parallel','1']
  assert json.loads((P/(b+'-execution-process.json')).read_text())['stdout']==(P/(b+'-response.json')).read_text()
 a=module('trace_assessment',P/'assess.py').run();assert a==json.loads((P/'assessment.json').read_text())
 for b in ['native','wasm']:
  assert a[b]['diagnostic_verified'] and a[b]['initial_raw_jacobian_failed'] and a[b]['full_rollback']
  assert not a[b]['material_solve_ok'] and a[b]['newton_corrections']==a[b]['backtracking_trials']==0
  assert a[b]['nearest_physical_state_admissible'] and not a[b]['nearest_physical_state_raw_evaluable']
 assert json.loads((P/'native-response.json').read_text())==json.loads((P/'wasm-response.json').read_text())
 return a
if __name__=='__main__':print(json.dumps({'saved_evidence_verified':True,'cause_verified':all(v['diagnostic_verified']for v in verify().values()),'material_qualification_pass':False}))
