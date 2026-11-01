"""Prospective trace checks and independent rounded-branch comparison, no material calls."""
from pathlib import Path
from fractions import Fraction as F
import json
P=Path(__file__).parent

def assess(row,inputs,reference):
 assert row['equivalent'] and row['input_unchanged'] and row['recovery']
 assert row['baseline']==row['traced']
 assert row['baseline']['state']==inputs['parent']
 # These are diagnostic comparisons, not a predeclared cause or a material pass.
 events=row['events'];trials=[e for e in events if e['kind']=='trial'];jac=[e for e in events if e['kind']=='jacobian-evaluation'];active=[r for r in row['derived']if r['loading']==inputs['loading']]
 assert active,'missing active-increment branch observation'
 for r in active:
  assert r['trial']==reference['trial_dev']
  assert r['vmax']==reference['trial_dev'][0] and r['vmid']==r['vmin']==reference['trial_dev'][1]
  assert r['branch']==3 and r['width']==16
  assert F.from_float(r['vmax'])-F.from_float(r['vmin'])>F(16)
  assert 3*r['vmid']==r['trace_trial']-r['width']
 for e in trials:
  assert e['post_physical']==bool(e['physical'])
  if e['raw']>=0:assert e['post_raw_ok']==bool(e['raw'])
  if e['descent']>=0:assert e['descent'] in (0,1)
 failed_eval=bool(jac)and jac[0]['raw']==0
 conclusion='Raw Jacobian evaluation rejects before a Newton correction or backtracking; exact range and rounded corner branch disagree at repeated-minimum boundary.' if failed_eval and not trials else 'Recorded trace requires further interpretation.'
 return {'diagnostic_verified':True,'material_solve_ok':row['baseline']['ok'],'full_rollback':row['full_rollback'],'initial_raw_jacobian_failed':failed_eval,'newton_corrections':sum(e['kind']=='delta'for e in events),'backtracking_trials':len(trials),'active_derived_observations':len(active),'nearest_physical_state_admissible':row['nearest_probe']['physical'],'nearest_physical_state_raw_evaluable':row['nearest_probe']['raw_ok'],'conclusion':conclusion}
def run():
 inputs=json.loads((P/'inputs.json').read_text());ref=json.loads((P/'rounded-reference.json').read_text());return {b:assess(json.loads((P/(b+'-response.json')).read_text()),inputs,ref)for b in ['native','wasm']}
if __name__=='__main__':print(json.dumps(run(),indent=2))
