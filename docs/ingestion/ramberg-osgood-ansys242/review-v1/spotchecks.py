"""Independent reviewer algebra, no atlas or production/reference helper imports."""
import hashlib,json,math,random
from pathlib import Path
root=Path(__file__).resolve().parents[4]
rng=random.Random(492731)
checks=[]
for n in (1.5,2.5,5.,8.):
 for nu in (-.2,.25,.45):
  E=3e7; a=.5; s0=1e5
  for _ in range(8):
   sig=[rng.uniform(-3e5,3e5) for i in range(6)]
   m=sum(sig[:3])/3
   s=[v-(m if i<3 else 0) for i,v in enumerate(sig)]
   q=math.sqrt(1.5*sum(v*v for v in s))
   f=(1+nu+1.5*a*(q/s0)**(n-1))/E
   eps=[f*v+((1-2*nu)*m/E if i<3 else 0) for i,v in enumerate(s)]
   ev=sum(eps[:3]); ed=[v-(ev/3 if i<3 else 0) for i,v in enumerate(eps)]
   eeq=math.sqrt(2*sum(v*v for v in ed)/3)
   rhs=(2*(1+nu)/3+a*(q/s0)**(n-1))*q
   err=abs(E*eeq-rhs)/max(1,abs(rhs))
   assert err<1e-12
   # Eigenvalues of derivative epsilon(sigma): volumetric, deviatoric tangential/radial.
   eig=((1-2*nu)/E,(1+nu+1.5*a*(q/s0)**(n-1))/E,(1+nu+1.5*n*a*(q/s0)**(n-1))/E)
   assert min(eig)>0
   checks.append({'n':n,'nu':nu,'equivalent_relation_relative_error':err,'min_compliance_eigenvalue':min(eig)})
receipt=json.loads((root/'docs/ingestion/ramberg-osgood-ansys242/source-v1/source-receipt.json').read_text())
for r in receipt['files']:
 assert hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
out={'reviewer_run':'/root/ramberg_review','independence':'No atlas or implementation/oracle imports; independent tensor to equivalent scalar reduction and analytic positive compliance spectrum. These are algebra checks, not compiled qualification.','source_files_hash_verified':len(receipt['files']),'checks':checks,'passed':len(checks),'max_relative_error':max(x['equivalent_relation_relative_error'] for x in checks)}
print(json.dumps(out,indent=2))
