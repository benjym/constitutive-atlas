"""Independent finite-path reference tests; Python only, no subprocesses."""
import copy,math,unittest,json,hashlib
from pathlib import Path
from tools import barodesy2017_isotropic_reference as r
from tools import reference_barodesy2017 as cart
from atlas.model import ROOT,load,interpret

class IsotropicReference(unittest.TestCase):
 def test_ncl_identity_uses_p_not_critical_2p(self):
  for soil in r.SOILS:
   pars=r.parameters(soil);_,t,_=r.coefficients(pars)
   for p in r.PRESSURES:
    e=r.ncl_initial(soil,p)[6];self.assertLess(abs(r.ncl_residual([p]*3+[0.]*3+[e],pars)),2e-16)
    density=(1+e)/math.exp(pars['N']-pars['lambda_star']*math.log(2*p/1000))
    self.assertAlmostEqual(density,2**pars['lambda_star'],places=14)
    self.assertAlmostEqual(r.scalar_slope(p,e,pars,1),1/pars['lambda_star'],delta=2e-11)
    wrong_e=math.exp(pars['N']-pars['lambda_star']*math.log(2*p/1000))-1
    self.assertGreater(abs(r.scalar_slope(p,wrong_e,pars,1)-1/pars['lambda_star']),1.)
 def test_full_model_and_cartesian_rates_match_scalar_both_branches(self):
  model=load(ROOT/'models/research/barodesy2017/body-zero-spin.json')
  for soil in r.SOILS:
   pars=r.parameters(soil)
   for p0 in r.PRESSURES:
    for v in(0.,.015,.03):
     z=r.ncl_state(soil,p0,v);state={'sigma':z[:6],'e':z[6]};before=copy.deepcopy(state)
     for dv in(1.,-1.,0.):
      inc=[dv/3]*3+[0.]*3;expected=r.scalar_rate(z[0],z[6],dv,pars);actual=cart.rate(state,inc,pars);typed=interpret(model,state,state,inc,pars|{'sigma_star':1000.})
      for values in[actual['sigma_rhs'],typed['sigma'].v]:
       for x,y in zip(values,expected['sigma_rhs']):self.assertLessEqual(abs(x-y),1e-6+2e-12*abs(y))
      for e in[actual['e_rhs'],typed['e']]:self.assertLessEqual(abs(e-expected['e_rhs']),2e-14)
     self.assertEqual(state,before)
 def test_off_ncl_full_rates_and_closedform_derivative(self):
  model=load(ROOT/'models/research/barodesy2017/body-zero-spin.json')
  for soil in r.SOILS:
   pars=r.parameters(soil);initial=r.ncl_initial(soil,100000.);initial[6]=(1+initial[6])*.9-1
   for dv in(1.,-1.):
    state={'sigma':initial[:6],'e':initial[6]};inc=[dv/3]*3+[0.]*3;expected=r.scalar_rate(initial[0],initial[6],dv,pars)
    for actual in[cart.rate(state,inc,pars)['sigma_rhs'],interpret(model,state,state,inc,pars|{'sigma_star':1000.})['sigma'].v]:
     for x,y in zip(actual,expected['sigma_rhs']):self.assertLessEqual(abs(x-y),1e-6+2e-12*abs(y))
   v=.01;h=1e-6;left=r.rounded_initial_compression(soil,initial[0],initial[6],v-h);mid=r.rounded_initial_compression(soil,initial[0],initial[6],v);right=r.rounded_initial_compression(soil,initial[0],initial[6],v+h)
   derivative=(math.log(right[0])-math.log(left[0]))/(2*h)
   self.assertLess(abs(derivative-r.scalar_slope(mid[0],mid[6],pars,1)),1e-6)
 def test_retained_reference_replay(self):
  folder=Path(__file__).resolve().parents[1]/'catalogue/investigations/barodesy2017-isotropic-reference-v1/reference.json'
  self.assertEqual(r.study(),json.loads(folder.read_text()))
 def test_exact_ncl_composition_and_volume(self):
  for soil in r.SOILS:
   for p0 in r.PRESSURES:
    a=r.ncl_state(soil,p0,.01);b=r.ncl_state(soil,a[0],.02,a[6]);c=r.ncl_state(soil,p0,.03)
    for x,y in zip(b,c):self.assertLessEqual(abs(x-y),1e-12*max(abs(y),1.))
    self.assertGreater(c[6],0.)
    e0=r.ncl_initial(soil,p0)[6];self.assertLessEqual(abs(math.log1p(c[6])-math.log1p(e0)+.03),3e-16)
    self.assertLess(abs(r.ncl_residual(c,r.parameters(soil))),3e-16)
 def test_rounded_initial_correction_precision_and_composition(self):
  for soil in r.SOILS:
   for p0 in r.PRESSURES:
    e0=r.ncl_initial(soil,p0)[6];a=r.rounded_initial_compression(soil,p0,e0,.03,80);b=r.rounded_initial_compression(soil,p0,e0,.03,120)
    self.assertEqual(a,b)
    ideal=r.ncl_state(soil,p0,.03,e0);self.assertLessEqual(abs(a[0]-ideal[0]),1e-8)
    first=r.rounded_initial_compression(soil,p0,e0,.01);chained=r.rounded_initial_compression(soil,first[0],first[6],.02)
    self.assertLessEqual(abs(chained[0]-a[0]),1e-8)
 def test_off_ncl_compression_rk4_against_analytical_actual_state(self):
  for soil in r.SOILS:
   initial=r.ncl_initial(soil,100000.);initial[6]=(1+initial[6])*.9-1;pars=r.parameters(soil)
   grids=[r.rk4_scalar(initial,[.005,.01,.015],pars,n)for n in(16,32,64)]
   exact=r.rounded_initial_compression(soil,initial[0],initial[6],.03)
   errs=[abs(g['trajectory'][-1]['state'][0]-exact[0])for g in grids]
   self.assertLess(errs[2],1e-5);self.assertLess(errs[1],.15*errs[0]+1e-8);self.assertLess(errs[2],.15*errs[1]+1e-8)
 def test_reversal_uses_density_dependent_expansion(self):
  for soil in r.SOILS:
   initial=r.ncl_initial(soil,100000.);pars=r.parameters(soil);slope=r.scalar_slope(initial[0],initial[6],pars,-1)
   self.assertGreater(abs(slope-1/pars['kappa_star']),1.)
   a=r.rk4_scalar(initial,[.01,-.002,.005],pars,64);b=r.rk4_scalar(initial,[.01,-.002,.005],pars,128)
   self.assertLess(max(abs(x['state'][0]-y['state'][0])for x,y in zip(a['trajectory'],b['trajectory'])),1e-5)
   ideal=r.ncl_state(soil,100000.,.013);self.assertGreater(abs(b['trajectory'][-1]['state'][0]-ideal[0]),1.)
   self.assertGreater(b['stage_domains']['minimum_e'],0.);self.assertEqual(b['stage_domains']['evaluations'],3*128*4)
 def test_study_matrix_hashes_and_no_mutation(self):
  before=copy.deepcopy(r.SOILS);study=r.study();
  for path,pin in r.REVIEWED_DEPENDENCIES.items():self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),pin)
  self.assertEqual(r.SOILS,before);self.assertEqual(len(study['cases']),9);self.assertEqual(len(study['matrix']),5);self.assertEqual(len(study['scalar_diagnostics']),6)
  for case in study['cases']:
   self.assertEqual(case['input_sha256'],r.digest(case['input']));self.assertEqual(len(case['exact']),4)
   self.assertLess(max(abs(x['ncl_residual'])for x in case['exact']),3e-16)
 def test_rejections(self):
  pars=r.parameters('London');initial=r.ncl_initial('London',100000.)
  for p,e in[(0.,.5),(-1.,.5),(1000.,-.1),(float('nan'),.5),(True,.5)]:
   with self.assertRaises(ValueError):r.scalar_rate(p,e,1.,pars)
  for direction in(0,True,1.,2):
   with self.assertRaises(ValueError):r.scalar_slope(100000.,.5,pars,direction)
  for n in(0,True,1.5,4097):
   with self.assertRaises(ValueError):r.rk4_scalar(initial,[.01],pars,n)
  with self.assertRaises(ValueError):r.rounded_initial_compression('London',100000.,initial[6],-.01)
  with self.assertRaises(ValueError):r.ncl_state('Dresden',400000.,1.)
if __name__=='__main__':unittest.main()
