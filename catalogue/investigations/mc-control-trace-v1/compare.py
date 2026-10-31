"""Post-observation diagnostic only: original acceptance limits are unchanged."""
from pathlib import Path
import json
from assess import load,same,q
s=Path(__file__).resolve().parent;n,w=[load(s/b/'raw.json')for b in ('native','wasm')]
def first_point(a,b):
 for i,(x,y)in enumerate(zip(a['points'],b['points'])):
  if not same(x,y):return {'step':i,'native':x,'wasm':y}
 return None
def first_call(a,b):
 for i,(x,y)in enumerate(zip(a['calls'],b['calls'])):
  if not same(x,y):return {'call_index':i,'left':x,'right':y,'same_parent':same(x['parent'],y['parent']),'same_de':same(x['de'],y['de'])}
 return None
out={'identity':'post-observation-control-trace-comparison-v1','numeric_bounds_changed':False,'within_backend':{},'between_backends':{}}
for b,doc in [('native',n),('wasm',w)]:
 a,c=doc['streams'];out['within_backend'][b]={'sine_vs_literal_points_identical':same(a['traced'],c['traced']),'sine_vs_literal_calls_identical':same(a['calls'],c['calls'])}
for i,mode in enumerate(('backend-sine','common-literal')):
 a,b=n['streams'][i],w['streams'][i]
 fail=[]
 for step,(x,y)in enumerate(zip(a['traced']['points'],b['traced']['points'])):
  for key in ('control','state','strain','u','q_signed'):
   xx,yy=(q(x['state']),q(y['state']))if key=='q_signed'else(x[key],y[key]);xx=xx if isinstance(xx,list)else[xx];yy=yy if isinstance(yy,list)else[yy]
   for j,(v,z)in enumerate(zip(xx,yy)):
    fraction=abs(v-z)/(1e-10*max(1,abs(v),abs(z)))
    if fraction>1:fail.append(dict(step=step,field=key,component=j,difference=abs(v-z),budget_fraction=fraction))
 out['between_backends'][mode]={'controls_identical':same([p['control']for p in a['traced']['points']],[p['control']for p in b['traced']['points']]),'first_point_difference':first_point(a['traced'],b['traced']),'first_call_difference':first_call(a,b),'call_counts':[len(a['calls']),len(b['calls'])],'failed_subset_parity_scalars':fail}
(s/'comparison.json').write_text(json.dumps(out,indent=2)+'\n')
for mode,x in out['between_backends'].items():
 print(mode,'controls_identical',x['controls_identical'],'first_point',x['first_point_difference']['step']if x['first_point_difference']else None,'first_call',None if x['first_call_difference']is None else {k:v for k,v in x['first_call_difference'].items()if k in('call_index','same_parent','same_de')},'subset_failures',len(x['failed_subset_parity_scalars']))
 if x['first_call_difference']:
  v=x['first_call_difference'];print('first-call-detail',v['left']['step'],v['left']['iteration'],v['left']['role'],v['left']['de'],v['right']['de'],v['left']['state'],v['right']['state'])
print(out['within_backend'])
