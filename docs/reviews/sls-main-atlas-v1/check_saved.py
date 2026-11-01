"""Independent Decimal source-gamma references for saved main-atlas exported runs; no engine execution."""
import sys,json,math,hashlib
from pathlib import Path
from decimal import Decimal as D,localcontext
B=Path(__file__).resolve().parent
MODEL='sls-comsol63-deviatoric-zero-spin-ode'
MODEL_SHA='eccfeb372810afd81a5e9cddf5d8ac33e2cb5df6921fc88e14e9175c73e50906'
def dec(v):return [D(str(x)) for x in v]
def dev(v):
 m=sum(v[:3])/3
 return [x-(m if i<3 else 0) for i,x in enumerate(v)]
def stress(z,p):
 k,g,h,tau=p;v=dev(z[:6]);tr=sum(z[:3])
 return [(k*tr if i<3 else 0)+2*g*v[i]+z[6+i] for i in range(6)]
def exact(z,r,p,t):
 z=dec(z);r=dec(r);p=dec(p);t=D(str(t));k,g,h,tau=p;f=(-t/tau).exp();ed=dev(z[:6]);rd=dev(r)
 gamma0=[a-b/(2*h) for a,b in zip(ed,z[6:])]
 gamma=[f*a+(1-f)*b+(t-tau*(1-f))*c for a,b,c in zip(gamma0,ed,rd)]
 e=[a+t*b for a,b in zip(z[:6],r)]
 return e+[2*h*(a-b) for a,b in zip(dev(e),gamma)]
def creep(z,p,t):
 z=dec(z);p=dec(p);k,g,h,tau=p;t=D(str(t));sd=dev(stress(z,p));ed=dev(z[:6]);m=sum(z[:3])/3;f=(-t*g/(tau*(g+h))).exp()
 e=[(m if i<3 else 0)+a/(2*g)+(b-a/(2*g))*f for i,(a,b) in enumerate(zip(sd,ed))]
 return e+[a-2*g*b for a,b in zip(sd,dev(e))]
def err(a,b):
 assert len(a)==len(b) and all(math.isfinite(float(x)) for x in list(a)+list(b))
 return max(abs(float(x)-float(y)) for x,y in zip(a,b))
def assess(path):
 doc=json.loads(path.read_text());c=doc['controls'];r=doc['result'];identity=doc['provenance']
 assert doc['kind']=='atlas-sls-laboratory-v1' and identity['model']==MODEL and identity['model_sha256']==MODEL_SHA
 assert r['ok'] and r['model']==MODEL and r['catalogue_hash']==identity['catalogue_hash'];assert r['initial']==c['initial'] and r['parameters']==c['parameters'] and r['initial_strain']==c['initial'][:6]
 assert len(r['points'])==c['samples']+2 and r['start_time']==c['start'];maximum=[0.,0.,0.]
 for i,pt in enumerate(r['points']):
  t=c['start']+(0 if i<2 else c['duration']*(i-1)/c['samples']);assert abs(pt['time']-t)<=1e-12*max(1,abs(t))
  assert pt['side']==('right' if i==1 else 'left') and pt['segment']==(-1 if i==0 else 0)
  dt=pt['time']-c['start'];ref=creep(c['initial'],c['parameters'],dt) if c['mode']=='creep' else exact(c['initial'],c['rates'] if c['mode']=='rate' else [0]*6,c['parameters'],dt)
  ss=stress(ref,dec(c['parameters']));errors=[err(pt['state'][:6],ref[:6]),err(pt['state'][6:],ref[6:]),err(pt['observables'],ss)];assert errors[0]<=3e-8 and max(errors[1:])<=1.,(str(path),i,errors)
  assert pt['strain']==pt['state'][:6];maximum=[max(a,b) for a,b in zip(maximum,errors)]
 return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mode':c['mode'],'points':len(r['points']),'physical_state_stress_scalars':len(r['points'])*18,'maximum_error':dict(zip(['strain','q_Pa','stress_Pa'],maximum))}
if __name__=='__main__':
 with localcontext() as ctx:
  ctx.prec=50;results=[assess(Path(p)) for p in sys.argv[1:]];assert results;print(json.dumps({'passed':True,'cases':results},indent=2))
