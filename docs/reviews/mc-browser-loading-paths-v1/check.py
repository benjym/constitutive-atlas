"""Cross-precision and source/control checks only; no Atlas imports."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import json,sys,collections

def run(low,high,policy):
 a,b,gate=[json.loads(Path(x).read_bytes())for x in(low,high,policy)];tol=D(gate['maximum_normalized_precision_difference']);ctol=D(gate['maximum_normalized_source_check']);failures=[];count=0;worst=D(0);checkmax=D(0);branches=collections.Counter();protocols=collections.Counter()
 def compare(x,y,path):
  nonlocal count,worst
  if isinstance(y,dict):
   if set(x)!=set(y):failures.append({'path':path,'reason':'keys'});return
   for k in y:
    if k=='precision':continue
    compare(x[k],y[k],path+'/'+k)
  elif isinstance(y,list):
   if len(x)!=len(y):failures.append({'path':path,'reason':'length'});return
   for i,(u,v)in enumerate(zip(x,y)):compare(u,v,path+'/'+str(i))
  elif isinstance(y,str):
   try:u,v=D(x),D(y)
   except Exception:
    if x!=y:failures.append({'path':path,'reason':'branch-or-metadata','low':x,'high':y})
   else:
    error=abs(u-v)/max(D(1),abs(u),abs(v));worst=max(worst,error);count+=1
    if error>tol:failures.append({'path':path,'reason':'precision','error':str(error)})
  elif x!=y:failures.append({'path':path,'reason':'metadata'})
 with localcontext()as ctx:
  ctx.prec=220;compare(a,b,'')
  for res in(a,b):
   for path in res['paths']:
    if res is b:protocols[path['protocol']]+=1;branches.update(x['branch']for x in path['points'][1:])
    for row in path['checks']:
     for k,v in row['defects'].items():
      value=D(v);checkmax=max(checkmax,value)
      if value>ctol:failures.append({'path':path['id'],'step':row['step'],'reason':'source-'+k,'error':str(value)})
 return {'identity':'mc-axisymmetric-source-reference-check-v1','passed':not failures,'numeric_fields':count,'maximum_normalized_precision_difference':str(worst),'maximum_source_defect':str(checkmax),'protocol_path_counts':dict(protocols),'branch_point_counts':dict(branches),'failures':failures,'candidate_calls':0,'compiled_observations':0}
if __name__=='__main__':
 r=run(*sys.argv[1:]);print(json.dumps(r,indent=2,sort_keys=True));raise SystemExit(0 if r['passed']else 1)
