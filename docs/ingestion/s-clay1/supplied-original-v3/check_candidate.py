"""Algebraic candidate/source comparison; no compiled/model trajectory calls."""
import hashlib,json,math,random
from pathlib import Path
import numpy as np
from atlas.model import load,evaluation_environment,interpret,prepare_increment
O=Path(__file__).parent;m=load(O/'candidate/s-clay1.json');base={f['name']:f['initial'] for f in m['state']};checks=0;worst=0
I=np.eye(3)
def mat(x):return np.array([[x[0],x[3]/math.sqrt(2),x[5]/math.sqrt(2)],[x[3]/math.sqrt(2),x[1],x[4]/math.sqrt(2)],[x[5]/math.sqrt(2),x[4]/math.sqrt(2),x[2]]])
def mand(A):return list(map(float,[A[0,0],A[1,1],A[2,2],math.sqrt(2)*A[0,1],math.sqrt(2)*A[1,2],math.sqrt(2)*A[0,2]]))
def originalF(S,A,pm,M=1.1):
 p=np.trace(S)/3;d=S-p*I;t=d-p*A
 return 1.5*np.trace(t@t)-(M*M-1.5*np.trace(A@A))*(pm-p)*p
rng=random.Random(20261103)
for i in range(40):
 sig=[15000+rng.uniform(-1000,1000) for _ in range(3)]+[rng.uniform(-1000,1000) for _ in range(3)]
 af=[rng.uniform(-.15,.15) for _ in range(6)];a=sum(af[:3])/3;af[:3]=[x-a for x in af[:3]]
 s={**base,'sigma':sig,'fabric':af,'gamma':.001};env=evaluation_environment(m,s,s,[0]*6)
 f=originalF(mat(sig),mat(af),s['pm']);assert abs(f-env['yield_dim'])/20000**2<2e-14;checks+=1
 gradient=np.array(env['flow_dev'].v)+env['flow_volume']/3*np.array([1,1,1,0,0,0])
 for j in range(6):
  plus=sig.copy();minus=sig.copy();plus[j]+=.01;minus[j]-=.01
  fd=(originalF(mat(plus),mat(af),s['pm'])-originalF(mat(minus),mat(af),s['pm']))/.02
  err=abs(fd-gradient[j])/20000;worst=max(worst,err);assert err<2e-6;checks+=1
 theta=.371;Q=np.array([[math.cos(theta),-math.sin(theta),0],[math.sin(theta),math.cos(theta),0],[0,0,1]])
 ss={**s,'sigma':mand(Q@mat(sig)@Q.T),'fabric':mand(Q@mat(af)@Q.T)};ee=evaluation_environment(m,ss,ss,[0]*6)
 assert abs(ee['yield_dim']-env['yield_dim'])/20000**2<2e-10;checks+=1
 for name in ['flow_dev','shift']:
  assert np.max(np.abs(mat(ee[name].v)-Q@mat(env[name].v)@Q.T))/20000<2e-10;checks+=1
for p,q,a in [(10000,6000,.42),(10000,-6000,-.42),(10000,15000,.42),(10000,0,0)]:
 pm=p+(q-a*p)**2/((1.1**2-a*a)*p)
 s={**base,'sigma':[p+2*q/3,p-q/3,p-q/3,0,0,0],'fabric':[2*a/3,-a/3,-a/3,0,0,0],'pm':pm,'gamma':.001}
 e=evaluation_environment(m,s,s,[0]*6);assert abs(e['yield_dim'])/20000**2<1e-14;checks+=1
 if abs(1.1**2-(q/p)**2)>1e-9:
  gd=e['flow_dev'].v[0];assert abs(gd/e['flow_volume']-2*(q/p-a)/(1.1**2-(q/p)**2))<1e-12;checks+=1
for key,value in [('v',1),('pm',-1),('sigma',[-1,-1,-1,0,0,0]),('fabric',[2,-1,-1,0,0,0]),('fabric',[.1,.1,.1,0,0,0])]:
 try:prepare_increment(m,{**base,key:value},[0]*6)
 except ValueError:checks+=1
 else:raise AssertionError(key)
z=interpret(m,base,base,[0]*6)
assert all(max(map(abs,x.v))==0 if hasattr(x,'v') else x==0 for x in z.values());checks+=1
print(json.dumps({'ok':True,'checks':checks,'maximum_gradient_scaled_error':worst,'candidate_sha256':hashlib.sha256((O/'candidate/s-clay1.json').read_bytes()).hexdigest(),'scope':'candidate algebra/metadata/invalid initialization; no compiled trajectories'},indent=2))
