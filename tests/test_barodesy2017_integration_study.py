"""Synthetic finite-path protocol tests, no subprocess/native/Wasm execution."""
import copy,json,math,unittest,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from tools import barodesy2017_integration_study as s
from atlas.model import load

def response(r,model,state,ok=True,partial=False):
 return dict(ok=ok,message=''if ok else'synthetic rejection',state=state.copy(),model=r['model'],catalogue_hash=s.digest([model]),parameters=r['parameters'].copy(),initial=r['initial'].copy(),strain=r['strain'].copy(),integration_settings=s.settings(r),diagnostics=dict(substeps=2 if ok or partial else 0,iterations=0,rejected=1 if partial else 0,increment_fractions=[.125,.125]if partial else[.5,.5]if ok else[]))

def synthetic():
 ref,cases=s.checked_reference();model=load(s.MODEL_PATH);report=s.metadata(model,ref,'native')|dict(native_sha256='0'*64,runtime_descriptor=dict(models=[model],sha256=s.digest([model])),records=[],failure_probes=[])
 for name,c in cases.items():
  case=c['input']
  for tol,n in s.MATRIX:
   group=dict(case=name,tolerance=tol,partitions=n,calls=[]);report['records'].append(group);initial=case['initial'].copy();components=[]
   for _,strain in s.expected_calls(case,n):
    r=s.make_request(model,case,initial,strain,tol);components.extend(strain[:3]);v=math.fsum(components);z=s.target(case,v)
    coefficient={1e-4:1e-5,1e-6:1e-7,1e-8:1e-9}[tol]*(1 if n==1 else .5)*v/.03
    for j in range(3):z[j]+=case['p0']*coefficient
    z[6]+=coefficient*.001
    a=response(r,model,z);group['calls'].append(dict(request=r,response=a));initial=z.copy()
 control=copy.deepcopy(next(g for g in report['records']if(g['case'],g['tolerance'],g['partitions'])==(next(iter(cases)),1e-8,1))['calls'][0]);report['recovery_control']=control
 for w in s.probe_requests(model,cases):
  report['failure_probes'].append(w|dict(response=response(w['request'],model,w['request']['initial'],ok=w['kind']=='zero',partial=w['kind']=='budget'),recovery=copy.deepcopy(control)))
 return report

