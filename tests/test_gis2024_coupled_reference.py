"""Pure stdlib tests of a14-state instantaneous Cartesian reference; no Atlas."""
import copy,math,random,unittest
from tools.reference_gis2024_coupled import coupled_rates,ReferenceDomainError
from tools import reference_gis2024_hp_host as hp

PARAMETERS=dict(phi=math.radians(34),hs=111746000.,ei0=1.027,ec0=.893,ed0=.520,n=.346,alpha=.15,beta=2.2,R=1e-4,m_R=5.,m_T=2.5,beta_R=.1,chi_R=4.,gamma_chi=1.7,chi_0=.8,chi_max=1.5,C_Omega=45.,gamma_Omega=1.)
STATE=dict(sigma=[100000.,100000.,100000.,0.,0.,0.],e=.595,h=[0.]*6,Omega=0.)

def cases():
    cases=[]
    for name,h,d,Omega in [
      ('zero-memory',[0.]*6,[2e-4,-1e-4,-1e-4,0.,0.,0.],0.),
      ('zero-direction',[2e-5,1e-5,3e-5,0.,0.,0.],[0.]*6,.2),
      ('forward-full',[1e-4,0.,0.,0.,0.,0.],[1e-3,0.,0.,0.,0.,0.],.2),
      ('reverse-full',[1e-4,0.,0.,0.,0.,0.],[-1e-3,0.,0.,0.,0.,0.],.2),
      ('tangent-full',[1e-4,0.,0.,0.,0.,0.],[0.,1e-3,0.,0.,0.,0.],.2),
      ('isotropic-full',[math.nextafter(1e-4/math.sqrt(3),-math.inf)]*3+[0.]*3,[1e-4]*3+[0.]*3,0.)]:
        cases.append(dict(id=name,state=STATE|dict(h=h,Omega=Omega),de=d,parameters=PARAMETERS.copy()))
    rng=random.Random(20261102)
    for i in range(32):
        z=[[rng.uniform(-1,1) for _ in range(3)] for _ in range(3)];scale=10**rng.uniform(3,6)
        A=[[scale*((1 if i==j else 0)+sum(z[k][i]*z[k][j] for k in range(3))) for j in range(3)] for i in range(3)]
        p=hp.trace(A)/3;c=math.exp(-(3*p/PARAMETERS['hs'])**PARAMETERS['n'])
        e=(PARAMETERS['ed0']+.55*(PARAMETERS['ei0']-PARAMETERS['ed0']))*c
        h=[rng.uniform(-1e-5,1e-5) for _ in range(6)];d=[rng.uniform(-1e-3,1e-3) for _ in range(6)]
        cases.append(dict(id='random-'+str(i),state=dict(sigma=hp.mandel(A),e=e,h=h,Omega=rng.uniform(0,1)),de=d,parameters=PARAMETERS.copy()))
    return cases

