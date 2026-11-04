"""Independent manuscript arithmetic witness; neither correction nor material model."""
import math,unittest,json

def witness(g=2.,r=2.**1.25,v=2.,nu=.1):
 B=1-nu-2*r*nu*nu/(v*v)
 a=[r*B,r*nu*(1+r*nu/(v*v)),r*nu*(1/v+nu/v-1-r*nu/(v*v)),r*B*(1-g)/g,r*(1-r*nu*nu/(v*v))+1-nu*nu-2*r*nu*(1+nu)/v-2*r*B/g]
 # Normal n=e3, X=I. Independent Cartesian action from Eqs2-3.
 P=[[float(i==2 and j==2)for j in range(3)]for i in range(3)]
 I=[[float(i==j)for j in range(3)]for i in range(3)]
 LI=[[a[0]*I[i][j]+3*a[1]*I[i][j]+a[2]*(3*P[i][j]+I[i][j])+2*a[3]*P[i][j]+a[4]*P[i][j]for j in range(3)]for i in range(3)]
 trace=sum(LI[i][i]for i in range(3))
 Am=nu*nu*(4*r/v-2*r*r+2*r*r/(v*v)-1)+nu*(4*r/v+2*r)+2*r+1
 expected=2*r*r*nu*nu*(1-1/(v*v))
 return {'alpha_G':g,'alpha_E':r,'alpha_nu':v,'nu_pp':nu,'coefficients':a,'L_I':LI,'trace_L_I':trace,'printed_Am':Am,'difference':trace-Am,'derived_difference':expected,'relative_unloading_coefficient':trace/Am,'scope':'printed expressions only; no source repair or integration'}
class PrintedWitness(unittest.TestCase):
 def test_discrepancy(self):
  d=witness();self.assertAlmostEqual(d['difference'],d['derived_difference'],places=13);self.assertGreater(abs(d['difference']),.08)
 def test_isotropic_limit_hides_discrepancy(self):
  d=witness(1,1,1,.1);self.assertAlmostEqual(d['difference'],0,places=13)
 def test_nu_zero_hides_discrepancy(self):self.assertAlmostEqual(witness(nu=0)['difference'],0,places=13)
 def test_v_one_hides_discrepancy(self):self.assertAlmostEqual(witness(v=1)['difference'],0,places=13)
if __name__=='__main__':unittest.main()