class IntegrationStudy(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.no_native=patch.object(s.subprocess,'run',side_effect=AssertionError('native execution forbidden in unit tests'));cls.no_native.start();cls.report=synthetic()
 @classmethod
 def tearDownClass(cls):cls.no_native.stop()
 def reject(self,change):
  r=copy.deepcopy(self.report);change(r)
  with self.assertRaises((ValueError,KeyError,TypeError)):s.verify(r)
 def test_complete45_by459(self):
  result=s.verify(self.report);self.assertEqual(result['trajectory_count'],45);self.assertEqual(result['call_count'],459)
 def test_metadata_does_not_alias_policy(self):
  _,cases=s.checked_reference();m=load(s.MODEL_PATH);r=s.metadata(m,s.reference.study(),'native');r['policy']['partition_shrink']=1.;self.assertEqual(s.POLICY['partition_shrink'],.35)
 def test_matrix_order_and_completeness_corruptions(self):
  for fn in[lambda r:r['records'].pop(),lambda r:r['records'].__setitem__(1,copy.deepcopy(r['records'][0])),lambda r:r['records'][0]['calls'].pop(),lambda r:r['records'][0].__setitem__('partitions',True),lambda r:r['records'][0].__setitem__('tolerance',True)]:self.reject(fn)
 def test_actual_chain_and_intermediate_points(self):
  self.reject(lambda r:r['records'][3]['calls'][1]['request']['initial'].__setitem__(0,25000.))
  self.reject(lambda r:r['records'][3]['calls'][1]['response']['state'].__setitem__(0,1e9))
  self.reject(lambda r:r['records'][3]['calls'][1]['response']['state'].__setitem__(6,-.1))
 def test_full_echo_and_numeric_types(self):
  changes=[lambda r:r['records'][0]['calls'][0]['response']['parameters'].__setitem__(4,999),lambda r:r['records'][0]['calls'][0]['response']['strain'].__setitem__(3,False),lambda r:r['records'][0]['calls'][0]['response'].__setitem__('ok',1),lambda r:r['records'][0]['calls'][0]['request']['settings'].__setitem__(2,45.),lambda r:r['records'][0]['calls'][0]['response']['state'].__setitem__(6,float('nan')),lambda r:r['records'][0]['calls'][0]['response']['integration_settings'].__setitem__('max_depth',20.)]
  for f in changes:self.reject(f)
 def test_settings_catalogue_and_protocol(self):
  for f in[lambda r:r['records'][0]['calls'][0]['request']['strain'].__setitem__(0,.002),lambda r:r['records'][0]['calls'][0]['response'].__setitem__('catalogue_hash','bad'),lambda r:r['records'][0]['calls'][0]['response']['integration_settings'].__setitem__('rate_tolerance',1.),lambda r:r['runtime_descriptor'].__setitem__('models',[])]:self.reject(f)
 def test_diagnostics_and_fractions(self):
  for f in[lambda r:r['records'][0]['calls'][0]['response']['diagnostics'].__setitem__('substeps',True),lambda r:r['records'][0]['calls'][0]['response']['diagnostics'].__setitem__('increment_fractions',[1.]),lambda r:r['records'][0]['calls'][0]['response']['diagnostics'].__setitem__('increment_fractions',[.2,.2]),lambda r:r['records'][0]['calls'][0]['response']['diagnostics'].__setitem__('error',float('nan'))]:self.reject(f)
 def test_identity_and_budget_relaxation(self):
  for f in[lambda r:r.__setitem__('source_sha256','0'*64),lambda r:r['source_pins'].__setitem__('cpp/main.cpp','0'*64),lambda r:r.__setitem__('reference_sha256','0'*64),lambda r:r['policy'].__setitem__('successive_refinement',1.),lambda r:r['claims'].__setitem__('AD_validated',True),lambda r:r['model_definition'].__setitem__('description','forged')]:self.reject(f)
 def test_fresh_reference_catches_payload_and_grid_corruption(self):
  ref=s.reference.study();ref['cases'][0]['exact'][0]['state'][0]+=1
  with self.assertRaises(ValueError):s.verify(self.report,ref)
  ref=s.reference.study();ref['cases'][0]['input']['initial'][0]+=1
  with self.assertRaises(ValueError):s.verify(self.report,ref)
 def test_failure_and_recovery_corruptions(self):
  mutations=[lambda r:r['failure_probes'].pop(),lambda r:r['failure_probes'][0]['response']['state'].__setitem__(0,1.),lambda r:r['failure_probes'][0]['response']['diagnostics'].__setitem__('increment_fractions',[]),lambda r:r['failure_probes'][0]['response']['diagnostics'].__setitem__('substeps',True),lambda r:r['failure_probes'][0]['request']['settings'].__setitem__(4,4),lambda r:r['failure_probes'][1]['response']['initial'].__setitem__(6,float('nan')),lambda r:r['failure_probes'][0]['recovery']['request']['strain'].__setitem__(0,.1),lambda r:r['failure_probes'][1]['recovery']['response']['state'].__setitem__(0,1.),lambda r:r['recovery_control']['response']['parameters'].__setitem__(0,False)]
  for f in mutations:self.reject(f)
 def test_refinement_gate_rejects_well_chained_in_budget_nonrefinement(self):
  _,cases=s.checked_reference();model=load(s.MODEL_PATH);records=copy.deepcopy(self.report['records'])
  for g in records:
   if g['tolerance']==1e-8:
    initial=cases[g['case']]['input']['initial'].copy();bias=initial[0]*1e-5
    for call in g['calls']:
     call['request']['initial']=initial.copy();call['response']['initial']=initial.copy()
     for j in range(3):call['response']['state'][j]+=bias
     initial=call['response']['state'].copy()
  with self.assertRaisesRegex(ValueError,'global refinement unresolved'):s.assess_records(records,model,cases)
 def test_partition_gate_rejects_well_chained_in_budget_nondecrease(self):
  _,cases=s.checked_reference();model=load(s.MODEL_PATH);records=copy.deepcopy(self.report['records'])
  for g in records:
   if g['tolerance']==1e-8 and g['partitions']==7:
    initial=cases[g['case']]['input']['initial'].copy();bias=initial[0]*1e-5
    for call in g['calls']:
     call['request']['initial']=initial.copy();call['response']['initial']=initial.copy()
     for j in range(3):call['response']['state'][j]+=bias
     initial=call['response']['state'].copy()
  with self.assertRaisesRegex(ValueError,'caller partition shrink unresolved'):s.assess_records(records,model,cases)
 def test_numeric_integer_serialization_is_portable(self):
  r=copy.deepcopy(self.report)
  def convert(x):
   if type(x)is float and x.is_integer():return int(x)
   if type(x)is list:return [convert(v)for v in x]
   if type(x)is dict:return {k:convert(v)for k,v in x.items()}
   return x
  # JavaScript JSON numbers do not preserve the token distinction 25000.0/25000.
  r=convert(r);s.verify(r)
 def test_wasm_recovery_receipt_and_parity_checks(self):
  wasm=copy.deepcopy(self.report);wasm['backend']='wasm';wasm.pop('native_sha256');wasm.update(persistent_recovery=True,native_report_sha256='f'*64,wasm_loader_sha256='1'*64,wasm_binary_sha256='2'*64)
  s.verify(wasm)
  # Patch only the unavailable native receipt, not source dependency hashes.
  original=s.sha
  with patch.object(s,'sha',side_effect=lambda path:'f'*64 if str(path)=='native-receipt'else original(path)):
   self.assertEqual(s.parity(wasm,self.report,'native-receipt'),0.)
  wasm['persistent_recovery']=1
  with self.assertRaises(ValueError):s.verify(wasm)
 def test_parity_rejects_individually_acceptable_well_chained_bias(self):
  wasm=copy.deepcopy(self.report);wasm['backend']='wasm';wasm.pop('native_sha256');wasm.update(persistent_recovery=True,native_report_sha256='f'*64,wasm_loader_sha256='1'*64,wasm_binary_sha256='2'*64)
  _,cases=s.checked_reference()
  for group in wasm['records']:
   initial=cases[group['case']]['input']['initial'].copy()
   for call in group['calls']:
    call['request']['initial']=initial.copy();call['response']['initial']=initial.copy()
    for j in range(3):call['response']['state'][j]+=1e-4
    initial=call['response']['state'].copy()
  control=copy.deepcopy(next(g for g in wasm['records']if(g['case'],g['tolerance'],g['partitions'])==(next(iter(cases)),1e-8,1))['calls'][0])
  wasm['recovery_control']=control
  for probe in wasm['failure_probes']:probe['recovery']=copy.deepcopy(control)
  s.verify(wasm) # remains independently acceptable under the finite-update budgets
  original=s.sha
  with patch.object(s,'sha',side_effect=lambda path:'f'*64 if str(path)=='native-receipt'else original(path)):
   with self.assertRaisesRegex(ValueError,'native/Wasm state parity budget'):s.parity(wasm,self.report,'native-receipt')
class RawTransportTests(unittest.TestCase):
 def test_malformed_native_stdout_is_saved_before_parse(self):
  _,cases=s.checked_reference();m=load(s.MODEL_PATH);c=next(iter(cases.values()))['input'];r=s.make_request(m,c,c['initial'],c['increments'][0],1e-8)
  with tempfile.TemporaryDirectory()as temp:
   path=Path(temp)/'transport.jsonl'
   with patch.object(s.subprocess,'run',return_value=SimpleNamespace(stdout='{broken',stderr='retained stderr',returncode=7)):
    with self.assertRaises(json.JSONDecodeError):s.native_call('fake-solver',r,path)
   row=json.loads(path.read_text());self.assertEqual(row['stdout'],'{broken');self.assertEqual(row['stderr'],'retained stderr');self.assertEqual(row['returncode'],7);self.assertEqual(row['request'],r);self.assertEqual(row['args'][0],'fake-solver')
 def test_status_failure_and_timeout_are_retained(self):
  _,cases=s.checked_reference();m=load(s.MODEL_PATH);c=next(iter(cases.values()))['input'];r=s.make_request(m,c,c['initial'],c['increments'][0],1e-8)
  with tempfile.TemporaryDirectory()as temp:
   path=Path(temp)/'transport.jsonl'
   with patch.object(s.subprocess,'run',return_value=SimpleNamespace(stdout='{"ok":true}',stderr='diagnostic',returncode=9)):
    with self.assertRaisesRegex(ValueError,'native exit status'):s.native_call('fake',r,path)
   with patch.object(s.subprocess,'run',side_effect=s.subprocess.TimeoutExpired(['fake'],60,output=b'partial',stderr=b'timeout stderr')):
    with self.assertRaises(s.subprocess.TimeoutExpired):s.native_call('fake',r,path)
   rows=[json.loads(x)for x in path.read_text().splitlines()];self.assertEqual(len(rows),2);self.assertEqual(rows[0]['returncode'],9);self.assertEqual(rows[1]['stdout'],'partial');self.assertEqual(rows[1]['exception'],'TimeoutExpired')
 def test_descriptor_is_retained_before_parse(self):
  with tempfile.TemporaryDirectory()as temp:
   output=Path(temp)/'native.json'
   with patch.object(s.subprocess,'run',return_value=SimpleNamespace(stdout='not JSON',stderr='describe stderr',returncode=0)):
    with self.assertRaises(json.JSONDecodeError):s.run('fake',output)
   row=json.loads(output.with_suffix('.transport.jsonl').read_text());self.assertEqual(row['request'],{'mode':'describe'});self.assertEqual(row['args'],['fake','--describe']);self.assertEqual(row['stdout'],'not JSON')
if __name__=='__main__':unittest.main()
