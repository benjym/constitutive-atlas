"""Additional physical-state/tangent/controller parity, fixed before observation."""
import json,math
from pathlib import Path
from supplement import base
B=Path(__file__).resolve().parent;worst=0.;count=0;statuses=[]
def compare(u,v,floor):
 global worst,count
 assert len(u)==len(v)
 for i,(a,b) in enumerate(zip(u,v)):
  assert math.isfinite(a) and math.isfinite(b)
  error=abs(a-b)/max(floor(i),abs(a),abs(b));worst=max(worst,error);count+=1;assert error<=2e-10,error
for study in ('supplement','transaction','public'):
 a,b=[json.loads((B/f'{s}-{study}-raw.json').read_text()) for s in ('native','wasm')];assert a['request_sha256']==b['request_sha256']
 req=json.loads((B/f"{'supplement' if study=='supplement' else 'transaction' if study=='transaction' else 'public'}-requests.json").read_text())
 for key in ('cases','tangents'):
  if key not in a:continue
  assert len(a[key])==len(b[key])==len(req[key])
  if study!='supplement':assert [r['name'] for r in a[key]]==[r['name'] for r in b[key]]==[r['name'] for r in req[key]]
  for x,y in zip(a[key],b[key]):
   x,y=json.loads(x['stdout']),json.loads(y['stdout']);assert x['ok']==y['ok'];statuses.append(x['ok'])
   if 'state' in x:compare(x['state'],y['state'],lambda i:1000. if i<6 else 1.)
   if x.get('tangent_ok') or y.get('tangent_ok'):
    assert x['tangent_ok']==y['tangent_ok']
    for i,(u,v) in enumerate(zip(x['state_tangent'],y['state_tangent'])):compare(u,v,lambda j:1e5 if i<6 else 1.)
   if 'points' in x:
    assert len(x['points'])==len(y['points'])
    for u,v in zip(x['points'],y['points']):compare(u['state'],v['state'],lambda i:1000. if i<6 else 1.);compare(u['strain'],v['strain'],lambda i:1.)
 if study=='public':
  x,y=[json.loads(r['reference_pressure']['stdout']) for r in (a,b)];assert x['ok'] and y['ok'];compare(x['state'],y['state'],lambda i:1000. if i<6 else 1.)
report=dict(passed=True,physical_scalar_comparisons=count,worst_relative_error=worst,matched_statuses=statuses)
base.dump(B/'extra-parity-results.json',report);print(json.dumps(report,indent=2))
