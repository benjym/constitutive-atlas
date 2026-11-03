"""Exact original-law algebra; no material trajectories or implementation import."""
from fractions import Fraction as R
import json

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def dev(a):
 p=sum(a[:3])/3
 return [x-p if i<3 else x for i,x in enumerate(a)]
def yield_and_grad(sig,A,pm,M):
 p=sum(sig[:3])/3;s=dev(sig);a2=R(3,2)*dot(A,A)
 u=[x-p*a for x,a in zip(s,A)]
 f=R(3,2)*dot(u,u)-(M*M-a2)*(pm-p)*p
 fp=-3*dot(s,A)+2*M*M*p-(M*M-a2)*pm
 g=[3*x+(fp/3 if i<3 else 0) for i,x in enumerate(u)]
 return f,g
count=0
for sig in ([R(20),R(12),R(13),R(1),R(2),R(-1)], [R(9),R(9),R(9),R(0),R(0),R(0)]):
 for A in ([R(2,5),R(-1,5),R(-1,5),R(0),R(0),R(0)], [R(1,10),R(1,5),R(-3,10),R(1,20),R(0),R(-1,30)]):
  f,g=yield_and_grad(sig,A,R(30),R(11,10))
  for i in range(6):
   h=R(1,7);plus=list(sig);minus=list(sig);plus[i]+=h;minus[i]-=h
   df=(yield_and_grad(plus,A,R(30),R(11,10))[0]-yield_and_grad(minus,A,R(30),R(11,10))[0])/(2*h)
   assert df==g[i];count+=1
# Main-text Eq9 versus Appendix A12 in y-axis triaxial embedding, including
# extension shear and dry-side plastic dilation. A6 supplies |signed shear|.
for eta in [R(-4,5),R(0),R(3,5)]:
 for pv in [R(-1,10),R(0),R(1,10)]:
  for pd in [R(-1,5),R(0),R(1,5)]:
   a,mu,beta=R(2,5),R(20),R(2,3)
   scalar=mu*((3*eta/4-a)*max(pv,0)+beta*(eta/3-a)*abs(pd))
   tensor=[]
   for c in [R(-1,3),R(2,3),R(-1,3)]:
    tensor.append(mu*((R(3,4)*eta*c-a*c)*max(pv,0)+beta*(eta*c/3-a*c)*abs(pd)))
   assert tensor==[-scalar/3,2*scalar/3,-scalar/3];count+=1
# K0 recipe jointly satisfies associated plastic strain ratio and stationary rotation.
for eta,M in [(R(67,100),R(11,10)),(R(3,5),R(1))]:
 alpha=(eta*eta+3*eta-M*M)/3
 beta=3*(4*M*M-4*eta*eta-3*eta)/(8*(eta*eta-M*M+2*eta))
 assert 2*(eta-alpha)/(M*M-eta*eta)==R(2,3);count+=1
 assert (3*eta/4-alpha)+beta*(eta/3-alpha)*R(2,3)==0;count+=1
print(json.dumps({'ok':True,'exact_assertions':count,'scope':'dimensional constant-M yield stress gradient; Eq9/A12 axisymmetric rotation including dilation and extension; approximate-K0 recipe algebra','source_doi':'10.1139/T02-119','source_sha256':'1923aff43b80f14970dec624deb8f78b09635f419adbf71d797fa0a1a4169511','finite_material_trajectories':0,'compiled_calls':0,'e5_approval':False},indent=2))
