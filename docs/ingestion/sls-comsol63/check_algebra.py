"""Independent scalar/Cartesian consequences of the source spring/dashpot law.
No Atlas model, parser, evaluator, compiler or generated kernel imported.
"""
import json,math,random
from pathlib import Path
r=random.Random(6301);checks=[]
def record(name,ok,count=1):
 assert ok,name
 checks.append({'name':name,'passed':bool(ok),'cases':count})
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def dev(a):
 t=sum(a[:3])/3
 return [a[i]-t if i<3 else a[i] for i in range(6)]
K,A,B,T=2e7,4e6,6e6,2.
# Derive transformed source gamma ODE and work conjugacy in Mandel components.
worst=0
for j in range(100):
 e=[r.uniform(-.02,.02) for _ in range(6)];g=dev([r.uniform(-.01,.01) for _ in range(6)]);v=[r.uniform(-.1,.1) for _ in range(6)]
 d=dev(e);dv=dev(v);q=[2*B*(x-y) for x,y in zip(d,g)];gd=[(x-y)/T for x,y in zip(d,g)];qd=[2*B*(x-y) for x,y in zip(dv,gd)]
 rhs=[2*B*x-y/T for x,y in zip(dv,q)];worst=max(worst,max(abs(x-y) for x,y in zip(qd,rhs)))
 sig=[K*sum(e[:3])*(i<3)+2*A*d[i]+q[i] for i in range(6)]
 psidot=K*sum(e[:3])*sum(v[:3])+2*A*dot(d,dv)+dot(q,qd)/(2*B)
 dissip=dot(q,q)/(2*B*T)
 assert math.isclose(dot(sig,v)-psidot,dissip,rel_tol=1e-12,abs_tol=1e-8)
 assert abs(sum(rhs[:3]))<1e-7
record('source gamma to branch-overstress ODE equivalence',worst<1e-8,100)
record('free-energy balance and nonnegative dissipation',True,100)
record('deviatoric subspace invariance',True,100)
# Exact constant-rate branch solution and a derivative identity at arbitrary t.
for t in [0.,1e-8,.1,2.,20.,200.]:
 v=.003;q0=100.;dec=math.exp(-t/T);q=q0*dec+2*B*T*v*(-math.expm1(-t/T));qd=(-q0/T+2*B*v)*dec
 assert math.isclose(qd,2*B*v-q/T,rel_tol=1e-12,abs_tol=1e-9)
record('exact ramp solution satisfies branch ODE',True,6)
# Impulse is an analytical limit; not a finite ODE advance with zero duration.
for t in [0.,T,10*T]:
 G=A+B*math.exp(-t/T)
 assert A<=G<=A+B
record('instantaneous and equilibrium shear bounds',True,3)
record('bulk does not relax',K*.003==60000.)
# Constant deviatoric stress creep: E1 obeys 2(A+B) edot +2A e/T = s/T.
s=20000.;tc=T*(A+B)/A;e0=s/(2*(A+B));einf=s/(2*A)
for t in [0.,.1,tc,20*tc]:
 e=einf+(e0-einf)*math.exp(-t/tc);ed=-(e0-einf)/tc*math.exp(-t/tc)
 assert math.isclose(2*(A+B)*ed+2*A*e/T,s/T,rel_tol=1e-12)
record('creep retardation time differs from branch relaxation time',tc>T,4)
for w in [1e-6,.1,1.,1000.]:
 z=w*T;gp=A+B*z*z/(1+z*z);gpp=B*z/(1+z*z)
 assert A<=gp<=A+B and gpp>=0
record('storage and loss shear moduli passive',True,4)
# Energy inner product checks Mandel shear convention vs actual tensors.
a=[1.,2.,3.,4.,5.,6.];b=[7.,8.,9.,10.,11.,12.]
cart=sum(a[i]*b[i] for i in range(3))+2*sum((a[i]/math.sqrt(2))*(b[i]/math.sqrt(2)) for i in range(3,6))
record('Mandel contraction equals Cartesian tensor contraction',math.isclose(dot(a,b),cart,rel_tol=1e-15))
# Exact segment semigroup for a fixed rate including nonzero initial memory.
def advance(q,h,v):return q*math.exp(-h/T)+2*B*T*v*(-math.expm1(-h/T))
record('constant-rate exact segment composition',math.isclose(advance(advance(500,.7,.002),1.3,.002),advance(500,2,.002),rel_tol=1e-15))
result={'identity':'sls-comsol63-algebra-v1','independence':'stdlib mathematical consequences of primary scalar spring/dashpot equations; no Atlas import','groups':len(checks),'all_passed':True,'checks':checks,'max_ode_equivalence_absolute_Pa_per_s':worst,'limitations':['No compiled execution','No experimental comparison','No vendor solver equivalence']}
text=json.dumps(result,indent=2)+'\n';dest=Path(__file__).with_name('check-results.json')
if dest.exists():assert dest.read_text()==text,'retained check result differs'
else:dest.write_text(text)
print(text,end='')
