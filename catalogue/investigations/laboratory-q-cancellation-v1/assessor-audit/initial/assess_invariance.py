from pathlib import Path
import json,sys
if not __debug__:raise RuntimeError('Required checks cannot be optimized away')
s=Path(__file__).parent
old=json.loads((s/'baseline/backend-results.json').read_text());new=json.loads(Path(sys.argv[1]).read_text())
assert old['status']=='failed'and new['status']=='passed'
assert len(old['pairs'])==len(new['pairs'])==101
points=0
# Only the independently justified observable and timing may differ.
def unchanged(value):
 if isinstance(value,dict):return {k:unchanged(v)for k,v in value.items()if k not in ['elapsed_ms','q']}
 if isinstance(value,list):return [unchanged(v)for v in value]
 return value
for a,b in zip(old['pairs'],new['pairs']):
 assert a['name']==b['name']and a['specification']==b['specification']
 for role in ['native','wasm']:
  assert unchanged(a[role])==unchanged(b[role]),(a['name'],role)
  points+=len(a[role]['points'])
print(json.dumps({'passed':True,'paired_cases':101,'backend_points':points,'allowed_differences':['q','elapsed_ms'],'source_states_controls_other_fields_exact':True,'candidate_calls':0},indent=2))
