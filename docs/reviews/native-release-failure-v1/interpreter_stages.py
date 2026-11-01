import sys,json,math,copy
from pathlib import Path
sys.path.insert(0,'/Users/bmar5496/code/constitutive-atlas')
from atlas.model import load,evaluation_environment,interpret
from atlas.dsl import evaluate,parse,Sym
m=load('/Users/bmar5496/code/constitutive-atlas/models/research-hp-extracted-asbs-gis-2024-v03.json');z={f['name']:copy.deepcopy(f['initial'])for f in m['state']};de=[.0002,-.00004,-.00004,.00003,0,0];rows=[]
def env(state,inc):
 e=evaluation_environment(m,state,z,inc,_check_domain=False)
 return e,[c for c in m['domain']if not evaluate(parse(c),e)]
def add(state,rate,factor):
 return {k:([a+factor*b for a,b in zip(v,rate[k].v)]if isinstance(v,list)else v+factor*rate[k])for k,v in state.items()}
for depth in range(15):
 inc=[math.ldexp(v,-depth)for v in de];row={'depth':depth,'increment':inc,'stages':[]}
 state=copy.deepcopy(z)
 for stage in ['start','midpoint','end-domain']:
  e,failed=env(state,inc if stage!='end-domain'else[0]*6)
  row['stages'].append({'stage':stage,'failed_domain':failed,'Omega':state['Omega'],'h':state['h'],'q':e['q'],'cos3theta':e['cos3theta']})
  if failed:break
  if stage=='start':k1=interpret(m,state,z,inc);state=add(z,k1,.5)
  elif stage=='midpoint':k2=interpret(m,state,z,inc);state=add(z,k2,1)
 rows.append(row)
print(json.dumps(rows,indent=2))
