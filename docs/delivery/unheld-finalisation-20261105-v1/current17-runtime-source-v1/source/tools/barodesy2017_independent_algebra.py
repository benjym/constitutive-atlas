"""Independent scalar consistency checks; no full material evaluator/integrator."""
import hashlib,json,math
from pathlib import Path

def check():
 out=[]
 for name,phi,N,lam,kap in [('London',22.6,1.375,.11,.016),('Dresden',35,.622,.038,.008),('Weald',24,.8,.059,.018)]:
  s=math.sin(math.radians(phi));rt3=math.sqrt(3)
  c2=-1.5*(math.sqrt(2)+1);c1=(1-s)/(2*c2*c2*s);c5=(1+s)/(1-s)
  exponent=c5*lam
  c3=rt3*(1/kap-1/lam)/(math.exp(exponent*math.log(2))+math.exp(exponent*math.log(1/500))-2)
  beta=-1/(c3*lam)+math.expm1(exponent*math.log(2))/rt3
  slope=lambda pressure_factor:c3/rt3*(math.expm1(exponent*math.log(pressure_factor))-rt3*beta)
  K=1-1/(1+c1*(1.5-c2)**2)
  body,app=slope(2),slope(6)
  assert math.isclose(body,1/lam,rel_tol=1e-13)
  assert math.isclose(K,1-s,rel_tol=1e-13)
  assert not math.isclose(body,app,rel_tol=1e-6)
  out.append(dict(material=name,c3=c3,ncl_expected=1/lam,body_ncl_slope=body,appendix_ncl_slope=app,
                  oedometric_K=K,jaky_K0=1-s))
 return {'scope':'Independent scalar algebra only; source choice consistency, not material validation',
         'rows':out,'checks':9,'result':'pass'}

if __name__=='__main__':print(json.dumps(check(),indent=2,allow_nan=False))
