"""Manufacture exact source certificates, then serialize actual binary64 inputs. No Atlas imports."""
from pathlib import Path
from fractions import Fraction as F
import json,math,random,hashlib,datetime,sys
R=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent/'frozen';P=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else Path(__file__).resolve().parent;P.mkdir(exist_ok=True);C=Path(sys.argv[3]).resolve() if len(sys.argv)>3 else Path(__file__).resolve().parent/'retained-v1-holds.json'
source=R/'docs/ingestion/mohr-coulomb/results.json';cert=json.loads(source.read_text());zero=[0.]*6
q=[[F(-2,3),F(2,15),F(11,15)],[F(2,3),F(-1,3),F(2,3)],[F(1,3),F(14,15),F(2,15)]]
assert all(sum(q[i][k]*q[j][k]for k in range(3))==int(i==j)for i in range(3)for j in range(3))
def diagonal(v):return [[v[i]if i==j else F(0)for j in range(3)]for i in range(3)]
def matrix(v):return [[sum(q[i][k]*v[k]*q[j][k]for k in range(3))for j in range(3)]for i in range(3)]
def mandel(a):return [float(a[0][0]),float(a[1][1]),float(a[2][2]),math.sqrt(2)*float(a[0][1]),math.sqrt(2)*float(a[1][2]),math.sqrt(2)*float(a[0][2])]
def moduli(p):return p['E']/(3*(1-2*p['nu'])),p['E']/(2*(1+p['nu']))
def elastic(v,K,G):return [2*G*x+(K-F(2,3)*G)*sum(v)for x in v]
def compliance(v,K,G):return [(x-sum(v)/3)/(2*G)+sum(v)/(9*K)for x in v]
def params(E=2.25,nu=.125,c=5.,phi=math.asin(.6),psi=math.asin(1/3)):
 return {'E':float(E),'nu':float(nu),'c':float(c),'phi':float(phi),'psi':float(psi),'p_ref':1.}
base=params();cases=[]
def add(name,parent,loading,parameters,tags,metadata=None):
 assert all(math.isfinite(x)for x in parent+loading)
 K,G=moduli(parameters);co={'K':K,'G':G,'sf':math.sin(parameters['phi']),'sd':math.sin(parameters['psi']),'cf':math.cos(parameters['phi'])}
 cases.append({'id':name,'current':[float(x).hex()for x in parent],'parent':[float(x).hex()for x in parent],'loading':[float(x).hex()for x in loading],'parameters':{k:v.hex()for k,v in parameters.items()},'resolved_coefficients':{k:float(v).hex()for k,v in co.items()},'tags':tags,'construction':metadata or {}})
for row in cert['certificates']:
 name=row['case'];t=list(map(F,row.get('source_tension_principal_trial',row.get('trial'))));ret=list(map(F,row.get('source_tension_return',row.get('return'))));de=[-x for x in compliance(t,F(1),F(1))]
 add('certificate/'+name+'/diagonal',zero,mandel(diagonal(de)),base,['original-certificate',row['branch'],'diagonal'],{'exact_source_certificate':name})
 add('hold/'+name+'/diagonal',mandel(diagonal([-x for x in ret])),zero,base,['zero-increment-hold','original-certificate',row['branch'],'diagonal'])
 if 'compression_cartesian_increment'in row:
  fraction=lambda m:[[F(x)for x in r]for r in m]
  add('certificate/'+name+'/planar',zero,mandel(fraction(row['compression_cartesian_increment'])),base,['original-certificate',row['branch'],'planar-rotation'])
  add('hold/'+name+'/planar',mandel(fraction(row['compression_cartesian_return'])),zero,base,['zero-increment-hold','original-certificate',row['branch'],'planar-rotation'])
 # A fully dense rational rotation is rounded once to the actual stored Mandel input.
 add('certificate/'+name+'/dense',zero,mandel(matrix(de)),base,['original-certificate',row['branch'],'dense-rotation'])
 if 'boundary'in name:
  for power in (16,36,48):
   for sign in (-1,1):
    pert=t.copy();pert[0]+=F(sign,2**power)
    loading=mandel(matrix([-x for x in compliance(pert,F(1),F(1))]))
    add(f'neighbor/{name}/{power}/{sign}',zero,loading,base,['one-sided-neighbor','dense-rotation','target-'+row['branch']],{'nominal_boundary':name,'trial_t1_perturbation':str(F(sign,2**power))})
# Source-scaled cases preserve dimensionless loading while changing all stress units.
for name in ['elastic_compression','face','left_repeated_trial','right_repeated_trial','apex_interior','hydrostatic_apex']:
 row=next(r for r in cert['certificates']if r['case']==name);t=list(map(F,row.get('source_tension_principal_trial',row.get('trial'))));loading=mandel(matrix([-x for x in compliance(t,F(1),F(1))]))
 for power in (-300,-100,100,300):
  factor=math.ldexp(1.,power);p=params(E=2.25*factor,c=5.*factor)
  add(f'scale/{name}/{power}',zero,loading,p,['power-of-two-stress-scale',row['branch'],'dense-rotation'],{'stress_scale':factor.hex()})
