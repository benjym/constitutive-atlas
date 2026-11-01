"""Saved generic predicate qualification; exact decisions, no numeric tolerance."""
from pathlib import Path
import json
P=Path(__file__).parent

def assess(lines,requests):
    rows=[l.split()for l in lines.splitlines()];assert len(rows)==len(requests)+1
    for i,(row,expected)in enumerate(zip(rows,requests)):
        assert len(row)==9 and list(map(int,row))==[i,1,int(expected['result']),1,int(expected['result']),int(expected['result']),1,1,int(expected['result'])],(i,expected['id'],row)
    assert rows[-1]==['summary',str(len(requests)),'819','1','1'],rows[-1]
    return {'requests':len(requests),'double_decisions':len(requests),'jet_decisions':len(requests),'generated_initial_checks':len(requests),'raw_residual_domain_derived_checks':len(requests),'physical_observation_checks':len(requests),'state_and_output_preserved':len(requests),'seed_and_primal_rejections':819,'failure_masking_and_recovery':True,'history_rollback_and_recovery':True}
if __name__=='__main__':
    requests=json.loads((P/'requests.json').read_text())
    print(json.dumps({backend:assess((P/(backend+'-responses.txt')).read_text(),requests)for backend in ('native','wasm')},indent=2))
