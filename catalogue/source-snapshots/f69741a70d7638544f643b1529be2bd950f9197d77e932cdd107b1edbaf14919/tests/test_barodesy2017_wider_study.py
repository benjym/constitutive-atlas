"""Synthetic protocol/corruption tests; no compiled engine is called here."""
import copy,json,math,tempfile,unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
from tools import barodesy2017_wider_study as s
from atlas.model import load

def response(r,model,state,ok=True,partial=False):
 return dict(ok=ok,message=''if ok else'synthetic rejection',state=state.copy(),model=r['model'],catalogue_hash=s.digest([model]),parameters=r['parameters'].copy(),initial=r['initial'].copy(),strain=r['strain'].copy(),integration_settings=s.settings(r),diagnostics=dict(substeps=2 if ok or partial else 0,iterations=0,rejected=6 if partial else 0,increment_fractions=[.0078125]*2 if partial else[.5]*2 if ok else[]))

def synthetic(ref,cases,points,model):
 report=s.metadata(model,ref,'native')|dict(native_sha256='0'*64,transport_sha256='a'*64,runtime_descriptor=dict(models=[model],sha256=s.digest([model])),records=[],failure_probes=[])
 for name,case in cases.items():
  for tol,n in s.MATRIX:
   group=dict(case=name,tolerance=tol,partitions=n,calls=[]);report['records'].append(group);initial=case['initial'].copy()
   for p in points[name,n]['points'][1:]:
    r=s.make_request(model,case,initial,p['increment'],tol);z=s.point_state(p).copy();bias={1e-4:1e-6,1e-6:1e-8,1e-8:1e-10}[tol]*(1 if n==1 else .5)*p['index']/(3*n)
    z[0]+=case['stress_scale']*bias;z[6]=s.exact_void(case['initial'],p)+bias*.001
    a=response(r,model,z);group['calls'].append(dict(request=r,response=a));initial=z.copy()
 report['transaction_prefix'],report['recovery_control']=s.committed_controls(report['records'],cases)
 for w in s.probe_requests(report['recovery_control']):report['failure_probes'].append(w|dict(response=response(w['request'],model,w['request']['initial'],ok=w['kind']=='zero',partial=w['kind']=='budget'),recovery=copy.deepcopy(report['recovery_control'])))
 return report

