"""Fresh reviewer replay/refinement of proposed independent reference, no compiled calls."""
import hashlib,importlib.util,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
PLAN=HERE.parent
spec=importlib.util.spec_from_file_location('reviewed_reference',PLAN/'reference.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
retained=json.loads((PLAN/'references.json').read_text())
records=[]
for case in r.cases():
    old=retained[case['id']]['points']; fresh=r.solve(case,32)
    errors=[max(abs(x[j]-y[j]) for x,y in zip(old,fresh)) for j in range(7)]
    assert max(errors[:3])<=.01 and max(errors[3:])<=1e-10,errors
    checks=[]
    for c,y in zip(case['controls'],fresh):
        assert all(math.isfinite(v) for v in y) and min(y[:3])>0 and y[3]>.35
        if case['protocol']==1:assert abs((y[1]+y[2])/2-100000)<2e-7
        if case['protocol']==3:assert abs(y[0]-(y[1]+y[2])/2-c)<2e-7
        # Exact incompressible-grain relation for the integrated total strain.
        assert abs(y[3]-(1.75*math.exp(-math.fsum(y[4:]))-1))<1e-10
    records.append({'id':case['id'],'points':len(fresh),'refinement_16_to_32_maximum':errors,'all_states_finite_positive_stress_density_interior':True,'volume_control_checks':True})
result={'reviewer':'/root/barodesy_sand_review','reference_sha256':hashlib.sha256((PLAN/'reference.py').read_bytes()).hexdigest(),'references_sha256':hashlib.sha256((PLAN/'references.json').read_bytes()).hexdigest(),'records':records,'pass':True,'scope':'Prospective discrete endpoint-control reference; not stagewise drained closure or compiled qualification','compiled_calls':0}
print(json.dumps(result,indent=2))
