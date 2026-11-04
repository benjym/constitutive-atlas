"""Synthetic transport corruption tests; no constitutive or compiled acceptance claim."""
import copy
import hashlib
import importlib.util
import json
import runpy
import sys
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'tools/research_rate_observations.py'
spec=importlib.util.spec_from_file_location('rate_transport_under_test',TOOL)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class RateEvidence(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  self.patch=patch.object(r,'ROOT',self.root);self.patch.start();self.addCleanup(self.patch.stop)
  self.model=json.loads((ROOT/'docs/ingestion/hypoplastic-clay-2005/rate-study-v1/model.json').read_text())
  shutil.copytree(ROOT/'schemas',self.root/'schemas')
  self.write('model.json',self.model)
  for name in ('tools/research_rate_observations.py','tools/collect_research_rates_wasm.mjs'):
   path=self.root/name;path.parent.mkdir(exist_ok=True);path.write_bytes(TOOL.read_bytes())
  args=[self.model['id'],'1,2,3','1,2,3,4,5,6,0.8','0,0,0,0,0,0']
  self.protocol={'version':'research-instantaneous-rate-protocol-0.1','files':{'model.json':r.sha(self.root/'model.json')},'model_file':'model.json','model_definition':self.model,'cases':[{'id':'control','args':args,'expectation':{'ok':True,'values':[0.]*7,'absolute_budgets':[0.]*7,'parity_budgets':[0.]*7}}]}
  self.write('protocol.json',self.protocol)
  self.build={'backend':'native','protocol_sha256':r.sha(self.root/'protocol.json'),'all_commands_succeeded':True,'artifacts':{'native':{'path':'/private/tmp/nonexecuted-synthetic','sha256':'0'*64}}}
  self.response={'ok':True,'model':self.model['id'],'catalogue_hash':r.digest([self.model]),'parameters':[1.,2.,3.],'state':[1.,2.,3.,4.,5.,6.,.8],'increment':[0.]*6,'values':[0.]*7,'message':''}
 def write(self,name,value):
  (self.root/name).write_text(json.dumps(value,allow_nan=False)+'\n')
 def evidence(self,responses=None,backend='native'):
  self.write('protocol.json',self.protocol)
  self.build['protocol_sha256']=r.sha(self.root/'protocol.json');self.build['backend']=backend
  if backend=='wasm':self.build['artifacts']={'loader':{'path':'fake.js','sha256':'0'*64},'wasm':{'path':'fake.wasm','sha256':'1'*64}}
  self.write('build.json',self.build)
  descriptor=json.dumps({'models':[self.model],'sha256':r.digest([self.model])})
  lines=[descriptor]+[json.dumps(x) for x in (responses or [self.response])]
  if backend=='native':raw={'argv':[self.build['artifacts']['native']['path'],'--stream'],'stdin':r.stream_text(self.protocol),'stdout':'\n'.join(lines)+'\n','stderr':'','returncode':0}
  else:raw=[{'name':'atlas_describe','types':[],'args':[],'raw':lines[0]}]+[{'name':'atlas_research_rate','types':['string']*4,'args':case['args'],'raw':line} for case,line in zip(self.protocol['cases'],lines[1:])]
  self.write('raw.json',raw)
  tool='tools/research_rate_observations.py' if backend=='native' else 'tools/collect_research_rates_wasm.mjs'
  self.write('observation.json',{'version':'research-instantaneous-rate-observation-0.1','backend':backend,'completed':True,'protocol_sha256':r.sha(self.root/'protocol.json'),'build_receipt_sha256':r.sha(self.root/'build.json'),'build_receipt':self.build,'collector_sha256':r.sha(self.root/tool),'transport_sha256':r.sha(self.root/'raw.json')})
 def audit(self):return r.audit(*[self.root/name for name in ('protocol.json','build.json','observation.json','raw.json')])
 def test_native_and_wasm_literal_contract(self):
  for backend in ('native','wasm'):
   self.evidence(backend=backend);result=self.audit();self.assertEqual(result['outcome'],'passed')
 def test_tampered_literal_rejected_even_with_rebound_raw_hash(self):
  self.evidence();raw=json.loads((self.root/'raw.json').read_text());raw['stdin']=raw['stdin'].replace('1,2,3','9,2,3',1);self.write('raw.json',raw)
  obs=json.loads((self.root/'observation.json').read_text());obs['transport_sha256']=r.sha(self.root/'raw.json');self.write('observation.json',obs)
  with self.assertRaisesRegex(ValueError,'control binding'):self.audit()
 def test_changed_raw_after_parse_is_rejected(self):
  self.evidence();original=r.Snapshot.read
  def mutating(snapshot,path):
   value=original(snapshot,path)
   if Path(path)==self.root/'raw.json':(self.root/'raw.json').write_text('{}\n')
   return value
  with patch.object(r.Snapshot,'read',mutating):
   with self.assertRaisesRegex(ValueError,'input changed'):self.audit()
 def test_overflow_error_retained_as_failed_serializable_assessment(self):
  self.protocol['cases'][0]['expectation']['values'][0]=-1e308
  self.response['values'][0]=1e308;self.evidence();result=self.audit()
  self.assertEqual(result['outcome'],'failed');self.assertTrue(result['failures'][0]['error_overflow']);self.assertIsNone(result['failures'][0]['error'])
  json.dumps(result,allow_nan=False)
 def test_parity_rejects_truncated_vectors(self):
  self.evidence();n=self.audit();w=copy.deepcopy(n);w['backend']='wasm'
  n['cases'][0]['response']['values']=[];w['cases'][0]['response']['values']=[99.]
  with self.assertRaisesRegex(ValueError,'parity output shape'):r.parity(self.root/'protocol.json',n,w)
 def test_zero_budget_parity_failure_and_overflow_are_serializable(self):
  self.evidence();n=self.audit();w=copy.deepcopy(n);w['backend']='wasm'
  for value in (1.,1e308):
   n['cases'][0]['response']['values'][0]=-value;w['cases'][0]['response']['values'][0]=value
   result=r.parity(self.root/'protocol.json',n,w)
   self.assertFalse(result['passed']);self.assertTrue(result['parity_budget_fraction_unbounded']);self.assertIsNone(result['maximum_parity_budget_fraction']);json.dumps(result,allow_nan=False)
 def test_rejection_then_persistent_recovery(self):
  control=self.protocol['cases'][0]
  invalid=copy.deepcopy(control);invalid['id']='invalid';invalid['args'][2]='-1,2,3,4,5,6,0.8';invalid['expectation']={'ok':False}
  recovery=copy.deepcopy(control);recovery.update(id='recovery',recovery_of='control')
  self.protocol['cases'] += [invalid,recovery]
  bad=copy.deepcopy(self.response);bad.update(state=[-1.,2.,3.,4.,5.,6.,.8],ok=False,values=None,message='synthetic rejection')
  self.evidence([self.response,bad,self.response]);self.assertEqual(self.audit()['outcome'],'passed')
  changed=copy.deepcopy(self.response);changed['values'][0]=1
  self.evidence([self.response,bad,changed])
  with self.assertRaisesRegex(ValueError,'known-state recovery'):self.audit()
 def test_collection_retains_raw_then_rejects_changed_frozen_policy(self):
  binary=self.root/'nonexecuted-synthetic';binary.write_text('synthetic artifact, never executed')
  self.build['artifacts']['native']={'path':str(binary),'sha256':r.sha(binary)}
  self.write('build.json',self.build)
  def simulated(argv,**kwargs):
   changed=copy.deepcopy(self.protocol);changed['cases'][0]['expectation']['absolute_budgets'][0]=1.
   self.write('protocol.json',changed)
   return subprocess.CompletedProcess(argv,0,stdout='retained synthetic raw',stderr='')
  output=self.root/'collection.json'
  with patch.object(r.subprocess,'run',simulated):
   with self.assertRaisesRegex(ValueError,'input changed'):r.collect_native(self.root/'protocol.json',self.root/'build.json',output)
  self.assertEqual(json.loads(output.with_suffix('.transport.json').read_text())['stdout'],'retained synthetic raw')
 def test_cli_retains_failed_report_then_exits_nonzero(self):
  self.response['values'][0]=1;self.evidence()
  argv=[str(TOOL),'--protocol',str(self.root/'protocol.json'),'--build-receipt',str(self.root/'build.json'),'--observation',str(self.root/'observation.json'),'--transport',str(self.root/'raw.json'),'--output',str(self.root/'assessment.json')]
  with patch('atlas.model.ROOT',self.root),patch.object(sys,'argv',argv):
   with self.assertRaises(SystemExit) as exc:runpy.run_path(str(TOOL),run_name='__main__')
  self.assertEqual(exc.exception.code,1);self.assertEqual(json.loads((self.root/'assessment.json').read_text())['outcome'],'failed')
 def test_oversized_integer_and_duplicate_keys_rejected(self):
  self.assertFalse(r.finite(10**10000))
  path=self.root/'duplicate.json';path.write_text('{"x":1,"x":2}')
  with self.assertRaises(ValueError):r.Snapshot().read(path)
 def test_unpinned_model_and_cr_control_rejected(self):
  for kind in ('unpinned','cr'):
   protocol=copy.deepcopy(self.protocol)
   if kind=='unpinned':protocol['files']={}
   else:protocol['cases'][0]['args'][1]='1\r2,3'
   self.write('protocol.json',protocol)
   with self.assertRaises(ValueError):r.checked_protocol(self.root/'protocol.json')

if __name__=='__main__':unittest.main()
