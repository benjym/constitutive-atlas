"""Exact source-geometry identities, not constitutive execution."""
from fractions import Fraction as Q
from pathlib import Path
import json,hashlib
OUT=Path(__file__).parent

def tensor_yield(p,q,pm,M,a):
 s=(-q/3,2*q/3,-q/3);A=(-a/3,2*a/3,-a/3)
 return Q(3,2)*sum((si-p*ai)**2 for si,ai in zip(s,A))-(M*M-Q(3,2)*sum(ai*ai for ai in A))*(pm-p)*p

def main():
 count=0;pm=Q(2);M=Q(5,4)
 for p in map(Q,[0,1,2,3,4]):
  for q in map(Q,[-2,-1,0,1,2]):
   for a in (Q(-3,4),Q(0),Q(3,4)):
    expanded=q*q-2*a*p*q+M*M*p*p-(M*M-a*a)*pm*p
    assert tensor_yield(p,q,pm,M,a)==expanded;count+=1
   assert tensor_yield(p,q,pm,M,Q(0))==q*q-M*M*(pm-p)*p;count+=1
 for p in (Q(0),pm):assert tensor_yield(p,Q(0),pm,M,Q(0))==0;count+=1
 p=pm/2;a=Q(3,4)
 for q in (a*p-p,a*p+p):assert tensor_yield(p,q,pm,M,a)==0;count+=1
 for a in (Q(-3,4),Q(0),Q(3,4)):
  A=(-a/3,2*a/3,-a/3);assert sum(A)==0;count+=1;assert Q(3,2)*sum(x*x for x in A)==a*a;count+=1
 assert count==110
 result={'result':'PASS','exact_rational_assertions':count,'constitutive_material_requests':0,'native_or_wasm_calls':0,'original_journal_equations_verified':False,'scope':'Presentation yield geometry, tensor-to-triaxial/isotropic reductions and fabric trace/invariant only','policy_sha256':hashlib.sha256((OUT/'ALGEBRA_POLICY.md').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (OUT/'algebra-result-v1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
