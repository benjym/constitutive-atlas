"""Read-only supplementary probes; import installed Python operator, no native."""
import math,random,unittest
from atlas.symmetric_expm import symmetric_expm
from tools.reference_symmetric_expm import oracle

class SupplementaryExpm(unittest.TestCase):
 def test_signed_zero_small_norm_and_subnormal_are_finite(self):
  for j in range(6):
   for value in (0.,-0.,math.ulp(0.),-math.ulp(0.),1e-300,-1e-300,1e-16,-1e-16):
    v=[0.]*6;v[j]=value;a=symmetric_expm(v)
    self.assertTrue(all(math.isfinite(x)for x in a))
    target=[float(x)for x in oracle(v,100)['value']]
    self.assertLessEqual(max(abs(x-y)for x,y in zip(a,target)),4*math.ulp(1.))
 def test_support_is_computed_hypot_not_exact_decimal(self):
  v=[-40.29124936290316,-.4064675048402311,-1.8251977454570099,40.12517679158712,16.072818492774548,24.510270403976502]
  for values in (v,v[::-1],v[2:]+v[:2]):
   norm=0.
   for x in values:norm=math.hypot(norm,x)
   if norm>64:
    with self.assertRaises(ValueError):symmetric_expm(values)
   else:self.assertTrue(all(math.isfinite(x)for x in symmetric_expm(values)))
 def test_all_components_nonfinite_and_single_axis_support_neighbors(self):
  for j in range(6):
   for value in (math.nan,math.inf,-math.inf,math.nextafter(64.,math.inf),-math.nextafter(64.,math.inf)):
    v=[0.]*6;v[j]=value
    with self.assertRaises(ValueError):symmetric_expm(v)
   for value in (64.,-64.,math.nextafter(64.,0.),math.nextafter(-64.,0.)):
    v=[0.]*6;v[j]=value
    self.assertTrue(all(math.isfinite(x)for x in symmetric_expm(v)))
 def test_deterministic_large_matrix_sample(self):
  rng=random.Random(1993)
  for _ in range(80):
   v=[rng.uniform(-1,1)for _ in range(6)];v=[x*63/math.hypot(*v)for x in v]
   a=symmetric_expm(v);target=[float(x)for x in oracle(v,100)['value']]
   self.assertLessEqual(max(abs(x-y)for x,y in zip(a,target))/max(1.,math.hypot(*target)),2e-13)

if __name__=='__main__':unittest.main()
