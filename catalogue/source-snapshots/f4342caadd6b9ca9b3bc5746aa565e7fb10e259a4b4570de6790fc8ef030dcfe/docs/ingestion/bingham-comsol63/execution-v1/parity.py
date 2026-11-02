"""Physical output parity, independent accuracy assessed separately."""
import json,math,sys
from pathlib import Path
def main(native,wasm):
 a=json.loads(Path(native).read_text());b=json.loads(Path(wasm).read_text());assert len(a)==len(b);n=0;worst=0.
 def compare(x,y,path=''):
  nonlocal n,worst
  if isinstance(x,list):
   assert isinstance(y,list) and len(x)==len(y),path
   for i,(xx,yy) in enumerate(zip(x,y)):compare(xx,yy,path+'/'+str(i))
  elif isinstance(x,dict):
   assert isinstance(y,dict) and set(x)==set(y),path
   for k in x:
    if k not in ('substeps','rejected','iterations','backtracks','error'):compare(x[k],y[k],path+'/'+k)
  elif type(x) in (int,float) and type(y) in (int,float):
   assert math.isfinite(x) and math.isfinite(y),path
   floor=1000. if '/observables/' in path or '/values/' in path else 1.
   err=abs(x-y)/max(floor,abs(x),abs(y));assert err<=2e-10,(path,x,y,err);n+=1;worst=max(worst,err)
  else:assert x==y,(path,x,y)
 for x,y in zip(a,b):
  assert x['id']==y['id'];compare(json.loads(x['calls'][0]['stdout']),json.loads(y['calls'][0]['stdout']),x['id'])
  if 'observation' in x:compare(json.loads(x['observation']),json.loads(y['observation']),x['id']+'/observation')
 return dict(passed=True,cases=len(a),physical_numeric_comparisons=n,worst_scaled_difference=worst,relative_budget=2e-10,diagnostic_counts_excluded=True)
if __name__=='__main__':print(json.dumps(main(*sys.argv[1:]),indent=2))
