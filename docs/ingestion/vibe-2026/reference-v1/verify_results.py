"""Check retained reference evidence gates; no production calls or constitutive equations."""
from pathlib import Path
from decimal import Decimal as D
import json,hashlib
ROOT=Path(__file__).parent
plan=ROOT/'plan.json'
assert hashlib.sha256(plan.read_bytes()).hexdigest()=='facc17e21d786328f4b28e8c20d9d3e5b1909becb3e3d971195ca5d7c9435a63'
p=json.loads((ROOT/'point-results.json').read_text());assert len(p['cases'])==32 and len(p['invalid_cases'])==7
for case in p['cases']:
 assert case['status']=='pass'
 assert all(x['pass'] for x in case['precision_convergence'].values())
for case in p['invalid_cases']:assert case['status']=='refused'
points={x['id']:x['reference'] for x in p['cases']}
assert all(D(x)==0 for x in points['rate_independent_hold']['rate'])
assert D(points['IvT_zero_hold']['rate'][0])!=0
for name in ['dry_hold','near_hold']:
 assert all(D(x)==0 for x in points[name]['rate'][6:])
summary=[]
for name in ['near_hold_1000','near_hold_3600','dry_hold_1000','mixed_ramp_100','hydraulic_reversal_100']:
 r=json.loads((ROOT/(name+'.json')).read_text());assert len(r['runs'])==4 and all(x['status']=='pass' for x in r['runs'])
 for gate in ['partition_convergence','precision_convergence']:assert all(x['pass'] for x in r[gate].values())
 v=r['runs'][2]['result'];assert len(v['final_state'])==8 and all(D(x)==0 for x in v['change'][3:6])
 if 'hold' in name:assert all(D(x)==0 for x in v['change'][6:])
 assert D(v['change'][6])==0
 summary.append({'id':name,'compression_change_Pa':v['change'][0],'scan_change':v['change'][7],'partition_max_ratios':{k:v['max_tolerance_ratio'] for k,v in r['partition_convergence'].items()},'precision_max_ratios':{k:v['max_tolerance_ratio'] for k,v in r['precision_convergence'].items()}})
print(json.dumps({'status':'pass','point_cases':32,'invalid_refusals':7,'converged_trajectories':5,'trajectories':summary},indent=2))
