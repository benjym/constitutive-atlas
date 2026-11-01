"""Retained v3 failure + prospective midpoint algebra; no material advance."""
from pathlib import Path
from decimal import Decimal as D,localcontext
from fractions import Fraction
import json,math,hashlib,sys
R=Path(__file__).resolve().parents[5];sys.path.insert(0,str(R))
from atlas.model import load,interpret,defaults
B=Path(__file__).resolve().parent.parent;V=B.parent/'midpoint-control-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((B/'native-domain-results.json').read_text());assert not report['passed'] and len(report['checks'])==94 and sum(not c['passed'] for c in report['checks'])==2
row=report['requests'][360];rawpath=R/row['raw_path'];assert sha(rawpath)==row['raw_sha256'];raw=json.loads(rawpath.read_text());diag=raw['diagnostics'];fs=diag['increment_fractions'];assert not raw['ok'] and raw['state']==[60000]*3+[0]*3+[6,0]
assert diag['substeps']==len(fs)==170958 and diag['reserved_path_trials']==512901
assert diag['substeps']<200000 and diag['reserved_path_trials']<3*200000
assert min(fs)==2**-21
fraction=sum(map(Fraction,fs));pressure=60000.;L=.004107031422195062
for f in fs:
 pressure-=1600*101325*(pressure/101325)**.86*L*f
 assert pressure>0
nextsteps=[]
for depth in [19,20,21]:
 h=L*2**(-depth);full=pressure-1600*101325*(pressure/101325)**.86*h;half=pressure-1600*101325*(pressure/101325)**.86*h/2;two=half-1600*101325*(half/101325)**.86*h/2
 err=math.sqrt(3)*abs(full-two)/min(pressure,full,half,two)
 nextsteps.append(dict(depth=depth,relative_defect=err,passes_1e_7=err<1e-7))
assert not nextsteps[1]['passes_1e_7'] and nextsteps[2]['passes_1e_7']
proof=[]
with localcontext() as ctx:
 ctx.prec=80
 for n in [D('.8'),D('.86')]:
  for v in [D('.999'),D('.9'),D('.5'),D('.01'),D('1e-6')]:
   midpoint_length=(1-v)/(((1+v)/2)**n)
   exact_length=(1-v**(1-n))/(1-n)
   assert 0<midpoint_length<exact_length
   proof.append(dict(n=str(n),endpoint_ratio=str(v),midpoint_length_over_exact=str(midpoint_length/exact_length)))
model=load(V/'model.json');rotation=json.loads(Path(__file__).with_name('left-reference-results.json').read_text())['rotation_Q'];Q=[[Fraction(v) for v in row] for row in rotation];ev=[Fraction(11,10),Fraction(1),Fraction(9,10)]
A=[[sum(Q[i][k]*ev[k]*Q[j][k] for k in range(3)) for j in range(3)] for i in range(3)];direction=[float(A[i][i]) for i in range(3)]+[math.sqrt(2)*float(A[i][j]) for i,j in [(0,1),(1,2),(0,2)]];f=300/11;endpoints=[]
for label,over in [('dense',{}),('loose',dict(k1=58,ft=33,A=.39,rf=.97,M=.00068,l=1.17,Kur=1600,n=.86))]:
 p={**defaults(model),**over}
 for p0 in [60000.,1e-6,1e-12,1e-24]:
  p1=.8*p0;E=p['Kur']*p['pa']*(.9*(p0+p1)/(2*p['pa']))**p['n'];old={'sigma':[p0*x for x in direction],'q':p['ft']-f,'wp':0.};new={'sigma':[p1*x for x in direction],'q':p['ft']-f,'wp':0.};de=[(p1-p0)/E*x for x in direction];res=interpret(model,new,old,de,p);err=max(abs(x)/p['pa'] for x in res['sigma'].v);assert err<2e-12 and abs(res['q'])<2e-12 and res['wp']==0
  endpoints.append(dict(set=label,p0=p0,relative_residual=err))
out={'id':'REVIEW-lade-v3-depth-failure-and-prospective-midpoint-v1','retained_v3':{'report_sha256':sha(B/'native-domain-results.json'),'raw_sha256':sha(rawpath),'checks':94,'failures':2,'exact_rollback':True,'accepted_halves':len(fs),'reserved_trials':diag['reserved_path_trials'],'accepted_fraction_sum':str(fraction),'accepted_fraction':float(fraction),'smallest_half_fraction':min(fs),'hardstop':'Depth cap is remaining recursive termination condition after excluding accepted-half/trial budgets in frozen code.','exact_scalar_FE_prefix_pressure_Pa':pressure,'next_exact_scalar_macrosteps':nextsteps,'limit':'Scalar replay supports estimator-driven depth exhaustion; native raw does not log last per-attempt rejection reason or committed internal states, so exclusive nonlinear root-cause assertion is not made.'},'prospective_v4_model_sha256':sha(V/'model.json'),'midpoint_source_quadrature_checks':proof,'rotated_midpoint_known_endpoint_checks':endpoints,'conclusion':'Convex inverse-rate midpoint quadrature preserves hydro/proportional arbitrary-positive-substep one-sided lifetime; elastic second order only, active endpoint plasticity remains first order.','limits':['No compiled or material advance','No v3 gate changed','No v4 numerical qualification or E5 approval']}
Path(__file__).with_name('v3-failure-midpoint-results.json').write_text(json.dumps(out,indent=2)+'\n');print('v3failure/raw verified;10midpoint quadrature inequalities and8rotated endpoint checks pass')
