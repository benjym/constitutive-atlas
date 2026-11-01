"""Independent Cartesian/analytical checks; no compiled or vendor calls.
Run from repository root: python3 docs/ingestion/maxwell-itasca900/check_packet.py
"""
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from atlas.model import load, interpret
from atlas.initialization import initialize_state
from atlas.dsl import ValidationError

BASE = Path(__file__).resolve().parent
m = load(BASE / 'candidate-v03.json')
checks = []
def record(name): checks.append(name)
def close(a, b):
    assert len(a) == len(b)
    assert all(abs(x-y) <= 1e-9 + 2e-14*max(abs(x),abs(y)) for x,y in zip(a,b)), (a,b)

record('v0.3 semantic/dimensional validation')
try:
    import jsonschema
    jsonschema.Draft202012Validator(json.loads((ROOT/'schemas/model-v0.3.schema.json').read_text())).validate(m)
except ImportError:
    raise RuntimeError('jsonschema required for structural validation')
record('v0.3 JSON schema validation')
params={'Kmod':20e6,'Gmod':12e6,'eta':24e6}
z=[140000,80000,80000,3000,-2000,1000]
assert initialize_state(m,{'sigma':z},params,time=0,loading=[0]*6)['initial']==z
for missing in ({},):
    try:initialize_state(m,missing,params,time=0,loading=[0]*6)
    except ValidationError:pass
    else:raise AssertionError('missing stress accepted')
record('explicit complete initial stress required and preserved')
# Cartesian oracle uses raw off-diagonal entries, not DSL trace/dev primitives.
sqrt2=math.sqrt(2)
def pack(a):return [a[0][0],a[1][1],a[2][2],sqrt2*a[0][1],sqrt2*a[1][2],sqrt2*a[0][2]]
def cart_rate(s,d,K,G,eta):
    trd=sum(d[i][i] for i in range(3));trs=sum(s[i][i] for i in range(3))
    return [[(K*trd if i==j else 0)+2*G*(d[i][j]-(trd/3 if i==j else 0))-G/eta*(s[i][j]-(trs/3 if i==j else 0)) for j in range(3)] for i in range(3)]
for n in range(1,41):
    s=[[10000*(n+1),250*n,-170*n],[250*n,20000-n*100,80*n],[-170*n,80*n,30000+n*700]]
    d=[[n*1e-5,-n*1e-6,2e-5],[-n*1e-6,-n*3e-6,1e-5],[2e-5,1e-5,4e-6]]
    expected=pack(cart_rate(s,d,**{'K':params['Kmod'],'G':params['Gmod'],'eta':params['eta']}))
    close(interpret(m,{'sigma':pack(s)},None,pack(d),params,time=n)['sigma'].v,expected)
record('40 full-tensor Cartesian rates including all shear components')
# Exact rational recovery of the source timestep equation from trapezoidal ODE.
K,G,eta=F(20),F(12),F(24)
for h in (F(1,100),F(1,2),F(4),F(8)):
    x=G*h/(2*eta);sn=F(7);de=F(3,100)
    snew=((1-x)*sn+2*G*de)/(1+x)
    assert snew-sn-2*G*de+h*G*(snew+sn)/(2*eta)==0
record('four exact central-difference/trapezoidal residual identities')
x=F(2);R=(1-x)/(1+x)
assert R==F(-1,3) and math.exp(-float(2*x))>0
record('retained coarse-hold stress sign reversal witness h=4 tau')
# Actual second-order refinement of CN relaxation, not a backend agreement check.
errors=[]
for N in (10,20,40,80):
    h=1/N;R=(1-h/2)/(1+h/2);errors.append(abs(R**N-math.exp(-1)))
assert all(3.9 < a/b < 4.1 for a,b in zip(errors,errors[1:]))
record('central-difference hold second-order refinement at four partitions')
# Tensor energy balance: stored elastic energy derivative and viscous dissipation.
s=[[F(12),F(2),F(-1)],[F(2),F(4),F(3)],[F(-1),F(3),F(8)]]
d=[[F(1,10),F(1,20),F(0)],[F(1,20),F(-1,30),F(1,40)],[F(0),F(1,40),F(1,50)]]
sdot=cart_rate(s,d,K,G,eta);p=sum(s[i][i] for i in range(3))/3;pdot=sum(sdot[i][i] for i in range(3))/3
power=sum(s[i][j]*d[i][j] for i in range(3) for j in range(3));ss=sum((s[i][j]-(p if i==j else 0))**2 for i in range(3) for j in range(3))
psidot=p*pdot/K+sum((s[i][j]-(p if i==j else 0))*(sdot[i][j]-(pdot if i==j else 0)) for i in range(3) for j in range(3))/(2*G)
assert power-psidot==ss/(2*eta)>0
record('exact work/elastic-energy/positive dissipation identity')
# Oedometer source closed form: independent substitution of analytic derivatives.
# Compression-positive ezz, szz=P; only zz strain varies; r=exp(-bt).
P=F(3);A=K+4*G/3;a=2*G/A;b=K*G/(eta*A);c=4*G/(3*A)
for r in (F(1),F(1,2),F(0)):
    stress=[[P*(1-a*r),0,0],[0,P*(1-a*r),0],[0,0,P]]
    rate=[[0,0,0],[0,0,0],[0,0,P/K*c*b*r]]
    got=cart_rate(stress,rate,K,G,eta)
    expected=[[P*a*b*r,0,0],[0,P*a*b*r,0],[0,0,0]]
    assert got==expected
assert P/K*(1-c)==P/A
record('three exact oedometer analytic-derivative substitutions and elastic initial strain')
# Constitutive shear creep, volumetric elasticity, hold behavior and sign conversion.
assert cart_rate([[2,0,0],[0,2,0],[0,0,2]],[[0]*3 for _ in range(3)],K,G,eta)==[[0]*3 for _ in range(3)]
assert F(9)/(2*eta)==F(3,16)  # epsilon_xy_dot for constant shear stress 9
s0=[[F(0),F(9),0],[F(9),0,0],[0,0,0]];dc=[[0,F(9)/(2*eta),0],[F(9)/(2*eta),0,0],[0,0,0]]
assert cart_rate(s0,dc,K,G,eta)==[[0]*3 for _ in range(3)]
record('hydrostatic hold invariant and constant-shear creep balance')
neg=lambda t:[[-v for v in row] for row in t]
assert cart_rate(neg(s),neg(d),K,G,eta)==neg(cart_rate(s,d,K,G,eta))
record('complete stress and strain sign reversal preserves law')
# Printed ij instead of kk is not a trace-free projector, even on isotropic input.
literal=[F(3)-F(3)/3]*3
assert sum(literal)==6
record('printed malformed deviator index witness retained; trace interpretation required')
receipts=json.loads((BASE/'source-receipts.json').read_text())
for receipt in receipts['sources']:
    assert hashlib.sha256(Path(receipt['private_path']).read_bytes()).hexdigest()==receipt['sha256']
record('four exact private source hashes verified')
result={'passed':True,'checks':checks,'check_groups':len(checks),'cn_relaxation_errors':errors,'coarse_hold_witness':{'h_over_tau':4,'CN_ratio':'-1/3','exact_ratio':math.exp(-4)},'compiled_calls':0,'vendor_calls':0,'scientific_admission':False}
(BASE/'check-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
