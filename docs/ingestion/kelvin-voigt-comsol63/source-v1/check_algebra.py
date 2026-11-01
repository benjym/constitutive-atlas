"""Source-derived independent analytical checks: no Atlas imports/builds."""
import json,math,random
from pathlib import Path
from reference import cart,mandel,source_stress,constant_rate,deviatoric_stress_ramp
D=Path(__file__).resolve().parent
checks=[]
def record(name,n=1):checks.append({'name':name,'cases':n,'passed':True})
def close(a,b,atol=1e-7,rtol=1e-12):
    for x,y in zip(a,b):assert math.isclose(x,y,rel_tol=rtol,abs_tol=atol),(x,y)
def dev6(v):
    t=sum(v[:3])/3
    return [x-t if i<3 else x for i,x in enumerate(v)]
def contraction(a,b):return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
K,G,tau=2e7,1.2e7,2.
rng=random.Random(63036)
for _ in range(100):
    e=[rng.uniform(-.01,.01) for _ in range(6)]
    v=[rng.uniform(-.003,.003) for _ in range(6)]
    close(mandel(cart(e)),e,atol=1e-15)
    # Source stress/strain are tension-positive; Atlas reverses both, preserving law/work.
    close(source_stress([-x for x in e],[-x for x in v],K,G,tau),[-x for x in source_stress(e,v,K,G,tau)])
    E,V=cart(e),cart(v);trE=sum(E[i][i] for i in range(3));trV=sum(V[i][i] for i in range(3))
    Ed=[[E[i][j]-trE/3*(i==j) for j in range(3)] for i in range(3)]
    Vd=[[V[i][j]-trV/3*(i==j) for j in range(3)] for i in range(3)]
    stress=cart(source_stress(e,v,K,G,tau))
    psi_rate=K*trE*trV+2*G*contraction(Ed,Vd)
    dissip=2*G*tau*contraction(Vd,Vd)
    assert dissip>=0
    assert math.isclose(contraction(stress,V)-psi_rate,dissip,rel_tol=1e-11,abs_tol=1e-8)
    assert math.isclose(sum(x*y for x,y in zip(e,v)),contraction(E,V),abs_tol=1e-15)
record('Mandel transport and Cartesian work conjugacy',100)
record('joint sign reversal preserves source law and energy',100)
record('free-energy rate plus nonnegative source dashpot dissipation',100)
for t in [0.,1e-9,.1,2.,20.]:
    e0=[.001,-.0005,-.0005,.0002,.0001,-.0003];v=[.002,-.001,-.001,.0003,-.0002,.0001]
    e=constant_rate(e0,v,t)
    close(source_stress(e,v,K,G,tau),[a+t*b for a,b in zip(source_stress(e0,v,K,G,tau),source_stress(v,[0.]*6,K,G,tau))])
record('all-six constant-rate stress is affine in physical time',5)
# Hydrostatic loading has no viscosity; all pressure is purely elastic.
close(source_stress([.001]*3+[0]*3,[.1]*3+[0]*3,K,G,tau),[60000.]*3+[0.]*3)
record('pure volumetric rate has zero viscous stress')
# Engineering shear gamma = sqrt(2)*eps_M; tau_xy=G*gamma+eta*gammadot.
gamma,gammadot=.004,.003
e=[0.,0.,0.,gamma/math.sqrt(2),0.,0.];v=[0.,0.,0.,gammadot/math.sqrt(2),0.,0.]
assert math.isclose(source_stress(e,v,K,G,tau)[3]/math.sqrt(2),G*gamma+G*tau*gammadot,rel_tol=1e-15)
record('engineering shear factor and tensor shear factor agree')
for t in [0.,1e-9,.1,2.,20.]:
    s=[12000.,-6000.,-6000.,3000.,-5000.,1000.]
    A=[0.]*6;e0=[0.]*6
    e,v=deviatoric_stress_ramp(e0,s,A,t,G,tau)
    close(source_stress(e,v,K,G,tau),s)
    expected=[x/(2*G)*(-math.expm1(-t/tau)) for x in s]
    close(e,expected,atol=1e-15)
record('six-component constant-stress creep exact exponential tau=eta/G',5)
for t in [0.,.001,1.,10.]:
    e0=[.0001,-.00005,-.00005,.0003,-.0002,.0001]
    s0=[15000.,-7500.,-7500.,2000.,-5000.,3000.]
    A=[1200.,-600.,-600.,800.,-700.,500.]
    e,v=deviatoric_stress_ramp(e0,s0,A,t,G,tau)
    close(source_stress(e,v,K,G,tau),[s+t*a for s,a in zip(s0,A)])
record('all-six nonzero-initial-strain stress ramp exact integrating-factor solution',4)
e=[.002,-.001,-.001,0,0,0];v=[.001,-.0005,-.0005,0,0,0]
close(source_stress(e,v,K,G,tau),[96000.,-48000.,-48000.,0,0,0])
close(source_stress(e,[0.]*6,K,G,tau),[48000.,-24000.,-24000.,0,0,0])
close(source_stress(e,[-x for x in v],K,G,tau),[0.]*6)
record('finite rate jump changes stress at fixed continuous strain; hold does not relax')
result={'identity':'kelvin-voigt-comsol63-independent-algebra-v1','independence':'standard library Cartesian Lame spring/dashpot and integrating-factor solutions; no Atlas/parser/generated expression imports','all_passed':True,'groups':len(checks),'checks':checks,'limitations':['No native/Wasm/vendor execution','No experimental data or calibration','No finite-strain or spin qualification']}
out=json.dumps(result,indent=2)+'\n';dest=D/'check-results.json'
if dest.exists():assert dest.read_text()==out,'retained results differ'
else:dest.write_text(out)
print(out,end='')
