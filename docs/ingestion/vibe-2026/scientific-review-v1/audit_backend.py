"""Reassess saved actual backend outputs only; never imports or loads an engine."""
from pathlib import Path
from decimal import Decimal as D,localcontext
from collections import Counter
import json,hashlib,sys,math
ROOT=Path(__file__).resolve().parents[4];W=Path('/private/tmp/atlas-vibe2026-controlled-time-v1');OUT=Path(__file__).parent
backend=sys.argv[1];folder=ROOT/'docs/ingestion/vibe-2026/execution-v1'/(backend+'-vibe-results')
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
planpath=W/'docs/ingestion/vibe-2026/numerical-qualification-v1/plan-v2.json';plan=load(planpath);assert sha(planpath)=='b70950d1981602d9bc053f708214fde7c93efda1dde97420b10295c015d890da'
summary=load(folder/'summary.json');assert summary['bindings']['model_file_sha256']=='a7d3f0f61ff6654f1dc924178a3551a740ca39212a99813c2b9ce5c15b16c987';assert summary['bindings']['plan_sha256']==sha(planpath)
for name,h in summary['result_files'].items():assert sha(folder/name)==h,name
assert sha(folder/'events.jsonl')==summary['events_sha256']
ratios=[]
def check(a,b,absolute,relative='1e-7'):
 a,b=D(str(a)),D(str(b));assert a.is_finite() and b.is_finite();r=abs(a-b)/(D(absolute)+D(relative)*max(abs(a),abs(b)));assert r<=1,(a,b,r);ratios.append(r)
def state_flat(s):return s['sigma_net']+[s['e'],s['a_scan']]
def endpoint(result,ref):
 for i,(a,b) in enumerate(zip(state_flat(result['context']['state']),ref['expected_state'])):check(a,b,'.01' if i<6 else '1e-9')
 obs=result['points'][-1]['observables']
 for k,b in ref['expected_observables'].items():check(obs[k],b,'1e-8')
 for p in result['points']:
  assert p['context']['profile']=='controlled-time-ode-v1';assert p['context']['model_sha256']==plan['model_sha256']
  for a,b in zip(p['observables']['stress'],p['context']['state']['sigma_net']):check(a,b,'.01')
  for v in p.get('diagnostics',{}).values():assert math.isfinite(v)
with localcontext() as c:
 c.prec=100
 points=load(folder/'points.json');assert len(points)==32
 for actual,ref in zip(points,plan['points']):
  assert actual['id']==ref['id']
  for i,(a,b) in enumerate(zip(state_flat(actual['rate']),ref['expected_rate'])):check(a,b,'1e-8' if i<6 else '1e-12')
  for k,b in ref['expected_observables'].items():check(actual['observables'][k],b,'1e-8')
  for a,b in zip(actual['observables']['stress'],ref['context']['state']['sigma_net']):check(a,b,'.01')
 histories=[]
 for ref in plan['histories']:
  name=ref['id'];counts=[]
  for suffix in ['', '-restart','-maxstep-10.0','-maxstep-5.0','-maxstep-2.5']:
   r=load(folder/(name+suffix+'.json'));endpoint(r,ref);counts.append(len(r['points']))
  histories.append({'id':name,'checked_variants':5,'saved_sample_counts':counts})
events=[json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines()];kinds=Counter(x['kind'] for x in events)
# Every actual call must pair an immutable preimage with a matching terminal record.
pending=None;refusals=0
for e in events:
 if e['kind']=='before-CABI':assert pending is None;pending=e
 if e['kind']=='after-CABI':
  assert pending is not None and pending['operation']==e['operation'];assert pending['inputs']==e['inputs'];assert e['status'] in [0,1]
  if e['status']==0:assert pending['outputs']==e['outputs'];refusals+=1
  pending=None
assert pending is None
raw_before=[e for e in events if e['kind']=='before-raw-domain'];raw_after=[e for e in events if e['kind']=='after-raw-domain'];assert len(raw_after)==10
for a,b in zip(raw_before,raw_after):
 assert a['case']==b['case'] and a['operation']==b['operation'] and b['status']==0
 # These records retain all explicitly sentinel-initialized raw output buffers.
 assert all(v==-1234567.0 for ar in b['outputs'] for v in ar)
assert {x['case'] for x in raw_after if x['operation']=='evaluate'}=={x['id'] for x in plan['invalid_cases']}
result={'status':'pass-saved-evidence','backend':backend,'summary_sha256':sha(folder/'summary.json'),'direct_result_files':len(summary['result_files']),'event_kinds':dict(kinds),'raw_CABI_refusals_rechecked':refusals,'raw_model_domain_refusals':len(raw_after),'point_cases':32,'histories':histories,'numeric_components_reassessed':len(ratios),'max_original_tolerance_ratio':str(max(ratios)),'no_compiled_calls_by_reviewer':True}
with (OUT/(backend+'-audit-results.json')).open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
