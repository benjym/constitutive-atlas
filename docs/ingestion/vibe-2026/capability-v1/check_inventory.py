"""Read-only contract/type probes and exact independent rank-one identity.
No VIBE implementation is imported or executed; no material integration occurs.
"""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from atlas.model import load,migrate_formulation,validate,MAX_STATE_COMPONENTS
from atlas.dsl import Type,parse,infer,DIMS
OUT=Path(__file__).resolve().parent
paths=['AGENTS.md','docs/FORMULATION_CONTRACT.md','docs/TIME_ODE_API.md','docs/TIMED_SCHEDULES.md','docs/STATE_CAPACITY.md','schemas/model-v0.3.schema.json','schemas/run-v0.2.schema.json','atlas/model.py','atlas/dsl.py','atlas/compiler.py','atlas/path.py','atlas/path_compiler.py','atlas/initialization.py','atlas/schedule.py','atlas/stress.py','cpp/include/atlas/time.hpp','cpp/include/atlas/schedule.hpp','cpp/include/atlas/path_runtime.hpp','cpp/main.cpp','web/app.js','web/timed-laboratory.mjs','tools/build_web.py']
inputs=[]
for p in paths:
    f=ROOT/p
    if f.is_file(): inputs.append({'path':p,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
private=ROOT/'.local/private-sources/vibe-2026/dataset-readable/VIBEPaperDataset/lintriax'
for name in ['generalmod.cc','generalmod.h']:
    p=private/name
    inputs.append({'private_source_path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'executed':False})
base=migrate_formulation(load(ROOT/'tests/fixtures/time/maxwell.json'),stress_scope='total')
probes=[]
def reject(label,mutate):
    m=deepcopy(base);mutate(m)
    try: validate(m)
    except ValueError as e: probes.append({'name':label,'expected':'reject','actual':'reject','message':str(e)});return
    raise AssertionError('unexpected acceptance: '+label)
reject('extra_temperature_stage_input',lambda m:m['formulation']['inputs']['equation'].update(temperature={'quantity':'temperature','shape':'scalar','unit':'K','sampling':'stage','constraint':'positive_finite'}))
reject('extra_suction_stage_input',lambda m:m['formulation']['inputs']['equation'].update(suction={'quantity':'pressure','shape':'scalar','unit':'Pa','sampling':'stage','constraint':'finite'}))
reject('net_stress_scope',lambda m:m['formulation']['stress'].update(scope='net'))
reject('physical_time_path_ode_relabel',lambda m:m['formulation'].update(equation_form='path_ode'))
symbols={'X':Type('sym',DIMS['Pa']),'q':Type(),'I':Type('sym')}
expr='X-q/(1+3*q)*trace(X)*I'
assert infer(parse(expr),symbols)==Type('sym',DIMS['Pa'])
probes.append({'name':'rank_one_inverse_action_type','expected':'supported','actual':'supported','expression':expr})
for expression in ['inverse(X)','X[0]','X*X']:
    try:infer(parse(expression),symbols)
    except ValueError as e:probes.append({'name':expression,'expected':'reject','actual':'reject','message':str(e)});continue
    raise AssertionError(expression)
# Exact inverse B=Id+q I tensor I, in six-component Mandel order.
# This is algebra, not compiled output or a VIBE trajectory.
identities=0
for q in [F(-1,4),F(0),F(1,7),F(3),F(100)]:
    for x in [[F(i+1) for i in range(6)],[F(-7),F(2),F(9),F(3,2),F(-4),F(1,3)]]:
        inv=[a-q/(1+3*q)*sum(x[:3]) if i<3 else a for i,a in enumerate(x)]
        recovered=[a+q*sum(inv[:3]) if i<3 else a for i,a in enumerate(inv)]
        assert recovered==x;identities+=6
result={'task':'CAP-vibe2026-contract-inventory-v1','scope':'source/schema/code introspection; no VIBE/backend/browser execution','inputs':inputs,'probes':probes,'algebra':{'exact_fraction_components_checked':identities,'rank_one_singularity':'1+3*q == 0 must reject or have source-supported separate branch','arbitrary_matrix_inverse_required_by_this_source_fragment':False},'state_capacity':{'source_upper_bound_with_all_qstates_plus_net_stress':15,'runtime_limit':MAX_STATE_COMPONENTS,'capacity_gap':False},'source_completeness':'Readable dataset implementation only; paper reconciliation pending source specialist','scientific_approval':False}
(OUT/'inventory-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'probes':len(probes),'all_as_expected':True,'exact_rank_one_components':identities,'source_files_executed':0}))