# KKT constructions for negative Lame modulus and dilation greater than friction.
for label,nu,d in [('negative-lame',F(-3,5),F(1,3)),('high-poisson',F(49,100),F(1,3)),('dilation-above-friction',F(1,8),F(4,5))]:
 E=F(9,4);K=E/(3*(1-2*nu));G=E/(2*(1+nu));s=F(3,5);h=F(8);ap=h/(2*s);p=params(E=float(E),nu=float(nu),psi=math.asin(float(d)))
 for branch in ['face','left','right','apex']:
  ret={'face':[F(5),F(2),F(0)],'left':[F(5),F(5),F(0)],'right':[F(5),F(0),F(0)],'apex':[ap]*3}[branch]
  flow={'face':[1+d,F(0),-1+d],'left':[(1+d)/2,(1+d)/2,-1+d],'right':[1+d,(-1+d)/2,(-1+d)/2],'apex':[2*d/3]*3}[branch]
  t=[r+F(1,4)*cv for r,cv in zip(ret,elastic(flow,K,G))]
  add('parameter/'+label+'/'+branch,zero,mandel(matrix([-x for x in compliance(t,K,G)])),p,['parameter-regime',label,branch,'dense-rotation'])
# Coincident face-to-apex transition, all four source thresholds coincide.
d=F(1,3);s=F(3,5);ap=F(20,3);flow=[1+d,F(0),-1+d];t=[ap+F(1,4)*v for v in elastic(flow,F(1),F(1))]
for power,sign in [(0,0),(20,-1),(20,1),(44,-1),(44,1)]:
 pert=t.copy();pert[0]+=F(sign,2**power)
 add(f'coincident/{power}/{sign}',zero,mandel(matrix([-x for x in compliance(pert,F(1),F(1))])),base,['coincident-face-apex','dense-rotation'],{'trial_t1_perturbation':str(F(sign,2**power))})
# Literal capture of the four previously observed v1 failures, separate provenance.
capture=json.loads(C.read_text())
for row in capture['cases']:
 p={k:float.fromhex(v)for k,v in row['parameters'].items()}
 add('retained-v1-hold/'+row['id'],[float.fromhex(v)for v in row['parent']],zero,p,['retained-negative-regression','zero-increment-hold','rounded-apex-parent'],{'capture_sha256':hashlib.sha256(C.read_bytes()).hexdigest(),'original_failure':row['failure']})
for i,loading in enumerate([[0.]*6,[.001]*3+[0.]*3,[-.001]*3+[0.]*3,[.01,-.005,-.005,.003,-.002,.001]]):
 add('default-parameters/'+str(i),zero,loading,params(E=30000000.,nu=.25,c=10000.,phi=0.5235987755982988,psi=0.17453292519943295),['default-parameter-interface'])
# Mixed-scale smooth faces retain a meaningful middle value under exact stored loading.
for label,mag,middle in [('large',1e100,1.),('extreme',1e300,1.),('tiny',1e-100,1e-300)]:
 p=params(E=2.,nu=0.,c=.625*mag)
 add('mixed-scale-middle/'+label,zero,[-mag/2,-middle/2,mag/2,0.,0.,0.],p,['mixed-scale','diagonal','face','preserved-middle'],{'source_trial_extreme':mag.hex(),'source_middle':middle.hex(),'reason':'K=2/3,G=1,Lame=0; middle maps directly without trace-minus-extrema cancellation'})
# Eighteen coordinate bases plus twenty mixed incoming columns.
seeds=[]
for group in ('current','parent','loading'):
 for k in range(6):
  seed={g:[0.]*6 for g in ('current','parent','loading')};seed[group][k]=1.;seeds.append(seed)
rng=random.Random(917731)
for j in range(20):
 seeds.append({g:[math.ldexp(float(rng.randint(-16,16)),-3)for k in range(6)]for g in ('current','parent','loading')})
seeds=[{g:[x.hex()for x in v]for g,v in seed.items()}for seed in seeds]
assert len(seeds)==38 and len({x['id']for x in cases})==len(cases)
inputs={'identity':'mc-stored-input-v1','columns':38,'seeds':seeds,'cases':cases,'coefficient_interfaces':{'canonical':'Exact stored E,nu,c,phi,psi with highprecision mathematical trig/moduli','resolved_coefficients':'Independent Python standard-math binary64 coefficients supplied for rounding diagnostics only; not a replacement canonical reference'},'source_certificate_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'compiled_observations':0,'candidate_interpreter_capture_calls':capture['candidate_interpreter_capture_calls'],'capture_sha256':hashlib.sha256(C.read_bytes()).hexdigest()}
(P/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
print(json.dumps({'cases':len(cases),'columns':38,'candidate_interpreter_capture_calls':capture['candidate_interpreter_capture_calls'],'capture_sha256':hashlib.sha256(C.read_bytes()).hexdigest()}))
