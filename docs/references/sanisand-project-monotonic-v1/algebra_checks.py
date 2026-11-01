"""Independent triaxial and Cartesian rotation challenges for the new oracle."""
from decimal import Decimal as D,localcontext
from pathlib import Path
import importlib.util,json
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('new_reference',P/'reference.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def verify():
 checks=0;worst=D(0)
 with localcontext()as ctx:
  ctx.prec=70;k=m.parameters(json.loads((P/'inputs.json').read_text())['parameters']);e=D('.735');p=D(100000)
  G=D(125)*100000*(D('2.97')-e)**2/(1+e);K=2*(1+D('.05'))/(3*(1-2*D('.05')))*G
  def compare(actual,expected):
   nonlocal checks,worst
   for x,y in zip(actual,expected):
    error=abs(x-y)/max(D(1),abs(y));worst=max(worst,error);assert error<D('1e-55'),(x,y,error);checks+=1
  def state(sign,a):
   q=sign*(k['m']+a)*p;al=sign*a
   return [p+2*q/3,D(0),D(0),D(0),p-q/3,D(0),D(0),D(0),p-q/3]+[2*al/3,D(0),D(0),D(0),-al/3,D(0),D(0),D(0),-al/3]+[D(0)]*9
  for sign in [D(1),D(-1)]:
   v=[sign,D(0),D(0),D(0),-sign/2,D(0),D(0),D(0),-sign/2]
   for a in [D('.2'),D('.9')]:
    y=state(sign,a);actual=m.rates(y,v,e,k);g=D(1)if sign>0 else k['c'];psi=e-k['e0']+k['lambda_c']
    Mb=g*k['M']*(-k['nb']*psi).exp();Md=g*k['M']*(k['nd']*psi).exp()
    b0=k['G0']*k['h0']*(1-k['ch']*e);H=b0/a*(Mb-k['m']-a);dil=k['A0']*(Md-k['m']-a)
    plastic=3*G/(p*H+3*G-(k['m']+a)*K*dil)
    assert plastic>0
    qdot=sign*3*G*(1-plastic);pdot=-K*dil*plastic;adot=sign*H*plastic
    expected_s=[pdot+2*qdot/3,D(0),D(0),D(0),pdot-qdot/3,D(0),D(0),D(0),pdot-qdot/3]
    expected_a=[2*adot/3,D(0),D(0),D(0),-adot/3,D(0),D(0),D(0),-adot/3]
    compare(actual[:18],expected_s+expected_a)
  # Proper exact-rational rotations challenge matrix square/cube and all tensors.
  def rotate(a,Q):return [sum((Q[3*i+k]*a[3*k+l]*Q[3*j+l]for k in range(3)for l in range(3)),D(0))for i in range(3)for j in range(3)]
  Q=[D('.6'),D('-.8'),D(0),D('.8'),D('.6'),D(0),D(0),D(0),D(1)]
  y=state(D(1),D('.2'));v=list(map(D,['.2','.6','-.3','.6','-.1','.2','-.3','.2','-.1']))
  actual=m.rates(y,v,e,k);rotated=m.rates(rotate(y[:9],Q)+rotate(y[9:18],Q)+rotate(y[18:],Q),rotate(v,Q),e,k)
  compare(rotated,rotate(actual[:9],Q)+rotate(actual[9:18],Q)+rotate(actual[18:],Q))
  for sign in [D(1),D(-1)]:
   v=[sign,D(0),D(0),D(0),-sign/2,D(0),D(0),D(0),-sign/2];y=state(sign,D(0));actual=m.rates(y,v,e,k)
   compare(actual[:9],[2*G*x for x in v]);compare(actual[18:],[D(0)]*9)
   adot=sign*3*G/p;compare(actual[9:18],[2*adot/3,D(0),D(0),D(0),-adot/3,D(0),D(0),D(0),-adot/3])
 return {'checks':checks,'maximum_relative_or_unit_error':str(worst),'gate':'1e-55','source_reductions':'Appendix28–30; regular zero-distance limit; exact-rational proper rotation','compiled_calls':0,'scientific_signature':None}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
