"""Reject corrupted operator evidence independently of its stored assessment."""
import copy
import unittest
from tools.expm_study import (assess, catalogue, CONTEXTS, invalid_requests,
                             OPERATOR_VERSION, reference, REFERENCE, sha, VERSION,
                             VALUE_BUDGET, JACOBIAN_BUDGET)

class ExpmEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  _, h=catalogue(); ref=reference()
  def response(a, success=True):
   return dict(operator_version=OPERATOR_VERSION,catalogue_hash=h,input=a,mode=0,ok=success,contexts=dict.fromkeys(CONTEXTS,True),primitive_ok=success,schema_ok=success)
  records=[]
  for c in ref['cases']:
   r=response(c['input'])
   for prefix in ('','schema_'):
    r[prefix+'values']=c['oracle']['value'];r[prefix+'jacobian']=c['oracle']['jacobian']
   records.append(dict(id=c['id'],request=dict(csv=','.join(map(repr,c['input'])),input=c['input'],mode=0),response=r))
  invalid=[]
  for request in invalid_requests():
   r=response(request.get('input'),False) if request['parseable'] else dict(ok=False,error='invalid probe input or missing isolated fixtures')
   if request['parseable']:
    for prefix in ('','schema_'):r[prefix+'values']=None;r[prefix+'jacobian']=None
   invalid.append(dict(request=request,response=r,recovery=copy.deepcopy(records[0]['response'])))
  cls.report=dict(version=VERSION,backend='wasm',operator_version=OPERATOR_VERSION,catalogue_hash=h,reference_sha256=sha(REFERENCE),budgets=dict(value=VALUE_BUDGET,jacobian=JACOBIAN_BUDGET),records=records,invalid_records=invalid)
 def reject(self, change):
  r=copy.deepcopy(self.report);change(r)
  with self.assertRaises((ValueError,KeyError,TypeError)):assess(r,fresh=False)
 def test_retained_packet_identity_and_fresh_decimal_replay(self):
  from tools.expm_study import ROOT, read, verify_parity
  packet=ROOT/'catalogue/investigations/symmetric-expm-v1'
  manifest=read(packet/'manifest.json')
  for path,pin in manifest['files'].items():
   with self.subTest(path=path):self.assertEqual(sha(ROOT/path),pin)
  native=read(packet/'native.json');wasm=read(packet/'wasm.json')
  self.assertEqual(assess(native)['cases'],44);self.assertEqual(assess(wasm)['cases'],44)
  self.assertLessEqual(verify_parity(wasm,native,packet/'native.json'),2e-13)
 def test_parity_binding_and_numerical_corruption(self):
  from tools.expm_study import ROOT, read, verify_parity
  packet=ROOT/'catalogue/investigations/symmetric-expm-v1'
  native=read(packet/'native.json');wasm=read(packet/'wasm.json')
  broken=copy.deepcopy(wasm);broken['native_report_sha256']='0'*64
  with self.assertRaises(ValueError):verify_parity(broken,native,packet/'native.json')
  broken=copy.deepcopy(wasm);broken['records'][0]['response']['schema_jacobian'][5][4]=.1
  with self.assertRaises(ValueError):verify_parity(broken,native,packet/'native.json')
 def test_complete_reference_transcript(self):
  a=assess(self.report,fresh=False);self.assertEqual(a['cases'],44);self.assertEqual(a['contexts_per_call'],29);self.assertEqual(a['invalid_cases'],23)
 def test_missing_case_or_input_binding(self):
  self.reject(lambda r:r['records'].pop())
  self.reject(lambda r:r['records'][0]['request']['input'].__setitem__(0,1.))
  self.reject(lambda r:r['records'][0]['response']['input'].__setitem__(0,1.))
 def test_complete_full_jacobian_required(self):
  self.reject(lambda r:r['records'][0]['response']['jacobian'].pop())
  self.reject(lambda r:r['records'][0]['response']['schema_jacobian'][5].__setitem__(5,1.1))
  self.reject(lambda r:r['records'][0]['response']['jacobian'][2].__setitem__(3,True))
 def test_failure_context_not_just_count(self):
  self.reject(lambda r:r['records'][0]['response']['contexts'].__setitem__('history_active_failure_rollback',False))
  self.reject(lambda r:r['records'][0]['response']['contexts'].__setitem__('invented',True))
 def test_nonfinite_or_wrong_values(self):
  self.reject(lambda r:r['records'][0]['response']['values'].__setitem__(1,float('nan')))
  self.reject(lambda r:r['records'][0]['response']['schema_values'].__setitem__(2,1.01))
 def test_identity_and_budgets(self):
  self.reject(lambda r:r.__setitem__('reference_sha256','0'*64))
  self.reject(lambda r:r['records'][0]['response'].__setitem__('operator_version','future'))
  self.reject(lambda r:r['records'][0]['response'].__setitem__('catalogue_hash','0'*64))
  self.reject(lambda r:r['budgets'].__setitem__('jacobian',1.))
 def test_boolean_numeric_aliases_rejected_in_loaded_transcript(self):
  from tools.expm_study import ROOT,read
  original=read(ROOT/'catalogue/investigations/symmetric-expm-v1/wasm.json')
  for change in ('request-input','recovery-ok','recovery-value','parser-ok','parseable-flag'):
   r=copy.deepcopy(original)
   if change=='request-input':r['records'][0]['request']['input'][0]=False
   elif change=='recovery-ok':r['invalid_records'][0]['recovery']['ok']=1
   elif change=='recovery-value':r['invalid_records'][0]['recovery']['values'][0]=True
   elif change=='parser-ok':r['invalid_records'][2]['response']['ok']=0
   else:r['invalid_records'][2]['request']['parseable']=0
   with self.subTest(change=change),self.assertRaises(ValueError):assess(r,fresh=False)
 def test_invalid_calls_and_recovery(self):
  self.reject(lambda r:r['invalid_records'].pop())
  self.reject(lambda r:r['invalid_records'][0]['response'].__setitem__('primitive_ok',True))
  self.reject(lambda r:r['invalid_records'][0]['recovery'].__setitem__('ok',False))

if __name__=='__main__':unittest.main()
