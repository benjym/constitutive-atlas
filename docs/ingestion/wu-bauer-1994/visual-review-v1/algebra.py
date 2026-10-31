"""Independent rational witnesses from visually transcribed Wu/Bauer1994 body/appendix.
Standard library only; no Atlas, retained helper, author code or integrator imports.
"""
from fractions import Fraction as F
from math import isqrt
import json
P=((0,0),(1,1),(2,2),(0,1),(0,2),(1,2));G=(1,1,1,2,2,2)
def mat(v):
 a=[[F(0)for j in range(3)]for i in range(3)]
 for x,(i,j)in zip(v,P):a[i][j]=a[j][i]=F(x)
 return a
def raw(a):return [a[i][j]for i,j in P]
def mm(a,b):return [[sum(a[i][k]*b[k][j]for k in range(3))for j in range(3)]for i in range(3)]
def body(s,d,c):
 a,b=mat(s),mat(d);t=sum(s[:3]);assert t
 dev=[[a[i][j]-(t/3 if i==j else 0)for j in range(3)]for i in range(3)];ss,dd=mm(a,a),mm(dev,dev);dot=sum(a[i][j]*b[i][j]for i in range(3)for j in range(3));ns=sum(x*x*g for x,g in zip(d,G));n=F(isqrt(ns.numerator),isqrt(ns.denominator));assert n*n==ns
 lin=raw([[c[0]*t*b[i][j]+c[1]*dot*a[i][j]/t for j in range(3)]for i in range(3)])
 non=raw([[(c[2]*ss[i][j]+c[3]*dd[i][j])*n/t for j in range(3)]for i in range(3)])
 return lin,non,[x+y for x,y in zip(lin,non)]
def serial(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:serial(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [serial(v)for v in x]
 return x
def run():
 s=list(map(F,[11,7,5,2,3,4]));c=list(map(F,[-2,-3,-5,7]));t=sum(s[:3]);a,b,z,u,v,w=s
 L=[[(c[0]*t if i==j else 0)+c[1]*s[i]*G[j]*s[j]/t for j in range(6)]for i in range(6)]
 printed15=2*c[1]*a*w/t;printed55=2*c[1]*v*a/t+c[0]*t
 assert printed15==F(-264,23)and L[0][4]==F(-198,23)
 assert printed55==F(-1256,23)and L[4][4]==F(-1112,23)
 assert L[0][3]==2*L[3][0]and L[0][3]!=L[3][0]
 for i in range(6):
  for j in range(6):assert G[i]*L[i][j]==G[j]*L[j][i]
 for j in range(6):
  d=[F(int(k==j))for k in range(6)]
  # unit raw shear has irrational norm, but the linear term is separately rational
  dot=G[j]*s[j]
  direct=raw([[c[0]*t*mat(d)[i][k]+c[1]*dot*mat(s)[i][k]/t for k in range(3)]for i in range(3)])
  assert direct==[L[i][j]for i in range(6)]
 x,y,z=a-t/3,b-t/3,z-t/3
 N=[-(c[2]*(a*a+u*u+v*v)+c[3]*(u*u+v*v+x*x))/t,
 -(c[2]*(u*u+b*b+w*w)+c[3]*(u*u+w*w+y*y))/t,
 -(c[2]*(v*v+w*w+(s[2])**2)+c[3]*(v*v+w*w+z*z))/t,
 -(c[2]*(a*u+u*b+v*w)+c[3]*(v*w+u*x+u*y))/t,
 -(c[2]*(a*v+u*w+v*s[2])+c[3]*(u*w+v*x+v*z))/t,
 -(c[2]*(u*v+b*w+w*s[2])+c[3]*(u*v+w*y+w*z))/t]
 d=list(map(F,[1,2,2,0,0,0]));lin,non,h=body(s,d,c);lm,nm,hm=body(s,[-q for q in d],c)
 assert lm==[-q for q in lin]and nm==non and hm!=[-q for q in h]
 assert non==[-3*q for q in N]
 assert body([-q for q in s],d,c)[2]==[-q for q in h]
 assert body(s,[F(0)]*6,c)[2]==[0]*6
 # Eq25 visually transcribed specialization vi=vf=0,Rf=3,Ei/sigma3=3.
 A=[[F(3),F(1,3),F(-1,3),F(0)],[F(0),F(-1),F(1),F(0)],[F(-25),F(-9),F(9),F(16,9)],[F(0),F(-3),F(1),F(4,9)]];rhs=[F(3),F(0),F(0),F(0)]
 literal=[F(1),F(25,8),F(-25,8),F(225,16)];candidate=[F(1),F(25,8),F(25,8),F(225,16)]
 residual=lambda co:[sum(x*y for x,y in zip(row,co))-r for row,r in zip(A,rhs)]
 assert residual(literal)==[F(25,12),F(-25,4),F(-225,4),F(-25,4)]and residual(candidate)==[0]*4
 return serial({'version':'wu-bauer-independent-visual-algebra-v1','all_assertions_passed':True,'L15':{'printed':printed15,'body':L[0][4]},'L55':{'printed':printed55,'body':L[4][4]},'raw_symmetry':{'L14':L[0][3],'L41':L[3][0],'metric_symmetry_entries':36,'body_basis_entries':36},'nonlinear_N_over_norm':N,'direction':d,'norm':3,'body_linear':lin,'body_nonlinear':non,'body_rate':h,'operational_mapped_rate':hm,'full_rate_negation_is_wrong':True,'zero_direction_rate':[0]*6,'calibration_literal':literal,'calibration_residual':residual(literal),'matrix_solution_candidate_not_adopted':candidate,'Rf3_printed_arcsin_argument':F(2),'reciprocal_geometric_candidate_not_adopted':F(1,2),'compiled_calls':0,'Atlas_imports':False,'scientific_admission':False})
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
