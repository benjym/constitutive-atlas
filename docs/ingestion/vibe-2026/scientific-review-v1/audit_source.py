"""Independent E5 review checks; no production/compiled model execution."""
import json,hashlib,importlib.util
from pathlib import Path
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
W=Path('/private/tmp/atlas-vibe2026-controlled-time-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
model=W/'models/research/vibe/vibe-2026-explicit-appendix-a.json'
assert sha(model)=='a7d3f0f61ff6654f1dc924178a3551a740ca39212a99813c2b9ce5c15b16c987'
source=ROOT/'docs/ingestion/vibe-2026/source-v2'
receipt=load(source/'source-receipt.json')
for x in receipt['private_artifacts']:assert sha(ROOT/x['path'])==x['sha256']
assert sha(Path(receipt['user_original']['path']))==receipt['user_original']['sha256']
# Check every file directly, not just a parent receipt.
closures=[]
for name in ['source-v2','reference-v1','reference-v2','review-numerical-v1','review-numerical-v2']:
 p=ROOT/'docs/ingestion/vibe-2026'/name/'manifest.json';d=load(p);count=0
 for x in d.get('files',[]):
  if isinstance(x,dict) and 'path' in x and 'sha256' in x:
   q=ROOT/x['path'];assert q.is_file() and sha(q)==x['sha256'],str(q);count+=1
 closures.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'direct_files_verified':count})
# Direct rational action verifies source-completed rank-four inverse, not production expressions.
rank_checks=0
for q in [F(-1,4),F(-1,10),F(0),F(1,3),F(4)]:
 for k in range(6):
  x=[F(i==k) for i in range(6)];tr=sum(x[:3]);bx=[v+(q*tr if i<3 else 0) for i,v in enumerate(x)]
  inverse=[v-(q/(1+3*q)*sum(bx[:3]) if i<3 else 0) for i,v in enumerate(bx)]
  assert inverse==x;rank_checks+=6
# Independently import source oracle only: all 32 retained point rates reproduce.
spec=importlib.util.spec_from_file_location('vibe_source_oracle',ROOT/'docs/ingestion/vibe-2026/reference-v1/oracle.py');o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
points=load(ROOT/'docs/ingestion/vibe-2026/reference-v1/point-results.json')
point_checks=[]
with localcontext() as c:
 c.prec=100
 for row in points['cases']:
  r=row['reference'];p=o.params();p.update({k:D(str(v)) for k,v in r['parameter_overrides'].items()})
  y=list(map(D,r['initial_state']));mech=list(map(D,r['mechanical_rate_per_s']))
  actual,obs=o.rate(y,D(r['suction_Pa']),D(r['temperature_K']),D(r['suction_rate_Pa_per_s']),D(r['temperature_rate_K_per_s']),mech,p,True)
  assert actual==list(map(D,r['rate'])),row['id']
  assert all(obs[k]==D(v) for k,v in r['observables'].items()),row['id']
  # A15 mechanical void law is trace, not sum of all Mandel entries.
  assert actual[6]==-(1+y[6])*sum(mech[:3])
  point_checks.append(row['id'])
 # Reassess raw saved endpoints/refinement numerically rather than trusting pass flags.
 histories=[]
 for directory,names in [('reference-v1',['near_hold_1000','near_hold_3600','dry_hold_1000','mixed_ramp_100','hydraulic_reversal_100']),('reference-v2',['mixed_mechanical_100','mechanical_reversal_100','coupled_mechanical_THM_100'])]:
  for name in names:
   d=load(ROOT/'docs/ingestion/vibe-2026'/directory/(name+'.json'));runs=[r['result'] for r in d['runs']];assert [(r['partitions'],r['precision']) for r in runs]==[(64,70),(128,70),(256,70),(256,50)]
   ratios=[]
   for ia,ib in [(1,2),(2,3)]:
    a,b=runs[ia],runs[ib]
    for i,(x,y) in enumerate(zip(a['final_state'],b['final_state'])):
     x,y=D(x),D(y);tol=(D('.01') if i<6 else D('1e-9'))+D('1e-7')*max(abs(x),abs(y));ratio=abs(x-y)/tol;assert ratio<=1;(ratios.append(ratio))
    for k in ['em','eM','S','Sr','OA','re']:
     x,y=D(a['endpoint_observables'][k]),D(b['endpoint_observables'][k]);ratio=abs(x-y)/(D('1e-8')+D('1e-7')*max(abs(x),abs(y)));assert ratio<=1;ratios.append(ratio)
   r=runs[2];e0=D(r['initial_state'][6]);trace=D('4e-8') if name in ['mixed_mechanical_100','coupled_mechanical_THM_100'] else D(0)
   target=(1+e0)*(-trace*D(r['duration_s'])).exp()-1
   error=abs(D(r['final_state'][6])-target);assert error<D('1e-9')
   histories.append({'id':name,'raw_endpoint_convergence_max_ratio':str(max(ratios)),'independent_A15_void_error':str(error)})
summary={'status':'pass','reviewer':'/root/vibe_scientific_review','no_compiled_calls':True,'model_sha256':sha(model),'source_pdf_sha256':receipt['user_original']['sha256'],'closure_checks':closures,'rational_inverse_component_checks':rank_checks,'independent_oracle_points_reproduced_exactly':point_checks,'histories_raw_gates_reassessed':histories,'backend_e5':'pending actual native/Wasm evidence'}
with (OUT/'source-audit-results.json').open('x') as f:f.write(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
