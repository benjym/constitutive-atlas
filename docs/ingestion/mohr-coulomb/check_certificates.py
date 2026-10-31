"""Independent exact rational MC certificates; no Atlas or author-code imports."""
from fractions import Fraction as F
import json
K=G=F(1);sphi=F(3,5);cphi=F(4,5);spsi=F(1,3);cohesion=F(5)
h=2*cohesion*cphi
A=F(2,3)*(3*K-2*G)*spsi
Ds=2*A*sphi+4*G*(1+sphi*spsi)
Dl=2*A*sphi+G*(1+spsi)*(1+sphi)+2*G*(1-spsi)*(1-sphi)
Dr=2*A*sphi+2*G*(1+spsi)*(1+sphi)+G*(1-spsi)*(1-sphi)
Da=4*K*spsi*sphi

def elastic(v):return tuple(2*G*x+(K-F(2,3)*G)*sum(v) for x in v)
def compliance(v):return tuple((x-sum(v)/3)/(2*G)+sum(v)/(9*K) for x in v)
def yield_value(v):return (1+sphi)*v[0]-(1-sphi)*v[2]-h

def mapped(t):
 assert t[0]>=t[1]>=t[2]
 if yield_value(t)<=0:return 'elastic',F(0),t
 gsl=(t[0]-t[1])/(2*G*(1+spsi));gsr=(t[1]-t[2])/(2*G*(1-spsi))
 gla=(t[0]+t[1]-2*t[2])/(2*G*(3-spsi));gra=(2*t[0]-t[1]-t[2])/(2*G*(3+spsi))
 roots=[('face',yield_value(t)/Ds),('left',( (1+sphi)*(t[0]+t[1])/2-(1-sphi)*t[2]-h)/Dl),('right',((1+sphi)*t[0]-(1-sphi)*(t[1]+t[2])/2-h)/Dr),('apex',(F(2,3)*sphi*sum(t)-h)/Da)]
 accepted=[]
 for branch,l in roots:
  valid=l>0 and {'face':l<min(gsl,gsr),'left':gsl<=l<gla,'right':gsr<=l<gra,'apex':l>=max(gla,gra)}[branch]
  if not valid:continue
  if branch=='face':r=tuple(t[i]-l*(A+(2*G*(1+spsi) if i==0 else -2*G*(1-spsi) if i==2 else 0)) for i in range(3))
  elif branch=='left':r=((t[0]+t[1])/2-l*(A+G*(1+spsi)),)*2+(t[2]-l*(A-2*G*(1-spsi)),)
  elif branch=='right':r=(t[0]-l*(A+2*G*(1+spsi)),)+((t[1]+t[2])/2-l*(A-G*(1-spsi)),)*2
  else:r=(sum(t)/3-l*2*K*spsi,)*3
  assert r[0]>=r[1]>=r[2] and yield_value(r)==0
  accepted.append((branch,l,r))
 assert len(accepted)==1,accepted
 return accepted[0]

def matrix(v,Q):return [[sum(Q[i][k]*v[k]*Q[j][k] for k in range(3)) for j in range(3)] for i in range(3)]
def encoded(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,(list,tuple)):return [encoded(v) for v in x]
 if isinstance(x,dict):return {k:encoded(v) for k,v in x.items()}
 return x

