"""Synthetic transport corruption tests only; never execute a material binary."""
import copy,json,math,pathlib,tempfile,types,unittest
from unittest.mock import patch
from tools import clay2014_rate_study as c
class Corruption(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=pathlib.Path(self.tmp.name)
  self.model={'id':'synthetic','parameters':{'K':{}},'state':[{'name':'sigma','shape':'sym'},{'name':'e','shape':'scalar'}]}
  normal=dict(id='normal',parameters={'K':2.},state=[100.,100.,100.,0.,0.,0.,.5],increment=[.01,0.,0.,0.,0.,0.],expected=[1.,2.,3.,0.,0.,0.,-.015],stress_scale=math.sqrt(30000)*.01,void_scale=1.)
  zero=dict(normal,id='zero',increment=[0.]*6,expected=[0.]*7,stress_scale=0.)
  bad=dict(normal,id='bad',parameters={'K':-1.})
  self.ref={'parameter_order':['K'],'cases':[normal,zero],'invalid_cases':[bad],'policy':{'stress_scaled_bound':1e-10,'void_scaled_bound':1e-10,'stress_absolute_floor_Pa':1e-12,'void_absolute_floor':1e-12}}
  self.patches=[patch.object(c,'checked_reference',return_value=(self.ref,self.model)),patch.object(c,'identity',side_effect=lambda ref,model,backend:{'version':'synthetic','backend':backend,'source_pins':{'x':'a'*64}})]
  for p in self.patches:p.start();self.addCleanup(p.stop)
 def report(self,backend='native'):
  targets={x['id']:x for x in self.ref['cases']};calls=[]
  for r in c.requests(self.ref,self.model):
   ok=r['role']!='invalid';a={k:copy.deepcopy(r[k])for k in('model','parameters','state','increment')};a.update(ok=ok,catalogue_hash=c.digest([self.model]),values=targets[r['id']]['expected'][:]if ok else None,message=''if ok else 'invalid domain');calls.append({'request':r,'response':a})
  d={'version':'synthetic','backend':backend,'source_pins':{'x':'a'*64},'descriptor':{'models':[copy.deepcopy(self.model)],'sha256':c.digest([self.model])},'calls':calls,'persistent_instance':True,'transport_sha256':'b'*64}
  if backend=='native':d['native_sha256']='c'*64
  else:d.update(native_report_sha256='c'*64,wasm_loader_sha256='d'*64,wasm_binary_sha256='e'*64)
  return d
 def corrupt(self,fn):
  r=self.report();fn(r)
  with self.assertRaises((ValueError,TypeError)):c.verify(r)
 def test_control(self):self.assertEqual(c.verify(self.report())['call_count'],4)
 def test_wrong_full_seventh_rate(self):self.corrupt(lambda r:r['calls'][0]['response']['values'].__setitem__(6,.001))
 def test_six_rate_response(self):self.corrupt(lambda r:r['calls'][0]['response'].__setitem__('values',[0.]*6))
 def test_bool_response_value(self):self.corrupt(lambda r:r['calls'][0]['response']['values'].__setitem__(3,False))
 def test_bool_echo(self):self.corrupt(lambda r:r['calls'][0]['response']['state'].__setitem__(3,False))
 def test_bool_status(self):self.corrupt(lambda r:r['calls'][0]['response'].__setitem__('ok',1))
 def test_source_corruption(self):self.corrupt(lambda r:r['source_pins'].__setitem__('x','f'*64))
 def test_request_order(self):self.corrupt(lambda r:r['calls'].reverse())
 def test_inexact_zero_rejected(self):self.corrupt(lambda r:r['calls'][1]['response']['values'].__setitem__(0,1e-30))
 def test_invalid_false_required(self):self.corrupt(lambda r:r['calls'][2]['response'].__setitem__('ok',True))
 def test_recovery_exact_required(self):self.corrupt(lambda r:r['calls'][3]['response']['values'].__setitem__(0,1+1e-12))
 def test_metadata_bool_impostor(self):self.corrupt(lambda r:r['descriptor']['models'][0]['parameters'].__setitem__('K',False))
 def test_finite_int_float_identity(self):
  self.assertTrue(c.same({'v':[1.,0.]},{'v':[1,0]}));self.assertFalse(c.same({'v':[True]},{'v':[1.]}));self.assertFalse(c.same({'v':[False]},{'v':[0.]}))
 def native_transport(self,r):
  return {'args':['synthetic-native','--stream'],'returncode':0,'stderr':'','stdin':'--describe\n'+''.join(c.stream_request(x['request'])+'\n'for x in r['calls']),'stdout':'\n'.join(json.dumps(x)for x in[r['descriptor']]+[x['response']for x in r['calls']])+'\n'}
 def wasm_transport(self,r):
  rows=[dict(name='atlas_describe',types=[],args=[],raw=json.dumps(r['descriptor']))]
  for x in r['calls']:
   q=x['request'];rows.append(dict(name='atlas_research_rate',types=['string']*4,args=[q['model'],c.csv(q['parameters']),c.csv(q['state']),c.csv(q['increment'])],raw=json.dumps(x['response'])))
  return rows
 def transport_test(self,backend,mutate=None):
  r=self.report(backend);raw=self.native_transport(r)if backend=='native'else self.wasm_transport(r)
  if mutate:mutate(raw)
  p=self.folder/(backend+'-transport.json');p.write_text(json.dumps(raw));r['transport_sha256']=c.sha(p)
  return r,p
 def test_raw_native_control(self):
  r,p=self.transport_test('native');self.assertEqual(c.verify_transport(r,p),5)
 def test_raw_native_stdout_corruption(self):
  r,p=self.transport_test('native',lambda raw:raw.__setitem__('stdout',raw['stdout'].replace('100.0','101.0',1)))
  with self.assertRaises(ValueError):c.verify_transport(r,p)
 def test_raw_native_exit_status(self):
  r,p=self.transport_test('native',lambda raw:raw.__setitem__('returncode',1))
  with self.assertRaises(ValueError):c.verify_transport(r,p)
 def test_raw_native_stdin_corruption(self):
  r,p=self.transport_test('native',lambda raw:raw.__setitem__('stdin',raw['stdin']+'extra\n'))
  with self.assertRaises(ValueError):c.verify_transport(r,p)
 def test_raw_wasm_control(self):
  r,p=self.transport_test('wasm');self.assertEqual(c.verify_transport(r,p),5)
 def test_raw_wasm_wrong_function(self):
  r,p=self.transport_test('wasm',lambda raw:raw[1].__setitem__('name','atlas_wrong'))
  with self.assertRaises(ValueError):c.verify_transport(r,p)
 def test_raw_wasm_wrong_csv(self):
  r,p=self.transport_test('wasm',lambda raw:raw[1]['args'].__setitem__(1,'3'))
  with self.assertRaises(ValueError):c.verify_transport(r,p)
 def test_raw_wasm_bool_corruption(self):
  def change(raw):
   x=json.loads(raw[1]['raw']);x['state'][3]=False;raw[1]['raw']=json.dumps(x)
  r,p=self.transport_test('wasm',change)
  with self.assertRaises(ValueError):c.verify_transport(r,p)
 def paired(self):
  native,np=self.transport_test('native');nativepath=self.folder/'native.json';nativepath.write_text(json.dumps(native));wasm,wp=self.transport_test('wasm');wasm['native_report_sha256']=c.sha(nativepath)
  return native,wasm,nativepath,np,wp
 def test_compare_control(self):
  n,w,p,np,wp=self.paired();self.assertEqual(c.compare(w,n,p,wp,np),0.)
 def test_compare_native_file_object_binding(self):
  n,w,p,np,wp=self.paired();other=copy.deepcopy(n);other['unassessed_extra']='different file';p.write_text(json.dumps(other));w['native_report_sha256']=c.sha(p)
  with self.assertRaises(ValueError):c.compare(w,n,p,wp,np)
 def test_tighter_parity_than_independent_budget(self):
  n,w,p,np,wp=self.paired()
  for x in w['calls']:
   if x['request']['id']=='normal':x['response']['values'][0]+=1e-10
  c.verify(w) # independently acceptable but exceeds separate predeclared parity
  wp.write_text(json.dumps(self.wasm_transport(w)));w['transport_sha256']=c.sha(wp)
  with self.assertRaises(ValueError):c.compare(w,n,p,wp,np)
 def test_native_artifact_mutation_preserves_raw(self):
  binary=self.folder/'fakebinary';binary.write_bytes(b'before');r=self.report();out=self.folder/'out.json';raw=self.native_transport(r)
  def mocked_run(*args,**kwargs):
   binary.write_bytes(b'after');return types.SimpleNamespace(stdout=raw['stdout'],stderr='',returncode=0)
  with patch.object(c.subprocess,'run',side_effect=mocked_run):
   with self.assertRaises(ValueError):c.run(binary,out)
  self.assertTrue(out.with_suffix('.transport.json').is_file())
 def test_numerical_failure_preserves_unassessed_report_and_raw(self):
  binary=self.folder/'fakebinary';binary.write_bytes(b'unchanged');r=self.report();r['calls'][0]['response']['values'][6]=1.;out=self.folder/'out.json';raw=self.native_transport(r)
  with patch.object(c.subprocess,'run',return_value=types.SimpleNamespace(stdout=raw['stdout'],stderr='',returncode=0)):
   with self.assertRaises(ValueError):c.run(binary,out)
  self.assertTrue(out.with_suffix('.transport.json').is_file());self.assertTrue(out.is_file());self.assertNotIn('assessment',c.read(out))
 def test_reopen_native_artifact_mutation(self):
  p=self.folder/'native';p.write_bytes(b'original');r=self.report();r['native_sha256']=c.sha(p);self.assertTrue(c.verify_artifacts(r,p));p.write_bytes(b'modified')
  with self.assertRaises(ValueError):c.verify_artifacts(r,p)
 def test_reopen_wasm_loader_mutation(self):
  p=self.folder/'research.mjs';b=p.with_suffix('.wasm');p.write_bytes(b'loader');b.write_bytes(b'wasm');r=self.report('wasm');r['wasm_loader_sha256']=c.sha(p);r['wasm_binary_sha256']=c.sha(b);self.assertTrue(c.verify_artifacts(r,p));p.write_bytes(b'changedloader')
  with self.assertRaises(ValueError):c.verify_artifacts(r,p)
 def test_reopen_wasm_binary_mutation(self):
  p=self.folder/'research.js';b=p.with_suffix('.wasm');p.write_bytes(b'loader');b.write_bytes(b'wasm');r=self.report('wasm');r['wasm_loader_sha256']=c.sha(p);r['wasm_binary_sha256']=c.sha(b);self.assertTrue(c.verify_artifacts(r,p));b.write_bytes(b'changedwasm')
  with self.assertRaises(ValueError):c.verify_artifacts(r,p)
if __name__=='__main__':unittest.main()
