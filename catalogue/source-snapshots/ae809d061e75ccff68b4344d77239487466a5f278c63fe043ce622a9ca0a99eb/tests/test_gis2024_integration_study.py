"""GIS finite-path evidence integrity and corruption checks; no native execution."""
import copy,hashlib,json,unittest
from pathlib import Path
from atlas.model import ROOT,load
from tools import gis2024_integration_study as g
from tools.verify_gis2024_paths import verify,assess_recovery

PACKET=ROOT/'catalogue/investigations/gis2024-integration-v1'
class GISIntegrationEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.model=load(g.MODEL_PATH)
  cls.native=json.loads((PACKET/'native.json').read_text())
  cls.wasm=json.loads((PACKET/'wasm.json').read_text())
  cls.receipt=json.loads((ROOT/'catalogue/investigations/gis2024-path-reference-v1/reference.json').read_text())
  cls.ref=g.reference.study()
 def test_native_and_wasm_against_fresh_independent_paths(self):
  for report in (self.native,self.wasm):
   result=verify(report,reference_receipt=self.receipt)
   self.assertEqual(len(result['trajectories']),20)
   self.assertEqual(sum(len(r['calls'])for r in report['records']),204)
 def test_native_wasm_parity_recomputed(self):
  self.assertEqual(self.wasm['native_report_sha256'],hashlib.sha256((PACKET/'native.json').read_bytes()).hexdigest())
  maximum=0.
  for a,b in zip(self.native['records'],self.wasm['records']):
   self.assertEqual((a['case'],a['tolerance'],a['partitions']),(b['case'],b['tolerance'],b['partitions']))
   self.assertEqual(len(a['calls']),len(b['calls']))
   for x,y in zip(a['calls'],b['calls']):
    for key in ('model','strain','parameters','settings'):self.assertEqual(x['request'][key],y['request'][key])
    params=dict(zip(self.model['parameters'],x['request']['parameters']))
    scales=[params['p_scale']]*6+[1.]+[params['R']]*6+[1.]
    for key in ('initial','state'):
     maximum=max(maximum,max(abs(v-w)/s for v,w,s in zip(x['response'][key],y['response'][key],scales)))
  self.assertLessEqual(maximum,2e-10)
 def test_matrix_missing_duplicate_and_broken_chain_reject(self):
  for mode in ('missing','duplicate','chain','boolean_partition'):
   records=copy.deepcopy(self.native['records'])
   if mode=='missing':records.pop()
   if mode=='duplicate':records.append(copy.deepcopy(records[0]))
   if mode=='boolean_partition':records[0]['partitions']=True
   if mode=='chain':records[0]['calls'][1]['request']['initial'][0]+=1.
   with self.subTest(mode=mode),self.assertRaises(ValueError):g.assess(records,self.model,self.ref)
 def test_corrupt_intermediate_memory_rejects_even_when_rechained(self):
  for index,value in ((13,2.),(7,.01)):
   records=copy.deepcopy(self.native['records']);calls=next(r for r in records if r['partitions']==7)['calls']
   calls[0]['response']['state'][index]=value
   calls[1]['request']['initial'][index]=value;calls[1]['response']['initial'][index]=value
   with self.subTest(index=index),self.assertRaisesRegex(ValueError,'outside independent selected domain'):g.assess(records,self.model,self.ref)
 def test_failure_diagnostics_settings_and_rollback_reject(self):
  for mode in ('settings','counter','coverage','rollback','echo'):
   probes=copy.deepcopy(self.native['failure_probes']);a=probes[0]['response']
   if mode=='settings':a['integration_settings']={}
   if mode=='counter':a['diagnostics']['iterations']=float('nan')
   if mode=='coverage':a['diagnostics']['increment_fractions']=[2.]*a['diagnostics']['substeps']
   if mode=='rollback':a['state'][0]+=1.
   if mode=='echo':a['initial'][0]=True
   with self.subTest(mode=mode),self.assertRaises(ValueError):g.assess_probes(probes,self.native['records'],self.model)
 def test_response_contract_rejects_nonfinite_and_partial_coverage(self):
  c=self.native['records'][0]['calls'][0]
  for mode in ('state','settings','coverage','counter','catalogue'):
   a=copy.deepcopy(c['response'])
   if mode=='state':a['state'][0]=float('inf')
   if mode=='settings':a['integration_settings']['rate_tolerance']=.5
   if mode=='coverage':a['diagnostics']['increment_fractions']=[.1]*a['diagnostics']['substeps']
   if mode=='counter':a['diagnostics']['rejected']=-1
   if mode=='catalogue':a['catalogue_hash']='wrong'
   with self.subTest(mode=mode),self.assertRaises(ValueError):g.check_response(a,c['request'],self.model)
 def test_model_and_reference_identity_reject(self):
  refs={c['input']['id']:c for c in self.ref['cases']}
  for mode in ('id','layout','parameters','bounds'):
   model=copy.deepcopy(self.model)
   if mode=='id':model['id']='another'
   if mode=='layout':model['state'][2]['scale']='1'
   if mode=='parameters':model['parameters'].pop('phi')
   if mode=='bounds':model['parameters']['R']['max']=1e-6
   with self.subTest(mode=mode),self.assertRaises(ValueError):g.validate_model(model,refs)
  for mode in ('source','dependency','grid','summary'):
   ref=copy.deepcopy(self.ref)
   if mode=='source':ref['source_sha256']='wrong'
   if mode=='dependency':ref['dependency_sha256']['tools/gis2024_path_reference.py']='wrong'
   if mode=='grid':ref['cases'][0]['grids'][-1]['trajectory'][1]['state'][0]+=1.
   if mode=='summary':ref['cases'][0]['fine_difference']['stress']=0.
   with self.subTest(mode=mode),self.assertRaises(ValueError):g.checked_reference(ref)
 def test_persistent_recovery_corruption_rejects(self):
  assess_recovery(self.wasm,self.model)
  for mode in ('control','response','ordering','missing','boolean'):
   report=copy.deepcopy(self.wasm)
   if mode=='control':report['recovery_control']['request']['initial'][0]+=1.
   if mode=='response':report['recovery_responses'][0]['response']['state'][0]+=1.
   if mode=='ordering':report['recovery_responses'].reverse()
   if mode=='missing':report['recovery_responses'].pop()
   if mode=='boolean':report['persistent_recovery_verified']=False
   with self.subTest(mode=mode),self.assertRaises(ValueError):assess_recovery(report,self.model)
 def test_packet_hashes_and_source_packets(self):
  for folder in ('gis2024-integration-v1','gis2024-path-reference-v1','barodesy2017-source-v1','isa2020-source-v1','norsand1993-source-v1','clay2014-source-v1','pm4silt-v1-source-v1'):
   manifest=json.loads((ROOT/'catalogue/investigations'/folder/'manifest.json').read_text())
   for name,pin in manifest['files'].items():
    with self.subTest(packet=folder,path=name):self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),pin)

if __name__=='__main__':unittest.main()
