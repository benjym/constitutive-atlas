"""Exact independent Tresca backward-Euler KKT and repeated-spectrum witnesses.
No Atlas imports, numerical spectrum, author code or compiled execution.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse,hashlib,json
P=Path(__file__).parent

def mm(a,b):return [[sum(x*y for x,y in zip(row,col))for col in zip(*b)]for row in a]
def transpose(a):return list(map(list,zip(*a)))
def diag(v):return [[v[i]if i==j else F(0)for j in range(3)]for i in range(3)]
def rotate(v,Q):return mm(mm(Q,diag(v)),transpose(Q))
def ret(t,Y):
 if t[0]-t[2]<=Y:return list(t),'elastic'
 S=sum(t)
 if 3*t[1]>S+Y:a=(S+Y)/3;return [a,a,a-Y],'upper'
 if 3*t[1]<S-Y:b=(S-Y)/3;return [b+Y,b,b],'lower'
 q=(t[0]-t[2]-Y)/2;return [t[0]-q,t[1],t[2]+q],'face'
def enc(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:enc(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [enc(v)for v in x]
 return x
def run():
 f=json.loads((P/'prospective-freeze.json').read_text());mu=F(f['parameters_Pa']['mu']);lam=F(f['parameters_Pa']['lame_lambda']);Y=2*F(f['parameters_Pa']['k']);Q=[[F(v)for v in row]for row in f['rotation']];assert mm(Q,transpose(Q))==diag([F(1)]*3)
 rows=[];counts={'base_certificates':0,'rotated_certificates':0,'permutations':0,'strict_principal_tangent_directions':0,'corner_normal_cone_checks':0}
 from itertools import permutations
 for row in f['cases']:
  t=list(map(F,row['trial_eigenvalues']));u=list(map(F,row['expected_return_eigenvalues']));r=[x-y for x,y in zip(t,u)]
  got,branch=ret(t,Y);assert got==u and branch==row['branch'];assert u[0]>=u[1]>=u[2]and u[0]-u[2]<=Y and sum(r)==0
  gamma={}
  if any(r):
   if r[1]>=0:gamma={(0,2):r[0]/(2*mu),(1,2):r[1]/(2*mu)}
   else:gamma={(0,1):-r[1]/(2*mu),(0,2):-r[2]/(2*mu)}
  flow=[F(0)]*3
  for(i,j),g in gamma.items():assert g>=0 and(g==0 or u[i]-u[j]==Y);flow[i]+=g;flow[j]-=g
  assert r==[2*mu*x for x in flow]and sum(flow)==0
  # All six oriented planes must be admissible, including inactive ones.
  assert all(u[i]-u[j]-Y<=0 for i in range(3)for j in range(3)if i!=j)
  de=[x/(2*mu)-lam*sum(t)/(2*mu*(3*lam+2*mu))for x in t]
  assert [2*mu*x+lam*sum(de)for x in de]==t
  # Known spectral frames certify covariance without an eigenvalue implementation.
  T,U,E,DP=rotate(t,Q),rotate(u,Q),rotate(de,Q),rotate(flow,Q)
  assert all(T[i][j]-U[i][j]==2*mu*DP[i][j]for i in range(3)for j in range(3));counts['rotated_certificates']+=1
  for perm in permutations(range(3)):
   assert sorted([u[i]for i in perm],reverse=True)==u;counts['permutations']+=1
  # Degenerate eigenspace rotations cannot alter reconstruction when coefficients equal.
  # Rational Q2 is an exact rotation in the first/last repeated two-dimensional block.
  if t[0]==t[1]:R=[[F(3,5),F(4,5),F(0)],[-F(4,5),F(3,5),F(0)],[F(0),F(0),F(1)]];assert rotate(t,R)==diag(t)and rotate(u,R)==diag(u)
  if t[1]==t[2]:R=[[F(1),F(0),F(0)],[F(0),F(3,5),F(4,5)],[F(0),-F(4,5),F(3,5)]];assert rotate(t,R)==diag(t)and rotate(u,R)==diag(u)
  if row['id']in ['face','upper-edge','lower-edge']:
   J=([[F(1,2),F(0),F(1,2)],[F(0),F(1),F(0)],[F(1,2),F(0),F(1,2)]]if branch=='face'else[[F(1,3)]*3 for _ in range(3)])
   h=F(1,1000)
   for j in range(3):
    for sign in [-1,1]:
     v=list(t);v[j]+=sign*h;w,b=ret(v,Y);assert b==branch and w==[u[i]+sign*h*J[i][j]for i in range(3)]
    counts['strict_principal_tangent_directions']+=1
  counts['base_certificates']+=1
  rows.append({'id':row['id'],'branch':branch,'trial':t,'return':u,'plastic_increment':flow,'multipliers_g_ij_sigmai_minus_sigmaj_minus_2k':{f'{i+1}{j+1}':g for(i,j),g in gamma.items()},'initial_stress':[0]*6,'strain_increment_principal':de,'rotated_trial_cartesian':T,'rotated_return_cartesian':U,'rotated_strain_cartesian':E,'KKT_passed':True})
 corners=[]
 for pair in f['corner_mu_pairs']:
  a,b=map(F,pair);tau=[a,b,-a-b]
  if a>=0 and b>=0:x,y=a,b
  elif a+b/2<=0 and b+a/2<=0:x=y=F(0)
  elif b<0 and a+b/2>0:x,y=a+b/2,F(0)
  else:x,y=F(0),b+a/2
  normal=[x,y,-x-y];res=[t-n for t,n in zip(tau,normal)]
  assert x>=0 and y>=0 and res[0]<=res[2]and res[1]<=res[2]and sum(x*y for x,y in zip(normal,res))==0
  floor=min(a,b,F(0));S=[a-floor,b-floor,-floor];rho=max(F(1,4)+3*(a+b)/(4*(abs(a)+abs(b))),F(0))if a or b else F(0);printed=[rho*S[0],rho*S[1],rho*(S[2]-sum(S))]
  assert printed==normal
  corners.append({'projected_block_eigenvalues':[a,b],'rate':tau,'normal_projection':normal,'tangent_projection':res,'printed_rho':rho,'printed_Eq93_to99_matches_Eq108':True});counts['corner_normal_cone_checks']+=1
 return enc({'version':'tresca-independent-exact-fixtures-v1','freeze_sha256':hashlib.sha256((P/'prospective-freeze.json').read_bytes()).hexdigest(),'counts':counts,'cases':rows,'repeated_upper_corner_rate_checks':corners,'all_checks_passed':True,'compiled_calls':0,'Atlas_imports':False,'floating_spectral_claim':False,'scientific_admission':False})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();r=run()
 if a.check:assert r==json.loads((P/'fixtures.json').read_text());print('exact fixtures reproduced; all checks pass')
 else:print(json.dumps(r,indent=2,sort_keys=True))
