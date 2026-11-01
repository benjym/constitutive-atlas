"""Exact-root scalar BE counterexample to event guarantees from step doubling.
No Atlas imports or compiled calls. Constants are Table1 elastic exponents.
"""
import math,json
from pathlib import Path

def root(parent,coefficient,n):
 lo,hi=0.,parent
 for _ in range(160):
  mid=(lo+hi)/2
  if mid+coefficient*mid**n>parent:hi=mid
  else:lo=mid
 return (lo+hi)/2

def factors(t,n):
 full=root(1.,t,n);half=root(1.,t/2,n);two=root(half,t/2,n)
 return full,half,two

rows=[]
for n in [.8,.86]:
 for tolerance in [.01,.001,.0001]:
  # Use the conservative smaller-endpoint denominator. A larger denominator
  # only permits larger t and cannot remove this counterexample.
  lo,hi=1e-8,1.
  for _ in range(100):
   t=(lo+hi)/2;full,half,two=factors(t,n)
   error=abs(full-two)/min(full,two)
   if error>tolerance:hi=t
   else:lo=t
  t=lo;full,half,b=factors(t,n);error=abs(full-b)/min(full,b)
  # Each accepted macro increment L=t*u_parent^(1-n)/Kur.
  # Parent u rescales by b. Infinite geometric sum delays extinction.
  ratio=(1-n)*t/(1-b**(1-n))
  assert error<=tolerance*(1+1e-10) and ratio>1
  # Choose a target strictly past the source event but before delayed
  # numerical extinction. A finite number of accepted macrosteps exceeds it.
  target=(1+ratio)/2
  N=math.ceil(math.log(1-target/ratio)/math.log(b**(1-n)))
  reached=ratio*(1-b**((1-n)*N))
  assert N>0 and reached>1 and reached>=target
  rows.append({'n':n,'tolerance':tolerance,'dimensionless_macro_step':t,
    'full_factor':full,'first_half_factor':half,'two_half_factor':b,
    'relative_step_doubling_error':error,'positive_BE_lifetime_over_source_lifetime':ratio,
    'finite_accepted_macrosteps':N,'accumulated_strain_over_source_critical_strain':reached,
    'final_pressure_over_initial':b**N})
result={'id':'REVIEW-lade-domain-control-v1-exact-root-extinction-witness','rows':rows,
 'conclusion':'Fixed nonzero relative step-doubling tolerance permits finite exact-root positive-pressure paths past the differential source event. No nonlinear residual error is needed.',
 'limits':['Hydrostatic source witness only','Not a compiled controller simulation','Does not assert a proposed stricter monitor fails before its exact definition exists']}
Path(__file__).with_name('extinction-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
