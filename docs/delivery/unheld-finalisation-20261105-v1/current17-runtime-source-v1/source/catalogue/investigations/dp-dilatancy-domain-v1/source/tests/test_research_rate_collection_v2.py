"""Synthetic ESM-loader and raw-bundle tests; never instantiate compiled Wasm."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tools import research_rate_observations_v2 as rates
from tools import research_rate_parity_v2 as compare

ROOT=Path(__file__).resolve().parents[1]

class CollectionEvidence(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=Path(self.tmp.name)
  name='docs/ingestion/hypoplastic-clay-2005/rate-study-v1/model.json'
  self.model=json.loads((ROOT/name).read_text());self.hash=rates.digest([self.model])
  self.args=[self.model['id'],'1,2,3','1,2,3,4,5,6,0.8','0,0,0,0,0,0']
  self.response={'ok':True,'model':self.model['id'],'catalogue_hash':self.hash,'parameters':[1.,2.,3.],'state':[1.,2.,3.,4.,5.,6.,.8],'increment':[0.]*6,'values':[0.]*7,'message':''}
  self.protocol={'version':'research-instantaneous-rate-protocol-0.2','files':{name:rates.sha(ROOT/name)},'model_file':name,'model_definition':self.model,'cases':[{'id':'control','args':self.args,'expectation':{'ok':True,'values':[0.]*7,'absolute_budgets':[0.]*7,'parity_budgets':[0.]*7}}]}
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
  return subprocess.run(['node',str(ROOT/'tools/collect_research_rates_wasm_v2.mjs'),str(self.folder/'protocol.json'),str(self.folder/'wasm-build.json'),str(self.folder/'wasm-observation.json')],cwd=ROOT,text=True,capture_output=True,timeout=30)
 def native(self,response=None):
  buildpath=self.build('native');build=json.loads(buildpath.read_text())
  response=response or self.response
  raw=self.write('native.transport.json',{'argv':['/nonexecuted-synthetic','--stream'],'stdin':rates.stream_text(self.protocol),'stdout':json.dumps({'models':[self.model],'sha256':self.hash})+'\n'+json.dumps(response)+'\n','stderr':'','returncode':0})
  observation=self.write('native-observation.json',{'version':'research-instantaneous-rate-observation-0.2','backend':'native','completed':True,'protocol_sha256':rates.sha(self.folder/'protocol.json'),'build_receipt_sha256':rates.sha(buildpath),'build_receipt':build,'collector_sha256':rates.sha(ROOT/'tools/research_rate_observations_v2.py'),'transport_sha256':rates.sha(raw)})
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

 def mutate_raw(self,paths,change):
  build,observation,raw=paths;doc=json.loads(raw.read_text())
  if isinstance(doc,list):
   lines=[row['raw'] for row in doc];change(lines)
   for row,line in zip(doc,lines):row['raw']=line
  else:
   lines=doc['stdout'].splitlines();change(lines);doc['stdout']='\n'.join(lines)+'\n'
  raw.write_text(json.dumps(doc)+'\n')
  receipt=json.loads(observation.read_text());receipt['transport_sha256']=rates.sha(raw);observation.write_text(json.dumps(receipt)+'\n')
 def test_reordered_descriptor_rejected_standalone_and_comparison_both_roles(self):
  self.prepare();native=self.native();wasm=self.wasm_paths()
  def reorder(lines):
   descriptor=json.loads(lines[0]);parameters=descriptor['models'][0]['parameters']
   descriptor['models'][0]['parameters']=dict(reversed(list(parameters.items())))
   self.assertNotEqual(list(parameters),list(descriptor['models'][0]['parameters']))
   self.assertEqual(rates.digest(descriptor['models']),self.hash);lines[0]=json.dumps(descriptor)
  for paths in (native,wasm):
   originals=[p.read_bytes() for p in paths];self.mutate_raw(paths,reorder)
   with self.assertRaisesRegex(ValueError,'compiled positional parameter layout'):rates.audit(self.folder/'protocol.json',*paths)
   with self.assertRaisesRegex(ValueError,'compiled positional parameter layout'):compare.assess(self.folder/'protocol.json',native,wasm)
   for p,data in zip(paths,originals):p.write_bytes(data)
 def test_duplicate_response_keys_rejected_standalone_and_comparison_both_roles(self):
  self.prepare();native=self.native();wasm=self.wasm_paths()
  for paths in (native,wasm):
   originals=[p.read_bytes() for p in paths]
   for index in (0,1):
    def duplicate(lines):
     if index==0:lines[0]='{"sha256":"invalid",'+lines[0][1:]
     else:lines[1]='{"ok":false,'+lines[1][1:]
    self.mutate_raw(paths,duplicate)
    with self.assertRaisesRegex(ValueError,'duplicate'):rates.audit(self.folder/'protocol.json',*paths)
    with self.assertRaisesRegex(ValueError,'duplicate'):compare.assess(self.folder/'protocol.json',native,wasm)
    for p,data in zip(paths,originals):p.write_bytes(data)
 def test_protocol_definition_positional_order_is_bound(self):
  p=self.protocol['model_definition']['parameters'];self.protocol['model_definition']['parameters']=dict(reversed(list(p.items())))
  self.write('protocol.json',self.protocol)
  with self.assertRaisesRegex(ValueError,'frozen positional parameter layout'):rates.checked_protocol(self.folder/'protocol.json')
 def test_duplicate_protocol_rejected_before_import(self):
  self.loader();self.build();p=self.folder/'protocol.json';p.write_text('{"version":"wrong",'+p.read_text()[1:])
  self.assertNotEqual(self.collect().returncode,0);self.assertFalse((self.folder/'wasm-observation.json').exists())
  with self.assertRaisesRegex(ValueError,'duplicate'):rates.read(p)
 def test_v03_strain_path_model_collects_and_compares(self):
  name='models/barodesy-clay-2017.json';self.model=json.loads((ROOT/name).read_text());self.hash=rates.digest([self.model])
  parameters=[p['default'] for p in self.model['parameters'].values()]
  state=[100000.,100000.,100000.,0.,0.,0.,.8]
  self.args=[self.model['id'],','.join(map(str,parameters)),','.join(map(str,state)),','.join(['0']*6)]
  self.response.update(model=self.model['id'],catalogue_hash=self.hash,parameters=parameters,state=state)
  self.protocol.update(files={name:rates.sha(ROOT/name)},model_file=name,model_definition=self.model)
  self.protocol['cases'][0]['args']=self.args;self.write('protocol.json',self.protocol)
  self.prepare();result=compare.assess(self.folder/'protocol.json',self.native(),self.wasm_paths())
  self.assertEqual(result['outcome'],'passed');self.assertFalse(result['claims']['integration'])
 def test_physical_time_and_residual_profiles_rejected(self):
  for name in ('models/research/terracotta-2024-fig1.json','models/modified-cam-clay.json'):
   self.protocol.update(files={name:rates.sha(ROOT/name)},model_file=name,model_definition=json.loads((ROOT/name).read_text()))
   self.write('protocol.json',self.protocol)
   with self.assertRaisesRegex(ValueError,'strain-path instantaneous rate model required'):rates.checked_protocol(self.folder/'protocol.json')
 def test_known_state_recovery_must_be_identical(self):
  recovery=copy.deepcopy(self.protocol['cases'][0]);recovery.update(id='recovery',recovery_of='control');self.protocol['cases'].append(recovery)
  self.write('protocol.json',self.protocol);self.prepare();native=self.native()
  # Add the second native response explicitly; synthetic loader already journals both calls.
  doc=json.loads(native[2].read_text());doc['stdout']+=json.dumps(self.response)+'\n';native[2].write_text(json.dumps(doc)+'\n')
  receipt=json.loads(native[1].read_text());receipt['transport_sha256']=rates.sha(native[2]);native[1].write_text(json.dumps(receipt)+'\n')
  self.assertEqual(compare.assess(self.folder/'protocol.json',native,self.wasm_paths())['outcome'],'passed')
  def changed(lines):
   response=json.loads(lines[2]);response['parameters'][0]=999.;lines[2]=json.dumps(response)
  self.mutate_raw(self.wasm_paths(),changed)
  with self.assertRaisesRegex(ValueError,'numeric echo parameters'):rates.audit(self.folder/'protocol.json',*self.wasm_paths())

if __name__=='__main__':unittest.main()
