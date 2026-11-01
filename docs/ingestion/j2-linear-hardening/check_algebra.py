#!/usr/bin/env python3
"""Independent exact-rational linear-hardening reduction; never executes vendor/Atlas kernels."""
from fractions import Fraction as F
import hashlib,json,pathlib,math
P=pathlib.Path(__file__).resolve().parent
ROOT=P.parents[2]

def run():
    checks=[]
    def check(name,condition):
        assert condition,name
        checks.append(name)
    # Axial deviator (2t,-t,-t): q_VM=3|t| exactly, Frobenius norm=sqrt(6)|t|.
    # Project gamma = sqrt(2/3) gamma_src; multiplying source residual by sqrt(3/2)
    # turns 2G gamma_src into 3G gamma and hardening increment into H gamma.
    for G in (F(7),F(31),F(80000)):
      for H in (F(0),F(3),F(1000)):
       for alpha in (F(0),F(1,100)):
        for t in (F(0),F(1),F(10),F(100)):
          y=F(25); qt=3*t; radius=y+H*alpha
          gamma=max(F(0),(qt-radius)/(3*G+H))
          q=qt-3*G*gamma; anew=alpha+gamma
          check(f'complementarity-{G}-{H}-{alpha}-{t}', gamma>=0 and q<=y+H*anew and gamma*(q-y-H*anew)==0)
          check(f'no-crossing-{G}-{H}-{alpha}-{t}',q>=0 and anew>=alpha)
          # sqrt(6)t-2G gamma_src-sqrt(2/3)(y+H anew)=0 on plastic branch.
          # Divide by sqrt(2/3), use sqrt(6)/sqrt(2/3)=3, gamma_src/sqrt(2/3)=3gamma/2.
          check(f'source-normalization-{G}-{H}-{alpha}-{t}',not gamma or 3*t-3*G*gamma-y-H*anew==0)
          # Discrete associated flow work = (y+H anew) gamma >=0.
          check(f'dissipation-{G}-{H}-{alpha}-{t}',(y+H*anew)*gamma>=0)
    # Mandel contraction equals full symmetric tensor contraction, including all three shears.
    A=[[7.,2.,-3.],[2.,-4.,5.],[-3.,5.,9.]]
    v=[A[0][0],A[1][1],A[2][2],math.sqrt(2)*A[0][1],math.sqrt(2)*A[1][2],math.sqrt(2)*A[0][2]]
    check('mandel-frobenius',abs(sum(x*x for x in v)-sum(x*x for row in A for x in row))<1e-12)
    check('equivalent-plastic-strain',abs(math.sqrt(F(2,3))*math.sqrt(F(3,2))-1)<1e-15)
    # Source normalization with arbitrary tensor, independently through physical components.
    for scale in (0.001,0.02,0.3):
      tr=sum(A[i][i] for i in range(3))/3
      s=[[scale*(A[i][j]-(tr if i==j else 0)) for j in range(3)] for i in range(3)]
      norm=math.sqrt(sum(x*x for row in s for x in row)); G=31.;H=3.;y=.25;alpha=.01
      gs=max(0.,(norm-math.sqrt(2/3)*(y+H*alpha))/(2*G+2*H/3));g=math.sqrt(2/3)*gs
      gp=max(0.,(math.sqrt(1.5)*norm-y-H*alpha)/(3*G+H))
      check(f'tensor-source-gamma-{scale}',abs(g-gp)<1e-15)
      a=[[s[i][j]-2*G*gs*s[i][j]/norm for j in range(3)] for i in range(3)]
      b=[[s[i][j]-3*G*gp*s[i][j]/(math.sqrt(1.5)*norm) for j in range(3)] for i in range(3)]
      check(f'tensor-source-stress-{scale}',max(abs(a[i][j]-b[i][j]) for i in range(3) for j in range(3))<1e-14)
    # Candidate structural/semantic validation is separate from above independent algebra.
    import sys
    sys.path.insert(0,str(ROOT))
    from atlas.model import load
    model=load(P/'candidate-v03.json')
    private=ROOT/'.local/private-sources/j2-linear-hardening'
    receipts=json.loads((P/'source-receipts.json').read_text())
    source_checks=[]
    for receipt in receipts['sources']:
      source=private/receipt['private_filename']
      assert hashlib.sha256(source.read_bytes()).hexdigest()==receipt['sha256']
      source_checks.append(receipt['id'])
    return {'version':'j2-ingestion-algebra-0.1','passed':True,'algebra_checks':len(checks),'checks':checks,'source_hash_checks':source_checks,'candidate_sha256':hashlib.sha256((P/'candidate-v03.json').read_bytes()).hexdigest(),'candidate_valid':True,'compiled_calls':0,'vendor_calls':0,'limitations':['Exact-rational coaxial and independent Cartesian normalization checks; no numerical solver execution, path integration, tangent or experimental validation.']}
if __name__=='__main__':
    print(json.dumps(run(),indent=2))
