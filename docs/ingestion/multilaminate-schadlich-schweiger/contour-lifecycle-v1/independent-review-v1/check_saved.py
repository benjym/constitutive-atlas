"""Independent finite lifecycle review replay; no material/compiled execution."""
from pathlib import Path
import json,hashlib,subprocess,sys,importlib.util,copy
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
def load(path,name):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 frozen=json.loads((HERE/'input-freeze.json').read_text())
 for p,h in frozen.items():
  if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h:raise RuntimeError('changed input '+p)
 results=[]
 for folder,count in [(BASE,22),(BASE/'reference-v2',27)]:
  proc=subprocess.run([sys.executable,'-B','check.py'],cwd=folder,text=True,capture_output=True,check=True)
  result=json.loads(proc.stdout)
  if result!=json.loads((folder/'checks.json').read_text()) or result['count']!=count:raise RuntimeError('saved replay mismatch')
  results.append({'scope':folder.name,'count':count,'saved_output_equal':True})
 old=load(BASE/'reference.py','review_old');new=load(BASE/'reference-v2/reference.py','review_new')
 bad=old.prepare();bad['x']=[1e308,0.,0.]
 original,_=old.trial(bad,[0.,0.,0.])
 if original['gamma']!=0:raise RuntimeError('old counterexample changed')
 rejected=False
 try:new.trial(bad,[0.,0.,0.])
 except ValueError:rejected=True
 if not rejected:raise RuntimeError('v2 accepted inconsistent restart')
 a=new.prepare();a,_=new.trial(a,[8.,0.,0.]);a,_=new.trial(a,[-4.,0.,0.]);frozen_a=copy.deepcopy(a)
 # The failure-inhibition asymmetry is real and remains explicitly unresolved.
 proposed,event=new.trial(a,[4.,0.,0.],creation_permitted=False)
 if event!='erase-inner' or len(proposed['contours'])!=1 or a!=frozen_a:raise RuntimeError('inhibited erasure changed')
 rejections=[]
 for name,mut in [('profile mismatch',lambda v:v.update(profile='wrong')),('nonfinite anchor',lambda v:v.update(anchor=[float('inf'),0,0])),('negative gamma',lambda v:v.update(gamma=-1)),('negative radius',lambda v:v['contours'][0].update(radius=-1)),('inconsistent gamma',lambda v:v.update(gamma=100))]:
  b=copy.deepcopy(a);mut(b);ok=False
  try:new.validate(b)
  except ValueError:ok=True
  if not ok:raise RuntimeError('accepted malformed state '+name)
  rejections.append(name)
 return {'status':'PASS','frozen_inputs':len(frozen),'fixture_replays':results,'original_overflow_counterexample_reproduced':True,'v2_counterexample_rejected':True,'additional_rejections':rejections,'creation_inhibited_outer_erasure_confirmed':True,'parent_unchanged':a==frozen_a,'limits':'Standalone geometry and caller publication mock only; no common-engine transaction, coupled stiffness, material or experimental proof.'}
if __name__=='__main__':print(json.dumps(main(),indent=2))
