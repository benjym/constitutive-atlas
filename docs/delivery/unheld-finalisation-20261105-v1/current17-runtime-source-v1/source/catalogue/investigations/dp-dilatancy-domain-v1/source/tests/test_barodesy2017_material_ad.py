"""Independent FD/verifier tests. Synthetic Jacobians are NOT native AD evidence."""
import copy,json,math,pathlib,tempfile,unittest
from unittest.mock import patch
from types import SimpleNamespace
from tools import barodesy2017_material_ad as ad
class MaterialStudy(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.model,cls.hash=ad.rate.catalogue();cls.request=ad.rate.wire(ad.selected()[1],cls.model);cls.fd=ad.difference_reference(cls.request,cls.model)
  # Richardson FD mock exercises verifier machinery only, never retained as AD evidence.
  coarse,fine=cls.fd['scaled_columns_by_step'][-2:];s=cls.fd['state_loading_scales']
  j=[[(4*fine[k][i]-coarse[k][i])/3/s[k]for k in range(13)]for i in range(7)]
  j[6]=[0.]*6+[-sum(cls.request['increment'][:3])]+[-(1+cls.request['state'][6])]*3+[0.]*3
  cls.response=ad.rate.envelope(cls.request,cls.hash,cls.fd['primal'])|{'jacobian':j,'columns':ad.COLUMNS}
 def rejected(self,mutate):
  r=copy.deepcopy(self.response);mutate(r)
  with self.assertRaises((ValueError,TypeError,KeyError)):ad.assess_case(r,self.request,self.hash,self.fd)
 def test_all_regular_independent_refinement(self):
  self.assertEqual(len(ad.selected()),21)
  for c in ad.selected():
   d=ad.difference_reference(ad.rate.wire(c,self.model),self.model)
   self.assertLess(d['successive_normalized_differences'][-1],1e-9)
 def test_synthetic_verifier_control(self):self.assertLess(ad.assess_case(self.response,self.request,self.hash,self.fd)['normalized_derivative_errors_by_step'][-1],ad.FD_BUDGET)
 def test_state_echo(self):self.rejected(lambda r:r['state'].__setitem__(0,0.))
 def test_column_order(self):self.rejected(lambda r:r['columns'].reverse())
 def test_boolean_derivative(self):self.rejected(lambda r:r['jacobian'][0].__setitem__(0,False))
 def test_nonfinite_derivative(self):self.rejected(lambda r:r['jacobian'][0].__setitem__(0,float('nan')))
 def test_wrong_column_count(self):self.rejected(lambda r:r['jacobian'][0].pop())
 def test_bad_derivative(self):self.rejected(lambda r:r['jacobian'][0].__setitem__(7,1e30))
 def test_bad_void_derivative(self):self.rejected(lambda r:r['jacobian'][6].__setitem__(0,1e-6))
 def test_extra_response_field(self):self.rejected(lambda r:r.__setitem__('seeded_previous',True))
 def test_failure_shape(self):
  r=ad.rate.envelope(self.request,self.hash,None)|{'jacobian':None,'columns':ad.COLUMNS};r['message']='unsupported regular material AD request'
  ad.checked_response(r,self.request,self.hash,False);r['jacobian']=[[0.]*13]*7
  with self.assertRaises(ValueError):ad.checked_response(r,self.request,self.hash,False)
 def test_zero_hydro_not_in_corpus(self):
  for c in ad.selected():self.assertEqual(c['oracle']['branch'],'regular');self.assertNotIn('nearhydro',c['id'])
 def test_oracle_void_derivatives(self):
  expected=[0.]*6+[-sum(self.request['increment'][:3])]+[-(1+self.request['state'][6])]*3+[0.]*3
  s=self.fd['state_loading_scales']
  for k,co in enumerate(self.fd['scaled_columns_by_step'][-1]):self.assertAlmostEqual(co[6]/s[k],expected[k],delta=1e-9)
 def test_reference_not_mutated(self):
  before=ad.rate.sha(ad.rate.REFERENCE);ad.difference_reference(self.request,self.model);self.assertEqual(ad.rate.sha(ad.rate.REFERENCE),before)
 def header(self):
  return {'version':ad.VERSION,'backend':'native','catalogue_hash':self.hash,'model_definition':self.model,'model_sha256':ad.rate.sha(ad.rate.MODEL),'reference_sha256':ad.rate.sha(ad.rate.REFERENCE),'oracle_script_sha256':ad.rate.sha(ad.rate.ROOT/'tools/reference_barodesy2017.py'),'study_script_sha256':ad.rate.sha(ad.__file__),'parameter_order':list(self.model['parameters']),'columns':ad.COLUMNS,'steps':ad.STEPS,'budgets':{'FD':ad.FD_BUDGET,'refinement':ad.REFINEMENT_BUDGET,'identity':ad.IDENTITY_BUDGET,'primal':ad.rate.BUDGET},'claims':{'regular_instantaneous_material_AD':False,'zero_hydro_derivatives':False,'integrated':False,'admitted':False}}
 def test_report_model_hash(self):
  r=self.header();r['model_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'AD binding:model_sha256'):ad.assess(r,False)
 def test_report_study_hash(self):
  r=self.header();r['study_script_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'AD binding:study_script_sha256'):ad.assess(r,False)
 def test_report_no_budget_relaxation(self):
  r=copy.deepcopy(self.header());r['budgets']['FD']=1e-3
  with self.assertRaisesRegex(ValueError,'AD binding:budgets'):ad.assess(r,False)
 def test_report_no_hydro_claim(self):
  r=copy.deepcopy(self.header());r['claims']['zero_hydro_derivatives']=True
  with self.assertRaisesRegex(ValueError,'AD binding:claims'):ad.assess(r,False)
 def test_report_parameter_order(self):
  r=self.header();r['parameter_order'].reverse()
  with self.assertRaisesRegex(ValueError,'AD binding:parameter_order'):ad.assess(r,False)
 def test_report_step_binding(self):
  r=self.header();r['steps']=[1e-3]
  with self.assertRaisesRegex(ValueError,'AD binding:steps'):ad.assess(r,False)
 def test_artifact_shape_even_without_bytes(self):
  for artifact in ({'path':None,'sha256':'0'*64},{'path':'/x','sha256':False},{'path':'/x','sha256':'xyz'},{'path':'','sha256':'0'*64}):
   r=self.header();r.update(collection_complete=True,artifacts=[artifact])
   with self.assertRaisesRegex(ValueError,'artifact .* shape'):ad.assess(r,False)
 def test_exit_status_strict_correspondence(self):
  ad.native_exit(0,{'ok':True});ad.native_exit(1,{'ok':False});ad.native_exit(0,{},True)
  for code,response in [(1,{'ok':True}),(0,{'ok':False}),(0,{'ok':1}),(2,{'ok':False})]:
   with self.assertRaises(ValueError):ad.native_exit(code,response)
  with self.assertRaises(ValueError):ad.native_exit(1,{},True)
 def test_native_override_portability_and_hash(self):
  with tempfile.TemporaryDirectory()as directory:
   p=pathlib.Path(directory)/'moved.json';p.write_text('{"backend":"native"}')
   r={'native_report_path':'/unavailable/original.json','native_report_sha256':ad.rate.sha(p)}
   self.assertEqual(ad.native_transcript(r,p)['backend'],'native')
   r['native_report_sha256']='0'*64
   with self.assertRaises(ValueError):ad.native_transcript(r,p)
 def test_raw_partial_transport_retained(self):
  with tempfile.TemporaryDirectory()as directory:
   binary=pathlib.Path(directory)/'mock-binary';binary.write_bytes(b'not executed')
   output=pathlib.Path(directory)/'report.json';desc={'sha256':self.hash,'models':[self.model]}
   results=[SimpleNamespace(returncode=0,stdout=json.dumps(desc),stderr=''),SimpleNamespace(returncode=0,stdout='{"ok":false}',stderr='captured error')]
   with patch.object(ad.subprocess,'run',side_effect=results):
    with self.assertRaisesRegex(ValueError,'exit/status mismatch'):ad.native_report(binary,output)
   raw=json.loads(pathlib.Path(str(output)+'.transport.json').read_text());self.assertEqual(raw['calls'][-1]['stdout'],'{"ok":false}');self.assertEqual(raw['calls'][-1]['returncode'],0);self.assertEqual(raw['calls'][-1]['stderr'],'captured error');self.assertFalse(raw['complete'])
   partial=json.loads(output.read_text());self.assertFalse(partial['collection_complete']);self.assertEqual(partial['records'],[])
 def test_wrong_numerical_results_retained_before_acceptance(self):
  with tempfile.TemporaryDirectory()as directory:
   output=pathlib.Path(directory)/'raw.json'
   def call(w):return ad.rate.envelope(w,self.hash,[0.]*7)|{'jacobian':[[0.]*13 for _ in range(7)],'columns':ad.COLUMNS}
   report=ad.collect(call,'native',[{'path':'/not-read','sha256':'0'*64}],output)
   self.assertEqual(len(json.loads(output.read_text())['records']),21)
   with self.assertRaises(ValueError):ad.assess(report,False)
   self.assertEqual(json.loads(output.read_text())['records'][0]['response']['values'],[0.]*7)
 def test_point_one_hydro_exclusions(self):
  inv={c['id']:c['request']['increment']for c in ad.invalids(self.model)}
  self.assertEqual(inv['excluded-hydro-point-one'],[.1,.1,.1,0.,0.,0.]);self.assertEqual(inv['excluded-hydro-negative-point-one'],[-.1,-.1,-.1,0.,0.,0.])
 def test_frozen_entire_reference_recomputed(self):self.assertEqual(ad.verify_frozen_reference()['regular_cases'],21)
if __name__=='__main__':unittest.main()
