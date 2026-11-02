"""Independent E1-E3 review. Pure Python; no author harness execution or writes."""
import sys,json,math,hashlib,random
from pathlib import Path
from decimal import Decimal,localcontext
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'source-v1'
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from atlas.model import load,interpret,observe
from atlas.initialization import initialize_state
checks=[]
def check(label,ok):
 checks.append({'name':label,'pass':bool(ok)})
 assert ok,label
def close(a,b,atol=2e-13,rtol=2e-12):return abs(a-b)<=atol+rtol*max(abs(a),abs(b))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((SOURCE/'MANIFEST.json').read_text())
for name,receipt in manifest['files'].items():
 p=SOURCE/name;check('sealed:'+name,digest(p)==receipt['sha256'] and p.stat().st_size==receipt['bytes'])
for receipt in json.loads((SOURCE/'source-receipts.json').read_text())['receipts']:
 p=Path(receipt['path']);check('primary:'+p.name,digest(p)==receipt['sha256'] and p.stat().st_size==receipt['bytes'])
m=load(SOURCE/'candidate.json')
check('inventory',len(m['parameters'])==5 and sum(6 if v['shape']=='sym' else 1 for v in m['state'])==13)
# Independent pairwise J2 invariant, avoiding the candidate norm(dev()) construction.
def law(z,p):
 K,G,Y,A,n=p;e=[z[i]-z[i+6] for i in range(6)];tr=sum(e[:3]);s=[2*G*(e[i]-tr/3 if i<3 else e[i]) for i in range(6)]
 sig=[s[i]+(K*tr if i<3 else 0) for i in range(6)]
 q=math.sqrt(((sig[0]-sig[1])**2+(sig[1]-sig[2])**2+(sig[2]-sig[0])**2)/2+1.5*sum(v*v for v in sig[3:]))
 lam=A*(q/Y-1)**n if q>Y else 0.
 v=[1.5*lam*x/q if q else 0. for x in s]
 return sig,q,lam,v
rng=random.Random(2103)
for i in range(160):
 p=[20e6,10e6,100e3,.002,[1.,1.00001,1.5,2.,3.,8.][i%6]]
 vp=[rng.uniform(-.001,.001) for _ in range(6)];vp[2]=-vp[0]-vp[1]
 z=[rng.uniform(-.006,.006) for _ in range(6)]+vp+[1.]
 if i<4:z=[0.]*13;z[:3]=[.01]*3 if i==1 else [0.]*3;z[3]=p[2]/(math.sqrt(3)*p[1]) if i==2 else 0.;z[0]=p[2]/(2*p[1]) if i==3 else z[0]
 d=[rng.uniform(-.001,.001) for _ in range(6)];named={'eps':z[:6],'eps_vp':z[6:12],'alpha':z[12]};params=dict(zip(m['parameters'],p));r=interpret(m,named,None,d,params,time=3.)
 sig,q,lam,v=law(z,p);obs=observe(m,named,d,params,time=3.)['stress'].v
 check(f'rhs-{i}',all(close(a,b) for a,b in zip(v,r['eps_vp'].v)) and close(lam,r['alpha']) and list(r['eps'].v)==d)
 check(f'stress-{i}',all(close(a,b,atol=2e-8) for a,b in zip(sig,obs)))
 check(f'dissipation-{i}',close(sum(a*b for a,b in zip(sig,v)),q*lam,atol=2e-8))
 check(f'volume-{i}',abs(sum(v[:3]))<1e-12)
# 50-digit independently integrated scalar relaxation; check every saved endpoint.
refs=json.loads((SOURCE/'analytical-references.json').read_text())['cases']
with localcontext() as ctx:
 ctx.prec=50
 dec=lambda x:Decimal(str(x))
 for c in refs:
  z=c['initial'];p=c['parameters'];sig,q,lam,v=law(z,p);K,G,Y,A,n=map(dec,p);t=dec(c['duration']);q0=dec(q)
  if q0>Y:
   u=q0/Y-1;rate=3*G*A/Y
   end=u*(-rate*t).exp() if n==1 else (u**(1-n)+(n-1)*rate*t)**(1/(1-n))
   qend=Y*(1+end);loss=float(q0-qend)
  else:loss=0.
  s=[sig[i]-sum(sig[:3])/3 if i<3 else sig[i] for i in range(6)]
  expected=z[:6]+[z[i+6]+(loss*s[i]/(2*float(G)*q) if q else 0.) for i in range(6)]+[z[12]+loss/(3*float(G))]
  check('decimal-relaxation:'+c['id'],all(close(a,b) for a,b in zip(expected,c['relaxation']['state'])))
  creep=z[:6]+z[6:12]+[z[12]]
  for j in range(6):
   delta=float(t)*v[j];creep[j]+=delta;creep[j+6]+=delta
  creep[12]+=float(t)*lam
  check('constant-stress-creep:'+c['id'],all(close(a,b) for a,b in zip(creep,c['creep']['state'])))
saved=json.loads((SOURCE/'SOURCE-CHECKS.json').read_text());check('saved-check-inventory',saved['passed'] and saved['analytical_cases']==180 and len(saved['checks'])==1106 and all(c['passed'] for c in saved['checks']))
a=(SOURCE/'check_source.py').read_text();b=(SOURCE/'check_source_v2.py').read_text()
check('retained-harness-only-call-fix',a.replace('interpret(m,named,params,o.ZERO,time=0.)','interpret(m,named,None,o.ZERO,params,time=0.)')==b)
params=dict(zip(m['parameters'],[20e6,10e6,100e3,.002,2.]))
valid={'eps':[.01,-.005,-.005,0,0,0],'eps_vp':[0.]*6,'alpha':0.}
check('overstress-allowed',len(initialize_state(m,valid,params,time=0.,loading=[0.]*6)['initial'])==13)
for name,bad in [('missing-vp',{'eps':valid['eps'],'alpha':0.}),('negative-alpha',{**valid,'alpha':-1.}),('trace-vp',{**valid,'eps_vp':[.001,0,0,0,0,0]}),('impossible-history',{**valid,'eps_vp':[.01,-.005,-.005,0,0,0]})]:
 try:initialize_state(m,bad,params,time=0.,loading=[0.]*6)
 except (ValueError,KeyError):check(name,True)
 else:check(name,False)
result={'identity':'perzyna-independent-source-contract-checks-v1','reviewer':'/root/perzyna_source_review','passed':all(c['pass'] for c in checks),'check_count':len(checks),'saved_cases_recomputed':len(refs),'independent_rhs_cases':160,'compiled_execution':False,'checks':checks}
(HERE/'CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
