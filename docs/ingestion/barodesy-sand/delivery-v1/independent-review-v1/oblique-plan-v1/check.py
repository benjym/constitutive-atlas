"""Independent reviewer checks of the Cartesian oblique reference addition."""
from pathlib import Path
import hashlib,importlib.util,json,math
HERE=Path(__file__).resolve().parent
PLAN=HERE.parents[1]
ROOT=HERE.parents[5]
spec=importlib.util.spec_from_file_location('candidate_reference',PLAN/'reference.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
ret=json.loads((PLAN/'oblique-reference.json').read_text())
inputs=json.loads((ROOT/'docs/ingestion/barodesy-sand/rate-study-v2/inputs.json').read_text())
source=json.loads((ROOT/'docs/ingestion/barodesy-sand/rate-study-v2/reference.json').read_text())
case=next(x for x in inputs['valid'] if x['id']=='oblique')
expected=next(x['oracle120']['values'] for x in source['records'] if x['id']=='oblique')
rate=r.tensor_rate(case['state'],case['loading'])
rateerr=max(abs(x-y) for x,y in zip(rate[:6],expected[:6]))/max(r.PARAMETERS[3]*math.hypot(*case['loading']),math.hypot(*expected[:6]))
assert rateerr<2e-12
assert abs(rate[6]-expected[6])<1e-17
current=list(ret['initial']);points=[current]
for d in ret['increments']:
    after=r.tensor_advance(current,d,64)
    if not any(d):assert after==current
    points.append(after);current=after
error=[max(abs(a[j]-b[j]) for a,b in zip(points,ret['points'])) for j in range(7)]
assert max(error[:6])<.01 and error[6]<1e-10
cum=[0.]*6
for i,y in enumerate(points):
    if i:cum=[a+b for a,b in zip(cum,ret['increments'][i-1])]
    assert abs(y[6]-(1.75*math.exp(-math.fsum(cum[:3]))-1))<1e-12
    xx,yy,zz,xy,yz,xz=y[:6]
    assert xx>0 and xx*yy-xy*xy/2>0
    assert xx*yy*zz-(xx*yz*yz+yy*xz*xz+zz*xy*xy)/2+xy*yz*xz/math.sqrt(2)>0
result={'reviewer':'/root/barodesy_sand_review','pass':True,'scope':'prospective oblique source reference only; no compiled calls','input_sha256':{f:hashlib.sha256((PLAN/f).read_bytes()).hexdigest() for f in ['reference.py','references.json','oblique-reference.json']},'numpy_version':r.np.__version__,'source_rate_scaled_stress_error':rateerr,'refinement_32_to_64_maximum':error,'exact_zero_preserves_all_state':True,'volume_identity_all_points':True,'positive_definite_all_points':True,'prospective_stress_budget_Pa':5,'prospective_void_budget':2e-7,'accepted_prospective_plan':True,'compiled_approval':False}
print(json.dumps(result,indent=2))
