"""Independent rational matrix oracle plus uncompiled declarative crosswalk checks."""
import json,sys,hashlib
from fractions import Fraction as Q
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
from atlas.model import validate,defaults,interpret

def fraction(x):return Q(str(x))
def compliance(p):
 e1,e2,e3,g12,g23,g13,n12,n23,n13=map(fraction,p.values())
 z=Q(0);s=[[z for _ in range(6)] for _ in range(6)]
 for i,e in enumerate([e1,e2,e3]):s[i][i]=1/e
 for i,j,v in [(0,1,-n12/e1),(0,2,-n13/e1),(1,2,-n23/e2)]:s[i][j]=s[j][i]=v
 for i,g in enumerate([g12,g23,g13],3):s[i][i]=1/(2*g)
 return s

def inverse(s):
 n=len(s);a=[list(row)+[Q(i==j) for j in range(n)] for i,row in enumerate(s)]
 for k in range(n):
  ix=next(i for i in range(k,n) if a[i][k]);a[ix],a[k]=a[k],a[ix]
  d=a[k][k];a[k]=[v/d for v in a[k]]
  for i in range(n):
   if i!=k:
    d=a[i][k];a[i]=[v-d*w for v,w in zip(a[i],a[k])]
 return [row[n:] for row in a]

def matvec(a,x):return [sum(v*w for v,w in zip(row,x)) for row in a]
def determinant3(a):
 return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
def spd(a):return all(a[i][i]>0 for i in range(6)) and a[0][0]*a[1][1]-a[0][1]**2>0 and determinant3(a)>0

def run():
 m=json.loads((HERE/'candidate.json').read_text());validate(m)
 policy=json.loads((HERE/'reference-policy.json').read_text());tol=policy['residual_absolute_tolerance_Pa']
 p0=defaults(m);sets=[('default',p0),('auxetic',dict(p0,nu12=-.2,nu23=.1,nu13=-.15)),('large-admissible-poisson',dict(p0,E1=100e6,E2=10e6,E3=20e6,nu12=.8,nu23=.1,nu13=.6)),('isotropic',dict(p0,E1=60e6,E2=60e6,E3=60e6,G12=24e6,G23=24e6,G13=24e6,nu12=.25,nu23=.25,nu13=.25))]
 for k in range(12):sets.append((f'varied-{k}',dict(p0,E1=(20+3*k)*1e6,E2=(25+2*k)*1e6,E3=(33+4*k)*1e6,G12=(8+k)*1e6,G23=(11+2*k)*1e6,G13=(7+3*k)*1e6,nu12=(k-5)/50,nu23=(4-k)/60,nu13=(k-6)/70)))
 incs=[[Q(int(i==j),1000) for i in range(6)] for j in range(6)]+[[Q(1,1000),Q(-2,1000),Q(3,2000),Q(4,3000),Q(-5,4000),Q(6,5000)],[Q(0)]*6]
 previous=list(map(Q,[100000,-200000,300000,40000,-50000,60000]))
 refs=[];maxres=0;inversechecks=0;energychecks=0
 for name,p in sets:
  s=compliance(p);assert spd(s);assert all(s[i][j]==s[j][i] for i in range(6) for j in range(6));c=inverse(s)
  for i in range(6):
   for j in range(6):assert sum(s[i][k]*c[k][j] for k in range(6))==Q(i==j);inversechecks+=1
  for j,de in enumerate(incs):
   ds=matvec(c,de);energy=sum(x*y for x,y in zip(de,ds))/2
   assert energy>0 if any(de) else energy==0;energychecks+=1
   endpoint=[a+b for a,b in zip(previous,ds)]
   residual=interpret(m,{'sigma':list(map(float,endpoint))},{'sigma':list(map(float,previous))},list(map(float,de)),p)['sigma'].v
   maxres=max(maxres,max(map(abs,residual)));assert max(map(abs,residual))<=tol,(name,j,residual)
   refs.append(dict(case=f'{name}-{j}',parameters=p,previous_state=list(map(float,previous)),strain_increment=list(map(float,de)),expected_state=list(map(float,endpoint)),exact_state=[str(v) for v in endpoint],exact_energy_Pa=str(energy)))
 invalid=[('negative-E1',dict(p0,E1=-30e6)),('negative-G12',dict(p0,G12=-12e6)),('negative-G23',dict(p0,G23=-18e6)),('negative-G13',dict(p0,G13=-15e6)),('failed-pair-minor',dict(p0,nu12=.9)),('failed-determinant-with-positive-pairs',dict(p0,E1=30e6,E2=30e6,E3=30e6,nu12=.6,nu23=.6,nu13=.6)),('singular',dict(p0,E1=30e6,E2=30e6,E3=30e6,nu12=.5,nu23=.5,nu13=.5))]
 bad=[]
 for name,p in invalid:
  assert not spd(compliance(p))
  try:interpret(m,{'sigma':[0]*6},{'sigma':[0]*6},[0]*6,p)
  except (ValueError,ZeroDivisionError,OverflowError) as exc:bad.append(dict(case=name,rejected=True,exception=type(exc).__name__))
  else:raise AssertionError(name+' not rejected')
 out=dict(identity=policy['identity'],status='pass',candidate_sha256=hashlib.sha256((HERE/'candidate.json').read_bytes()).hexdigest(),parameter_sets=len(sets),endpoint_cases=len(refs),residual_scalar_checks=6*len(refs),exact_inverse_identity_checks=inversechecks,energy_checks=energychecks,maximum_absolute_residual_Pa=maxres,tolerance_Pa=tol,invalid_rejections=bad,compiled_checks_run=False,experimental_validation=False)
 return out,refs
if __name__=='__main__':
 out,refs=run()
 if '--write' in sys.argv:
  (HERE/'checks.json').write_text(json.dumps(out,indent=2)+'\n');(HERE/'references.json').write_text(json.dumps(refs,indent=2)+'\n')
 print(json.dumps(out,indent=2))
