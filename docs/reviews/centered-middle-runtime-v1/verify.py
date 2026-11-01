"""Saved-only generic capability replay, with immutable source receipts."""
from pathlib import Path
import json,sys,importlib.util
P=Path(__file__).parent;ROOT=P.parents[2]
def verify():
 sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
 for name,h in json.loads((P/'prospective-freeze.json').read_text())['files'].items():checked_receipt(ROOT,str((P/'prospective-freeze.json').relative_to(ROOT)),name,h)
 s=importlib.util.spec_from_file_location('centered_runtime_assessor',P/'assess.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);requests=json.loads((P/'requests.json').read_text());results={}
 for b in ['native','wasm']:
  for phase in ['configure','build','execution']:assert json.loads((P/(b+'-'+phase+'-process.json')).read_text())['returncode']==0
  assert json.loads((P/(b+'-build-process.json')).read_text())['command'][-4:]==['--target','atlas_centered_middle','--parallel','1']
  assert json.loads((P/(b+'-execution-process.json')).read_text())['stdout']==(P/(b+'-responses.txt')).read_text()
  results[b]=m.assess((P/(b+'-responses.txt')).read_text(),requests)
 assert results==json.loads((P/'assessment.json').read_text())and results['native']==results['wasm'];assert len(requests)==1160
 return results
if __name__=='__main__':print(json.dumps({'saved_evidence_verified':True,'requests_per_backend':verify()['native']['requests'],'no_material_model_qualification':True}))
