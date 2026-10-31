"""Pure study validation; no subprocess/build and no retained evidence writes."""
import copy,hashlib,pathlib,unittest
from tools import barodesy2017_rate_study as study
class Study(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before={p:study.sha(p)for p in(study.REFERENCE,study.MODEL)}
  m,h=study.catalogue();cls.report=study.collect(lambda w:study.python_call(w,m,h),'python')
 @classmethod
 def tearDownClass(cls):
  for p,h in cls.before.items():
   if study.sha(p)!=h:raise AssertionError('test mutated retained evidence/model')
 def rejected(self,mutate):
  r=copy.deepcopy(self.report);mutate(r)
  with self.assertRaises((ValueError,TypeError,KeyError)):study.assess(r)
 def test_actual_python111_reference(self):
  r=study.assess(self.report);self.assertEqual(r['cases'],111);self.assertEqual(r['invalids'],len(study.invalid_requests(study.catalogue()[0],study.reference())));self.assertLess(r['maximum_normalized_rate_error'],3e-15);self.assertFalse(r['AD_validated'])
 def test_catalogue_parameter_order(self):self.rejected(lambda r:r['parameter_order'].reverse())
 def test_compiled_model_definition_binding(self):self.rejected(lambda r:r['model_definition'].__setitem__('name','forged'))
 def test_case_completeness(self):self.rejected(lambda r:r['records'].pop())
 def test_response_model_echo(self):self.rejected(lambda r:r['records'][0]['response'].__setitem__('model','wrong'))
 def test_response_state_echo(self):self.rejected(lambda r:r['records'][0]['response']['state'].__setitem__(0,999.))
 def test_boolean_numeric_impostor(self):self.rejected(lambda r:r['records'][0]['response']['state'].__setitem__(3,False))
 def test_boolean_output(self):self.rejected(lambda r:r['records'][0]['response']['values'].__setitem__(0,True))
 def test_nonfinite_output(self):self.rejected(lambda r:r['records'][0]['response']['values'].__setitem__(0,float('nan')))
 def test_false_success_numeric_status(self):self.rejected(lambda r:r['records'][0]['response'].__setitem__('ok',1))
 def test_rate_wrong_but_finite(self):self.rejected(lambda r:r['records'][0]['response']['values'].__setitem__(0,1.))
 def test_invalid_has_no_usable_values(self):self.rejected(lambda r:r['invalid_records'][0]['response'].__setitem__('values',[0.]*7))
 def test_recovery_bound(self):self.rejected(lambda r:r['invalid_records'][0]['recovery']['increment'].__setitem__(0,.9))
 def test_cannot_relax_budget(self):self.rejected(lambda r:r.__setitem__('budget',1e-5))
 def test_no_AD_promotion(self):self.rejected(lambda r:r['claims'].__setitem__('AD_validated',True))
 def test_reference_identity(self):self.rejected(lambda r:r.__setitem__('reference_sha256','0'*64))
if __name__=='__main__':unittest.main()
