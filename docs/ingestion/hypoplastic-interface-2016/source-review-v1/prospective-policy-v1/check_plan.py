"""Prospective plan assertions; no material equation or trajectory evaluations."""
import hashlib,json,math
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016/implementation-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'policy.json')=='bd8ee5fc47aff6dfd064ccd04b6be9fb1bf838afd3f695e5b0b74eec0d167928'
j=json.loads((P/'policy.json').read_text());assert j['parameters']['hs']==1000*1e6
assert math.isclose(j['parameters']['phi_c'],33*math.pi/180,rel_tol=0,abs_tol=1e-15)
assert j['reference']['scale']==[100000,100000,100000,100000,1]
assert j['state_order']==['sigma_n','sigma_p','tau_x','tau_z','e']
assert len(j['stress_order'])==6 and j['qualification']['all_five_states'] and j['qualification']['all_six_mandel_stresses']
cs={c['name']:c for c in j['cases']};assert len(cs)==10
assert cs['exact_isotropy']['initial']==[100000,100000,0,0,.67]
assert cs['near_isotropy']['initial'][2]!=0 and cs['near_isotropy']['initial'][3]!=0
assert cs['unequal_with_existing_shear']['initial'][2]!=0 and cs['unequal_with_existing_shear']['initial'][3]!=0
assert j['reference']['steps_per_segment']==[128,256,512]
sc=j['reference']['scale'];r=j['reference']['convergence_scaled_absolute'];q=j['qualification']['endpoint_scaled_absolute']
result=dict(accepted_for_bounded_prospective_study=True,material_trajectories_observed=0,reference_stress_convergence_Pa=r*sc[0],qualification_stress_endpoint_Pa=q*sc[0],reference_void_convergence=r,qualification_void_endpoint=q,reference_to_qualification_margin=q/r,case_count=10,policy_sha256=sha(P/'policy.json'),contract_sha256=sha(P/'CONTRACT.md'),scope='one inherited host material example and named supplied-state paths; no universal parameter/domain claim')
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
