"""Source-law checks independent of native/Wasm parity."""
import importlib.util,json,math,tempfile,unittest
from pathlib import Path
from atlas.model import ROOT,load,interpret,observe
from atlas.initialization import initialize_state
from atlas.compiler import generate
BASE=ROOT/'docs/ingestion/bingham-comsol63'
MODEL=ROOT/'models/research/bingham/bingham-comsol63-mises-perfect-zero-spin-ode.json'
spec=importlib.util.spec_from_file_location('bingham_reference',BASE/'execution-v1/oracle.py');oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
class BinghamSourceLawTests(unittest.TestCase):
 def test_zero_threshold_and_overstress_rates_from_exact_relaxation(self):
  m=load(MODEL);cases=json.loads((BASE/'source-v1/analytical-references.json').read_text())['cases']
  for c in cases:
   z=c['initial'];named=dict(eps=z[:6],eps_vp=z[6:12],alpha=z[12]);d=c['strain_rate'];r=interpret(m,named,None,d,time=0.)
   # Extrapolated derivative of an independently derived exact relaxation curve.
   h=1e-5;a=oracle.relaxation(z,h);b=oracle.relaxation(z,h/2)
   numerical=[2*(y-v)/(h/2)-(x-v)/h for v,x,y in zip(z,a,b)]
   self.assertEqual(list(r['eps'].v),d)
   for actual,expected in zip([*r['eps_vp'].v,r['alpha']],numerical[6:]):self.assertAlmostEqual(actual,expected,delta=1e-9,msg=c['id'])
 def test_dissipation_and_deviatoric_flow(self):
  m=load(MODEL)
  for e in [oracle.E,[.002]*3+[0.]*3,[0.]*6]:
   z=dict(eps=e,eps_vp=[0.]*6,alpha=0.);r=interpret(m,z,None,oracle.D,time=3.);s=observe(m,z,oracle.D,time=3.)['stress'].v
   # Pairwise diagonal differences avoid reproducing production dev/norm expression.
   q=math.sqrt(((s[0]-s[1])**2+(s[1]-s[2])**2+(s[2]-s[0])**2)/2+1.5*sum(x*x for x in s[3:]))
   power=math.fsum(a*b for a,b in zip(s,r['eps_vp'].v));expected=q*max(q-oracle.P[2],0)/oracle.P[3]
   self.assertAlmostEqual(power,expected,delta=1e-8);self.assertGreaterEqual(power,0);self.assertAlmostEqual(sum(r['eps_vp'].v[:3]),0,delta=1e-14)
 def test_explicit_history_domain_and_overstress_initialization(self):
  m=load(MODEL);params=dict(zip(m['parameters'],oracle.P));z=dict(eps=oracle.E,eps_vp=[0.]*6,alpha=0.)
  prepared=initialize_state(m,z,params,time=0.,loading=[0.]*6);self.assertEqual(prepared['initial'],oracle.Z)
  for bad in [dict(eps=oracle.E,eps_vp=[0.]*6,alpha=-1),dict(eps=oracle.E,eps_vp=[.01,0,0,0,0,0],alpha=0),dict(eps=oracle.E,alpha=0)]:
   with self.assertRaises((ValueError,KeyError)):initialize_state(m,bad,params,time=0.,loading=[0.]*6)
 def test_normal_generation_preserves_exact_profile_and_definition(self):
  with tempfile.TemporaryDirectory() as d:
   generate(d,[MODEL]);metadata=json.loads((Path(d)/'models.json').read_text());self.assertEqual(len(metadata['models']),1);self.assertEqual(metadata['models'][0]['id'],load(MODEL)['id'])
if __name__=='__main__':unittest.main()