def check():
 z=F(0);l=F(1,4);p=h/(2*sphi)
 # Expected return states and subgradients chosen analytically BEFORE trial construction.
 cases=[('face',(F(5),F(1),z),(1+spsi,z,-1+spsi),l,'face'),('left',(F(5),F(5),z),(F(5,6),F(1,2),-1+spsi),l,'left'),('right',(F(5),z,z),(1+spsi,F(-1,6),F(-1,2)),l,'right'),('apex_interior',(p,p,p),(F(1),F(0),F(-1,3)),l,'apex'),('left_repeated_trial',(F(5),F(5),z),(F(2,3),F(2,3),F(-2,3)),l,'left'),('right_repeated_trial',(F(5),z,z),(F(4,3),F(-1,3),F(-1,3)),l,'right'),('hydrostatic_apex',(p,p,p),(F(2,9),)*3,F(3),'apex'),('face_to_left_boundary',(F(5),F(5),z),(1+spsi,z,-1+spsi),l,'left'),('face_to_right_boundary',(F(5),z,z),(1+spsi,z,-1+spsi),l,'right'),('left_to_apex_boundary',(p,p,p),(F(2,3),F(2,3),F(-2,3)),l,'apex'),('right_to_apex_boundary',(p,p,p),(F(4,3),F(-1,3),F(-1,3)),l,'apex')]
 Q=[[F(3,5),F(-4,5),z],[F(4,5),F(3,5),z],[z,z,F(1)]]
 rows=[]
 for name,r,nu,gamma,branch in cases:
  assert yield_value(r)==0 and 1+spsi>=nu[0]>=nu[1]>=nu[2]>=-1+spsi and sum(nu)==2*spsi
  assert (nu[0]-1-spsi)*(r[0]-r[1])==0
  assert (nu[2]+1-spsi)*(r[1]-r[2])==0
  cn=elastic(nu);trial=tuple(x+gamma*d for x,d in zip(r,cn))
  actual=mapped(trial);assert actual==(branch,gamma,r),(name,actual)
  de=compliance(trial);ep=tuple(gamma*x for x in nu)
  assert elastic(tuple(a-b for a,b in zip(de,ep)))==r
  # Orthogonal Cartesian rotation and compression sign conversion preserve the constitutive relation exactly.
  rt=matrix(tuple(-x for x in r),Q);tt=matrix(tuple(-x for x in trial),Q)
  epm=matrix(tuple(-x for x in ep),Q);dem=matrix(tuple(-x for x in de),Q)
  tr=sum(dem[i][i]-epm[i][i] for i in range(3))
  assert all(2*G*(dem[i][j]-epm[i][j])+(K-F(2,3)*G)*tr*(i==j)==rt[i][j] for i in range(3) for j in range(3))
  rows.append({'case':name,'branch':branch,'source_tension_principal_trial':trial,'source_tension_return':r,'gamma':gamma,'source_subgradient':nu,'compression_cartesian_trial':tt,'compression_cartesian_return':rt,'compression_cartesian_increment':dem,'compression_cartesian_plastic_increment':epm})
 for name,trial in [('elastic_zero',(z,z,z)),('elastic_compression',(-F(10),)*3),('elastic_yield_hold',(F(5),F(1),z))]:
  assert mapped(trial)==('elastic',z,trial);rows.append({'case':name,'branch':'elastic','trial':trial,'return':trial,'gamma':z})
 # Interior smooth face principal tangent, checked with exact finite differences within same branch.
 face=rows[0];t=face['source_tension_principal_trial'];v=(F(1),F(2),F(3));dt=F(1,1000)
 dgamma=((1+sphi)*v[0]-(1-sphi)*v[2])/Ds;flow=elastic((1+spsi,z,-1+spsi))
 derivative=tuple(v[i]-flow[i]*dgamma for i in range(3));plus=mapped(tuple(t[i]+dt*v[i] for i in range(3)));minus=mapped(tuple(t[i]-dt*v[i] for i in range(3)))
 assert plus[0]==minus[0]=='face' and tuple((plus[2][i]-minus[2][i])/(2*dt) for i in range(3))==derivative
 # Interior apex response is constant for H=0: exact zero stress tangent within its branch.
 t=rows[3]['source_tension_principal_trial']
 assert mapped(tuple(t[i]+dt*v[i] for i in range(3)))[2]==mapped(tuple(t[i]-dt*v[i] for i in range(3)))[2]==(p,p,p)
 return encoded({'identity':'MC nonassociated H=0 exact rational constitutive certificates v1','parameters':{'K':K,'G':G,'E':F(9,4),'nu':F(1,8),'sin_phi':sphi,'cos_phi':cphi,'sin_psi':spsi,'c':cohesion},'certificates':rows,'certificate_count':len(rows),'additional_checks':['exact rotated Cartesian constitutive residuals for11 plastic cases','smooth face principal tangent exact centered difference','interior perfect-plastic apex zero tangent'],'failed':0,'limits':['No Atlas imports or author code','No floating spectral decomposition tested','No complete tensor tangent or AD38-column verification','Constructed analytical certificates, not experimental validation or compiled output']})
if __name__=='__main__':print(json.dumps(check(),indent=2,sort_keys=True))
