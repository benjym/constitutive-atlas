#!/usr/bin/env python3
"""Small exact source identities and applicability witnesses; no Atlas imports."""
from fractions import Fraction as Q
import json, math

def tr(A): return sum(A[i][i] for i in range(3))
def mm(A,B): return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)) for i in range(3))
def dot(A,B): return sum(A[i][j]*B[i][j] for i in range(3) for j in range(3))
def scale(A,s): return tuple(tuple(x*s for x in r) for r in A)
def add(A,B): return tuple(tuple(A[i][j]+B[i][j] for j in range(3)) for i in range(3))
I=tuple(tuple(Q(i==j) for j in range(3)) for i in range(3))
rows=[]; witnesses=[]
def check(n,b): rows.append({'id':n,'pass':bool(b)})
# C=-1/+1 axisymmetric cases, represented by x=u/sqrt2 to avoid irrational arithmetic.
for name,s,x,C,want in [('compression',(4,1,1),Q(1,2),-1,Q(1)),('extension',(1,4,4),Q(1,3),1,Q(2,3)),('mixed-sign-within-shape-range',(-1,3,3),Q(4,5),1,Q(1,5)),('parent-wider-continuation',(6,-1,-1),Q(7,4),-1,Q(1))]:
 A=tuple(Q(v,sum(s)) for v in s); B=tuple(v-Q(1,3) for v in A)
 j=sum(v*v for v in B); cube=sum(v**3 for v in B)
 check(name+'-u-squared',3*j==2*x*x)
 check(name+'-cosine-sign-and-square',6*cube*cube==j**3 and (-1 if cube>0 else 1)==C)
 rad=x*x/4+(1-x*x)/(1+x*C)
 check(name+'-shape-square-identity',rad==(want+x/2)**2 and want+x/2>0)
 witnesses.append({'id':name,'principal_stress_ratios':[str(Q(v)) for v in s],'normalized':[str(v) for v in A],'j2':str(j),'u_squared':str(3*j),'cos3theta':C,'F':str(want),'all_compressive':all(v>0 for v in s),'inside_stated_u_range':0<3*j<2})
check('exact-isotropic-F-one',Q(0)/8+Q(2)/2==1)
# At C=0 below the small-invariant switch, exact shape squared differs from the
# triaxial-compression continuation1 for every finite x>0; no tolerance gate.
x=Q(1,10**13)
check('near-isotropic-switch-active',Q(2,3)*x*x<Q(1,10**24))
check('threshold-is-not-exact-triaxial-F',1-Q(3,4)*x*x != (1+x/2)**2)
# C9 fundamental invariant equality on one non-axisymmetric compressive state.
a=(Q(1,2),Q(1,3),Q(1,6)); b=tuple(v-Q(1,3) for v in a)
j=sum(v*v for v in b); cube=sum(v**3 for v in b); u2=3*j
# sqrt2*u*C = -6*tr(B^3)/j, so no square roots remain in C9.
mixed=-6*cube/j
pairs=a[0]*a[1]+a[1]*a[2]+a[2]*a[0]; det=a[0]*a[1]*a[2]
f1=1-9*det/pairs
check('C9-fundamental-vs-deviatoric-invariants',f1==u2*(2+mixed)/(2-u2))
# AppendixA rank-one inverse, and AppendixB B3=-B2 reduction.
A=((Q(1,2),Q(1,20),Q(0)),(Q(1,20),Q(1,3),Q(1,30)),(Q(0),Q(1,30),Q(1,6)))
B=add(A,scale(I,-Q(1,3)));d=((Q(2),Q(3),Q(-1)),(Q(3),Q(0),Q(2)),(Q(-1),Q(2),Q(-3)))
k=Q(7,3)
Ld=add(d,scale(A,k*dot(A,d))); inverse=add(Ld,scale(A,-k*dot(A,Ld)/(1+k*dot(A,A))))
check('AppendixA-rank-one-inverse',inverse==d)
check('AppendixB-tensor-reduction',add(mm(A,A),scale(mm(B,B),-1))==scale(add(A,B),Q(1,3)))
# Source compression conversion: normalized stress invariant, linear odd, norm even.
T=scale(A,-9); sigma=scale(T,-1)
check('normalized-stress-invariant-under-sign',scale(T,1/tr(T))==scale(sigma,1/tr(sigma)))
check('Mandel-norm-isometry',dot(d,d)==sum(d[i][i]**2 for i in range(3))+2*(d[0][1]**2+d[1][2]**2+d[0][2]**2))
D=scale(d,-1)
check('linear-odd-nonlinear-norm-even',add(D,scale(A,dot(A,D)))==scale(add(d,scale(A,dot(A,d))),-1) and dot(D,D)==dot(d,d))
e,ed,ec,ei=Q(7,10),Q(1,2),Q(4,5),Q(1)
check('critical-density-factors-one',(ec-ed)/(ec-ed)==1 and ec/ec==1)
check('dense-limit-nonlinear-zero',(ed-ed)/(ec-ed)==0)
check('source-voidrate-compression-sign',-(1+e)*tr(d)==(1+e)*tr(D))
check('zero-loading-frozen-state',dot(scale(d,0),scale(d,0))==0 and tr(scale(d,0))==0)
# Witness evaluations use source formulas only and literal current defaults, not
# an import or call to the DSL, compiler, integration or domain helper.
phi=math.pi/6;hs=5.8e9;n=.28;alpha=.13;beta=1.05;ed0=.53;ec0=.84;ei0=1.
a=math.sqrt(3)*(3-math.sin(phi))/(2*math.sqrt(2)*math.sin(phi))
den=3+a*a-a*math.sqrt(3)*((ei0-ed0)/(ec0-ed0))**alpha
for name,s,p,Fvalue in [('mixed-sign-within-shape-range',[-1e5,3e5,3e5],5e5/3,.2),('parent-wider-continuation',[450000.,-75000.,-75000.],1e5,1.)]:
 c=math.exp(-(3*p/hs)**n); lo=ed0*c;hi=ei0*c
 fb=hs/n*(ei0/ec0)**beta*(1+hi)/hi*(3*p/hs)**(1-n)/den
 checks=[.7>0,p>1e5*1e-8,ed0<ec0,ec0<ei0,.7>lo,.7<hi,Fvalue>0,fb>0]
 check(name+'-literal-root-guards-all-satisfied',all(checks))
 w=next(w for w in witnesses if w['id']==name);w.update({'sigma_Pa':s,'mean_Pa':p,'void_ratio':.7,'ed':lo,'ei':hi,'fb_Pa':fb,'eight_literal_guards':checks,'note':'Source-only evaluation of literal guards; no candidate domain or model execution.'})
report={'task':'AUDIT-vw96-original-equations-v2','status':'pass' if all(r['pass'] for r in rows) else 'fail','checks':rows,'count':len(rows),'witnesses':witnesses,'scope':'illustrative exact algebra plus two source-only finite guard witnesses; no corpus or numerical trajectory evidence'}
if __name__=='__main__':
 print(json.dumps(report,indent=2))
 if report['status']!='pass':raise SystemExit(1)
