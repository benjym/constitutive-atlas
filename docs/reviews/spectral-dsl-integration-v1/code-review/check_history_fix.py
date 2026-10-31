"""Read-only staged-source reproduction; no compiled/author code."""
import sys,json
from pathlib import Path
STAGE=Path('/private/tmp/atlas-spectral-dsl-candidate-v1')
sys.path.insert(0,str(STAGE))
from atlas.history import validate_program,make_snapshot,advance
from atlas.dsl import ValidationError
program={'schema_version':'experimental-history-0.1','id':'spectral_guard_review','sources':[{'url':'https://example.com/project-review','locator':'synthetic arithmetic/event-policy probe only'}],'fields':{'x':{'shape':'scalar','unit':'1','storage':'state'}},'inputs':{'stress':{'shape':'sym','unit':'Pa'}},'phases':[{'name':'step','kind':'advance','base':'parent','bindings':{'A':{'input':'stress'}},'guard':'select(principal_max_value(A)>0*trace(A),-1,1)','writes':{'x':'1'}}]}

try:validate_program(program)
except ValidationError:rejected=True
else:rejected=False
assert rejected
program['phases'][0]['guard']='select(principal_max(A)>0*trace(A),-1,1)'
validate_program(program)
print(json.dumps({'value_only_signed_guard_rejected':rejected,'ordinary_spectral_control_accepted':True,'compiled_execution':False},indent=2))
