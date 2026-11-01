import json, hashlib, runpy, sys, math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(R))
from atlas.model import load,evaluation_environment
D=Path(__file__).resolve().parent; P=D.parent; S=P.parent/'source-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mp=P/'manzari-dafalias-1997-constant-m-be-v1.json'
assert sha(mp)=='28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064'
checks=[]
for f in json.loads((S/'source-receipt.json').read_text())['files']:
 p=R/f['private_path']; assert sha(p)==f['sha256'],str(p)
 checks.append({'kind':'source-byte-binding','path':f['private_path'],'passed':True})
for name,h in json.loads((P/'reference-v1/manifest.json').read_text()).items():
 assert sha(P/'reference-v1'/name)==h,name
 checks.append({'kind':'reference-byte-binding','path':name,'passed':True})
m=load(mp)
def mand(a):return list(map(float,[a[0,0],a[1,1],a[2,2],2**.5*a[0,1],2**.5*a[1,2],2**.5*a[0,2]]))
base=np.array([[.02,.007,-.004],[.007,-.013,.003],[-.004,.003,-.007]])
for j in range(6):
 t=np.array([[1+.19*j,.17,-.21],[.17,-.2-.07*j,.11],[-.21,.11,-.8-.12*j]])
 t-=np.trace(t)*np.eye(3)/3; n=t/np.linalg.norm(t)
 rho=math.sqrt(2/3)*.05*n
 sig=160000*(np.eye(3)+base+rho)
 eigen=np.linalg.eigvalsh(rho)
 J=math.sqrt(sum(eigen**2)/2)
 cosine=math.sqrt(3)/2*sum(eigen**3)/J**3
 g=lambda c:2*c/(1+c-(1-c)*cosine)
 for psi in [-.15,.05]:
  bscalar=g(1)*1.14+g(2/3.975)*3.975*max(-psi,0)-.05
  dscalar=g(1)*1.14+g(.07/4.2)*4.2*psi-.05
  b=math.sqrt(2/3)*bscalar*n-base
  bn=float(np.trace(b@n)); bref=2*math.sqrt(2/3)*(1.14+3.975*max(-psi,0)-.05)
  h=1200*abs(bn)/(bref-abs(bn))
  raw=2.64*float(np.trace((math.sqrt(2/3)*dscalar*n-base)@n))
  d=max(raw,0) if psi>0 else raw
  state={'sigma':mand(sig),'e':.8+psi,'alpha':mand(base),'gamma':0}
  env=evaluation_environment(m,state,state,[0]*6)
  expected={'cos3theta':cosine,'alpha_b_scalar':bscalar,'alpha_d_scalar':dscalar,'h':h,'D':d}
  for key,v in expected.items():
   err=abs(env[key]-v); assert err<=1e-11*max(1,abs(v)),(key,err)
   checks.append({'kind':'source-Cartesian-algebra','case':j,'psi':psi,'channel':key,'error':err,'passed':True})
ref=runpy.run_path(str(P/'reference-v1/reference.py'))
saved=json.loads((P/'reference-v1/reference-results.json').read_text())
for name,c in saved['cases'].items():
 actual=ref['solve'](c['axial_sign'],c['protocol'],c['e0'],1e-6)
 for a,b in zip(actual['checkpoints'],c['checkpoints']):
  for key in ['sigma_Pa','alpha','e','radial_strain']:
   av=a[key] if isinstance(a[key],list) else [a[key]];bv=b[key] if isinstance(b[key],list) else [b[key]]
   error=max(abs(x-y) for x,y in zip(av,bv));assert error<= (1e-8 if key=='sigma_Pa' else 1e-12)
 checks.append({'kind':'saved-reference-reproduction','case':name,'passed':True})
report={'reviewer':'/root/md1997_review','candidate_sha256':sha(mp),'compiled_execution':False,'passed':True,'checks':checks}
(D/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':True,'checks':len(checks)}))
