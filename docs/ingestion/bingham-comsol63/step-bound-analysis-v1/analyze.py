"""Source-only arithmetic; no constitutive backend, no compiled-output fitting."""
import hashlib,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
G=10e6;Y=100e3;eta=20e6;T=2.;a=3*G/eta;tau=1/a
zs=[0,99900,100000,100100,200000,-200000];ds=[0,.003,-.012]
F=max(abs(2*G*d-a*math.copysign(max(abs(z)-Y,0),z)) for z in zs for d in ds)
v=2*G*max(map(abs,ds)); M=min(tau/1024,Y/(v*1024));H=M/2
I=v*H*H/(2*eta)
# Conservative eventual impact of one missed exit, using contraction and Lipschitz alpha.
r={'identity':'bingham-source-only-step-bound-analysis-v1','parameters':{'G_Pa':G,'Y_Pa':Y,'eta_Pa_s':eta,'duration_s':T},'tau_s':tau,'max_initial_abs_scalar_stress_rate_Pa_per_s':F,'max_abs_elastic_scalar_loading_rate_Pa_per_s':v,'exact_BE_global':{'H_from_alpha_floor_s':3e-7*eta/(2*T*F),'host_M_from_alpha_floor_s':3e-7*eta/(T*F),'note':'exact solves only, no roundoff or nonlinear residual allocation'},'event_local_proposed_formula':{'M_s':M,'H_s':H,'H_over_tau':H/tau,'missed_exit_alpha_upper':I,'immediate_scalar_stress_error_upper_Pa':3*G*I,'immediate_vp_component_upper':1.5*math.sqrt(2/3)*I,'later_alpha_error_upper_over_T':I*(1+a*T),'conservative_using_entire_M_as_step_alpha_upper':v*M*M/(2*eta),'dyadic_halfsteps_for_two_seconds_from_cap_alone':2**(math.ceil(math.log2(T/M))+1),'note':'one active-exit omission only; not total integration error'},'source_hashes':{}}
for rel in ['docs/ingestion/bingham-comsol63/source-v1/candidate.json','docs/ingestion/bingham-comsol63/source-v1/analytical-references.json','docs/ingestion/bingham-comsol63/execution-v2/cases.json','docs/ingestion/bingham-comsol63/execution-v2/freeze-v1.json','cpp/include/atlas/schedule.hpp']:
 r['source_hashes'][rel]=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
# Check analytic logarithmic bound on an a-priori dimensionless grid; not compiled results.
checks=[]
for x in [1e-6,1e-4,.001,.01,.1,1,10]:
 exact=x-math.log1p(x)
 checks.append({'aH':x,'exit_integral_dimensionless':exact,'quadratic_upper':x*x/2,'pass':0<=exact<=x*x/2})
r['pure_algebra_checks']=checks
assert all(c['pass'] for c in checks)
(HERE/'results.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['tau_s','max_initial_abs_scalar_stress_rate_Pa_per_s','exact_BE_global','event_local_proposed_formula']},indent=2))
