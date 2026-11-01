"""Independent backend passes plus the prospective full-state parity budgets."""
from pathlib import Path
import json,sys,math
B=Path(__file__).resolve().parent
native=json.loads(Path(sys.argv[1]).read_text());wasm=json.loads(Path(sys.argv[2]).read_text());fail=[];worst=0.;comparisons=0
def check(x,label):
 if not x:fail.append(label)
def state(a,b,label):
 global worst,comparisons
 check(len(a)==len(b)==7,label+' shape')
 for x,y in zip(a,b):
  d=abs(x-y)/1e5;check(math.isfinite(d) and d<=4e-8,label+' state');worst=max(worst,d);comparisons+=1
for k in ['cases','paths','transactions','invalids','diagnostics','derivatives','presets']:
 check([x['id'] for x in native[k]]==[x['id'] for x in wasm[k]],k+' identities')
for a,b in zip(native['cases'],wasm['cases']):
 for x,y in zip(a['calls'],b['calls']):
  check(x['response']['ok']==y['response']['ok'],a['id']+' status')
  if x['response']['ok'] and y['response']['ok']:state(x['response']['state'],y['response']['state'],a['id'])
for a,b in zip(native['paths'],wasm['paths']):
 for key in ['calls','holds','restart']:
  check(len(a[key])==len(b[key]),a['id']+' '+key+' coverage')
  for x,y in zip(a[key],b[key]):
   check(x['response']['ok']==y['response']['ok'],a['id']+' '+key+' status')
   if x['response']['ok'] and y['response']['ok']:state(x['response']['state'],y['response']['state'],a['id']+' '+key)
for a,b in zip(native['presets'],wasm['presets']):
 for key in ['call','replay','restart','invalid','recovery']:
  x=a[key]['response'];y=b[key]['response'];check(x['ok']==y['ok'],a['id']+' '+key+' status');check(len(x.get('points',[]))==len(y.get('points',[])),a['id']+' '+key+' coverage')
  for p,q in zip(x.get('points',[]),y.get('points',[])):state(p['state'],q['state'],a['id']+' '+key)
for key in ['transactions','invalids','diagnostics']:
 for a,b in zip(native[key],wasm[key]):check(a['call']['response']['ok']==b['call']['response']['ok'],a['id']+' rejection parity')
for a,b in zip(native['derivatives'],wasm['derivatives']):
 x=a['call']['response'];y=b['call']['response'];check(x['ok'] and y['ok'],a['id']+' derivative status')
 for row,other in zip(x.get('jacobian',[]),y.get('jacobian',[])):
  for p,q in zip(row,other):check(math.isfinite(p-q) and abs(p-q)<=4e-5,a['id']+' derivative parity')
result=dict(identity='duncan-material-backend-parity-v1',pass_=not fail,failures=fail,state_components_compared=comparisons,worst_normalized_state_difference=worst,bitwise_backend_claim=False)
Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));sys.exit(bool(fail))
