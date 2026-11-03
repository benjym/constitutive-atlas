"""Frozen-policy native qualification. Stop at first failed gate; retain raw calls."""
from pathlib import Path
import hashlib,json,subprocess,sys,math,importlib.util,traceback
import numpy as np
O=Path(__file__).resolve().parent;R=O.parents[3];D=R/'.local/s-clay1-delivery-v3';S=D/'source';sys.path.insert(0,str(S))
from atlas.model import load,interpret,evaluation_environment
m=load(O/'candidate/s-clay1.json');base=[float(x) for f in m['state'] for x in (f['initial'] if f['shape']=='sym' else [f['initial']])];par=[float(f['default']) for f in m['parameters'].values()]
BIN=D/'native/atlas_solver';OUT=O/'native-v2';OUT.mkdir(exist_ok=False)
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
 # Actual public defaults and explicitly proposed bounded edits.
 for protocol,pp,zz,label in [(1,par,base,'drained'),(2,par,base,'undrained')]+[(1,[*par[:6],mu],base,'mu'+str(mu)) for mu in [10,50]]+[(1,[*par[:5],beta,par[6]],base,'beta'+str(beta)) for beta in [0,.9]]+[(1,par,base[:13]+[20000.,0.],'pm20000')]:
  result=request(mode='run',p=pp,z=zz,extra={'--protocol':protocol,'--target':'.01','--steps':100,'--cycles':0})
  points=result['points'];assert len(points)==101 and points[-1]['q']!=points[0]['q'];checks+=1
  for pt in points:assert all(math.isfinite(float(x)) for x in pt['state']);checks+=1
  results[label]={'points':len(points),'last':points[-1]}
 for model in ['linear-elastic','modified-cam-clay']:
  mm=load(S/'models'/f'{model}.json');zz=[float(x) for f in mm['state'] for x in (f['initial'] if f.get('shape')=='sym' else [f['initial']])]
  result=request(mode='run',model=model,z=zz,extra={'--protocol':1,'--target':'.01','--steps':100});assert len(result['points'])==101;checks+=1
 results.update(ok=True,checks=checks,calls=calls,scope='Continuation after nativev1 checker index defect; only previously unrun public examples/regressions')
except Exception:
 results.update(ok=False,checks=checks,calls=calls,failure=traceback.format_exc());raise
finally:
 LOG.close();results['candidate_sha256']=hashlib.sha256((O/'candidate/s-clay1.json').read_bytes()).hexdigest();results['executable_sha256']=hashlib.sha256(BIN.read_bytes()).hexdigest();(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n')
