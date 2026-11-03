"""Independent comparison of retained native/Wasm samples and raw failure recovery."""
from pathlib import Path
from decimal import Decimal as D
import json,hashlib
R=Path(__file__).resolve().parents[4];E=R/'docs/ingestion/vibe-2026/execution-v1';O=Path(__file__).parent
N=E/'native-vibe-results';W=E/'wasm-vibe-results'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ns=load(N/'summary.json');ws=load(W/'summary.json');assert ws['bindings']['native_peer_summary_sha256']==sha(N/'summary.json')
counts={'state':0,'observable':0,'identity_fields':0};maxratio=D(0)
def numeric(a,b,ab):
 global maxratio
 a,b=D(str(a)),D(str(b));assert a.is_finite() and b.is_finite();ratio=abs(a-b)/(D(ab)+D('1e-7')*max(abs(a),abs(b)));assert ratio<=1;maxratio=max(maxratio,ratio)
def context(a,b):
 for k in ['time','controls','control_rates','parameters','model_sha256','profile']:assert a[k]==b[k],k;counts['identity_fields']+=1
 for k in ['sigma_net','e','a_scan']:
  av,bv=(a['state'][k],b['state'][k]);av=av if isinstance(av,list) else [av];bv=bv if isinstance(bv,list) else [bv]
  for x,y in zip(av,bv):numeric(x,y,'.01' if k=='sigma_net' else '1e-9');counts['state']+=1
for name in ws['result_files']:
 if name=='bindings.json':continue
 a,b=load(N/name),load(W/name);assert a['request']==b['request'];context(a['context'],b['context']);assert len(a['points'])==len(b['points'])
 for x,y in zip(a['points'],b['points']):
  assert x['segment']==y['segment'] and x['side']==y['side'];context(x['context'],y['context'])
  for k in x['observables']:
   av,bv=x['observables'][k],y['observables'][k];av=av if isinstance(av,list) else [av];bv=bv if isinstance(bv,list) else [bv]
   for z,t in zip(av,bv):numeric(z,t,'.01' if k=='stress' else '1e-8');counts['observable']+=1
recoveries={}
for label,p in [('native',N),('wasm',W)]:
 ev=[json.loads(x) for x in (p/'events.jsonl').read_text().splitlines()];calls=[x for x in ev if x['kind']=='after-CABI'];failed=[i for i,x in enumerate(calls) if x['status']==0]
 for i in failed:assert i+1<len(calls) and calls[i+1]['status']==1
 domain=[]
 for i,x in enumerate(ev):
  if x['kind']==('before-raw-domain' if label=='native' else 'raw-domain-case'):
   call=next(z for z in ev[i+1:] if z['kind']=='after-CABI');assert call['status']==0;assert call['operation'].lstrip('_')=='controlled_time_'+x['operation'];domain.append([x['case'],x['operation']])
 assert len(domain)==10
 for suction in ['zero_suction','negative_suction']:
  assert [suction,'evaluate'] in domain and [suction,'advance'] in domain
 recoveries[label]={'actual_failure_then_success_pairs':len(failed),'raw_model_domain_cases':domain}
result={'status':'pass','history_result_pairs':40,'comparison_counts':counts,'max_original_parity_tolerance_ratio':str(maxratio),'raw_refusal_then_actual_success':recoveries,'native_summary_sha256':sha(N/'summary.json'),'wasm_summary_sha256':sha(W/'summary.json'),'no_compiled_calls_by_reviewer':True}
with (O/'parity-and-recovery-results.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
