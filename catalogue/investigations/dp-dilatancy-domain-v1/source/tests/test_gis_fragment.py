import copy, math, random, unittest, hashlib, json
from atlas.model import ROOT
from atlas.dsl import Sym, ValidationError
from tools.inspect_gis2024_rates import load_fragment,validate_fragment,rates

R2=math.sqrt(2)
def mat(v):
 x,y,z,u,v,w=v.v
 return [[x,u/R2,w/R2],[u/R2,y,v/R2],[w/R2,v/R2,z]]
def mandel(a):return Sym((a[0][0],a[1][1],a[2][2],R2*a[0][1],R2*a[1][2],R2*a[0][2]))
def inner(a,b):return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
def norm(a):return math.sqrt(inner(a,a))
def scale(a,s):return [[v*s for v in row] for row in a]
def combine(a,b,s=1):return [[a[i][j]+s*b[i][j] for j in range(3)] for i in range(3)]
def rotate(a):
 q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
 return [[sum(q[i][k]*a[k][l]*q[j][l] for k in range(3) for l in range(3)) for j in range(3)] for i in range(3)]
A=[[.7,.2,-.1],[.2,-.3,.4],[-.1,.4,.6]]
def action(x,a=A):
 tr=sum(x[i][i] for i in range(3));ax=inner(a,x)
 return [[1e6*(3*x[i][j]+(2*tr if i==j else 0)+a[i][j]*ax) for j in range(3)] for i in range(3)]
def matrix(a=A):
 cols=[]
 for j in range(6):
  basis=Sym(tuple(float(i==j) for i in range(6)))
  cols.append(mandel(action(mat(basis),a)).v)
 return [[cols[j][i] for j in range(6)] for i in range(6)]

def oracle(v,a=A):
 """Cartesian direct equations, no DSL norm/dot/evaluator/Mandel tensor algebra."""
 d,h,m,f=[mat(v[k]) for k in ('de','h','m','f')]
 hn=norm(h);dn=norm(d);rho=hn/v['R'];hd=scale(h,1/hn) if hn else [[0.]*3 for _ in range(3)]
 ld=inner(hd,d);q=ld/dn
 hr=combine(d,hd,-rho**v['beta_R']*ld) if ld>0 else d
 chi=v['chi_0']+v['Omega']*(v['chi_max']-v['chi_0']);gamma=v['gamma_chi']*chi
 power=rho**v['chi_R'];k=power*v['m_T']+(1-power)*v['m_R']
 k+=power*(1-v['m_T'])*q if ld>0 else -power*(v['m_R']-v['m_T'])*q
 sup=v['S']**(k**gamma)
 eff=combine(combine(d,m,-v['C']*sup*dn),f)
 return {'k':k,'suppression':sup,'h_rhs':mandel(hr),'Omega_rhs':v['C_Omega']*(1-rho**v['gamma_Omega']-v['Omega'])*dn,'sigma_rhs':mandel(scale(action(eff,a),k))}

