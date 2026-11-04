"""Synthetic ESM-loader and raw-bundle tests; never instantiate compiled Wasm."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from tools import research_rate_observations_v3 as rates
from tools import research_rate_parity_v3 as compare

ROOT=Path(__file__).resolve().parents[1]

class CollectionEvidence(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.folder=Path(self.tmp.name)
  name='docs/ingestion/hypoplastic-clay-2005/compiled-plan-v3/model.json'
  self.model=json.loads((ROOT/name).read_text());self.hash=rates.digest([self.model])
  self.args=[self.model['id'],','.join(format(p['default'],'.17g') for p in self.model['parameters'].values()),'1,2,3,4,5,6,0.8','0,0,0,0,0,0']
  self.response={'ok':True,'model':self.model['id'],'catalogue_hash':self.hash,'parameters':[p['default']for p in self.model['parameters'].values()],'state':[1.,2.,3.,4.,5.,6.,.8],'increment':[0.]*6,'values':[0.]*7,'message':''}
  self.protocol={'version':'research-instantaneous-rate-protocol-0.3','files':{name:rates.sha(ROOT/name)},'model_file':name,'model_definition':self.model,'cases':[{'id':'control','args':self.args,'expectation':{'kind':'accuracy','ok':True,'values':[0.]*7,'absolute_budgets':[0.]*7,'parity_budgets':[0.]*7}}]}
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
  return subprocess.run(['node',str(ROOT/'tools/collect_research_rates_wasm_v3.mjs'),str(self.folder/'protocol.json'),str(self.folder/'wasm-build.json'),str(self.folder/'wasm-observation.json')],cwd=ROOT,text=True,capture_output=True,timeout=30)
 def native(self,response=None):
  buildpath=self.build('native');build=json.loads(buildpath.read_text())
  response=response or self.response
  raw=self.write('native.transport.json',{'argv':['/nonexecuted-synthetic','--stream'],'stdin':rates.stream_text(self.protocol),'stdout':json.dumps({'models':[self.model],'sha256':self.hash})+'\n'+json.dumps(response)+'\n','stderr':'','returncode':0})
  observation=self.write('native-observation.json',{'version':'research-instantaneous-rate-observation-0.3','backend':'native','completed':True,'protocol_sha256':rates.sha(self.folder/'protocol.json'),'build_receipt_sha256':rates.sha(buildpath),'build_receipt':build,'collector_sha256':rates.sha(ROOT/'tools/research_rate_observations_v3.py'),'transport_sha256':rates.sha(raw)})
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
  self.assertEqual(result['outcome'],'failed');self.assertTrue(result['parity']['passed']);self.assertFalse(result['parity']['both_backend_assessments_passed'])
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
  base=self.protocol['cases'][0];bad=copy.deepcopy(base);bad.update(id='reject');bad['expectation']={'kind':'reject','ok':False};bad['args'][2]='-1,2,3,4,5,6,0.8'
  recovery=copy.deepcopy(base);recovery.update(id='recovery',recovery_of='control',after_rejection='reject');self.protocol['cases'] += [bad,recovery];self.write('protocol.json',self.protocol)
  rejected=copy.deepcopy(self.response);rejected.update(ok=False,state=[-1.,2.,3.,4.,5.,6.,.8],values=None,message='unsupported research rate request')
  self.loader();source=self.module.read_text()
  source=source.replace(' return '+json.dumps(json.dumps(self.response))+';', ' if(args[2].startsWith("-1,"))return '+json.dumps(json.dumps(rejected))+'; return '+json.dumps(json.dumps(self.response))+';')
  self.module.write_text(source);self.build();result=self.collect();self.assertEqual(result.returncode,0,result.stderr)
  native=self.native();doc=json.loads(native[2].read_text());doc['stdout']+=json.dumps(rejected)+'\n'+json.dumps(self.response)+'\n';self.write(native[2].name,doc)
  receipt=json.loads(native[1].read_text());receipt['transport_sha256']=rates.sha(native[2]);self.write(native[1].name,receipt)
  self.assertEqual(compare.assess(self.folder/'protocol.json',native,self.wasm_paths())['outcome'],'passed')
  def changed(lines):
   response=json.loads(lines[3]);response['parameters'][0]=999.;lines[3]=json.dumps(response)
  self.mutate_raw(self.wasm_paths(),changed)
  with self.assertRaisesRegex(ValueError,'numeric echo parameters'):rates.audit(self.folder/'protocol.json',*self.wasm_paths())
  # Valid echoes do not excuse changed output after the rejected call.
  def changed_output(lines):
   response=copy.deepcopy(self.response);response['values'][0]=0.5;lines[3]=json.dumps(response)
  self.mutate_raw(self.wasm_paths(),changed_output)
  with self.assertRaisesRegex(ValueError,'persistent known-state recovery'):rates.audit(self.folder/'protocol.json',*self.wasm_paths())

 def finite_protocol(self):
  self.protocol['cases'][0]['expectation']={'kind':'finite_only','ok':True}
  self.protocol['finite_only_parity']={'norm':'scaled_component_max','budget':1e-10}
  self.write('protocol.json',self.protocol)
 def test_finite_only_has_no_reference_errors_and_is_not_source_accuracy(self):
  self.finite_protocol();response=copy.deepcopy(self.response);response['values']=[1e308,-1e308,0.,1.,2.,3.,4.]
  self.prepare(response);native=self.native(response);report=compare.assess(self.folder/'protocol.json',native,self.wasm_paths())
  self.assertEqual(report['outcome'],'passed');self.assertIsNone(report['native']['cases'][0]['errors']);self.assertEqual(report['native']['row_counts'],{'accuracy':0,'finite_only':1,'reject':0});self.assertIs(report['parity']['finite_only_is_source_accuracy'],False)
 def test_finite_only_cannot_smuggle_source_values_or_budgets(self):
  self.finite_protocol()
  for name in ['values','absolute_budgets','parity_budgets','unknown']:
   doc=copy.deepcopy(self.protocol);doc['cases'][0]['expectation'][name]=[0.]*7;self.write('protocol.json',doc)
   with self.assertRaisesRegex(ValueError,'expectation fields'):rates.checked_protocol(self.folder/'protocol.json')
 def test_explicit_tags_status_and_scaled_policy_are_required(self):
  self.finite_protocol();original=copy.deepcopy(self.protocol)
  for change in ['tag','status','missing_policy','boolean_budget','negative_budget','unknown_policy']:
   doc=copy.deepcopy(original)
   if change=='tag':doc['cases'][0]['expectation']['kind']='unknown'
   if change=='status':doc['cases'][0]['expectation']['ok']=1
   if change=='missing_policy':doc.pop('finite_only_parity')
   if change=='boolean_budget':doc['finite_only_parity']['budget']=True
   if change=='negative_budget':doc['finite_only_parity']['budget']=-1
   if change=='unknown_policy':doc['finite_only_parity']['hidden']='source_accuracy'
   self.write('protocol.json',doc)
   with self.assertRaises(ValueError):rates.checked_protocol(self.folder/'protocol.json')
 def test_material_cases_require_exact_finite_decimal_arities(self):
  for text in ['1_0','1 ',' 1','0x1','nan','inf','１','1,,2','1e999']:
   doc=copy.deepcopy(self.protocol);doc['cases'][0]['args'][1]=text+','+','.join(self.args[1].split(',')[1:]);self.write('protocol.json',doc)
   with self.assertRaises(ValueError):rates.checked_protocol(self.folder/'protocol.json')
  doc=copy.deepcopy(self.protocol);doc['cases'][0]['args'][1]='1,2,3';self.write('protocol.json',doc)
  with self.assertRaisesRegex(ValueError,'arities'):rates.checked_protocol(self.folder/'protocol.json')
 def test_subnormal_literals_are_finite_material_inputs(self):
  self.protocol['cases'][0]['args'][2]='4.9406564584124654e-324,2,3,4,5,6,0.8';self.write('protocol.json',self.protocol)
  rates.checked_protocol(self.folder/'protocol.json') # no compiled parser claim
 def test_scaled_parity_detects_disagreement_and_serializes_overflow(self):
  self.finite_protocol();self.prepare();native=self.native();n=rates.audit(self.folder/'protocol.json',*native);w=rates.audit(self.folder/'protocol.json',*self.wasm_paths())
  for a,b in [(1e308,-1e308),(0.,1e-5)]:
   n['cases'][0]['response']['values'][0]=a;w['cases'][0]['response']['values'][0]=b
   report=rates.parity(self.folder/'protocol.json',n,w);self.assertFalse(report['passed']);self.assertEqual(report['failures'][0]['kind'],'finite_only');self.assertEqual(report['failures'][0]['norm'],'scaled_component_max');json.dumps(report,allow_nan=False)
 def test_recovery_contract_requires_prior_accepted_identical_baseline(self):
  base=self.protocol['cases'][0];bad=copy.deepcopy(base);bad.update(id='reject');bad['expectation']={'kind':'reject','ok':False};bad['args'][2]='-1,2,3,4,5,6,0.8';recovery=copy.deepcopy(base);recovery.update(id='recovery',recovery_of='control',after_rejection='reject');self.protocol['cases']+=[bad,recovery];self.write('protocol.json',self.protocol);rates.checked_protocol(self.folder/'protocol.json')
  for change in ['prior','args','expectation','after','orphan','missing_relation','interposed']:
   doc=copy.deepcopy(self.protocol);case=doc['cases'][-1]
   if change=='prior':case['recovery_of']='reject'
   if change=='args':case['args'][2]='2,2,3,4,5,6,0.8'
   if change=='expectation':case['expectation']['absolute_budgets'][0]=1
   if change=='after':case['after_rejection']='control'
   if change=='orphan':case.pop('recovery_of')
   if change=='missing_relation':case.pop('after_rejection')
   if change=='interposed':doc['cases'].insert(-1,dict(copy.deepcopy(doc['cases'][0]),id='unrelated'))
   self.write('protocol.json',doc)
   with self.assertRaises(ValueError):rates.checked_protocol(self.folder/'protocol.json')
 def test_reject_shape_distinguishes_material_from_parser(self):
  case=self.protocol['cases'][0];case['expectation']={'kind':'reject','ok':False};self.write('protocol.json',self.protocol)
  response=copy.deepcopy(self.response);response.update(ok=False,values=None,message='unsupported research rate request');self.prepare(response);native=self.native(response);self.assertEqual(compare.assess(self.folder/'protocol.json',native,self.wasm_paths())['outcome'],'passed')
  def changed(lines):
   row=json.loads(lines[1]);row['message']='invalid research CSV';lines[1]=json.dumps(row)
  self.mutate_raw(native,changed)
  with self.assertRaisesRegex(ValueError,'material/parser'):rates.audit(self.folder/'protocol.json',*native)
  case['expectation']={'kind':'reject','ok':False,'parser_error':True};case['args'][2]='not-a-number';self.write('protocol.json',self.protocol);response={'ok':False,'message':'invalid research CSV'}
  # Fresh synthetic outputs under the distinct parser protocol.
  self.loader(response=response);self.build();out=self.folder/'wasm-observation.json';out.unlink();out.with_suffix('.transport.json').unlink();result=self.collect();self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(rates.audit(self.folder/'protocol.json',*self.wasm_paths())['outcome'],'passed')

 def test_successful_raw_and_observation_cannot_carry_failure_markers(self):
  self.prepare();native=self.native();wasm=self.wasm_paths()
  for paths in (native,wasm):
   original=[p.read_bytes()for p in paths]
   for marker in ('error','exception'):
    receipt=json.loads(paths[1].read_text());receipt[marker]='synthetic failure';self.write(paths[1].name,receipt)
    with self.assertRaisesRegex(ValueError,'failure markers'):compare.assess(self.folder/'protocol.json',native,wasm)
    for p,data in zip(paths,original):p.write_bytes(data)
   raw=json.loads(paths[2].read_text())
   target=raw if isinstance(raw,dict)else raw[1];target['exception']='synthetic trap';self.write(paths[2].name,raw)
   receipt=json.loads(paths[1].read_text());receipt['transport_sha256']=rates.sha(paths[2]);self.write(paths[1].name,receipt)
   with self.assertRaisesRegex(ValueError,'raw shape'):compare.assess(self.folder/'protocol.json',native,wasm)
   for p,data in zip(paths,original):p.write_bytes(data)

if __name__=='__main__':unittest.main()
