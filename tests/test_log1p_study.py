import copy,math,unittest
from unittest.mock import patch
from tools import log1p_study as s
class Study(unittest.TestCase):
 def setUp(self):
  self.ref=s.corpus();self.hash='fixturehash'
  self.patches=[patch.object(s,'reference',return_value=self.ref),patch.object(s,'catalogue',return_value=([],self.hash)),patch.object(s,'sha',return_value='referencehash')]
  for p in self.patches:p.start();self.addCleanup(p.stop)
  def result(x,success=True):
   r={'ok':success,'input':x,'operator_version':s.OPERATOR_VERSION,'catalogue_hash':self.hash,'primitive_ok':success,'schema_ok':success,'contexts':dict.fromkeys(s.CONTEXTS,True),'negative_zero':False,'value':None,'derivatives':None,'schema_values':None,'schema_derivatives':None}
   if success:
    v,d=map(float,s.oracle(x,650));r.update(value=v,negative_zero=x==0 and math.copysign(1.,x)<0,derivatives=[d]*38,schema_values=[1+v]*3+[0.]*3,schema_derivatives=[[d]*38 for _ in range(3)]+[[0.]*38 for _ in range(3)])
   return r
  rows=[{'id':c['id'],'request':s.request(c),'response':result(c['x'])} for c in self.ref['cases']]
  invalid=[{'request':q,'response':result(q['input'],False) if q['parseable'] else {'ok':False,'error':'invalid input'},'recovery':copy.deepcopy(rows[0]['response'])} for q in s.invalid_requests()]
  self.report={'version':s.VERSION,'backend':'wasm','operator_version':s.OPERATOR_VERSION,'ulp_budget':4,'catalogue_hash':self.hash,'reference_sha256':'referencehash','records':rows,'invalid_records':invalid}
 def test_valid_full_matrix(self):self.assertEqual(s.assess(self.report)['cases'],38)
 def test_corruptions_rejected(self):
  mutations=[lambda r:r['records'].pop(),lambda r:r['records'].__setitem__(1,copy.deepcopy(r['records'][0])),lambda r:r['records'][0]['request'].__setitem__('input',False),lambda r:r['records'][0]['response'].__setitem__('ok',1),lambda r:r['records'][0]['response']['contexts'].pop(next(iter(s.CONTEXTS))),lambda r:r['records'][0]['response'].__setitem__('operator_version','wrong'),lambda r:r['records'][0]['response']['derivatives'].__setitem__(37,2.),lambda r:r['records'][0]['response']['schema_derivatives'][5].__setitem__(37,True),lambda r:r['records'][1]['response'].__setitem__('negative_zero',False),lambda r:r['records'][2]['response'].__setitem__('value',0.),lambda r:r['invalid_records'][0]['request'].__setitem__('parseable',1),lambda r:r['invalid_records'][3]['response'].__setitem__('ok',0),lambda r:r['invalid_records'][0]['recovery'].__setitem__('ok',1),lambda r:r['invalid_records'][0]['recovery']['schema_values'].__setitem__(0,True),lambda r:r['records'][0]['response'].__setitem__('catalogue_hash','wrong')]
  for i,mutate in enumerate(mutations):
   with self.subTest(case=i):
    r=copy.deepcopy(self.report);mutate(r)
    with self.assertRaises(ValueError):s.assess(r)
 def test_four_ulp_and_zero_policy(self):
  x=1.;y=x
  for _ in range(4):y=math.nextafter(y,math.inf)
  self.assertEqual(s.check(y,x),4)
  with self.assertRaises(ValueError):s.check(math.nextafter(y,math.inf),x)
  with self.assertRaises(ValueError):s.check(0.,math.ulp(0.))
 def test_standalone_parity_validates_completeness(self):
  native=copy.deepcopy(self.report);native['backend']='native'
  self.report['native_report_sha256']='referencehash'
  self.assertEqual(s.verify_parity(self.report,native,'ignored'),0)
  native['records'].pop()
  with self.assertRaises(ValueError):s.verify_parity(self.report,native,'ignored')
 def test_native_needs_no_recovery(self):
  self.report['backend']='native'
  for r in self.report['invalid_records']:r.pop('recovery')
  s.assess(self.report)
if __name__=='__main__':unittest.main()
