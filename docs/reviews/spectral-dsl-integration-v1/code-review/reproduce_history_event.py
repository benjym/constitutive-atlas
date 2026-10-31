"""Read-only staged-source reproduction; no compiled/author code."""
import sys,json
from pathlib import Path
STAGE=Path('/private/tmp/atlas-spectral-dsl-candidate-v1')
sys.path.insert(0,str(STAGE))
from atlas.history import validate_program,make_snapshot,advance
from atlas.dsl import ValidationError
program={'schema_version':'experimental-history-0.1','id':'spectral_guard_review','sources':[{'url':'https://example.com/project-review','locator':'synthetic arithmetic/event-policy probe only'}],'fields':{'x':{'shape':'scalar','unit':'1','storage':'state'}},'inputs':{'stress':{'shape':'sym','unit':'Pa'}},'phases':[{'name':'step','kind':'advance','base':'parent','bindings':{'A':{'input':'stress'}},'guard':'select(principal_max_value(A)>0*trace(A),-1,1)','writes':{'x':'1'}}]}
validate_program(program)
parent=make_snapshot(program,{'x':0.})
r=advance(program,parent,{'stress':[3.,3.,3.,0.,0.,0.]})
assert r['ok'] and r['snapshot']['values']['x']==1. and r['events']==[{'phase':'step','kind':'advance'}]
direct=json.loads(json.dumps(program));direct['phases'][0]['guard']='principal_max_value(A)/trace(A)'
try:validate_program(direct)
except ValidationError:direct_rejected=True
else:direct_rejected=False
assert direct_rejected
print(json.dumps({'current_candidate_accepts_value_only_control_in_history_guard':True,'active_event':r['events'],'result_x':r['snapshot']['values']['x'],'direct_value_only_guard_rejected':direct_rejected,'expected_under_agreed_strict_policy':'reject original program during validation','scope':'source-only synthetic history/event-policy probe'},indent=2))
