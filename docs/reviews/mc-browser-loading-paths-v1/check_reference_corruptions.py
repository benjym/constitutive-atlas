"""Supplemental source-only negative probes of unchanged precision checker."""
from pathlib import Path
import copy,json,tempfile
from decimal import Decimal as D
from check import run
P=Path(__file__).resolve().parent
low=json.loads((P/'reference-p280.json').read_bytes());high=json.loads((P/'reference-p360.json').read_bytes());probes=[]
with tempfile.TemporaryDirectory(prefix='atlas-browser-reference-corruptions-')as tmp:
 t=Path(tmp);a=t/'a.json';b=t/'b.json';b.write_text(json.dumps(high))
 mutations={
 'stress_component':lambda x:x['paths'][0]['points'][1]['state'].__setitem__(1,'0'),
 'strain_component':lambda x:x['paths'][0]['points'][1]['strain'].__setitem__(0,'0'),
 'q_control':lambda x:x['paths'][6]['points'][1].__setitem__('q','0'),
 'branch_metadata':lambda x:x['paths'][0]['points'][1].__setitem__('branch','fabricated'),
 'source_defect':lambda x:x['paths'][0]['checks'][0]['defects'].__setitem__('yield_violation','1e-20'),
 'missing_direction_shape':lambda x:x['paths'][0]['points'][1]['state'].pop(),
 }
 for label,mutate in mutations.items():
  x=copy.deepcopy(low);mutate(x);a.write_text(json.dumps(x));res=run(a,b,P/'reference-policy.json')
  if res['passed']:raise AssertionError('numeric corruption accepted '+label)
  probes.append({'name':label,'rejected':True,'failure_count':len(res['failures'])})
r={'identity':'mc-browser-loading-reference-corruptions-v1','timing':'supplemental source-only checker after dual references, no source/policy/output edits','passed':True,'probes':probes,'candidate_calls':0,'compiled_observations':0}
(P/'reference-corruption-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'corruption_probes':len(probes)}))
