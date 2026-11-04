"""Pure reference/assessor/transport-mock tests; not actual generated Jet evidence."""
import copy,json,pathlib,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import patch
from tools import barodesy2017_hydro_ad as h
class HydroStudy(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.model,cls.hash=h.rate.catalogue();cls.cases=h.cases();cls.refs={c['id']:h.expected(c)for c in cls.cases};cls.valid={h.rate.digest(h.wire(c,cls.model)):cls.refs[c['id']]for c in cls.cases}
  def call(w):
   ref=cls.valid.get(h.rate.digest(w));return {'ok':ref is not None,'model':w['model'],'catalogue_hash':cls.hash,'parameters':copy.deepcopy(w['parameters']),'state':copy.deepcopy(w['state']),'increment':copy.deepcopy(w['increment']),'values':copy.deepcopy(ref['values'])if ref else None,'jacobian':copy.deepcopy(ref['jacobian'])if ref else None,'columns':h.COLUMNS[:],'message':''if ref else h.FAILURE}
  cls.call=staticmethod(call);cls.report=h.collect(call,'native',[{'path':'/synthetic/not-executed','sha256':'0'*64}])
 def rejected(self,mutate):
  r=copy.deepcopy(self.report);mutate(r)
  with self.assertRaises((ValueError,TypeError,KeyError)):h.assess(r,False)
 def test_36_case_reference_matrix(self):
  self.assertEqual(len(self.cases),36);self.assertEqual({c['increment'][0]for c in self.cases},{-1.,-.1,-.001,.001,.1,1.});self.assertEqual(len({tuple(c['parameters'].values())for c in self.cases}),3)
  self.assertLess(max(float(r['maximum_precision_difference'])for r in self.refs.values()),1e-94)
 def test_mock_verifier_control_only(self):self.assertEqual(h.assess(self.report,False)['exact_hydro_cases'],36)
 def test_actual_frozen_reference_recomputed(self):self.assertEqual(h.verify_frozen(),36)
 def test_actual_python_primal_only(self):
  for c in self.cases:
   w=h.wire(c,self.model);r=h.rate.python_call(w,self.model,self.hash);self.assertIs(r['ok'],True);expected=self.refs[c['id']]['values']
   for a,b in zip(r['values'][:6],expected[:6]):self.assertLessEqual(abs(a-b)/max(1.,abs(b)),h.BUDGET)
   self.assertLessEqual(h.rate.ulp_distance(r['values'][6],expected[6]),4)
 def test_explicit_hydro_domain_rejections_are_not_scope_only(self):
  rows=[c for c in h.invalids(self.model)if c['id'].startswith('hydro-domain-')]
  self.assertEqual(len(rows),28);self.assertEqual({r['request']['increment'][0]for r in rows},{-.1,.1})
  for row in rows:
   w=row['request'];de=w['increment'];self.assertEqual(de[:3],[de[0]]*3);self.assertEqual(de[3:],[0.]*3);self.assertGreater(abs(de[0]),0)
   result=h.rate.python_call(w,self.model,self.hash);self.assertIs(result['ok'],False,row['id'])
 def test_added_hydro_domain_response_and_recovery_corruptions(self):
  index=next(i for i,c in enumerate(self.report['invalid_records'])if c['id'].startswith('hydro-domain-'))
  self.rejected(lambda r:r['invalid_records'][index]['response'].__setitem__('ok',True))
  self.rejected(lambda r:r['invalid_records'][index]['recovery']['values'].__setitem__(0,1e99))
 def test_one_ulp_nonhydro_rejected_by_reference(self):
  c=self.cases[0];w=next(x['request']for x in h.invalids(self.model)if x['id']=='hydro-one-ulp-nonhydro')
  with self.assertRaises(ValueError):h.reference.exact_hydro(w['state'][:6],w['state'][6],w['increment'],c['parameters'])
 def test_zero_rejected_by_reference(self):
  c=self.cases[0]
  with self.assertRaises(ValueError):h.reference.exact_hydro(c['state']['sigma'],.8,[0.]*6,c['parameters'])
 def test_indefinite_rejected_by_reference(self):
  c=self.cases[0]
  with self.assertRaises(ValueError):h.reference.exact_hydro([1.,1.,-1.,0.,0.,0.],.8,c['increment'],c['parameters'])
 def test_wrong_component(self):self.rejected(lambda r:r['records'][0]['response']['jacobian'][0].__setitem__(0,1e20))
 def test_wrong_void_value(self):self.rejected(lambda r:r['records'][0]['response']['values'].__setitem__(6,0.))
 def test_wrong_void_derivative(self):self.rejected(lambda r:r['records'][0]['response']['jacobian'][6].__setitem__(6,0.))
 def test_structural_zero(self):self.rejected(lambda r:r['records'][0]['response']['jacobian'][0].__setitem__(10,1e-100))
 def test_boolean_derivative(self):self.rejected(lambda r:r['records'][0]['response']['jacobian'][0].__setitem__(0,True))
 def test_nan_derivative(self):self.rejected(lambda r:r['records'][0]['response']['jacobian'][0].__setitem__(0,float('nan')))
 def test_wrong_shape(self):self.rejected(lambda r:r['records'][0]['response']['jacobian'][0].pop())
 def test_state_echo(self):self.rejected(lambda r:r['records'][0]['response']['state'].__setitem__(0,1.))
 def test_column_order(self):self.rejected(lambda r:r['columns'].reverse())
 def test_model_binding(self):self.rejected(lambda r:r['model_definition'].__setitem__('name','false'))
 def test_parameter_order(self):self.rejected(lambda r:r['parameter_order'].reverse())
 def test_claim_promotion(self):self.rejected(lambda r:r['claims'].__setitem__('zero_loading_AD',True))
 def test_budget_relaxation(self):self.rejected(lambda r:r['budgets'].__setitem__('component',1e-3))
 def test_forged_reference(self):self.rejected(lambda r:r['records'][0]['reference']['jacobian'][0].__setitem__(0,1.))
 def test_incomplete_collection(self):self.rejected(lambda r:r.__setitem__('collection_complete',False))
 def test_invalid_has_no_usable_jac(self):self.rejected(lambda r:r['invalid_records'][0]['response'].__setitem__('jacobian',[[0.]*13 for _ in range(7)]))
 def test_recovery_request_bound(self):self.rejected(lambda r:r['invalid_records'][0]['recovery']['increment'].__setitem__(0,0.))
 def test_artifact_shape_without_bytes(self):
  for a in ({'path':None,'sha256':'0'*64},{'path':'/x','sha256':True},{'path':'/x','sha256':'x'}):self.rejected(lambda r:r.__setitem__('artifacts',[a]))
 def test_batch_single_process_and_raw_retention(self):
  with tempfile.TemporaryDirectory()as d:
   binary=pathlib.Path(d)/'not-executed';binary.write_bytes(b'mock only');output=pathlib.Path(d)/'report.json';requests=[h.wire(c,self.model)for c in self.cases]
   for c in h.invalids(self.model):requests.extend([c['request'],requests[0]])
   desc={'sha256':self.hash,'models':[self.model]};responses=[json.dumps(desc)]+[json.dumps(self.call(w))for w in requests]
   result=SimpleNamespace(returncode=0,stdout='\n'.join(responses)+'\n',stderr='')
   with patch.object(h.subprocess,'run',return_value=result)as run:h.native_report(binary,output);self.assertEqual(run.call_count,1);self.assertEqual(run.call_args.args[0],[str(binary.resolve()),'--stream'])
   raw=json.loads(pathlib.Path(str(output)+'.transport.json').read_text());self.assertEqual(len(raw['request_lines']),len(requests)+1);self.assertEqual(raw['stdout'],result.stdout);self.assertTrue(raw['complete'])
 def test_bad_numerical_collection_remains_on_disk(self):
  with tempfile.TemporaryDirectory()as d:
   output=pathlib.Path(d)/'raw.json'
   def bad(w):
    r=self.call(w)
    if r['ok']:r['values'][0]=1e99
    return r
   r=h.collect(bad,'native',[{'path':'/not-read','sha256':'0'*64}],output)
   with self.assertRaises(ValueError):h.assess(r,False)
   self.assertEqual(h.rate.read(output)['records'][0]['response']['values'][0],1e99)
 def test_malformed_native_raw_output_retained(self):
  with tempfile.TemporaryDirectory()as d:
   binary=pathlib.Path(d)/'not-executed';binary.write_bytes(b'mock');output=pathlib.Path(d)/'raw.json'
   with patch.object(h.subprocess,'run',return_value=SimpleNamespace(returncode=2,stdout='partial raw',stderr='failure')):
    with self.assertRaises(ValueError):h.native_report(binary,output)
   raw=h.rate.read(str(output)+'.transport.json');self.assertEqual(raw['stdout'],'partial raw');self.assertEqual(raw['stderr'],'failure');self.assertEqual(raw['returncode'],2)
 def test_no_retained_writes(self):
  p=h.ROOT/'catalogue/investigations/barodesy2017-hydro-ad-v1/reference.json';before=h.rate.sha(p);h.verify_frozen();self.assertEqual(h.rate.sha(p),before)
if __name__=='__main__':unittest.main()
