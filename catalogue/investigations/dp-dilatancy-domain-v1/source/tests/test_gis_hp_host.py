import copy,math,random,unittest
from atlas.dsl import Sym,ValidationError
from tools.inspect_gis2024_hp_host import host,load_fragment,validate_fragment
from tools import reference_gis2024_hp_host as reference
mandel,trace,rotate,mul,solve=reference.mandel,reference.trace,reference.rotate,reference.mul,reference.solve

def mat(v):return reference.mat(v.v)
def oracle(v):
    result=reference.oracle(v|{'sigma':v['sigma'].v})
    result['m']=Sym(result['m'])
    return result

class HPHostTests(unittest.TestCase):
 def setUp(self):
  self.f=load_fragment();self.v=dict(sigma=Sym((100000.,100000.,100000.,0.,0.,0.)),e=.595,phi=34*math.pi/180,hs=111746000.,ei0=1.027,ec0=.893,ed0=.520,n=.346,alpha=.15,beta=2.2)
 def run_host(self,**kw):return host(self.f,**(self.v|kw))
 def close(self,a,b,rel=4e-10):
  av=a.v if isinstance(a,Sym) else [a];bv=b.v if isinstance(b,Sym) else [b]
  for x,y in zip(av,bv):self.assertAlmostEqual(x,y,delta=rel*max(1,abs(x),abs(y)))
 def test_typed_identity_and_no_defaults(self):
  validate_fragment(self.f);self.assertFalse(self.f['complete_constitutive_model']);self.assertEqual(self.f['independent_review'],'pending')
  for mutate in [lambda f:f['source'].update(sha256='0'*64),lambda f:f['inputs']['sigma'].update(unit='1'),lambda f:f['actions']['E'].update(unit='1')]:
   corrupt=copy.deepcopy(self.f);mutate(corrupt)
   with self.assertRaises(ValidationError):validate_fragment(corrupt)
  bad=copy.deepcopy(self.f);bad['terms'][-1]['unit']='Pa'
  with self.assertRaises(ValidationError):validate_fragment(bad)
  missing=self.v.copy();missing.pop('e')
  with self.assertRaises(ValidationError):host(self.f,**missing)
 def test_isotropic_analytic_limit_and_asbs(self):
  r=self.run_host();v=r['env'];a=v['a'];fs=v['fs'];g=v['G'];ratio=v['ratio']
  self.assertEqual(v['F'],1.);self.assertEqual(v['cos3theta'],0.)
  self.close(r['m'],Sym((1/math.sqrt(3),)*3+(0.,)*3))
  b=a/(3+a*a);c=1/(math.sqrt(3)*fs*(3+a*a))
  self.close(v['fdAstar'],abs(g-3*ratio*c)/(math.sqrt(3)*b*g))
  X=Sym((.2,-.3,.7,.1,-.5,.4));I=Sym((1.,1.,1.,0.,0.,0.))
  self.close(r['action']('L',X),X*3+I*(a*a*sum(X.v[:3])/3))
  self.close(v['B'],I*(-b));self.assertGreater(v['fdAstar'],0.)
 def test_dense_cartesian_source_signs_rotation_and_inverse(self):
  rng=random.Random(20261101)
  for case in range(36):
   z=[[rng.uniform(-1,1) for j in range(3)] for i in range(3)]
   p=10**rng.uniform(3,6)
   A=[[p*((1 if i==j else 0)+sum(z[k][i]*z[k][j] for k in range(3))) for j in range(3)] for i in range(3)]
   pressure=trace(A)/3;compression=math.exp(-(3*pressure/self.v['hs'])**self.v['n'])
   e=(self.v['ed0']+.55*(self.v['ei0']-self.v['ed0']))*compression
   v=self.v|dict(sigma=Sym(tuple(mandel(A))),e=e)
   r=host(self.f,**v);ref=oracle(v);env=r['env']
   for name in ('F','fs','fd','fdAstar'):self.close(env[name],ref[name])
   for name in ('m','C','S'):self.close(r[name],ref[name])
   self.close(env['B'],Sym(tuple(mandel(mul(ref['B_source'],-1)))))
   self.close(env['Caux'],Sym(tuple(mandel(mul(ref['C_source'],-1)))))
   self.close(env['G'],-ref['G_source'])
   X=Sym(tuple(rng.uniform(-1,1) for _ in range(6)))
   dense=Sym(tuple(solve(ref['L'],list(X.v))))
   self.close(r['action']('L_inverse',X),dense)
   self.close(r['action']('L',r['action']('L_inverse',X)),X)
   self.close(r['action']('L_inverse',r['action']('L',X)),X)
   vr=v|dict(sigma=Sym(tuple(mandel(rotate(A)))));rr=host(self.f,**vr)
   for name in ('C','S'):self.close(rr[name],r[name])
   self.close(rr['m'],Sym(tuple(mandel(rotate(mat(r['m']))))))
   self.close(rr['action']('E',Sym(tuple(mandel(rotate(mat(X)))))),Sym(tuple(mandel(rotate(mat(r['action']('E',X)))))))
 def test_axisymmetric_compression_extension_and_near_isotropic(self):
  for sigma in [(300000.,100000.,100000.,0.,0.,0.),(100000.,300000.,300000.,0.,0.,0.),(100000.00001,100000.,100000.,0.,0.,0.)]:
   v=self.v|dict(sigma=Sym(sigma));r=host(self.f,**v);ref=oracle(v)
   for name in ('F','fdAstar'):self.close(r['env'][name],ref[name])
   self.assertLessEqual(abs(r['env']['cos3theta']),1+1e-10)
  self.assertEqual(self.run_host()['env']['F'],1.)
 def test_host_reconstructs_original_HP_rate_and_supplied_GIS_compatibility(self):
  from tools.inspect_gis2024_rates import rates,load_fragment as load_gis
  r=self.run_host(sigma=Sym((180000.,100000.,70000.,12000.,-8000.,4000.)))
  de=Sym((2e-4,-.7e-4,.1e-4,.3e-4,0.,-.1e-4));normde=math.sqrt(sum(x*x for x in de.v))
  E=r['action'];v=r['env']
  rearranged=E('E',de-r['m']*(r['C']*r['S']*normde))
  direct=E('E',de)+v['N']*(v['fs']*v['fd']*normde)
  self.close(rearranged,direct)
  gis=dict(de=de,h=Sym((1e-5,2e-5,0.,0.,0.,0.)),Omega=.2,m=r['m'],C=r['C'],S=r['S'],f=r['f'],R=1e-4,m_R=5.,m_T=2.5,beta_R=.1,chi_R=4.,gamma_chi=1.7,chi_0=.8,chi_max=1.5,C_Omega=45.,gamma_Omega=1.)
  response=rates(load_gis(),E=r['E'],**gis)
  self.close(response['sigma_rhs'],E('E',response['effective_de'])*response['k'])
  self.assertTrue(all(math.isfinite(x) for x in response['sigma_rhs'].v))
 def test_invalid_domains_and_denominators(self):
  for kw in [dict(sigma=Sym((0.,)*6)),dict(sigma=Sym((-1.,-1.,-1.,0.,0.,0.))),dict(e=0),dict(e=.1),dict(e=2),dict(n=0),dict(phi=0),dict(hs=-1),dict(alpha=True),dict(hs=10**1000),dict(hs=10**20+1),dict(ec0=.1),dict(sigma=Sym((float('inf'),)*6))]:
   with self.subTest(kw=kw),self.assertRaises(ValidationError):self.run_host(**kw)
  # Force fsden<0 with an extreme density factor; no denominator floor.
  with self.assertRaises(ValidationError):self.run_host(alpha=100)

 def test_exact_spherical_and_unresolved_nonzero_invariants(self):
  for pressure in (.1,.3,1e5,9247007.657539926):
   e=.7*math.exp(-(3*pressure/self.v['hs'])**self.v['n'])
   result=self.run_host(sigma=Sym((pressure,)*3+(0.,)*3),e=e)
   self.assertEqual(result['env']['j2'],0.)
   self.assertEqual(result['env']['cos3theta'],0.)
   self.assertEqual(result['env']['F'],1.)
  with self.assertRaises(ValidationError):self.run_host(sigma=Sym((1e5,1e5,1e5,1e-300,0.,0.)))
 def test_strict_density_factor_underflow_is_rejected(self):
  compression=math.exp(-(300000/self.v['hs'])**self.v['n'])
  e=math.nextafter(.5*compression,math.inf)
  with self.assertRaises(ValidationError):self.run_host(e=e,ei0=1.000001,ec0=1.,ed0=.5,alpha=30.)

if __name__=='__main__':unittest.main()
