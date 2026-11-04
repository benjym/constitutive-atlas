import unittest
from decimal import Decimal as D,localcontext
from tools.reference_clay2013_isotropic import advance,path,state
P=dict(lambda_star='.12',kappa_star='.025',N='1.1')
class ClosedForm(unittest.TestCase):
 def close(self,a,b,tol=D('1e-75')):
  self.assertLessEqual(abs(a-b),tol*max(D(1),abs(a),abs(b)))
 def test_exact_density_surface_and_evolution(self):
  with localcontext() as c:
   c.prec=90;e=D('.8');pe=state(1,e,**P)['pe']
   r=advance(pe,e,'.01',**P)
   self.close(r['r'],D(1));self.close(r['p'],pe*(D('.01')/D(P['lambda_star'])).exp())
 def test_partition_for_densities_both_sides_and_both_signs(self):
  with localcontext() as c:
   c.prec=90
   for p in ('1','100','10000','100000000'):
    for sign in (1,-1):
     total=D('.03')*sign;a=advance(p,'.8',total,**P)
     b=path(p,'.8',[total/37]*37,**P)[-1]
     for k in ('p','e','pe','r'):self.close(a[k],b[k])
 def test_analytic_first_derivative(self):
  with localcontext() as c:
   c.prec=90;L=D(P['lambda_star']);K=D(P['kappa_star'])
   for p in ('10','100000'):
    a=state(p,'.8',**P)
    for sign in (1,-1):
     h=D('1e-28');b=advance(p,'.8',h*sign,**P)
     slope=a['p']/2*((1/L+1/K)*sign+(1/L-1/K)*a['r'])
     self.close((b['p']-a['p'])/h,slope,D('1e-22'))
     self.close((b['e']-a['e'])/h,-(1+a['e'])*sign,D('1e-24'))
 def test_reversal_not_reversible_and_zero(self):
  with localcontext() as c:
   c.prec=90;a=path('100','.8',['.02','-.02'],**P)[-1]
   self.close(a['e'],D('.8'));self.assertNotEqual(a['p'],D(100))
   b=advance('100','.8','0',**P);self.close(b['p'],D(100));self.close(b['e'],D('.8'))
 def test_domain_and_small_increment(self):
  for bad in [dict(p=0,e='.8'),dict(p=1,e='-.1')]:
   with self.assertRaises(ValueError):advance(**bad,dx='.01',**P)
  with self.assertRaises(ValueError):advance(1,'.1',1,**P)
  with localcontext() as c:
   c.prec=90;a=advance('1','.8','-1e-70',**P)
   self.assertTrue(a['p']>0);self.assertTrue(a['r']>0)
 def test_large_density_ratio_does_not_lose_exponential_product(self):
  with localcontext() as c:
   c.prec=90
   parameters=P|dict(kappa_star='.0001')
   a=advance('1e-1000','.8','.03',**parameters)
   initial=state('1e-1000','.8',**parameters)
   C=1/D(parameters['kappa_star'])-1/D(parameters['lambda_star'])
   expected=initial['p']*(D('.03')*(1/D(parameters['lambda_star'])+C/2)).exp()
   self.close(a['p']/expected,D(1))
 def test_precision_finite_inputs_and_binary64_identity(self):
  for precision in (True,0,31,1001,90.5):
   with self.assertRaises(ValueError):advance(1,'.8',0,precision=precision,**P)
  for invalid in (True,'NaN','Infinity'):
   with self.assertRaises(ValueError):advance(invalid,'.8',0,**P)
  self.assertEqual(advance(.1,.8,.01,**P),advance(D.from_float(.1),D.from_float(.8),D.from_float(.01),**P))
if __name__=='__main__':unittest.main()

