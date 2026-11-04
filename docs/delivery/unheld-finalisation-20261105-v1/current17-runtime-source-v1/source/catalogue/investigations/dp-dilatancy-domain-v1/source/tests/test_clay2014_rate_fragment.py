"""Typed source/model checks against separately authored Cartesian four-index law."""
import copy,math,unittest
from pathlib import Path
from atlas.dsl import Sym,ValidationError
from atlas.model import load,defaults,interpret,evaluation_environment,prepare_increment
from tools.inspect_clay2014_rate import load_fragment,evaluate_rate,validate_fragment,PARAMETERS
from tools import reference_clay2014_cartesian as independent
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'models/research/clay2014/hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane.json'
FRAGMENT=ROOT/'catalogue/source-audits/clay-hypoplasticity-2014-base-rate.json'
class Clay2014Fragment(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=load(MODEL);cls.f=load_fragment(FRAGMENT);cls.p=defaults(cls.m)
 def rate(self,sigma=None,de=None,e=.65,**p):
  return evaluate_rate(self.f,sigma or [120000.,90000.,80000.,3000.,-2000.,1000.],de or [.001,-.0003,.0002,.0004,-.0002,.0001],e,**{k:v for k,v in(self.p|p).items()if k in PARAMETERS})
 def test_model_typed_fragment_and_parameter_contract(self):
  self.assertEqual(list(self.m['parameters']),independent.PARAMETER_ORDER);self.assertEqual(len(self.m['state']),2);self.assertEqual(self.m['integration'],'rate')
  by={t['name']:t['expression'].replace('stretching','de')for t in self.f['terms']}
  for d in self.m['derived']:
   if d['name']in by:self.assertEqual(d['expr'],by[d['name']])
  self.assertEqual(self.m['equations'],{'sigma':'stress_rate','e':'e_rate'})
  self.assertNotIn('increment_reset',self.m);self.assertEqual(self.p['p_ref'],1000);self.assertEqual(self.p['source_a'],.3)
 def test_independent_cartesian37_allseven(self):
  cases=independent.cases();self.assertEqual(len(cases),37)
  for c in cases:
   with self.subTest(case=c['id']):
    ref=independent.evaluate(c);p=c['parameters'];z=c['state'];de=c['increment'];state={'sigma':z[:6],'e':z[6]};out=interpret(self.m,state,state,de,p);want=ref['expected'];r=self.rate(z[:6],de,z[6],**p)
    got=list(out['sigma'].v)+[out['e']]
    for x,y in zip(got[:6],want[:6]):self.assertLessEqual(abs(x-y),1e-10+2e-12*ref['stress_scale'])
    self.assertLessEqual(abs(got[6]-want[6]),1e-15+2e-13*ref['void_scale'])
    self.assertEqual(got,list(r['stress_rate'].v)+[r['e_rate']])
    for key,rkey in [('Am','Am_printed'),('Am_trace','Am_trace'),('alpha_f','alpha_f'),('fs','fs'),('fd','fd'),('fdA','fdA')]:self.assertAlmostEqual(r[key],ref['diagnostics'][rkey],delta=2e-12*max(1,abs(r[key])))
    if not any(de):self.assertEqual(got,[0.]*7)
 def test_printed_am_not_silently_repaired(self):
  r=self.rate();E=self.p['alpha_E'];v=self.p['alpha_nu'];nu=self.p['nu_pp']
  self.assertAlmostEqual(r['Am'],6.6609096228707845);self.assertAlmostEqual(r['Am_trace'],6.74576243661317)
  self.assertAlmostEqual(r['Am_discrepancy'],2*E*E*nu*nu*(1/v**2-1),delta=2e-15)
  self.assertAlmostEqual(r['fs'],9*r['p']/(2*r['Am'])*(1/self.p['lambda_star']+1/self.p['kappa_star']))
  self.assertNotAlmostEqual(r['fs'],9*r['p']/(2*r['Am_trace'])*(1/self.p['lambda_star']+1/self.p['kappa_star']))
 def test_both_density_exponents_and_inherited_direction(self):
  r=self.rate();self.assertGreater(abs(r['alpha_f']-2),.1)
  self.assertAlmostEqual(r['fd'],(2*r['p']/r['pe'])**r['alpha_f']);self.assertAlmostEqual(r['fdA'],2**r['alpha_f']*(1-r['fm'])**(r['alpha_f']/r['omega']))
  self.assertAlmostEqual(math.hypot(*r['d'].v),1.)
  for pressure in(.3,1e5):
   x=self.rate([pressure]*3+[0.]*3);self.assertEqual(x['fm'],0.)
   for a in x['d'].v[:3]:self.assertAlmostEqual(a,-1/math.sqrt(3),delta=3e-16)
 def test_plane_sign_and_no_normalization(self):
  n=[1/3,2/3,2/3];a=self.rate(**dict(zip(('n1','n2','n3'),n)));b=self.rate(**dict(zip(('n1','n2','n3'),[-x for x in n])))
  self.assertEqual(a['P'],b['P']);self.assertEqual(a['stress_rate'],b['stress_rate'])
  for v in [[0,0,0],[0,0,2],[.5,.5,.5]]:
   with self.assertRaises(ValidationError):self.rate(**dict(zip(('n1','n2','n3'),v)))
  tol=64*math.ulp(1.)
  for delta,ok in[(tol/2,True),(tol*2,False)]:
   x=math.sqrt((1+delta)/2);p=dict(n1=x,n2=x,n3=0.)
   if ok:
    r=self.rate(**p);self.assertNotEqual(r['axis_norm2'],1.)
   else:
    with self.assertRaises(ValidationError):self.rate(**p)
 def test_axis_constructs_actual_rankone_projector(self):
  n=[1/3,2/3,2/3];r=self.rate(**dict(zip(('n1','n2','n3'),n)));P=independent.from_mandel(r['P'].v)
  for i in range(3):
   for j in range(3):
    self.assertAlmostEqual(P[i][j],n[i]*n[j],delta=2e-16)
    self.assertAlmostEqual(sum(P[i][k]*P[k][j]for k in range(3)),P[i][j],delta=3e-16)
  self.assertAlmostEqual(sum(P[i][i]for i in range(3)),1.,delta=2e-16)
  self.assertAlmostEqual(independent.determinant(P),0.,delta=2e-16)
 def test_isotropic_linear_limit_not_full2013_equivalence(self):
  de=[.001,-.0003,.0002,.0004,-.0002,.0001];r=self.rate(de=de,alpha_G=1,alpha_E=1,alpha_nu=1);nu=self.p['nu_pp'];p=r['p'];factor=1.5*p*(1/self.p['lambda_star']+1/self.p['kappa_star'])*(1-2*nu)/(1+nu);c=nu/(1-2*nu)
  want=[factor*(v+(c*sum(de[:3])if i<3 else 0))for i,v in enumerate(de)]
  for a,b in zip(r['linear_stress_rate'].v,want):self.assertAlmostEqual(a,b,delta=2e-11)
  self.assertAlmostEqual(r['Am_discrepancy'],0.,delta=2e-15);self.assertNotEqual(r['alpha_f'],2.)
 def test_stiffness_support_and_source_domain_rejections(self):
  for p in[dict(alpha_G=0),dict(alpha_E=0),dict(alpha_nu=0),dict(nu_pp=.5),dict(phi_c=0),dict(lambda_star=.01,kappa_star=.02),dict(alpha_E=100,alpha_nu=.01),dict(n1=True,n2=0,n3=0)]:
   with self.assertRaises((ValidationError,ValueError)):self.rate(**p)
  for sigma in[[0.]*6,[1e5,1e5,-1e5,0,0,0],[1,1,1e-20,0,0,0],[float('nan'),1,1,0,0,0]]:
   with self.assertRaises((ValidationError,ValueError)):self.rate(sigma)
  with self.assertRaises(ValidationError):self.rate(e=-.1)
 def test_fragment_type_source_and_unit_corruptions(self):
  for how in('source','unit','constant','order'):
   f=copy.deepcopy(self.f)
   if how=='source':f['source']['sha256']='0'*64
   if how=='unit':f['inputs']['sigma']['unit']='1'
   if how=='constant':f['constants']['source_a']['value']=.4
   if how=='order':f['terms'][0],f['terms'][1]=f['terms'][1],f['terms'][0];f['terms'][0]['expression']='axis_norm2*I'
   with self.assertRaises(ValidationError):validate_fragment(f)
 def test_generic_failed_preparation_does_not_mutate_parent(self):
  state={'sigma':[1e5]*3+[0.]*3,'e':.65};before=copy.deepcopy(state);params=self.p|dict(n1=0,n2=0,n3=0)
  with self.assertRaises(ValueError):prepare_increment(self.m,state,[.001]*3+[0.]*3,params)
  self.assertEqual(state,before)
if __name__=='__main__':unittest.main()
