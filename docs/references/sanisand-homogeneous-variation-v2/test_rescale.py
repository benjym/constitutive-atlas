"""Algebraic tests of coordinate reconstruction, including independent RK checks."""
from decimal import Decimal as D,localcontext
import unittest
from generate import rescale,reconstructed,law

class RescaleTests(unittest.TestCase):
 def test_base_and_exact_reconstruction(self):
  with localcontext() as ctx:
   ctx.prec=80
   for values in [['1e49','-3.25e48','0'],['1e-50','2e-51','0'],['9.999e420','-8e419','1e-123']]:
    state=list(map(D,range(27)))+list(map(D,values));out,exponent=rescale(state,0)
    self.assertEqual(out[:27],state[:27]);self.assertEqual(reconstructed(out,exponent),state[27:]);self.assertEqual(state[:27],list(map(D,range(27))))
    self.assertTrue(D(1)<=max(abs(x) for x in out[27:])<D(10))
 def test_zero_variation(self):
  state=[D(0)]*30;self.assertEqual(rescale(state,12),(state,12))
 def test_signed_scaling_preserves_direction(self):
  state=[D(0)]*27+[D('-4e20'),D('2e20'),D(0)];out,e=rescale(state,19)
  self.assertEqual(reconstructed(out,e),[x.scaleb(19) for x in state[27:]])
 def test_linear_rhs_commutes_with_rescaling(self):
  with localcontext() as ctx:
   ctx.prec=90;m=[[D(3),D(1),D(-2)],[D(0),D(4),D(1)],[D(2),D(0),D(-1)]];y=[D(0)]*27+[D('2e40'),D('-3e40'),D('1e40')];scaled,e=rescale(y,0)
   fn=lambda v:[sum(m[i][j]*v[j] for j in range(3)) for i in range(3)]
   a=fn(y[27:]);b=[x.scaleb(e) for x in fn(scaled[27:])];self.assertEqual(a,b)
 def test_rk_reconstruction(self):
  with localcontext() as ctx:
   ctx.prec=90;v=[D('2e40'),D('-3e40'),D('1e40')];scaled,e=rescale([D(0)]*27+v,0)
   fn=lambda x:[x[0]+x[1],-2*x[1],x[0]-x[2]]
   high,low=law.law.rk(v,D('.001'),fn);hs,ls=law.law.rk(scaled[27:],D('.001'),fn)
   self.assertTrue(max(abs(x-y.scaleb(e))/D('1e40') for x,y in zip(high,hs))<D('1e-85'))
   self.assertTrue(max(abs(x-y.scaleb(e))/D('1e40') for x,y in zip(low,ls))<D('1e-85'))
if __name__=='__main__':unittest.main()
