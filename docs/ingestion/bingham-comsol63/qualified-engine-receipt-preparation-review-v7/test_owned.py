"""Mock-only receipt/archive contract tests; no engine or subprocess may execute."""
import copy,hashlib,importlib.util,json,pathlib,subprocess,tempfile,unittest,zipfile
from unittest.mock import patch
import sys
sys.path.insert(0,'/private/tmp/atlas-time-profile-v2/docs/ingestion/bingham-comsol63/qualified-engine-receipt-preparation-v7')
import compose as c
HERE=pathlib.Path(__file__).resolve().parent
class ComposerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=HERE,prefix='.mock-only-');self.base=pathlib.Path(self.tmp.name);self.study=self.base/'study';self.release=self.base/'release';self.study.mkdir();self.release.mkdir()
  self.block=patch.multiple(subprocess,run=unittest.mock.DEFAULT,Popen=unittest.mock.DEFAULT,check_output=unittest.mock.DEFAULT,check_call=unittest.mock.DEFAULT,call=unittest.mock.DEFAULT);self.mocks=self.block.start()
  for m in self.mocks.values():m.side_effect=AssertionError('subprocess forbidden in source-only mock tests')
  self.spec={'inputs':{}};self.paths={}
  def write(role,value,suffix='.json',root='study'):
   parent=self.study if root=='study' else self.release;p=parent/'inputs'/(role+suffix);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value if isinstance(value,bytes) else (json.dumps(value)+'\n').encode());self.paths[role]=p
   self.spec['inputs'][role]={'root':root,'path':p.relative_to(parent).as_posix(),'review_path':'docs/mock-evidence/'+p.name,'sha256':c.sha(p.read_bytes())};return p
  self.write=write
  for role in c.ROLES:write(role,{'fixture':role})
  self.spec['inputs']['source_receipts']['review_path']=c.SOURCE_RECEIPT
  write('definition',{'id':c.MODEL,'schema_version':'0.3'})
  candidate=self.study/'docs/ingestion/bingham-comsol63/source-v1/candidate.json';candidate.parent.mkdir(parents=True);candidate.write_bytes(self.paths['definition'].read_bytes())
  profile=self.study/'runtimes/physical-time-v2/include/atlas/schedule.hpp';profile.parent.mkdir(parents=True);profile.write_bytes(b'// mock profile\n');self.profile=profile
  for role in ['assessor','oracle','collector','parity_source']:write(role,b'# inert mock helper, never imported\n','.py')
  write('cases',{'identity':'MOCK_ONLY','cases':[{'id':str(i)} for i in range(136)]})
  write('study_sources',{'source_files':{str(profile):c.sha(profile.read_bytes())},'profile_freeze':{'sha256':'pending'}})
  inv={'files':{str(profile):c.sha(profile.read_bytes())}}
  write('profile_freeze',inv)
  write('study_sources',{'source_files':{str(profile):c.sha(profile.read_bytes())},'profile_freeze':{'sha256':self.spec['inputs']['profile_freeze']['sha256']}})
  write('study_freeze',{'cases':136,'repeats_per_case':2,'before_new_v5_compiled_calls':True,'files':{self.paths[r].relative_to(self.study).as_posix():self.spec['inputs'][r]['sha256'] for r in ['cases','assessor','oracle','collector','parity_source']}})
  # Frozen inventory also has at least one real path; helper pins above satisfy that.
  write('module_js',b'export default async()=>({});\n','.js');write('module_mjs',self.paths['module_js'].read_bytes(),'.mjs');write('wasm',b'\0asm\x01\0\0\0','.wasm')
  write('wasm_metadata',{'sha256':'mock-catalogue','models':[c.MODEL]});write('normal_metadata',self.paths['wasm_metadata'].read_bytes(),root='release')
  token=self.release/'mock-generator.py';token.write_text('# mock only\n')
  write('normal_sources',{token.relative_to(self.release).as_posix():c.sha(token.read_bytes())},root='release');write('normal_log',b'','.log',root='release')
  write('normal_header',b'// mock generated header\n','.hpp',root='release');write('native_header',self.paths['normal_header'].read_bytes(),'.hpp')
  write('normal_generation',{'identity':'bingham-current-release-normal-generator-metadata-equivalence-v1','returncode':0,'source_unchanged':True,'source_count':1,'source_before_sha256':self.spec['inputs']['normal_sources']['sha256'],'argv':['MOCK_ONLY_NEVER_EXECUTED'],'compiler_log_sha256':self.spec['inputs']['normal_log']['sha256'],'comparison':{n:{'generated_sha256':self.spec['inputs'][r]['sha256'],'tested_engine_generated_sha256':self.spec['inputs'][r]['sha256'],'byte_equal':True} for n,r in [('models.json','wasm_metadata'),('models.hpp','normal_header')]}},root='release')
  summary={'passed':True,'cases':136,'raw_calls':272,'numeric_comparisons':7771}
  for backend in ['native','wasm']:
   dep=self.study/backend/'main.cpp.o.d';dep.parent.mkdir();dep.write_text('object: '+str(profile)+'\n');flags=dep.parent/'flags.make';flags.write_text('-I'+str(profile.parents[1])+' -I'+str(self.study/'cpp/include'))
   binary=dep.parent/'MOCK_ENGINE_NEVER_EXECUTE';binary.write_bytes(b'mock\n')
   files={str(p.relative_to(self.study)):c.sha(p.read_bytes()) for p in [dep,flags,binary]}
   files.update({self.paths[r].relative_to(self.study).as_posix():self.spec['inputs'][r]['sha256'] for r in ['native_header','wasm_metadata']})
   if backend=='wasm':files.update({self.paths[r].relative_to(self.study).as_posix():self.spec['inputs'][r]['sha256'] for r in ['module_js','wasm','wasm_metadata']})
   write(backend+'_build',{'schedule_required':True,'versioned_schedule_sha256':c.sha(profile.read_bytes()),'actual_schedule_headers':[str(profile)],'files':files})
   write(backend+'_pre',inv);write(backend+'_linked',inv);write(backend+'_raw',[{'mock':'never actual results'}]);write(backend+'_report',summary)
   write(backend+'_post',{'passed':True,'errors':[],'summary':summary,'binary':{'path':str(binary),'sha256':c.sha(binary.read_bytes())},'outputs':{self.paths[r].name:self.spec['inputs'][r]['sha256'] for r in [backend+'_raw',backend+'_report']},'inventories':{self.paths[r].name:{'sha256':self.spec['inputs'][r]['sha256']} for r in [backend+'_pre',backend+'_build',backend+'_linked']}})
  write('parity_report',{'passed':True,'cases':136,'relative_budget':2e-10})
  self.complete_mock_chain()
 def complete_mock_chain(self):
  # Mock positives explicitly replace accepted anchors only within this test instance.
  self.real_anchors=c.ANCHORS
  w=self.write
  w('native_metadata',self.paths['wasm_metadata'].read_bytes());w('wasm_header',self.paths['native_header'].read_bytes(),'.hpp')
  w('tool_receipt',{'binary_files':{str(self.profile):c.sha(self.profile.read_bytes())}})
  for backend in ['native','wasm']:
   directory=self.study/backend/'CMakeFiles/atlas_bingham_solver.dir';directory.mkdir(parents=True,exist_ok=True)
   dep=directory/'mock/cpp/main.cpp.o.d';dep.parent.mkdir(parents=True);dep.write_text('object: '+str(self.profile)+'\n')
   flags=directory/'flags.make'
   if backend=='wasm':
    rsp=directory/'includes_CXX.rsp';rsp.write_text('-I'+str(self.profile.parents[1])+' -I'+str(self.study/'cpp/include'))
    flags.write_text('CXX_INCLUDES=@CMakeFiles/atlas_bingham_solver.dir/includes_CXX.rsp')
   else:flags.write_text('-I'+str(self.profile.parents[1])+' -I'+str(self.study/'cpp/include'))
   files={str(p.relative_to(self.study)):c.sha(p.read_bytes()) for p in [dep,flags]}
   if backend=='wasm':files[str(rsp.relative_to(self.study))]=c.sha(rsp.read_bytes())
   for role in [backend+'_metadata',backend+'_header']+(['native_binary'] if backend=='native' else ['module_js','module_mjs','wasm']):files[str(self.paths[role].relative_to(self.study))]=self.spec['inputs'][role]['sha256']
   w(backend+'_build',{'schedule_required':True,'versioned_schedule_sha256':c.sha(self.profile.read_bytes()),'actual_schedule_headers':[str(self.profile)],'files':files})
   w(backend+'_linked',{'files':{str(self.profile):c.sha(self.profile.read_bytes())},'binary_preobserved_sha256':self.spec['inputs']['native_binary']['sha256'],'completed_case_rows_at_capture':28})
   w(backend+'_log',b'MOCK LOG NEVER ACTUAL','.log')
   for kind in ['configure','build']:
    w(backend+'_'+kind+'_log',b'MOCK OPERATION NEVER ACTUAL','.log')
    w(backend+'_'+kind+'_operation',{'returncode':0,'preverified':True,'postverified':True,'cwd':str(self.study),'source_freeze_sha256':self.spec['inputs']['profile_freeze']['sha256'],'tools_sha256':self.spec['inputs']['tool_receipt']['sha256'],'recorder_sha256':self.spec['inputs']['operation_recorder']['sha256'],'log_sha256':self.spec['inputs'][backend+'_'+kind+'_log']['sha256']})
  f=json.loads(self.paths['study_freeze'].read_text());f['source_bindings_sha256']=self.spec['inputs']['study_sources']['sha256'];w('study_freeze',f)
  expected={**f['files'],**json.loads(self.paths['study_sources'].read_text())['source_files'],**json.loads(self.paths['profile_freeze'].read_text())['files']}
  for backend in ['native','wasm']:
   build=json.loads(self.paths[backend+'_build'].read_text());linked=json.loads(self.paths[backend+'_linked'].read_text())
   files={str(pathlib.Path(n) if pathlib.Path(n).is_absolute() else self.study/n):h for n,h in expected.items()}
   if backend=='wasm':files.update({str(self.study/n):h for n,h in build['files'].items()})
   if backend=='wasm':files.update(linked['files'])
   pre={'files':files,'native_build_inventory_sha256':self.spec['inputs'][backend+'_build']['sha256'],'build_inventory_sha256':self.spec['inputs'][backend+'_build']['sha256'],'linked_inventory_sha256':self.spec['inputs'][backend+'_linked']['sha256'],'binary':{'path':str(self.paths['native_binary']),'sha256':self.spec['inputs']['native_binary']['sha256']},'module_sha256':self.spec['inputs']['module_mjs']['sha256'],'wasm_sha256':self.spec['inputs']['wasm']['sha256'],'generated_metadata_sha256':self.spec['inputs']['wasm_metadata']['sha256']}
   if backend=='wasm':
    w('sdk_receipt',{'sdk_files':{str(self.profile):c.sha(self.profile.read_bytes())},'v5_freeze_sha256':self.spec['inputs']['study_freeze']['sha256'],'native_post_sha256':self.spec['inputs']['native_post']['sha256']})
    pre['sdk_cache_preparation_sha256']=self.spec['inputs']['sdk_receipt']['sha256']
   w(backend+'_pre',pre)
   status={'returncode':0,'preflight_sha256':self.spec['inputs'][backend+'_pre']['sha256'],'log_sha256':self.spec['inputs'][backend+'_log']['sha256'],'argv':['python3','-B',str(self.paths['assessor']),'native','--solver',str(self.paths['native_binary']),'--raw',str(self.paths['native_raw'])] if backend=='native' else ['node',str(self.paths['collector']),str(self.paths['module_mjs']),str(self.paths['cases']),str(self.paths['wasm_raw'])],'cwd':str(self.study),'recorder_sha256':self.spec['inputs']['wasm_recorder']['sha256'],'source_postverified':True,'error':None}
   w(backend+'_status',status)
   summary={'passed':True,'cases':136,'raw_calls':272,'numeric_comparisons':7771}
   roles=[backend+'_raw',backend+'_report',backend+'_status',backend+'_log']+(['parity_report'] if backend=='wasm' else [])
   w(backend+'_post',{'passed':True,'errors':[],'summary':summary,'binary':pre['binary'],'outputs':{self.paths[r].name:self.spec['inputs'][r]['sha256'] for r in roles},'inventories':{self.paths[r].name:{'sha256':self.spec['inputs'][r]['sha256']} for r in [backend+'_pre',backend+'_build',backend+'_linked']}})
  w('wasm_tool_supplement',{'binary_files':{str(self.profile):c.sha(self.profile.read_bytes())},'tools_receipt_sha256':self.spec['inputs']['tool_receipt']['sha256'],'build_operation_sha256':self.spec['inputs']['wasm_build_operation']['sha256'],'build_postverified_tools_before_collector':True})
  counts={r:len(json.loads(self.paths[r].read_text())['files']) for r in ['native_build','wasm_build','native_linked','wasm_linked']};counts.update(tool_receipt=1,sdk_receipt=1)
  c.ANCHORS={'inputs':{r:{k:v for k,v in item.items() if k!='review_path'} for r,item in self.spec['inputs'].items()},'expected_inventory_counts':counts,'source_freeze':self.spec['inputs']['study_freeze']['sha256'],'profile_freeze':self.spec['inputs']['profile_freeze']['sha256'],'candidate':self.spec['inputs']['definition']['sha256']}

 def tearDown(self):
  c.ANCHORS=self.real_anchors;self.block.stop();self.tmp.cleanup()
 def compose(self,sub='staging'):
  with patch.object(c,'pure_numerics',return_value=None):return c.compose(self.spec,self.study,self.release,self.base/sub)
 def repin(self,role,value):self.write(role,value,suffix=self.paths[role].suffix,root=self.spec['inputs'][role]['root'])
 def rejects(self,mutator):
  mutator()
  with self.assertRaises((ValueError,KeyError,TypeError,FileNotFoundError)):self.compose()
  self.assertFalse((self.base/'staging').exists())
 def test_mock_positive_three_members(self):
  result=self.compose();self.assertTrue(result['candidate_only']);p=self.base/'staging'
  with zipfile.ZipFile(p/c.ARCHIVE) as z:self.assertEqual(set(z.namelist()),c.MEMBERS);self.assertEqual(len(z.infolist()),3)
  r=json.loads((p/c.RECEIPT).read_text());self.assertEqual(r['approval_state'],'candidate-awaiting-independent-E5');self.assertFalse((self.study/c.RECEIPT).exists())
 def test_deterministic(self):
  a=self.compose('one');b=self.compose('two');self.assertEqual(a['hashes'],b['hashes'])
 def test_existing_output(self):
  (self.base/'staging').mkdir();self.assertRaises(ValueError,self.compose)
 def test_unpinned_mutation(self):self.rejects(lambda:self.paths['wasm'].write_bytes(b'changed'))
 def test_missing_wasm(self):self.rejects(lambda:self.paths['wasm'].unlink())
 def test_extra_role(self):self.rejects(lambda:self.spec['inputs'].update(extra=self.spec['inputs']['wasm']))
 def test_unsafe_review_path(self):self.rejects(lambda:self.spec['inputs']['wasm'].update(review_path='../escape'))
 def test_wrong_definition(self):self.rejects(lambda:self.repin('definition',{'id':'other','schema_version':'0.3'}))
 def test_candidate_changed(self):self.rejects(lambda:(self.study/'docs/ingestion/bingham-comsol63/source-v1/candidate.json').write_text('{}'))
 def test_helper_not_frozen(self):self.rejects(lambda:self.repin('assessor',b'# different\n'))
 def test_profile_wrong(self):
  def bad():
   d=json.loads(self.paths['wasm_build'].read_text());d['actual_schedule_headers']=[str(self.study/'cpp/include/atlas/schedule.hpp')];self.repin('wasm_build',d)
  self.rejects(bad)
 def test_dependency_common_header(self):
  def bad():
   p=self.study/'wasm/CMakeFiles/atlas_bingham_solver.dir/mock/cpp/main.cpp.o.d';p.write_text('object: '+str(self.profile)+' '+str(self.study/'cpp/include/atlas/schedule.hpp'))
  self.rejects(bad)
 def test_failed_report(self):self.rejects(lambda:self.repin('wasm_report',{'passed':False,'cases':136,'raw_calls':272,'numeric_comparisons':7771}))
 def test_incomplete_report(self):self.rejects(lambda:self.repin('wasm_report',{'passed':True,'cases':135,'raw_calls':270,'numeric_comparisons':7771}))
 def test_post_errors(self):
  def bad():
   p=json.loads(self.paths['wasm_post'].read_text());p['errors']=['changed'];self.repin('wasm_post',p)
  self.rejects(bad)
 def test_failed_parity(self):self.rejects(lambda:self.repin('parity_report',{'passed':False,'cases':136,'relative_budget':2e-10}))
 def test_js_mjs_mismatch(self):self.rejects(lambda:self.repin('module_mjs',b'changed'))
 def test_normal_metadata_difference(self):self.rejects(lambda:self.repin('normal_metadata',b'{}'))
 def test_normal_source_missing(self):
  def bad():
   p=json.loads(self.paths['normal_generation'].read_text());p['source_count']=0;self.repin('normal_generation',p)
  self.rejects(bad)
 def install_mock_approval(self):
  self.compose();staging=self.base/'staging'
  for name in [c.RECEIPT,c.INDEX,c.ARCHIVE]:
   p=self.release/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((staging/name).read_bytes())
  receipt=json.loads((self.release/c.RECEIPT).read_text());artifacts=[{'path':n,'sha256':c.sha((self.release/n).read_bytes())} for n in [c.RECEIPT,c.INDEX,c.ARCHIVE]]+list(receipt['evidence'].values())
  self.review={'status':'accepted','model':{'id':c.MODEL,'sha256':receipt['model']['sha256']},'artifacts':artifacts}
  self.approval={'model_id':c.MODEL,'MOCK_ONLY':True};p=self.release/'catalogue/approved-models.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps({'models':[self.approval]}))
 def approved(self):
  with patch('atlas.agent_review.validate_review',return_value=self.review) as v,patch('atlas.agent_review.approval_entry',return_value=self.approval):
   result=c.verify_approved(self.release,'catalogue/agent-reviews/MOCK_ONLY.json');v.assert_called_once();self.assertTrue(v.call_args.kwargs['for_approval']);return result
 def test_mock_accepted_phase(self):
  self.install_mock_approval();self.assertTrue(self.approved()['accepted_E5_and_registry_exact'])
 def test_registry_mismatch(self):
  self.install_mock_approval();(self.release/'catalogue/approved-models.json').write_text('{"models":[]}')
  self.assertRaises(ValueError,self.approved)
 def test_E5_omits_archive(self):
  self.install_mock_approval();self.review['artifacts']=[x for x in self.review['artifacts'] if x['path']!=c.ARCHIVE]
  self.assertRaises(ValueError,self.approved)
 def test_E5_omits_exact_input(self):
  self.install_mock_approval();receipt=json.loads((self.release/c.RECEIPT).read_text());missing=receipt['evidence']['parity_report']['path'];self.review['artifacts']=[x for x in self.review['artifacts'] if x['path']!=missing]
  self.assertRaises(ValueError,self.approved)
 def test_changed_archive_after_review(self):
  self.install_mock_approval();(self.release/c.ARCHIVE).write_bytes(b'changed');self.assertRaises(ValueError,self.approved)
 def test_existing_registry_provisioner_mock_compatibility(self):
  self.install_mock_approval()
  source=pathlib.Path('/private/tmp/atlas-bingham-release-v2/tools/provision_bingham_assets.py')
  spec=importlib.util.spec_from_file_location('_mock_provisioner',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=self.release
  with patch.object(m,'validate_review',return_value=self.review),patch.object(m,'approval_entry',return_value=self.approval):
   output=self.base/'mock-provisioned';index=m.provision(output)
  self.assertEqual(set(index['files']),c.MEMBERS)
  self.assertEqual((output/'bingham.mjs').read_bytes(),self.paths['module_mjs'].read_bytes())
  self.assertEqual((output/'bingham.wasm').read_bytes(),self.paths['wasm'].read_bytes())
 def test_existing_bundler_mock_receipt_compatibility(self):
  self.install_mock_approval()
  source=pathlib.Path('/private/tmp/atlas-bingham-release-v2/tools/build_bingham_laboratory.py')
  spec=importlib.util.spec_from_file_location('_mock_bundler',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=self.release
  modelpath='models/research/bingham/'+c.MODEL+'.json';p=self.release/modelpath;p.parent.mkdir(parents=True);p.write_bytes(self.paths['definition'].read_bytes())
  self.review['model'].update(path=modelpath)
  reviewpath='catalogue/agent-reviews/MOCK_ONLY.json';p=self.release/reviewpath;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(self.review))
  self.approval.update(definition={'path':modelpath,'sha256':c.sha(self.paths['definition'].read_bytes())},review={'path':reviewpath,'sha256':c.sha(p.read_bytes())},scope={'use':'MOCK_ONLY'},limitations=[])
  (self.release/'catalogue/approved-models.json').write_text(json.dumps({'models':[self.approval]}))
  # The real composer insists on the conventional exact source-receipt path.
  p=self.release/c.SOURCE_RECEIPT;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps({'receipts':[{'original':True,'url':'https://example.invalid/MOCK_ONLY','sha256':'0'*64}]}))
  self.review['artifacts']=[x for x in self.review['artifacts'] if x['path']!=c.SOURCE_RECEIPT]+[{'path':c.SOURCE_RECEIPT,'sha256':c.sha(p.read_bytes())}]
  web=self.release/'web';web.mkdir()
  for name in m.COMPONENTS:(web/name).write_text("modelSha256='"+self.approval['definition']['sha256']+"'" if name=='bingham-atlas-contract.mjs' else '// MOCK_ONLY')
  build=self.base/'mock-build';(build/'generated').mkdir(parents=True);(build/'generated/models.json').write_bytes(self.paths['wasm_metadata'].read_bytes());(build/'bingham.mjs').write_bytes(self.paths['module_mjs'].read_bytes());(build/'bingham.wasm').write_bytes(self.paths['wasm'].read_bytes())
  def fake_generate(directory,definitions):(pathlib.Path(directory)/'models.json').write_bytes(self.paths['wasm_metadata'].read_bytes())
  with patch.object(m,'validate_review',return_value=self.review),patch.object(m,'approval_entry',return_value=self.approval),patch.object(m,'generate',side_effect=fake_generate),patch.dict('os.environ',{'GITHUB_SHA':'MOCK_ONLY'}):
   dest=self.base/'mock-web';dest.mkdir();identity=m.bundle(dest,build)
  self.assertEqual(identity['module_sha256'],self.spec['inputs']['module_mjs']['sha256'])
 def chain(self,data=None):
  pins={r:{'path':i['review_path'],'sha256':i['sha256']} for r,i in self.spec['inputs'].items()}
  values={r:json.loads(p.read_text()) if p.suffix=='.json' else None for r,p in self.paths.items()}
  if data:values.update(data)
  return c.verify_chain(self.paths,pins,values,self.study,self.release)
 def test_production_default_rejects_repinned_fabrication_before_import(self):
  # Same accepted canonical paths, fake internally repinned freeze/functions, REAL anchors.
  mockanchors=c.ANCHORS;c.ANCHORS=self.real_anchors
  try:
   spec={'inputs':{}}
   for role,anchor in self.real_anchors['inputs'].items():
    root=self.study if anchor['root']=='study' else self.release;dest=root/anchor['path'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(self.paths[role].read_bytes())
    spec['inputs'][role]={**anchor,'review_path':self.spec['inputs'][role]['review_path'],'sha256':c.sha(dest.read_bytes())}
   for role,code in [('assessor',b'def assess(cases,rows):return {"passed":True}\n'),('parity_source',b'def main(a,b):return {"passed":True}\n')]:
    item=spec['inputs'][role];p=(self.study if item['root']=='study' else self.release)/item['path'];p.write_bytes(code);item['sha256']=c.sha(code)
   freeze=spec['inputs']['study_freeze'];p=self.study/freeze['path'];record=json.loads(p.read_text());record['files']={spec['inputs'][r]['path']:spec['inputs'][r]['sha256'] for r in ['cases','assessor','oracle','collector','parity_source']};p.write_text(json.dumps(record));freeze['sha256']=c.sha(p.read_bytes())
   with patch.object(c.importlib.util,'spec_from_file_location',side_effect=AssertionError('UNTRUSTED CODE IMPORTED')),self.assertRaises(ValueError):c.compose(spec,self.study,self.release,self.base/'real-default-fake-chain')
   self.assertFalse((self.base/'real-default-fake-chain').exists())
  finally:c.ANCHORS=mockanchors
 def test_native_unrelated_post_binary_chain_rejected(self):
  d=json.loads(self.paths['native_post'].read_text());d['binary']={'path':str(self.profile),'sha256':c.sha(self.profile.read_bytes())}
  with self.assertRaisesRegex(ValueError,'binary chain'):self.chain({'native_post':d})
 def test_native_indirect_inventory_positive_and_validate_no_write(self):
  pre=json.loads(self.paths['native_pre'].read_text());build=json.loads(self.paths['native_build'].read_text())
  self.assertTrue(all(str(self.study/n) not in pre['files'] for n in build['files']))
  before=set(self.base.rglob('*'))
  with patch.object(c,'pure_numerics',return_value=None):result=c.compose(self.spec,self.study,self.release,None)
  self.assertTrue(result['validated']);self.assertEqual(result['files_written'],0);self.assertEqual(set(self.base.rglob('*')),before)
 def test_native_indirect_inventory_hash_changed_rejected(self):
  pre=json.loads(self.paths['native_pre'].read_text());pre['native_build_inventory_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'Preflight build receipt differs'):self.chain({'native_pre':pre})
 def test_native_indirect_inventory_hash_omitted_rejected(self):
  pre=json.loads(self.paths['native_pre'].read_text());pre.pop('native_build_inventory_sha256')
  with self.assertRaisesRegex(ValueError,'Preflight build receipt differs'):self.chain({'native_pre':pre})
 def test_native_indirect_inventory_member_omitted_rejected(self):
  build=json.loads(self.paths['native_build'].read_text());build['files'].pop(next(iter(build['files'])))
  with self.assertRaisesRegex(ValueError,'Incomplete build'):self.chain({'native_build':build})
 def test_native_status_other_solver_rejected(self):
  d=json.loads(self.paths['native_status'].read_text());d['argv'][d['argv'].index('--solver')+1]=str(self.profile)
  with self.assertRaisesRegex(ValueError,'another solver'):self.chain({'native_status':d})
 def test_missing_mandatory_build_member_rejected(self):
  d=json.loads(self.paths['wasm_build'].read_text());d['files'].pop(next(iter(d['files'])))
  with self.assertRaisesRegex(ValueError,'Incomplete build'):self.chain({'wasm_build':d})
 def test_tool_binary_files_are_traversed(self):
  d=json.loads(self.paths['tool_receipt'].read_text());d['binary_files']={str(self.study/'MISSING_TOOL'):'0'*64}
  with self.assertRaisesRegex(ValueError,'Inventory missing|Missing/escaping input'):self.chain({'tool_receipt':d})
 def test_failed_actual_build_operation_rejected(self):
  d=json.loads(self.paths['wasm_build_operation'].read_text());d['returncode']=1
  with self.assertRaisesRegex(ValueError,'operation failed'):self.chain({'wasm_build_operation':d})
 def test_wasm_status_other_module_rejected(self):
  d=json.loads(self.paths['wasm_status'].read_text());d['argv'][2]=str(self.profile)
  with self.assertRaisesRegex(ValueError,'collector/module'):self.chain({'wasm_status':d})
 def test_honest_distinct_backend_metadata_and_headers_accepted(self):
  self.assertNotEqual(self.paths['native_metadata'],self.paths['wasm_metadata']);self.assertNotEqual(self.paths['native_header'],self.paths['wasm_header']);self.compose()
 def test_internal_symlink_ancestor_rejected(self):
  (self.study/'innerlink').symlink_to(self.study/'inputs',target_is_directory=True)
  with self.assertRaisesRegex(ValueError,'Symlink path component'):c.resolve(self.study,'innerlink/definition.json')
 def test_inventory_internal_symlink_ancestor_rejected(self):
  (self.study/'innerlink').symlink_to(self.study/'inputs',target_is_directory=True)
  p=self.paths['definition'];record={'files':{'innerlink/definition.json':c.sha(p.read_bytes())}}
  with self.assertRaisesRegex(ValueError,'Symlink path component'):c.inventory(record,self.study)
 def test_noncanonical_review_path_rejected(self):
  with self.assertRaises(ValueError):c.relative('docs//alias.json')
 def test_missing_frozen_preflight_source_member_rejected(self):
  d=json.loads(self.paths['wasm_pre'].read_text());name=str(self.paths['assessor']);d['files'].pop(name)
  with self.assertRaisesRegex(ValueError,'Required preflight source'):self.chain({'wasm_pre':d})
 def test_scalar_dependencies_do_not_require_schedule(self):
  p=self.study/'wasm/scalar.c.o.d';p.write_text('object: scalar.c only.h\n')
  d=json.loads(self.paths['wasm_linked'].read_text());d['files'][str(p.relative_to(self.study))]=c.sha(p.read_bytes());self.repin('wasm_linked',d)
  c.ANCHORS['inputs']['wasm_linked']['sha256']=self.spec['inputs']['wasm_linked']['sha256'];c.ANCHORS['expected_inventory_counts']['wasm_linked']=len(d['files'])
  pre=json.loads(self.paths['wasm_pre'].read_text());pre['files'][str(p)]=c.sha(p.read_bytes());pre['linked_inventory_sha256']=self.spec['inputs']['wasm_linked']['sha256'];self.repin('wasm_pre',pre);c.ANCHORS['inputs']['wasm_pre']['sha256']=self.spec['inputs']['wasm_pre']['sha256']
  st=json.loads(self.paths['wasm_status'].read_text());st['preflight_sha256']=self.spec['inputs']['wasm_pre']['sha256'];self.repin('wasm_status',st);c.ANCHORS['inputs']['wasm_status']['sha256']=self.spec['inputs']['wasm_status']['sha256']
  post=json.loads(self.paths['wasm_post'].read_text());post['inventories'][self.paths['wasm_pre'].name]['sha256']=self.spec['inputs']['wasm_pre']['sha256'];post['inventories'][self.paths['wasm_linked'].name]['sha256']=self.spec['inputs']['wasm_linked']['sha256'];post['outputs'][self.paths['wasm_status'].name]=self.spec['inputs']['wasm_status']['sha256'];self.repin('wasm_post',post);c.ANCHORS['inputs']['wasm_post']['sha256']=self.spec['inputs']['wasm_post']['sha256']
  self.compose()
 def test_response_file_is_pinned_and_resolved(self):
  self.compose();(self.study/'wasm/CMakeFiles/atlas_bingham_solver.dir/includes_CXX.rsp').write_text('-IWRONG')
  self.assertRaises(ValueError,self.compose)
 def test_numerical_reassessment_required(self):
  def reject(paths):raise ValueError('MOCK numerical reassessment rejected')
  with patch.object(c,'pure_numerics',side_effect=reject),self.assertRaises(ValueError):c.compose(self.spec,self.study,self.release,self.base/'staging')
  self.assertFalse((self.base/'staging').exists())
 def test_no_subprocess_calls(self):
  self.compose()
  for m in self.mocks.values():m.assert_not_called()
if __name__=='__main__':unittest.main()
