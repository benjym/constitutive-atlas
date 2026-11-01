"""Verify saved laboratory evidence, retaining its failed qualification verdict."""
from pathlib import Path
import json,hashlib,importlib.util,sys
P=Path(__file__).parent;ROOT=P.parents[2]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def verify():
 for name,h in json.loads((P/'prospective-freeze.json').read_text())['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
 sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
 for name,h in json.loads((P/'source-pins.json').read_text()).items():checked_receipt(ROOT,str((P/'source-pins.json').relative_to(ROOT)),name,h)
 inputs=json.loads((P/'inputs.json').read_text());refs=module('lab_references',P/'reference.py').generate(inputs);assert refs==json.loads((P/'references.json').read_text())
 for backend in ['native','wasm']:
  for phase in ['configure','build','execution']:assert json.loads((P/(backend+'-'+phase+'-process.json')).read_text())['returncode']==0
  assert json.loads((P/(backend+'-build-process.json')).read_text())['command'][-4:]==['--target','atlas_tresca_laboratory','--parallel','1']
  assert json.loads((P/(backend+'-execution-process.json')).read_text())['stdout']==(P/(backend+'-responses.jsonl')).read_text()
 actual=module('lab_assessment',P/'assess.py').run();assert actual==json.loads((P/'assessment.json').read_text());assert not actual['overall_pass']
 for backend in ['native','wasm']:
  assert actual[backend]['requests']==29 and actual[backend]['recoveries']==29 and actual[backend]['reference_components']==1710 and actual[backend]['admissibility_checks']==95
  assert [(f['label'],f['kind'])for f in actual[backend]['failures']]==[('isotropic-0','run-status'),('isotropic-0','prefix-length')]
 diagnostic=module('lab_diagnostic',P/'diagnose.py').run();assert diagnostic==json.loads((P/'reversal-diagnostic.json').read_text())
 return actual
if __name__=='__main__':print(json.dumps({'saved_evidence_verified':True,'qualification_pass':verify()['overall_pass']}))
