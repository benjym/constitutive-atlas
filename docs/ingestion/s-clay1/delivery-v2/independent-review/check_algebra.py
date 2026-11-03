"""Independent exact arithmetic checks on author-slide yield identities only."""
from fractions import Fraction as R
import json

def dot(x,y):
    return sum(a*b for a,b in zip(x,y))
def tensor_yield(p,q,alpha,M,pm):
    # y axial, independently embed principal invariants in trace-free tensors.
    s=[-q/3,2*q/3,-q/3]
    a=[-alpha/3,2*alpha/3,-alpha/3]
    u=[si-p*ai for si,ai in zip(s,a)]
    return R(3,2)*dot(u,u)-(M*M-R(3,2)*dot(a,a))*(pm-p)*p
count=0
for p in [R(1),R(5,2),R(100)]:
 for q in [R(-7),R(0),R(11)]:
  for alpha in [R(-1,3),R(0),R(2,5)]:
   M,pm=R(6,5),R(170)
   expected=(q-alpha*p)**2-(M*M-alpha*alpha)*(pm-p)*p
   assert tensor_yield(p,q,alpha,M,pm)==expected
   count+=1
# Distinct stress and fabric fields: zero fabric is not invariant under rotation law.
eta=[R(-1,3),R(2,3),R(-1,3)]
mu,beta,depv,depd=R(3),R(2,5),R(1,10),R(1,5)
da=[mu*(R(3,4)*x*max(depv,0)+beta*x*depd/3) for x in eta]
assert sum(da)==0 and any(x!=0 for x in da)
count+=1
print(json.dumps({'ok':True,'exact_assertions':count,'scope':'slide yield triaxial reduction; trace-free rotation counterexample','original_journal_verified':False,'backend_or_solver_tests':False},indent=2))
