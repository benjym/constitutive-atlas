"""Synthetic ESM-loader and raw-bundle tests; never instantiate compiled Wasm."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tools import research_rate_observations as rates
from tools import research_rate_parity as compare

ROOT=Path(__file__).resolve().parents[1]

class CollectionEvidence(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=Path(self.tmp.name)
  name='docs/ingestion/hypoplastic-clay-2005/rate-study-v1/model.json'
  self.model=json.loads((ROOT/name).read_text());self.hash=rates.digest([self.model])
  self.args=[self.model['id'],'1,2,3','1,2,3,4,5,6,0.8','0,0,0,0,0,0']
  self.response={'ok':True,'model':self.model['id'],'catalogue_hash':self.hash,'parameters':[1.,2.,3.],'state':[1.,2.,3.,4.,5.,6.,.8],'increment':[0.]*6,'values':[0.]*7,'message':''}
  self.protocol={'version':'research-instantaneous-rate-protocol-0.1','files':{name:rates.sha(ROOT/name)},'model_file':name,'model_definition':self.model,'cases':[{'id':'control','args':self.args,'expectation':{'ok':True,'values':[0.]*7,'absolute_budgets':[0.]*7,'parity_budgets':[0.]*7}}]}
  self.write('protocol.json',self.protocol)
  self.wasm=self.folder/'synthetic.wasm';self.wasm.write_bytes(b'synthetic-not-a-wasm-module')
 def write(self,name,doc):
  path=self.folder/name;path.write_text(json.dumps(doc,allow_nan=False)+'\n');return path
 def loader(self,mode='normal',response=None):
  response=response or self.response
  # Project-owned stub records exact inputs and returns opaque test strings.
  source='''import {writeFileSync} from 'node:fs';
export default async options=>{
 if(Buffer.from(options.wasmBinary).toString()!=='synthetic-not-a-wasm-module')throw new Error('wrong held bytes');
 return {ccall(name,returnType,types,args){
 if(name==='atlas_describe')return DESCRIPTOR;
 BODY
 return RESPONSE;
 }};
};
'''
  if mode=='throw':body="throw new Error('synthetic trap');"
  elif mode=='change-policy':body='writeFileSync('+json.dumps(str(self.folder/'protocol.json'))+',JSON.stringify({changed:true}));'
  elif mode=='not-string':body='return {ok:true};'
  else:body=''
  source=source.replace('DESCRIPTOR',json.dumps(json.dumps({'models':[self.model],'sha256':self.hash})))
  source=source.replace('RESPONSE',json.dumps(json.dumps(response))).replace('BODY',body)
  self.module=self.folder/'synthetic-loader.mjs';self.module.write_text(source)
  return self.module
 def build(self,backend='wasm'):
  artifacts={'loader':{'path':str(self.module),'sha256':rates.sha(self.module)},'wasm':{'path':str(self.wasm),'sha256':rates.sha(self.wasm)}} if backend=='wasm' else {'native':{'path':'/nonexecuted-synthetic','sha256':'0'*64}}
  return self.write(backend+'-build.json',{'backend':backend,'protocol_sha256':rates.sha(self.folder/'protocol.json'),'all_commands_succeeded':True,'artifacts':artifacts})
 def collect(self):
  return subprocess.run(['node',str(ROOT/'tools/collect_research_rates_wasm.mjs'),str(self.folder/'protocol.json'),str(self.folder/'wasm-build.json'),str(self.folder/'wasm-observation.json')],cwd=ROOT,text=True,capture_output=True,timeout=30)
 def native(self,response=None):
  buildpath=self.build('native');build=json.loads(buildpath.read_text())
  response=response or self.response
  raw=self.write('native.transport.json',{'argv':['/nonexecuted-synthetic','--stream'],'stdin':rates.stream_text(self.protocol),'stdout':json.dumps({'models':[self.model],'sha256':self.hash})+'\n'+json.dumps(response)+'\n','stderr':'','returncode':0})
  observation=self.write('native-observation.json',{'version':'research-instantaneous-rate-observation-0.1','backend':'native','completed':True,'protocol_sha256':rates.sha(self.folder/'protocol.json'),'build_receipt_sha256':rates.sha(buildpath),'build_receipt':build,'collector_sha256':rates.sha(ROOT/'tools/research_rate_observations.py'),'transport_sha256':rates.sha(raw)})
  return buildpath,observation,raw
 def wasm_paths(self):return self.folder/'wasm-build.json',self.folder/'wasm-observation.json',self.folder/'wasm-observation.transport.json'
 def prepare(self,response=None):
  self.loader(response=response);self.build();result=self.collect();self.assertEqual(result.returncode,0,result.stderr)
 def test_exact_literal_journal_and_assessment(self):
  self.prepare();paths=self.wasm_paths();raw=json.loads(paths[2].read_text())
  self.assertEqual(raw[1]['args'],self.args);self.assertEqual(raw[1]['raw'],json.dumps(self.response));self.assertEqual(rates.audit(self.folder/'protocol.json',*paths)['outcome'],'passed')
 def test_trap_retains_partial_journal_and_incomplete_receipt(self):
  self.loader('throw');self.build();result=self.collect();self.assertNotEqual(result.returncode,0)
  paths=self.wasm_paths();receipt=json.loads(paths[1].read_text());raw=json.loads(paths[2].read_text())
  self.assertFalse(receipt['completed']);self.assertEqual(len(raw),2);self.assertIn('synthetic trap',raw[1]['exception']);self.assertEqual(receipt['transport_sha256'],rates.sha(paths[2]))
  with self.assertRaisesRegex(ValueError,'complete transport'):rates.audit(self.folder/'protocol.json',*paths)
 def test_mutation_during_calls_fails_after_retaining_raw(self):
  self.loader('change-policy');self.build();result=self.collect();self.assertNotEqual(result.returncode,0)
  paths=self.wasm_paths();receipt=json.loads(paths[1].read_text());self.assertFalse(receipt['completed']);self.assertIn('input changed',receipt['error']);self.assertEqual(len(json.loads(paths[2].read_text())),2)
 def test_nonstring_response_and_overwrite_fail(self):
  self.loader('not-string');self.build();self.assertNotEqual(self.collect().returncode,0)
  paths=self.wasm_paths();before=[p.read_bytes() for p in paths]
  self.assertNotEqual(self.collect().returncode,0);self.assertEqual(before,[p.read_bytes() for p in paths])
 def test_tampered_artifact_rejected_before_loader_import(self):
  self.loader();self.build();self.wasm.write_bytes(b'changed')
  result=self.collect();self.assertNotEqual(result.returncode,0);self.assertFalse((self.folder/'wasm-observation.json').exists())
 def test_authenticated_comparison_reaudits_both_raw_bundles(self):
  self.prepare();native=self.native();result=compare.assess(self.folder/'protocol.json',native,self.wasm_paths());self.assertEqual(result['outcome'],'passed')
  raw=json.loads(native[2].read_text());raw['stdin']='changed';self.write(native[2].name,raw)
  with self.assertRaisesRegex(ValueError,'companion hash'):compare.assess(self.folder/'protocol.json',native,self.wasm_paths())
 def test_matching_backend_errors_still_fail_independent_gate(self):
  response=copy.deepcopy(self.response);response['values'][0]=1.
  self.prepare(response);native=self.native(response);result=compare.assess(self.folder/'protocol.json',native,self.wasm_paths())
  self.assertEqual(result['outcome'],'failed');self.assertTrue(result['parity']['passed']);self.assertFalse(result['parity']['both_independent_assessments_passed'])
 def test_comparison_detects_bundle_change_between_audits(self):
  self.prepare();native=self.native();original=rates.audit;calls=0
  def changed(*args,**kwargs):
   nonlocal calls
   result=original(*args,**kwargs);calls+=1
   if calls==2:native[2].write_text('{}')
   return result
  with patch.object(rates,'audit',changed):
   with self.assertRaisesRegex(ValueError,'input changed'):compare.assess(self.folder/'protocol.json',native,self.wasm_paths())

if __name__=='__main__':unittest.main()
