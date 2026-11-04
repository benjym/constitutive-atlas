"""Cartesian source diagnostics only: no Atlas, native/Wasm or material AD."""
import copy,json,math,pathlib,unittest
from tools import reference_clay2014_cartesian as r
class Reference(unittest.TestCase):
 def test_literal_four_index_matches_independent_matrix_action(self):
  c=r.default_parameters();n=[1/3,2/3,2/3];P=r.plane(n);a,_,_=r.coefficients(c['nu_pp'],c['alpha_G'],c['alpha_E'],c['alpha_nu']);E=r.from_mandel([.2,-.4,.5,.3,-.1,.2]);L=r.stiffness(a,P);four=r._contract(L,E);tr=r._trace(E);pd=r._multiply(P,E);dp=r._multiply(E,P);q=math.fsum(P[i][j]*E[i][j]for i in range(3)for j in range(3));I=[[float(i==j)for j in range(3)]for i in range(3)]
  matrix=[[a[0]*E[i][j]+a[1]*I[i][j]*tr+a[2]*(P[i][j]*tr+I[i][j]*q)+a[3]*(pd[i][j]+dp[i][j])+a[4]*P[i][j]*q for j in range(3)]for i in range(3)]
  self.assertLess(max(abs(x-y)for u,v in zip(matrix,four)for x,y in zip(u,v)),2e-15)
 def test_printed_Am_conflict_preserved(self):
  a,printed,trace=r.coefficients(.1,2.,2.**1.25,2.)
  self.assertAlmostEqual(printed,6.6609096228707845);self.assertAlmostEqual(trace,6.74576243661317);self.assertGreater(abs(printed-trace),.08)
  _,p,t=r.coefficients(.1,1.,1.,1.);self.assertAlmostEqual(p,t)
 def test_isotropic_scaled_linear_limit(self):
  nu=.1;p=323000.;la=.095;ka=.015;a,Am,_=r.coefficients(nu,1.,1.,1.);E=r.from_mandel([.2,-.4,.5,.3,-.1,.2]);L=r.stiffness(a,r.plane([1/3,2/3,2/3]));action=r._contract(L,E);fs=9*p/(2*Am)*(1/la+1/ka);old=1.5*p*(1/la+1/ka)*(1-2*nu)/(1+nu);tr=r._trace(E)
  for i in range(3):
   for j in range(3):self.assertLessEqual(abs(fs*action[i][j]-old*(E[i][j]+nu/(1-2*nu)*float(i==j)*tr)),2e-12*max(1,abs(fs*action[i][j])))
 def test_full_isotropic_pressure_scalar_both_signs(self):
  p=r.default_parameters()|dict(alpha_G=1.,alpha_E=1.,alpha_nu=1.);e=.65;pressure=1e5
  for v in(-.003,.003):
   case=dict(parameters=p,state=[pressure]*3+[0.]*3+[e],increment=[v/3]*3+[0.]*3);a=r.evaluate(case);d=a['diagnostics'];ratio=(pressure/d['pe'])**d['alpha_f'];want=pressure/2*((1/p['lambda_star']+1/p['kappa_star'])*v+ratio*(1/p['lambda_star']-1/p['kappa_star'])*abs(v))
   for x in a['expected'][:3]:self.assertLessEqual(abs(x-want),r.POLICY['stress_absolute_floor_Pa']+r.POLICY['stress_scaled_bound']*a['stress_scale'])
 def test_pure_shears_ratio(self):
  cases={c['id']:r.evaluate(c)for c in r.cases()if c['id'].startswith('canonical-')};self.assertAlmostEqual(cases['canonical-xy']['expected'][3]/cases['canonical-yz']['expected'][4],2.);self.assertAlmostEqual(cases['canonical-yz']['expected'][4],cases['canonical-xz']['expected'][5])
 def test_axis_sign_unchanged(self):
  cases={c['id']:r.evaluate(c)['expected']for c in r.cases()}
  for key,value in cases.items():
   if key.startswith('oblique-'):self.assertEqual(value,cases['negative-'+key])
 def test_full_rotation_covariance(self):
  cs={c['id']:c for c in r.cases()};a=r.evaluate(cs['oblique-p1.0-mixed']);b=r.evaluate(cs['rotated-oblique-mixed']);q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]];want=r.to_mandel(r.rotate(r.from_mandel(a['expected'][:6]),q));error=math.hypot(*(x-y for x,y in zip(want,b['expected'][:6])));self.assertLessEqual(error,2e-12*a['stress_scale']+1e-10);self.assertLessEqual(abs(a['expected'][6]-b['expected'][6]),1e-15)
 def test_zero_all_seven_exact(self):
  for c in r.cases():
   if c['increment']==[0.]*6:self.assertEqual(r.evaluate(c)['expected'],[0.]*7)
 def test_loading_homogeneity_and_nonoddness(self):
  c=r.cases()[0];a=r.evaluate(c);b=r.evaluate(c|dict(increment=[2*x for x in c['increment']]));rev=r.evaluate(c|dict(increment=[-x for x in c['increment']]))
  for x,y in zip(a['expected'],b['expected']):self.assertAlmostEqual(2*x,y,delta=2e-12*max(1,abs(y)))
  self.assertGreater(math.hypot(*(x+y for x,y in zip(a['expected'][:6],rev['expected'][:6]))),1.)
 def test_all_declared_invalids_reject_without_mutation(self):
  for c in r.invalid_cases():
   before=copy.deepcopy(c)
   with self.assertRaises(ValueError,msg=c['id']):r.evaluate(c)
   self.assertEqual(c,before)
 def test_finite_shape_boolean_and_axis_policy(self):
  c=r.cases()[0]
  for key,value in [('state',[True]+c['state'][1:]),('increment',[float('nan')]+c['increment'][1:]),('state',c['state'][:-1])]:
   with self.assertRaises(ValueError):r.evaluate(c|{key:value})
  with self.assertRaises(ValueError):r.plane([0.,0.,1.+1e-10])
  n=[1/3,2/3,2/3];P=r.plane(n);self.assertEqual(P[0][0],n[0]*n[0])
 def test_full_frozen_reference_replays(self):
  p=pathlib.Path(r.__file__).parents[1]/'catalogue/investigations/clay2014-rates-v1/reference.json';self.assertTrue(p.is_file());self.assertEqual(json.loads(p.read_text()),r.build_reference())
if __name__=='__main__':unittest.main()
