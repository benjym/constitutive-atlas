"""Independent source algebra diagnostics, not a model implementation/integration test."""
import json, math, pathlib, unittest
I=[[float(i==j) for j in range(3)] for i in range(3)]
def dot(a,b): return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
def mul(a,b): return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def coefficients(g,e,v,nu):
 b=1-nu-2*e/v**2*nu**2
 return [e*b,e*nu*(1+e/v**2*nu),e*nu*(1/v+nu/v-1-e/v**2*nu),e*b*(1-g)/g,e*(1-e/v**2*nu**2)+1-nu**2-2*e*nu*(1+nu)/v-2*e/g*b]
def action(a,n,d):
 p=[[x*y for y in n] for x in n];pd=mul(p,d);dp=mul(d,p);t=dot(I,d);q=dot(p,d)
 return [[a[0]*d[i][j]+a[1]*I[i][j]*t+a[2]*(p[i][j]*t+I[i][j]*q)+a[3]*(pd[i][j]+dp[i][j])+a[4]*p[i][j]*q for j in range(3)] for i in range(3)]
def four_index(a,n,d):
 p=[[x*y for y in n] for x in n]
 return [[sum((a[0]/2*(I[i][k]*I[j][l]+I[i][l]*I[j][k]+I[j][l]*I[i][k]+I[j][k]*I[i][l])/2+a[1]*I[i][j]*I[k][l]+a[2]*(p[i][j]*I[k][l]+I[i][j]*p[k][l])+a[3]/2*(p[i][k]*I[j][l]+p[i][l]*I[j][k]+p[j][l]*I[i][k]+p[j][k]*I[i][l])+a[4]*p[i][j]*p[k][l])*d[k][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
def close(a,b): return max(abs(a[i][j]-b[i][j]) for i in range(3) for j in range(3))
def rotate(q,a): return mul(mul(q,a),list(map(list,zip(*q))))
def diagnostics():
 nu=.1;g=2;e=g**1.25;v=g;a=coefficients(g,e,v,nu);n=[1/3,2/3,2/3];d=[[.2,.3,-.1],[.3,-.4,.2],[-.1,.2,.5]]
 x=action(a,n,d);y=four_index(a,n,d)
 sh=[[0,1,0],[1,0,0],[0,0,0]];sv=[[0,0,1],[0,0,0],[1,0,0]]
 hp=action(a,[0,0,1],sh)[0][1];ht=action(a,[0,0,1],sv)[0][2]
 iso=coefficients(1,1,1,nu);am=3*(1+nu)**2;p=323000.;lam=.095;kap=.015
 fs=9*p/(2*am)*(1/lam+1/kap)
 expected=[[1.5*p*(1/lam+1/kap)*(1-2*nu)/(1+nu)*(d[i][j]+nu/(1-2*nu)*I[i][j]*dot(I,d)) for j in range(3)] for i in range(3)]
 q=[[0,-1,0],[1,0,0],[0,0,1]];qn=[sum(q[i][j]*n[j] for j in range(3)) for i in range(3)]
 phi=math.radians(21.9);af=math.sqrt(3)*(3-math.sin(phi))/(2*math.sqrt(2)*math.sin(phi));alpha=math.log((lam-kap)/(lam+kap)*(3+af*af)/(af*math.sqrt(3)))/math.log(2)
 # Eq19/Eq17 inversion and pressure scaling (not native response).
 B=1-nu-2*e/v**2*nu**2
 Am=nu**2*(4*e/v-2*e**2+2*e**2/v**2-1)+nu*(4*e/v+2*e)+2*e+1
 Ag=270;ng=.7;pr=1000
 def mr(p):return pr*Ag*(p/pr)**ng*4*Am*g/(2*p*e)*(lam*kap/(lam+kap))/B
 G=mr(p)*9*p/(2*Am)*(1/lam+1/kap)*e/(2*g)*B
 return {'four_index_action_error':close(x,y),'shear_ratio':hp/ht,'expected_shear_ratio':g,'axis_reversal_error':close(x,action(a,[-z for z in n],d)),'covariance_error':close(rotate(q,x),action(a,qn,rotate(q,d))),'isotropic_fsL_error':close([[fs*z for z in r] for r in action(iso,n,d)],expected),'alpha_f_2014':alpha,'alpha_f_2013':2,'Gtp0_Pa':G,'Gtp0_expected_Pa':pr*Ag*(p/pr)**ng,'mR_double_pressure_ratio':mr(2*p)/mr(p),'mR_expected_ratio':2**(ng-1),'old_fd_at_ratio_half':.5**2,'new_fd_at_ratio_half':.5**alpha}
class Algebra(unittest.TestCase):
 def test_contractions(self): self.assertLess(diagnostics()['four_index_action_error'],1e-14)
 def test_plane_sign_covariance(self):
  d=diagnostics();self.assertLess(d['axis_reversal_error'],1e-14);self.assertLess(d['covariance_error'],1e-14)
 def test_shear_ratio(self): self.assertAlmostEqual(diagnostics()['shear_ratio'],2)
 def test_isotropic_limit(self): self.assertLess(diagnostics()['isotropic_fsL_error'],1e-7)
 def test_distinct_exponent(self): self.assertGreater(abs(diagnostics()['alpha_f_2014']-2),.1)
 def test_pressure_multiplier(self):
  d=diagnostics();self.assertAlmostEqual(d['Gtp0_Pa']/d['Gtp0_expected_Pa'],4.5);self.assertAlmostEqual(d['mR_double_pressure_ratio'],d['mR_expected_ratio'])
if __name__=='__main__':unittest.main()
