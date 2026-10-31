"""Frozen prospective native/Wasm physical path parity, separately from source accuracy."""
from pathlib import Path
import sys,json
from assess_paths import load,finite

def assess(a,b,requests):
 assert [r['id']for r in a]==[r['id']for r in b]==['describe']+[r['id']for r in requests]
 worst=0.;count=0
 for x,y,req in zip(a[1:],b[1:],requests):
  assert x['request']==y['request']==req
  x,y=json.loads(x['raw']),json.loads(y['raw'])
  assert x['ok']is True and y['ok']is True
  assert len(x['points'])==len(y['points'])==req['steps']+1
  for xp,yp in zip(x['points'],y['points']):
   for k in ('control','state','strain','p','q','q_signed','u'):
    xv,yv=(xp[k],yp[k])if k in('state','strain')else([xp[k]],[yp[k]])
    assert len(xv)==len(yv)
    for u,v in zip(xv,yv):
     u,v=finite(u),finite(v);error=abs(u-v)/(1e-10*max(1,abs(u),abs(v)));assert error<=1,(req['id'],k,error)
     worst=max(worst,error);count+=1
 return {'passed':True,'compared_physical_scalars':count,'maximum_parity_budget_fraction':worst}
if __name__=='__main__':print(json.dumps(assess(load(sys.argv[1]),load(sys.argv[2]),load(Path(__file__).parent/'requests.json')),indent=2))
