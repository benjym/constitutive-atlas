"""Prospective source/consumer/reference wiring, without compiled model evaluation."""
import hashlib,json,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
from atlas.model import validate
read=lambda p:json.loads(p.read_text())
class ProspectivePreview(unittest.TestCase):
 def test_nine_models_and_unchanged_math(self):
  models=sorted((HERE/'models').glob('*.json'));self.assertEqual(len(models),9)
  for p in models:validate(read(p))
  for p in (ROOT/'models').glob('*.json'):self.assertEqual(p.read_bytes(),(HERE/'models'/p.name).read_bytes())
  old=read(ROOT/'catalogue/investigations/clay2005-homogeneous-rates-v1/model.json');new=read(HERE/'models/hypoplastic-clay-2005.json')
  for key in old:
   if key not in ('id','name','description','sources'):self.assertEqual(old[key],new[key],key)
 def test_all_requests_and_recovery_order(self):
  req=read(HERE/'requests.json');self.assertEqual(len(req),27);self.assertEqual(len({r['id']for r in req}),27)
  self.assertEqual(sum(not r['expected_ok']for r in req),5)
  self.assertEqual({r['protocol']for r in req if r.get('cycles')==1},set(range(5)))
  for i,r in enumerate(req):
   if not r['expected_ok']:self.assertIn('same_result_as',req[i+1])
  self.assertEqual(next(r for r in req if r['id']=='actual-browser-default')['initial'],'100000,100000,100000,0,0,0,0.80000000000000004')
 def test_reference_adapter_and_gate_rejection(self):
  from isotropic_adapter import expected_endpoint
  from assess import check_isotropic_endpoint
  req=[r for r in read(HERE/'requests.json')if r.get('isotropic_reference')];self.assertEqual(len(req),5)
  for r in req:
   ref=expected_endpoint(HERE,r);state=[ref['p']]*3+[0.]*3+[ref['e']]
   response={'state':state}if r['mode']=='integrate'else{'points':[{'state':state}]}
   failures=[];check=lambda ok,why:failures.append(why)if not ok else None
   check_isotropic_endpoint(HERE,r,response,check,r['id']);self.assertEqual(failures,[])
   state[0]+=2e-5*max(1,abs(ref['p']));check_isotropic_endpoint(HERE,r,response,check,r['id']);self.assertTrue(failures)
if __name__=='__main__':unittest.main()
