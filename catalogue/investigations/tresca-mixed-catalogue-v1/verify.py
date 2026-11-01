"""Read-only retained compatibility check; never runs a compiled artifact."""
from pathlib import Path
import hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
if str(ROOT)not in sys.path:sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt

def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def verify():
 for name in ['source-pins.json','dependency-pins.json','prospective-freeze.json','manifest.json']:
  d=read(P/name);pins=d.get('files',d)
  for path,h in pins.items():
   if isinstance(h,str)and len(h)==64:checked_receipt(ROOT,(P/name).relative_to(ROOT),path,h)
 proposal='docs/reviews/tresca-v5-source-integration-v1/public-model.json'
 assert(P/'model.json').read_bytes()==checked_receipt(ROOT,(P/'dependency-pins.json').relative_to(ROOT),proposal,read(P/'dependency-pins.json')[proposal]).read_bytes()
 nine=read(P/'generated-nine/models.json')['models'];ten=read(P/'generated-ten/models.json')['models'];mid=read(P/'model.json')['id'];assert len(nine)==9 and len(ten)==10
 assert[m for m in ten if m['id']!=mid]==nine
 assert next(m for m in ten if m['id']==mid)==read(P/'model.json')
 # Recheck stored normal numerical blocks. Only generated dispatch indices differ.
 def block(text,start):
  i=text.index(start);j=text.index('{',i);k=j+1;depth=1
  while depth:depth+=(text[k]=='{')-(text[k]=='}');k+=1
  return text[i:k]
 single=(P/'generated-single/models.hpp').read_text();mixed=(P/'generated-ten/models.hpp').read_text();index=next(i for i,m in enumerate(ten)if m['id']==mid)
 assert block(single,'inline bool solution_constraints_0')==block(mixed,'inline bool solution_constraints_'+str(index)).replace('solution_constraints_'+str(index),'solution_constraints_0')
 for n in ['evaluate_model','prepare_model_increment','model_scales','model_observable_scales']:
  assert block(single[single.index(n):],'case 0: {')==block(mixed[mixed.index(n):],'case '+str(index)+': {').replace('case '+str(index)+': {','case 0: {',1)
 for b in ['native','wasm']:
  for phase in ['configure','build']:
   process=read(P/(b+'-'+phase+'-process.json'));assert process['returncode']==0
   if phase=='build':assert process['command'][-4:]==['--target','atlas_solver','--parallel','1']
  artifacts=read(P/(b+'-artifacts.json'));assert len(artifacts)==(1 if b=='native'else 2)
 result=module('mixed_saved_assessor',P/'assess.py').assess();assert result==read(P/'assessment.json');assert result['overall_pass']
 return {'overall_pass':True,'compiled_artifacts_executed':False,'baseline_models':9,'candidate_models':10,'old_model_requests_per_backend':126,'tresca_laboratory_requests_per_backend':29,'tresca_api_history_steps_per_backend':12,'scientific_admission':False,'public_installation':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