class CoupledReferenceTests(unittest.TestCase):
 def close(self,a,b,relative=2e-10):
  for x,y in zip(a,b):self.assertAlmostEqual(x,y,delta=relative*max(1,abs(x),abs(y)))
 def test_all14_shape_finite_identity_and_input_isolation(self):
  for c in cases():
   before=copy.deepcopy(c);r=coupled_rates(c['state'],c['de'],c['parameters'])
   self.assertEqual(c,before);self.assertEqual(len(r['derivative']),14)
   self.assertEqual(r['derivative'],r['sigma_rhs']+[r['e_rhs']]+r['h_rhs']+[r['Omega_rhs']])
   self.assertTrue(all(math.isfinite(v) for v in r['derivative']))
   self.assertAlmostEqual(r['e_rhs'],-(1+c['state']['e'])*sum(c['de'][:3]))
 def test_analytic_reversal_and_zero_memory(self):
  cs=cases()
  for index,k in [(0,5.),(2,1.),(3,5.),(4,2.5),(5,1.)]:
   c=cs[index];r=coupled_rates(c['state'],c['de'],c['parameters']);self.assertAlmostEqual(r['diagnostics']['k'],k,delta=4e-14)
  for index in [0,3,4]:
   c=cs[index];self.close(coupled_rates(c['state'],c['de'],c['parameters'])['h_rhs'],c['de'])
  for index in [2,5]:
   c=cs[index];self.close(coupled_rates(c['state'],c['de'],c['parameters'])['h_rhs'],[0.]*6)
  r=coupled_rates(cs[1]['state'],cs[1]['de'],PARAMETERS);self.assertEqual(r['derivative'],[0.]*14);self.assertIsNone(r['diagnostics']['k'])
 def test_covariance_and_positive_homogeneity(self):
  for c in cases():
   r=coupled_rates(c['state'],c['de'],c['parameters']);s=c['state']
   rs=s|dict(sigma=hp.mandel(hp.rotate(hp.mat(s['sigma']))),h=hp.mandel(hp.rotate(hp.mat(s['h']))))
   rd=hp.mandel(hp.rotate(hp.mat(c['de'])));rot=coupled_rates(rs,rd,c['parameters'])
   for key in ['sigma_rhs','h_rhs']:self.close(rot[key],hp.mandel(hp.rotate(hp.mat(r[key]))))
   self.close([rot['e_rhs'],rot['Omega_rhs']],[r['e_rhs'],r['Omega_rhs']])
   for scale in [.2,4.]:
    big=coupled_rates(s,[v*scale for v in c['de']],c['parameters']);self.close(big['derivative'],[v*scale for v in r['derivative']])
 def test_isotropic_stress_closed_rate_at_zero_memory(self):
  # For isotropic sigma: F=1,Q=1/3,m=I/sqrt3,k=m_R at h=0.
  de=[3e-4,-1e-4,2e-4,1e-4,-2e-4,4e-4];r=coupled_rates(STATE,de,PARAMETERS)
  host=hp.oracle({k:PARAMETERS[k] for k in ['phi','hs','ei0','ec0','ed0','n','alpha','beta']}|{'sigma':STATE['sigma'],'e':STATE['e']})
  a=math.sqrt(3/8)*(3-math.sin(PARAMETERS['phi']))/math.sin(PARAMETERS['phi']);k=5.;gamma=1.7*.8
  normd=math.sqrt(sum(v*v for v in de));coef=host['C']*host['S']**(k**gamma)*normd/math.sqrt(3)
  v=[x-(coef if i<3 else 0) for i,x in enumerate(de)];tr=sum(v[:3])
  expected=[k*host['fs']*(3*x+(a*a*tr/3 if i<3 else 0)) for i,x in enumerate(v)]
  self.close(r['sigma_rhs'],expected)
 def test_memory_analytic_differential_checks(self):
  # beta_R=1 aligned loading: h(s)=R-(R-h0)exp(-D*s/R).
  D=.0002;h0=.2*PARAMETERS['R'];p=PARAMETERS|dict(beta_R=1.)
  for s in [0.,.1,.5]:
   h=p['R']-(p['R']-h0)*math.exp(-D*s/p['R'])
   r=coupled_rates(STATE|dict(h=[h,0.,0.,0.,0.,0.]),[D,0.,0.,0.,0.,0.],p)
   expected=D*(1-h0/p['R'])*math.exp(-D*s/p['R'])
   self.assertAlmostEqual(r['h_rhs'][0],expected,delta=1e-18)
  # Frozen-h analytic Omega relaxation, not a coupled trajectory.
  rho=.4;rate=PARAMETERS['C_Omega']*D;target=1-rho**PARAMETERS['gamma_Omega'];O0=.2
  for s in [0.,1.,20.]:
   O=target+(O0-target)*math.exp(-rate*s)
   r=coupled_rates(STATE|dict(h=[rho*PARAMETERS['R'],0.,0.,0.,0.,0.],Omega=O),[D,0.,0.,0.,0.,0.],PARAMETERS)
   self.assertAlmostEqual(r['Omega_rhs'],-rate*(O0-target)*math.exp(-rate*s),delta=1e-17)
 def test_independent_gammaOmega_and_Omega_bounds(self):
  state=STATE|dict(h=[.4e-4,0.,0.,0.,0.,0.],Omega=.2);d=[1e-4,0.,0.,0.,0.,0.]
  a=coupled_rates(state,d,PARAMETERS|dict(gamma_Omega=.5));b=coupled_rates(state,d,PARAMETERS|dict(gamma_Omega=2.))
  self.assertNotEqual(a['Omega_rhs'],b['Omega_rhs']);self.assertEqual(a['sigma_rhs'],b['sigma_rhs'])
  self.assertGreater(coupled_rates(STATE|dict(Omega=.2),d,PARAMETERS)['Omega_rhs'],0.)
  self.assertLess(coupled_rates(STATE|dict(h=[1e-4,0.,0.,0.,0.,0.],Omega=.2),d,PARAMETERS)['Omega_rhs'],0.)
 def test_invalid_finite_domains_and_exact_inputs(self):
  for state,de,p in [(STATE,[1e-300,0.,0.,0.,0.,0.],PARAMETERS),(STATE,[True]*6,PARAMETERS),(STATE|dict(h=[.0002,0.,0.,0.,0.,0.]),[0.]*6,PARAMETERS),(STATE|dict(Omega=2),[0.]*6,PARAMETERS),(STATE,[0.]*6,PARAMETERS|dict(n=0)),(STATE,[0.]*6,PARAMETERS|dict(hs=10**1000)),(STATE|dict(e=.1),[0.]*6,PARAMETERS),(STATE|dict(sigma=[0.]*6),[0.]*6,PARAMETERS),(STATE,[0.]*6,PARAMETERS|dict(extra=1))]:
   with self.assertRaises(ReferenceDomainError):coupled_rates(state,de,p)

if __name__=='__main__':unittest.main()