class WiderStudy(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.no_native=patch.object(s.subprocess,'run',side_effect=AssertionError('native forbidden'));cls.no_native.start()
  cls.ref,cls.cases,cls.points=s.checked_reference();cls.model=load(s.MODEL_PATH)
  # Fresh numerical replay is exercised once above. All remaining cases concern
  # assessor corruption handling, so reuse identical fresh payload in the mock.
  cls.fresh=patch.object(s.reference,'study',side_effect=lambda:copy.deepcopy(cls.ref));cls.fresh.start();cls.report=synthetic(cls.ref,cls.cases,cls.points,cls.model)
 @classmethod
 def tearDownClass(cls):cls.fresh.stop();cls.no_native.stop()
 def reject(self,fn):
  r=copy.deepcopy(self.report);fn(r)
  with self.assertRaises((ValueError,KeyError,TypeError)):s.verify(r)
 def test_full48_by576(self):
  q=s.verify(self.report);self.assertEqual((q['trajectory_count'],q['call_count']),(48,576))
 def test_model_policy_no_alias(self):
  r=s.metadata(self.model,self.ref,'native');r['policy']['partition_shrink']=1;self.assertEqual(s.POLICY['partition_shrink'],.35)
 def test_matrix_completeness_and_labels(self):
  for fn in[lambda r:r['records'].pop(),lambda r:r['records'].__setitem__(1,copy.deepcopy(r['records'][0])),lambda r:r['records'][0]['calls'].pop(),lambda r:r['records'][0].__setitem__('partitions',True),lambda r:r['records'][0].__setitem__('tolerance',True)]:self.reject(fn)
 def test_chain_every_callerpoint_and_void(self):
  for fn in[lambda r:r['records'][3]['calls'][1]['request']['initial'].__setitem__(0,1.),lambda r:r['records'][3]['calls'][1]['response']['state'].__setitem__(0,1e9),lambda r:r['records'][3]['calls'][1]['response']['state'].__setitem__(6,-.1),lambda r:r['records'][3]['calls'][1]['response']['state'].__setitem__(6,.2)]:self.reject(fn)
 def test_echo_settings_types_and_catalogue(self):
  fs=[lambda a:a['parameters'].__setitem__(4,999),lambda a:a['strain'].__setitem__(3,False),lambda a:a.__setitem__('ok',1),lambda a:a['state'].__setitem__(6,float('nan')),lambda a:a['integration_settings'].__setitem__('max_depth',20.),lambda a:a['integration_settings'].__setitem__('rate_tolerance',True),lambda a:a.__setitem__('catalogue_hash','bad')]
  for f in fs:self.reject(lambda r:f(r['records'][0]['calls'][0]['response']))
  self.reject(lambda r:r['records'][0]['calls'][0]['request']['settings'].__setitem__(2,45.))
 def test_diag_pair_depth_count_and_success_message(self):
  fs=[lambda a:a['diagnostics'].__setitem__('substeps',True),lambda a:a['diagnostics'].__setitem__('increment_fractions',[.25,.75]),lambda a:a['diagnostics'].__setitem__('increment_fractions',[.2,.2]),lambda a:a['diagnostics'].__setitem__('error',float('nan')),lambda a:a.__setitem__('message','warning')]
  for f in fs:self.reject(lambda r:f(r['records'][0]['calls'][0]['response']))
 def test_identity_policy_and_reference_corruption(self):
  for f in[lambda r:r.__setitem__('source_sha256','0'*64),lambda r:r['source_pins'].__setitem__('cpp/main.cpp','0'*64),lambda r:r.__setitem__('reference_sha256','0'*64),lambda r:r['policy'].__setitem__('partition_shrink',1.),lambda r:r['claims'].__setitem__('AD_validated',True),lambda r:r['runtime_descriptor'].__setitem__('models',[])]:self.reject(f)
  ref=copy.deepcopy(self.ref);ref['scalar_cases'][0]['points'][1]['state160'][0]+=1
  with self.assertRaises(ValueError):s.verify(self.report,ref)
  ref=copy.deepcopy(self.ref);ref['tensor_cases'][0]['grids'][-1]['trajectory'][1][0]+=1
  with self.assertRaises(ValueError):s.verify(self.report,ref)
 def test_seven_state_interior_guard(self):
  for z in[[1.,1.,-1.,0.,0.,0.,.8],[1.,1.,1.,0.,0.,0.,-.1],[1.,1.,1e-20,0.,0.,0.,.8]]:
   with self.assertRaises(ValueError):s.check_interior(z)
  s.check_interior([1.,1.,1.,0.,0.,0.,.8])
 def test_prefix_sameparent_rollback_recovery(self):
  for f in[lambda r:r['failure_probes'].pop(),lambda r:r['transaction_prefix'][1]['response']['state'].__setitem__(0,1.),lambda r:r['failure_probes'][0]['request']['settings'].__setitem__(4,4),lambda r:r['failure_probes'][0]['response']['state'].__setitem__(0,1.),lambda r:r['failure_probes'][0]['response']['diagnostics'].__setitem__('increment_fractions',[]),lambda r:r['failure_probes'][1]['request'].__setitem__('strain',[.9,0.,0.,0.,0.,0.]),lambda r:r['failure_probes'][0]['recovery']['response']['state'].__setitem__(0,1.)]:self.reject(f)
 def test_same_parent_is_actual_valid_prefix(self):
  p,c=s.committed_controls(self.report['records'],self.cases);self.assertEqual(c['request']['initial'],p[1]['response']['state']);self.assertEqual(len(p),2);self.assertEqual(p[1]['request']['initial'],p[0]['response']['state']);self.assertNotEqual(c['request']['initial'],next(c['initial']for c in self.cases.values()if c['kind']=='tensor'))
  probes=s.probe_requests(c);self.assertEqual(probes[1]['request']['strain'],[.9,.9,.9,0.,0.,0.])
 def test_nonrefinement_rejected_with_valid_chains(self):
  records=copy.deepcopy(self.report['records'])
  for g in records:
   if g['tolerance']==1e-8:
    initial=self.cases[g['case']]['initial'].copy()
    for c in g['calls']:
     c['request']['initial']=initial.copy();c['response']['initial']=initial.copy();c['response']['state'][0]+=self.cases[g['case']]['stress_scale']*1e-5;initial=c['response']['state'].copy()
  with self.assertRaisesRegex(ValueError,'global refinement'):s.assess_records(records,self.model,self.cases,self.points)
 def test_partition_noncontraction_rejected(self):
  records=copy.deepcopy(self.report['records'])
  for g in records:
   if g['partitions']==7:
    case=self.cases[g['case']];initial=case['initial'].copy();coefficient={1e-4:1e-6,1e-6:1e-8,1e-8:1e-9}[g['tolerance']]
    for c,p in zip(g['calls'],self.points[g['case'],7]['points'][1:]):
     c['request']['initial']=initial.copy();c['response']['initial']=initial.copy();c['response']['state'][0]=s.point_state(p)[0]+case['stress_scale']*coefficient*p['index']/21;initial=c['response']['state'].copy()
  with self.assertRaisesRegex(ValueError,'caller partition shrink'):s.assess_records(records,self.model,self.cases,self.points)
 def test_every_channel_is_compared(self):
  for i in range(7):
   self.reject(lambda r:r['records'][0]['calls'][0]['response']['state'].__setitem__(i,1e9))
 def test_collector_checkpoints_bad_response_before_acceptance(self):
  with tempfile.TemporaryDirectory()as d:
   out=Path(d)/'raw.json';binary=Path(d)/'synthetic-solver';binary.write_text('not an executable')
   descriptor=SimpleNamespace(returncode=0,stdout=json.dumps(self.report['runtime_descriptor']))
   with patch.object(s,'checked_reference',return_value=(self.ref,self.cases,self.points)),patch.object(s,'native_transport',return_value=descriptor),patch.object(s,'native_call',return_value={'ok':False}):
    with self.assertRaises(ValueError):s.run(binary,out)
   raw=json.loads(out.read_text());self.assertEqual(raw['records'][0]['calls'][0]['response'],{'ok':False})
 def test_native_transport_retained_before_parse_or_status(self):
  request=self.report['records'][0]['calls'][0]['request']
  for stdout,code in[('not-json',1),(json.dumps(self.report['records'][0]['calls'][0]['response']),9)]:
   with tempfile.TemporaryDirectory()as d:
    path=Path(d)/'transport.jsonl'
    with patch.object(s.subprocess,'run',return_value=SimpleNamespace(stdout=stdout,stderr='diagnostic',returncode=code)):
     with self.assertRaises((ValueError,json.JSONDecodeError)):s.native_call('never-executed',request,path)
    row=json.loads(path.read_text());self.assertEqual(row['stdout'],stdout);self.assertEqual(row['returncode'],code)
 def test_integer_number_serialization_portable(self):
  def numbers(x):
   if type(x)is float and x.is_integer():return int(x)
   if type(x)is list:return [numbers(v)for v in x]
   if type(x)is dict:return {k:numbers(v)for k,v in x.items()}
   return x
  s.verify(numbers(copy.deepcopy(self.report)))
 def test_wasm_binding_and_parity(self):
  w=copy.deepcopy(self.report);w.update(backend='wasm',persistent_recovery=True,native_report_sha256='f'*64,wasm_loader_sha256='1'*64,wasm_binary_sha256='2'*64);w.pop('native_sha256');s.verify(w)
  original=s.sha
  with patch.object(s,'sha',side_effect=lambda p:'f'*64 if str(p)=='native-receipt'else original(p)),patch.object(s,'verify_transport')as raw:
   self.assertEqual(s.parity(w,self.report,'native-receipt','wasm-raw','native-raw'),0.);self.assertEqual(raw.call_count,2)
  w['persistent_recovery']=1
  with self.assertRaises(ValueError):s.verify(w)

class RawTransport(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  # Full metadata/reference checks are covered above; raw binding is an
  # independently checked receipt against a small synthetic report protocol.
  pass
 def fixture(self,backend='native'):
  ref,cases,points=s.checked_reference();model=load(s.MODEL_PATH);r=synthetic(ref,cases,points,model);r['backend']=backend
  entries=[dict(request=dict(mode='describe'),response=r['runtime_descriptor'])]+[c for g in r['records']for c in g['calls']]+[c for p in r['failure_probes']for c in(p,p['recovery'])];raw=[]
  for i,c in enumerate(entries):
   if backend=='native':
    q=c['request'];args=['synthetic-solver','--describe']if i==0 else['synthetic-solver','--mode','integrate','--model',q['model'],'--parameters',s.csv(q['parameters']),'--initial',s.csv(q['initial']),'--strain',s.csv(q['strain']),'--integration-settings',s.csv(q['settings'])]
    row=dict(backend=backend,args=args,request=c['request'],stdout=json.dumps(c['response']),stderr='',returncode=0 if i==0 or c['response']['ok']else 1)
   else:
    q=c['request'];row=dict(backend=backend,name='atlas_describe'if i==0 else'atlas_integrate_with_settings',types=[]if i==0 else['string']*5,args=[]if i==0 else[q['model']]+[s.csv(q[k])for k in('parameters','initial','strain','settings')],request=q,raw=json.dumps(c['response']))
   raw.append(row)
  return r,raw
 def test_raw_binding_and_corruptions(self):
  # One fresh reference replay suffices for both backend receipt fixtures.
  ref,cases,points=s.checked_reference()
  with patch.object(s,'checked_reference',return_value=(ref,cases,points)),tempfile.TemporaryDirectory()as d:
   p=Path(d)/'raw.jsonl'
   for backend in('native','wasm'):
    r,rows=self.fixture(backend)
    def bind():p.write_text(''.join(json.dumps(x)+'\n'for x in rows));r['transport_sha256']=s.sha(p)
    bind();self.assertEqual(s.verify_transport(r,p)['rows'],583)
    save=copy.deepcopy(rows)
    for change in[lambda:rows.pop(),lambda:rows[1]['request']['initial'].__setitem__(0,1.),lambda:rows[1].__setitem__('stdout'if backend=='native'else'raw','{}'),lambda:rows[1]['args'].__setitem__(0,'forged')]:
     rows=copy.deepcopy(save);change();bind()
     with self.assertRaises((ValueError,KeyError)):s.verify_transport(r,p)
    if backend=='native':
     for code in(True,1,9):
      rows=copy.deepcopy(save);rows[1]['returncode']=code;bind()
      with self.assertRaises(ValueError):s.verify_transport(r,p)

if __name__=='__main__':unittest.main()
