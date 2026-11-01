"""Independent analytic contract witnesses, not a material update or E5 approval."""
import json
import math
from pathlib import Path

M, lam, kap, pref, Gamma = 1.2, .2, .04, 1000., 2.5
p0, pc = 50000., 100000.
wk = Gamma + (lam-kap)*(1-math.log(pc/pref))
v0 = wk-kap*math.log(p0/pref)

# Two entire continuous interior stress paths share the same initial state,
# volumetric strain history, zero distortion, and fixed packing. Source 6.3/6.7
# and p98 constrain no interior q rate. Pressure is increasing, not a hold.
rows = []
for i in range(101):
    t = i/100
    p = p0*math.exp(math.log(1.1)*t)
    v = v0-kap*math.log(p/p0)
    Ev = math.log(v0/v)
    qA, qB = 0., 10000.*t
    fA = abs(qA)+M*p*math.log(p/pc)
    fB = abs(qB)+M*p*math.log(p/pc)
    assert fA < 0 and fB < 0 and v > 1
    assert abs(v+kap*math.log(p/pref)-wk) < 1e-14
    rows.append(dict(t=t,p=p,v=v,Ev=Ev,eps_s=0.,qA=qA,qB=qB,fA=fA,fB=fB))

# The proof is continuous: p<=55000, qB<=10000 and
# Mp ln(pc/p)>=M*50000*ln(100000/55000)>10000 on [0,1].
lower_radius_bound = M*p0*math.log(pc/(1.1*p0))
assert lower_radius_bound > 10000.

# At the virgin vertex p=pc, take dp/ds=1000 Pa. Total compressive
# volume rate=lambda*dp/(v*p); recoverable part=kappa*dp/(v*p).
# Source p101 permits all plastic directions between (M,+1),(M,-1).
p = pc
v = Gamma+lam-kap-lam*math.log(p/pref)
pdot = 1000.
Ev = lam*pdot/(v*p)
Evr = kap*pdot/(v*p)
Evp = Ev-Evr
vertex = []
for a in (-1.,-.5,0.,.5,1.):
    ds = a*Evp/M
    ea, er = Ev/3+ds, Ev/3-ds/2
    assert abs(ds) <= Evp/M+1e-16
    assert abs(ea+2*er-Ev) < 1e-16
    vertex.append(dict(subgradient=a,plastic_Ev=Evp,eps_s=ds,
                       axial=ea,radial=er,
                       plastic_work=p*Evp,
                       smooth_branch_friction_expression=M*p*abs(ds)))

report = dict(id='REVIEW-occ-full-contract-v1',compiled_calls=0,
    independent_scope='Analytic consequences of source constraints; no production evaluator.',
    parameters=dict(M=M,lambda_=lam,kappa=kap,p_ref=pref,Gamma=Gamma),
    interior=dict(p_c=pc,w_kappa=wk,continuous_radius_lower_bound=lower_radius_bound,
                  initial=rows[0],final=rows[-1],sampled_path=rows,
                  conclusion='Same complete incoming state and strain history, distinct admissible q histories.'),
    vertex=dict(p=p,v=v,p_rate=pdot,total_Ev=Ev,recoverable_Ev=Evr,
                plastic_Ev=Evp,normal_cone_directions=vertex,
                conclusion='p101 cone includes zero shear; smooth equality alone selects only endpoints.'))
Path(__file__).with_name('contract-review-witness.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: continuous interior nonuniqueness and five source-p101 cone directions')