class GISFragmentTests(unittest.TestCase):
 def setUp(self):
  self.f=load_fragment()
  self.v=dict(de=Sym((2e-4,-.7e-4,.1e-4,.3e-4,-.2e-4,.4e-4)),h=Sym((2e-5,1e-5,3e-5,1e-5,0.,-1e-5)),Omega=.2,m=Sym((1.,0.,0.,0.,0.,0.)),C=.8,S=.6,f=Sym((0.,)*6),R=1e-4,m_R=5.,m_T=2.5,beta_R=.1,chi_R=4.,gamma_chi=1.7,chi_0=.8,chi_max=1.5,C_Omega=45.,gamma_Omega=1.)
 def run_rate(self,**changes):return rates(self.f,E=matrix(),**(self.v|changes))
 def close_sym(self,a,b,rel=3e-12):
  for x,y in zip(a.v,b.v):self.assertAlmostEqual(x,y,delta=rel*max(1,abs(x),abs(y)))
 def test_typing_identity_and_nested_exponent(self):
  record=json.loads((ROOT/'catalogue/investigations/gis2024-algebra-v1/manifest.json').read_text())
  self.assertFalse(record['complete_model']);self.assertEqual(record['scientific_review'],'pending')
  self.assertEqual(set(record['files']),{'catalogue/source-audits/gis-2024-supplied-host-rates.json','tools/inspect_gis2024_rates.py','tests/test_gis_fragment.py','docs/models/gis-2024-supplied-host-rates.md','docs/reviews/clay2013-algebra-review.md'})
  for name,digest in record['files'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
  validate_fragment(self.f);self.assertFalse(self.f['complete_constitutive_model']);self.assertEqual(self.f['independent_review'],'pending')
  bad=copy.deepcopy(self.f);bad['terms'][-1]['unit']='1'
  with self.assertRaises(ValidationError):validate_fragment(bad)
  r=self.run_rate();self.assertAlmostEqual(r['suppression'],self.v['S']**(r['k']**r['gamma']))
  self.assertNotAlmostEqual(r['suppression'],self.v['S']*(r['k']**r['gamma']))
 def test_zero_memory_and_full_symmetric_h(self):
  r=self.run_rate(h=Sym((0.,)*6));self.assertEqual(r['k'],5.);self.close_sym(r['h_rhs'],self.v['de'])
  h=Sym((1e-4/math.sqrt(3),)*3+(0.,)*3)
  d=Sym((1e-3,)*3+(0.,)*3)
  r=self.run_rate(h=h,de=d);self.assertAlmostEqual(r['k'],1.,delta=3e-14)
  self.assertGreater(sum(h.v[:3]),0);self.close_sym(r['h_rhs'],Sym((0.,)*6))
 def test_zero_direction_has_zero_rates_and_no_invented_k(self):
  r=self.run_rate(de=Sym((0.,)*6))
  self.close_sym(r['h_rhs'],Sym((0.,)*6));self.close_sym(r['sigma_rhs'],Sym((0.,)*6));self.assertEqual(r['Omega_rhs'],0.)
  for key in ('k','q','suppression'):self.assertIsNone(r[key])
 def test_reversal_angles_and_direction_branches(self):
  h=Sym((self.v['R'],0.,0.,0.,0.,0.))
  for d,k in [(Sym((1e-3,0.,0.,0.,0.,0.)),1.),(Sym((-1e-3,0.,0.,0.,0.,0.)),5.),(Sym((0.,1e-3,0.,0.,0.,0.)),2.5)]:
   r=self.run_rate(h=h,de=d);self.assertAlmostEqual(r['k'],k)
   self.close_sym(r['h_rhs'],Sym((0.,)*6) if k==1 else d)
 def test_large_modulus_ratios_preserve_fully_mobilized_limits(self):
  h=Sym((self.v['R'],0.,0.,0.,0.,0.))
  for mR,mT in [(1e20,1e20),(2e20,1e20)]:
   for d,k in [(Sym((1e-3,0.,0.,0.,0.,0.)),1.),(Sym((-1e-3,0.,0.,0.,0.,0.)),mR),(Sym((0.,1e-3,0.,0.,0.,0.)),mT)]:
    # S=1 would still evaluate enormous k**gamma; gamma=1 isolates interpolation.
    r=self.run_rate(h=h,de=d,m_R=mR,m_T=mT,gamma_chi=1/self.v['chi_0'],Omega=0.,S=1.)
    self.assertEqual(r['k'],k)
    self.assertTrue(all(math.isfinite(v) for v in r['sigma_rhs'].v))
 def test_Omega_growth_decay_and_independent_gamma_Omega(self):
  self.assertGreater(self.run_rate(h=Sym((0.,)*6))['Omega_rhs'],0.)
  self.assertLess(self.run_rate(h=Sym((1e-4,0.,0.,0.,0.,0.)))['Omega_rhs'],0.)
  a=self.run_rate(gamma_Omega=.5);b=self.run_rate(gamma_Omega=2.)
  self.assertNotEqual(a['Omega_rhs'],b['Omega_rhs']);self.assertEqual(a['gamma'],b['gamma']);self.close_sym(a['sigma_rhs'],b['sigma_rhs'])
  c=self.run_rate(Omega=.8);self.assertNotEqual(a['gamma'],c['gamma'])
 def test_S_one_and_supplied_f_host_action(self):
  f=Sym((1e-5,-2e-5,3e-5,0.,4e-5,0.));v=self.v|dict(S=1.,f=f)
  r=rates(self.f,E=matrix(),**v);expected=oracle(v)
  self.assertEqual(r['suppression'],1.);self.close_sym(r['sigma_rhs'],expected['sigma_rhs'])
  no_f=self.run_rate(S=1.);self.assertGreater(norm(mat(r['sigma_rhs']-no_f['sigma_rhs'])),1.)
 def test_cartesian_oracle_covariance_sign_mapping_and_homogeneity(self):
  rng=random.Random(20261031)
  for _ in range(40):
   v=self.v.copy()
   for key,mag in [('de',1e-3),('h',1e-5),('f',1e-5)]:v[key]=Sym(tuple(rng.uniform(-mag,mag) for _ in range(6)))
   m=Sym(tuple(rng.uniform(-1,1) for _ in range(6)));v['m']=m/math.sqrt(sum(x*x for x in m.v))
   r=rates(self.f,E=matrix(),**v);ref=oracle(v)
   for key in ('h_rhs','sigma_rhs'):self.close_sym(r[key],ref[key])
   for key in ('k','suppression','Omega_rhs'):self.assertAlmostEqual(r[key],ref[key],delta=3e-12*max(1,abs(ref[key])))
   rot=v|{key:mandel(rotate(mat(v[key]))) for key in ('de','h','m','f')}
   rr=rates(self.f,E=matrix(rotate(A)),**rot)
   for key in ('h_rhs','sigma_rhs'):self.close_sym(rr[key],mandel(rotate(mat(r[key]))))
   self.assertAlmostEqual(rr['Omega_rhs'],r['Omega_rhs'],delta=1e-13)
   neg=v|{key:-v[key] for key in ('de','h','m','f')};rn=rates(self.f,E=matrix(),**neg)
   for key in ('h_rhs','sigma_rhs'):self.close_sym(rn[key],-r[key])
   self.assertEqual(rn['Omega_rhs'],r['Omega_rhs'])
   big=v|dict(de=v['de']*3,f=v['f']*3);rb=rates(self.f,E=matrix(),**big)
   for key in ('h_rhs','sigma_rhs'):self.close_sym(rb[key],r[key]*3)
   self.assertAlmostEqual(rb['Omega_rhs'],3*r['Omega_rhs'],delta=1e-13)
 def test_invalid_domain_shape_nonfinite_and_underflow_rejected(self):
  changes=[dict(R=0),dict(Omega=1.1),dict(m_R=1),dict(S=-.1),dict(gamma_Omega=0),dict(C=True),dict(h=Sym((2e-4,0.,0.,0.,0.,0.))),dict(m=Sym((0.,)*6)),dict(de=Sym((float('nan'),)*6)),dict(de=Sym((1e-300,0.,0.,0.,0.,0.))),dict(de=Sym((0.,)*6),f=Sym((1.,0.,0.,0.,0.,0.)))]
  for change in changes:
   with self.subTest(change=change),self.assertRaises(ValidationError):self.run_rate(**change)
  with self.assertRaises(ValidationError):rates(self.f,E=[[True]*6]*6,**self.v)
  with self.assertRaises(ValidationError):rates(self.f,E=matrix(),**(self.v|dict(extra=1)))

if __name__=='__main__':unittest.main()
