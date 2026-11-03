"""Frozen-policy native qualification. Stop at first failed gate; retain raw calls."""
from pathlib import Path
import hashlib,json,subprocess,sys,math,importlib.util,traceback
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[3];D=R/'.local/s-clay1-delivery-v3';S=D/'source';sys.path.insert(0,str(S))
from atlas.model import load,interpret,evaluation_environment
m=load(O/'candidate/s-clay1.json');base=[float(x) for f in m['state'] for x in (f['initial'] if f['shape']=='sym' else [f['initial']])];par=[float(f['default']) for f in m['parameters'].values()]
BIN=D/'native/atlas_solver';OUT=O/'native-v1';OUT.mkdir(exist_ok=False)
LOG=(OUT/'calls.jsonl').open('w');checks=0;calls=0;results={}
def csv(v):return ','.join(format(float(x),'.17g') for x in v)
def request(mode='integrate',z=None,de=None,p=None,extra=None,model='s-clay1',expected=True):
 global calls
 args=[str(BIN),'--model',model,'--mode',mode,'--initial',csv(base if z is None else z)]
 if p is not None:args+=['--parameters',csv(p)]
 if de is not None:args+=['--strain',csv(de)]
 if extra:
  for k,v in extra.items():args +=[k,str(v)]
 r=subprocess.run(args,capture_output=True,text=True,timeout=60);calls+=1
 LOG.write(json.dumps({'call':calls,'argv':args,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})+'\n');LOG.flush()
 value=json.loads(r.stdout);assert value['ok']==expected,(calls,value);assert r.returncode==(0 if expected else 1)
 return value
scales=np.array([20000.]*6+[1.]*7+[20000.,1.])
def err(a,b):return float(np.max(np.abs(np.array(a[:14])-np.array(b[:14]))/scales[:14]))
def state(z):return {'sigma':z[:6],'fabric':z[6:12],'v':z[12],'pm':z[13],'gamma':z[14]}
def valid(z):
 global checks
 e=evaluation_environment(m,state(z),state(z),[0]*6)
 assert e['yield_scaled']<=2e-8 and z[14]>=-1e-9 and abs(sum(z[6:9]))<=1e-8
 checks+=1
