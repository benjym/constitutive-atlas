from pathlib import Path
import json,hashlib,runpy,math
import numpy as np
D=Path(__file__).resolve().parent; P=D.parents[1]; R=D.parents[5]
T=P/'reference-v1/interior-lode-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for file,h in json.loads((D.parent/'manifest.json').read_text()).items():
 assert sha(R/file)==h,file
 checks.append({'kind':'preserved-original-review-binding','file':file,'passed':True})
for file,h in json.loads((T/'manifest.json').read_text()).items():
 assert sha(T/file)==h,file
 checks.append({'kind':'new-reference-binding','file':file,'passed':True})
ref=runpy.run_path(str(T/'reference.py'))
saved=json.loads((T/'reference-results.json').read_text());req=json.loads((T/'requests.json').read_text())
assert saved['passed'] and not saved['failures'] and len(saved['cases'])==6
assert {(c['e0'],c['cos3theta']) for c in saved['cases'].values()}=={(e,cs) for e in [.65,.85] for cs in [0,.5,-.5]}
for c in req['cases']:
 assert c=={'name':c['name'],**saved['cases'][c['name']]}
def mat(v):
 return np.array([[v[0],v[3]/2**.5,v[5]/2**.5],[v[3]/2**.5,v[1],v[4]/2**.5],[v[5]/2**.5,v[4]/2**.5,v[2]]])
for name,c in saved['cases'].items():
 n=mat(c['n_mandel']);eigen=np.linalg.eigvalsh(n);cs=c['cos3theta']
 assert abs(np.trace(n))<1e-12 and abs(np.sum(n*n)-1)<1e-12
 assert abs(math.sqrt(6)*sum(eigen**3)-cs)<1e-12
 fine=ref['solve'](c['e0'],cs,1e-6,c['n_mandel']);coarse=ref['solve'](c['e0'],cs,2e-6,c['n_mandel'])
 errs={'stress_Pa':0,'alpha':0,'e':0,'source_rate_relative':0}
 for f,b,o in zip(fine['checkpoints'],coarse['checkpoints'],c['checkpoints']):
  for key,tol in [('sigma_Pa',1e-8),('alpha',1e-12),('e',1e-12),('strain',1e-12)]:
   fv=f[key] if isinstance(f[key],list) else [f[key]];ov=o[key] if isinstance(o[key],list) else [o[key]]
   assert max(abs(x-y) for x,y in zip(fv,ov))<=tol
  for x,y in zip(f['sigma_Pa'],b['sigma_Pa']):
   err=abs(x-y);errs['stress_Pa']=max(errs['stress_Pa'],err);assert err<=5+2e-5*max(1000,abs(x))
  for x,y in zip(f['alpha'],b['alpha']):
   err=abs(x-y);errs['alpha']=max(errs['alpha'],err);assert err<=2e-6
  p=o['p_Pa']/1000;beta=o['beta'];x=o['x'];e=c['e0'];a=beta*n
  psi=e-(.8-.025*math.log(p/160));S=math.sqrt(2/3)
  g=lambda ratio:2*ratio/(1+ratio-(1-ratio)*cs)
  bb=S*(1.14*g(1)+3.975*g(2/3.975)*max(-psi,0)-.05)*n
  bd=S*(1.14*g(1)+4.2*g(.07/4.2)*psi-.05)*n
  bn=float(np.sum((bb-a)*n));bref=2*S*(1.14+3.975*max(-psi,0)-.05)
  h=1200*abs(bn)/(bref-abs(bn));Dflow=2.64*float(np.sum((bd-a)*n))
  if psi>0 and Dflow<0:Dflow=0
  G=31400*(p/100)**.6;K=G;N=float(np.sum(a*n))+S*.05
  Kp=p*h*bn
  L=2*G*float(np.sum(n*n))/(Kp+2*G-K*Dflow*N)
  sigdot=2*G*n-L*(2*G*n+K*Dflow*np.eye(3));adot=L*h*(bb-a)
  pd,betad,xd=ref['rhs']([p,beta,x],e,cs)
  reconstructed=pd*np.eye(3)+(pd*x+p*xd)*n
  err=max(float(np.max(abs(sigdot-reconstructed)))/max(1,float(np.max(abs(sigdot)))),float(np.max(abs(adot-betad*n)))/max(1,float(np.max(abs(adot)))))
  errs['source_rate_relative']=max(errs['source_rate_relative'],err);assert err<=1e-10
 assert fine['max_yield_drift']<=2e-5
 checks.append({'kind':'source-interior-Lode-case','name':name,'passed':True,'max_errors':errs,'yield_drift':fine['max_yield_drift']})
report={'reviewer':'/root/md1997_review','compiled_execution':False,'passed':True,'checks':checks}
(D/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks)}))
