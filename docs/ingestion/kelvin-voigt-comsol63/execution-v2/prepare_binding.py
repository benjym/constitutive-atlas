"""Freeze the prospective flag-only correction; no compiled calls."""
import copy,hashlib,json
from pathlib import Path
import study
B=Path(__file__).resolve().parent;OLD=B.parent/'execution-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not(B/'freeze.json').exists(),'Already frozen'
 oldstudy=(OLD/'study.py').read_text();assert oldstudy.count("'--current'")==2;assert(B/'study.py').read_text()==oldstudy.replace("'--current'","'--initial'")
 for name in['reference.py','PLAN.md','collect_wasm.mjs']:assert(B/name).read_bytes()==(OLD/name).read_bytes(),name
 original=json.loads((OLD/'cases.json').read_text());new={'cases':study.make_cases()};assert len(new['cases'])==len(original['cases'])==43
 changed=[]
 for c,d in zip(new['cases'],original['cases']):
  expected=copy.deepcopy(d)
  if d['kind']=='observe':expected['argv']=['--initial'if token=='--current'else token for token in d['argv']];changed.append(c['id'])
  assert c==expected,c['id']
 study.dump(B/'cases.json',new)
 names=['study.py','reference.py','PLAN.md','collect_wasm.mjs','README.md','recover_native.py','prepare_binding.py','cases.json','../execution-v1/study.py','../execution-v1/cases.json','../execution-v1/freeze.json','../execution-v1/native-raw.json','../execution-v1/native-assessment.log','../source-v1/candidate.json']
 freeze={'identity':'FIX-kelvin-native-observe-harness-v2','model':study.M,'model_sha256':study.SHA,'basis':'Retained v1 unsupported --current CLI diagnostic; flag-only correction frozen before corrected observations','compiled_calls_performed_by_preparer':0,'changed_case_native_argv_only':changed,'identical_C_ABI_and_references':True,'unchanged_acceptance':True,'pins':{n:sha(B/n)for n in names}}
 study.dump(B/'freeze.json',freeze);print('Frozen flag-only correction:',len(changed),'observe case argv;43cases unchanged otherwise')
if __name__=='__main__':main()