try:
 # Exact metadata and immutable source verification.
 desc=json.loads((O/'native-description.json').read_text());assert next(x for x in desc['models'] if x['id']=='s-clay1')==m;checks+=1
 manifest=json.loads((O/'build-source-manifest.json').read_text())
 def unchanged():
  for path,h in manifest['files'].items():assert hashlib.sha256((S/path).read_bytes()).hexdigest()==h,path
 unchanged();checks+=1
 spec=importlib.util.spec_from_file_location('independent_reference',O/'independent-review/reference_compliance.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
 errors=[]
 for n in [128,256,512]:
  y=[ref.v0,ref.a0,ref.pm0,0.,0.];z=[14000.,8000.,8000.,0.,0.,0.,.28,-.14,-.14,0.,0.,0.,ref.v0,ref.pm0,0.]
  step=(ref.p1-ref.p0)/n;stats={'min_H':math.inf,'min_multiplier_derivative':math.inf}
  for i in range(n):
   p=ref.p0+i*step
   a=ref.derivative(p,y,stats);b=ref.derivative(p+step/2,[v+step*x/2 for v,x in zip(y,a)],stats);c=ref.derivative(p+step/2,[v+step*x/2 for v,x in zip(y,b)],stats);d=ref.derivative(p+step,[v+step*x for v,x in zip(y,c)],stats)
   yn=[v+step*(a+2*b+2*c+d)/6 for v,a,b,c,d in zip(y,a,b,c,d)]
   dv,dd=yn[3]-y[3],yn[4]-y[4];de=[dv/3+dd,dv/3-dd/2,dv/3-dd/2,0,0,0]
   z[-1]=0.;z=request(z=z,de=de)['state'];valid(z);y=yn
  target=[16800.,9600.,9600.,0.,0.,0.,2*y[1]/3,-y[1]/3,-y[1]/3,0.,0.,0.,y[0],y[2],0.]
  errors.append(err(z,target));results['reference_'+str(n)]={'actual':z,'reference':target,'error':errors[-1]}
 assert errors[-1]<3e-3 and errors[-1]<errors[0],errors;checks+=1
 # Hydrostatic endpoint analytical check and continuum refinement.
 z0=[10000.]*3+[0.]*9+[3.,100000.,0.];de=[1e-5/3]*3+[0.]*3
 z=request(z=z0,de=de)['state'];v=3*math.exp(-1e-5);p=10000/(1-v*1e-5/.04);expected=[p]*3+[0.]*9+[v,100000,0.]
 assert err(z,expected)<2e-8;checks+=1
 hold=request(z=z,de=[0]*6)['state'];assert err(z,hold)<2e-10;checks+=1
 z=z0.copy()
 for i in range(512):z=request(z=z,de=[1e-5/(3*512)]*3+[0.]*3)['state']
 assert abs((z[12]-3)+.04*math.log(z[0]/10000))<1e-6;checks+=1
 # Fulltensor covariance, active yielding and reversal.
 I=np.eye(3)
 def mat(x):return np.array([[x[0],x[3]/math.sqrt(2),x[5]/math.sqrt(2)],[x[3]/math.sqrt(2),x[1],x[4]/math.sqrt(2)],[x[5]/math.sqrt(2),x[4]/math.sqrt(2),x[2]]])
 def mand(A):return list(map(float,[A[0,0],A[1,1],A[2,2],math.sqrt(2)*A[0,1],math.sqrt(2)*A[1,2],math.sqrt(2)*A[0,2]]))
 t=.371;Q=np.array([[math.cos(t),-math.sin(t),0],[math.sin(t),math.cos(t),0],[0,0,1]])
 rot=lambda x:mand(Q@mat(x)@Q.T)
 zr=rot(base[:6])+rot(base[6:12])+base[12:]
 for de in [[.001,0,0,0,0,0],[.01,0,0,0,0,0],[0,0,0,.001,0,0],[.001,-.0005,-.0005,.001,-.0007,.0003]]:
  z=request(de=de)['state'];valid(z);zz=request(z=zr,de=rot(de))['state'];expected=rot(z[:6])+rot(z[6:12])+z[12:]
  assert err(zz,expected)<2e-7;checks+=1
  z[-1]=0.;unload=request(z=z,de=[-x*.01 for x in de])['state'];valid(unload)
 # Inadmissible starts/loading/params, forced rollback, fresh recovery and replay.
 for idx,value in [(0,-100000),(12,1),(13,-1)]:
  zz=base.copy();zz[idx]=value;request(z=zz,de=[0]*6,expected=False);checks+=1
 zz=base.copy();zz[6:12]=[2,-1,-1,0,0,0];request(z=zz,de=[0]*6,expected=False);checks+=1
 zz=base.copy();zz[6]=.3;request(z=zz,de=[0]*6,expected=False);checks+=1
 pp=par.copy();pp[2]=pp[3];request(de=[.001,0,0,0,0,0],p=pp,expected=False);checks+=1
 request(de=[.001],expected=False);request(de=[float('nan')]*6,expected=False);checks+=2
 failed=request(de=[.01,0,0,0,0,0],extra={'--integration-settings':'2e-10,1e-6,1,0,20000,20'},expected=False)
 assert failed.get('state')==base;checks+=1
 a=request(de=[1e-5,0,0,0,0,0]);b=request(de=[1e-5,0,0,0,0,0]);assert a['state']==b['state'];checks+=1
 parent=a['state'];parent[-1]=0.;c=request(z=parent,de=[1e-5,0,0,0,0,0]);d=request(z=parent.copy(),de=[1e-5,0,0,0,0,0]);assert err(c['state'],d['state'])<2e-9;checks+=1
 # Actual public defaults and explicitly proposed bounded edits.
 for protocol,pp,zz,label in [(1,par,base,'drained'),(2,par,base,'undrained')]+[(1,[*par[:7],mu],base,'mu'+str(mu)) for mu in [10,50]]+[(1,[*par[:6],beta,par[7]],base,'beta'+str(beta)) for beta in [0,.9]]+[(1,par,base[:13]+[20000.,0.],'pm20000')]:
  result=request(mode='run',p=pp,z=zz,extra={'--protocol':protocol,'--target':'.01','--steps':100,'--cycles':0})
  points=result['points'];assert len(points)==101 and points[-1]['q']!=points[0]['q'];checks+=1
  for pt in points:assert all(math.isfinite(float(x)) for x in pt['state']);checks+=1
  results[label]={'points':len(points),'last':points[-1]}
 for model in ['linear-elastic','modified-cam-clay']:
  mm=load(S/'models'/f'{model}.json');zz=[float(x) for f in mm['state'] for x in (f['initial'] if f.get('shape')=='sym' else [f['initial']])]
  result=request(mode='run',model=model,z=zz,extra={'--protocol':1,'--target':'.01','--steps':100});assert len(result['points'])==101;checks+=1
 unchanged();checks+=1
 results.update(ok=True,checks=checks,calls=calls,reference_errors=errors)
except Exception:
 results.update(ok=False,checks=checks,calls=calls,failure=traceback.format_exc());raise
finally:
 LOG.close();results['candidate_sha256']=hashlib.sha256((O/'candidate/s-clay1.json').read_bytes()).hexdigest();results['executable_sha256']=hashlib.sha256(BIN.read_bytes()).hexdigest();(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
