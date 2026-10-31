"""Independent exact-rational boundary witness; no model/author imports or solver calls."""
from fractions import Fraction as F
import json
from pathlib import Path

def assess():
    # All three rheology constants are one. pc=phi=1, M=1, omega=1/3.
    K,G,ev,es,phi,M,omega = F(3,4),F(1),F(1),F(1,2),F(1),F(1),F(1,3)
    pe=phi**6*(K*ev**2+3*G*es**2)/2
    qe=3*G*phi**6*ev*es
    a=F(1); b=-a*qe/(M*M*pe); c=1/(M*omega)+a/(M*M)
    transport_det=a*c-b*b
    h11,h12,h22=phi**6*K*ev,phi**6*3*G*es,phi**6*3*G*ev
    elastic_det=h11*h22-h12*h12
    checks={
      'elastic_stress_exact':pe==F(3,4) and qe==F(3,2),
      'transport_matrix_exact':(a,b,c)==(F(1),F(-2),F(4)),
      'transport_determinant_zero':transport_det==0,
      'elastic_hessian_determinant_zero':elastic_det==0,
      'atlas_nonstrict_elastic_domain_accepts':K*ev*ev>=3*G*es*es,
      'atlas_nonstrict_transport_domain_accepts':transport_det>=0,
      'atlas_nonstrict_global_order_accepts':M*M<=3*G/K<=M*M*(1+M/omega),
      'author_negative_only_guard_does_not_reject_equality':not transport_det<0,
      'strict_transport_policy_would_reject':not transport_det>0,
      'strict_elastic_policy_would_reject':not elastic_det>0,
    }
    if not all(checks.values()):raise AssertionError(checks)
    return {'version':'terracotta-journal-followup-boundary-witness-v1','checks':checks,'count':len(checks),'status':'pass','exact_witness':{'K':'3/4','G':'1','ev_e':'1','es_e':'1/2','phi':'1','Tm':'0','alpha':'1','gamma':'1','eta':'1','M':'1','omega':'1/3','pc':'1','pe':str(pe),'qe':str(qe)},'scope':'Algebraic exposure of current nonstrict boundary policy; not a source admissibility decision or numerical integration test.'}
if __name__=='__main__':
    result=assess()
    print(json.dumps(result,indent=2))
