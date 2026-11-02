"""Verify frozen v2 evidence, including source-independent exact void-ratio solution."""
from pathlib import Path
from decimal import Decimal as D,localcontext
import hashlib,json
ROOT=Path(__file__).parent
assert hashlib.sha256((ROOT/'plan.json').read_bytes()).hexdigest()=='6dd5a3b20eabcac10ffe82e0385d72cd37364009133a92c596898d0b322e814d'
summary=[]
for label in ['mixed_mechanical_100','mechanical_reversal_100','coupled_mechanical_THM_100']:
 d=json.loads((ROOT/(label+'.json')).read_text());assert all(r['status']=='pass' for r in d['runs'])
 for gate in ['partition_convergence','precision_convergence']:assert all(v['pass'] for v in d[gate].values())
 v=d['runs'][2]['result'];assert len(v['final_state'])==8 and len(v['endpoint_rate'])==8
 with localcontext() as c:
  c.prec=80;e0=D(v['initial_state'][6]);target=e0 if label=='mechanical_reversal_100' else (1+e0)*(-D('4e-8')*100).exp()-1
  error=abs(D(v['final_state'][6])-target);assert error<D('1e-9')
  if label!='coupled_mechanical_THM_100':assert D(v['change'][7])==0
  else:assert D(v['change'][7])>0
  assert all(D(x)!=0 for x in v['change'][:6])
  summary.append({'id':label,'status':'pass','change':v['change'],'analytical_void_ratio_absolute_error':str(error),'partition_max_ratios':{k:x['max_tolerance_ratio'] for k,x in d['partition_convergence'].items()},'precision_max_ratios':{k:x['max_tolerance_ratio'] for k,x in d['precision_convergence'].items()}})
print(json.dumps({'task':'REF-vibe2026-mechanical-histories-v2','status':'pass','histories':summary},indent=2))
