"""Run after conservative normalized-interior policy is installed.
Actual binary64 input Decimal Sylvester check; no eigensystem presumed exact.
"""
import math,unittest
from decimal import Decimal,localcontext
from tools import barodesy2017_rate_study as s

def decimal_spd(sig):
 with localcontext() as ctx:
  ctx.prec=100
  x,y,z,xy,yz,xz=map(Decimal.from_float,map(float,sig));rt2=Decimal(2).sqrt();xy/=rt2;yz/=rt2;xz/=rt2
  return x>0 and x*y-xy*xy>0 and x*y*z+2*xy*yz*xz-x*yz*yz-y*xz*xz-z*xy*xy>0
class Interior(unittest.TestCase):
 def call(self,sig):
  m,h=s.catalogue();p={n:f['default'] for n,f in m['parameters'].items()}
  return s.python_call({'model':m['id'],'parameters':list(p.values()),'state':sig+[.8],'increment':[.001,0,0,0,0,0]},m,h)
 def test_indefinite_cancellation_repro_rejected(self):
  sig=[9.348667422616327,1.9672983155680759,-3.9997926126179505e-17,0.,0.,0.]
  self.assertFalse(decimal_spd(sig));self.assertFalse(self.call(sig)['ok'])
 def test_conservative_boundary_and_interior_scaling(self):
  for scale in (1e-50,1.,1e50):
   for tiny,accepted in ((-1e-16,False),(0.,False),(1e-16,False),(1e-10,True)):
    sig=[scale,scale,scale*tiny,0.,0.,0.]
    if accepted:self.assertTrue(decimal_spd(sig))
    with self.subTest(scale=scale,tiny=tiny):self.assertIs(self.call(sig)['ok'],accepted)
 def test_oblique_actual_input_boundary(self):
  # Analytically Q diag(1,1,t) Q^T = I+(t-1)nn^T.
  # We assess the rounded input independently; nearzero t is not assumed exact.
  n=[1/3,2/3,2/3]
  for t in (-1e-16,1e-16,1e-10):
   a=[[float(i==j)+(t-1)*n[i]*n[j] for j in range(3)] for i in range(3)]
   sig=[a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]
   with self.subTest(t=t):
    if t==1e-10:self.assertTrue(decimal_spd(sig));self.assertTrue(self.call(sig)['ok'])
    else:self.assertFalse(self.call(sig)['ok'])
if __name__=='__main__':unittest.main()
