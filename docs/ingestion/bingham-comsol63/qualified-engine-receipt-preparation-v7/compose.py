"""Offline candidate composer and post-E5 verifier. Never builds or executes an engine."""
import argparse,hashlib,importlib.util,io,json,pathlib,re,shlex,sys,tempfile,zipfile
MODEL='bingham-comsol63-mises-perfect-zero-spin-ode'
RECEIPT='docs/ingestion/bingham-comsol63/execution-v1/build-receipt.json'
PACKET='docs/ingestion/bingham-comsol63/asset-provision-v1/'
INDEX=PACKET+'INDEX.json';ARCHIVE=PACKET+'qualified-assets.zip'
SOURCE_RECEIPT='docs/ingestion/bingham-comsol63/source-v1/source-receipts.json'
MEMBERS={'bingham.mjs','bingham.wasm','generated/models.json'};LIMIT=16*1024*1024
ANCHORS_FILE=pathlib.Path(__file__).with_name('ANCHORS.json')
ANCHORS_FILE_SHA256='a065a2fe04bde52146e5c622e8f6d4552f55d2493262c5b4e2397ee65339a7fe'
sha=lambda b:hashlib.sha256(b).hexdigest()
if sha(ANCHORS_FILE.read_bytes())!=ANCHORS_FILE_SHA256:raise ValueError('Anchors file changed')
ANCHORS=json.loads(ANCHORS_FILE.read_text())
ROLES=set(ANCHORS['inputs'])
def demand(ok,message):
 if not ok:raise ValueError(message)
def relative(value):
 demand(isinstance(value,str),'Nonstring relative path');p=pathlib.PurePosixPath(value);demand(value and str(p)==value and not p.is_absolute() and '..' not in p.parts and '\\' not in value,'Unsafe/noncanonical relative path');return p

def resolve(root,name):
 relative(name);root=root.resolve();p=root
 for part in pathlib.PurePosixPath(name).parts:
  p=p/part;demand(not p.is_symlink(),'Symlink path component: '+name)
 demand(p.is_relative_to(root) and p.is_file(),'Missing/escaping input: '+name);return p

def inventory(record,root):
 """Verify each declared inventory, accepting original absolute tool/build paths."""
 count=0
 for key in ['files','source_files','tools','binary_files','sdk_files']:
  for name,item in record.get(key,{}).items():
   expected=item if isinstance(item,str) else item['sha256'];p=pathlib.Path(name)
   if not p.is_absolute():p=resolve(root,name)
   elif p.is_relative_to(root):p=resolve(root,p.relative_to(root).as_posix())
   demand(p.is_file() and sha(p.read_bytes())==expected,'Inventory missing/changed: '+name);count+=1
 return count

def pure_numerics(paths):
 """Re-run frozen pure assessors only, never their subprocess collector entrypoints."""
 def module(name,path):
  spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 oldpath=sys.path[:];oldoracle=sys.modules.get('oracle')
 try:
  sys.path.insert(0,str(paths['assessor'].parent));sys.modules['oracle']=module('_receipt_oracle',paths['oracle'])
  a=module('_receipt_assessor',paths['assessor']);p=module('_receipt_parity',paths['parity_source'])
  cases=json.loads(paths['cases'].read_text())['cases'];results=[]
  for backend in ['native','wasm']:
   result=a.assess(cases,json.loads(paths[backend+'_raw'].read_text()))
   demand(result==json.loads(paths[backend+'_report'].read_text()),'Recomputed '+backend+' assessment differs');results.append(result)
  result=p.main(paths['native_raw'],paths['wasm_raw'])
  demand(result==json.loads(paths['parity_report'].read_text()),'Recomputed parity differs');return results+[result]
 finally:
  sys.path[:]=oldpath
  if oldoracle is None:sys.modules.pop('oracle',None)
  else:sys.modules['oracle']=oldoracle

def verify_chain(paths,pins,data,root,release):
 """Known anchors already checked; now close every observed transport/artifact edge."""
 def value(v):return v if isinstance(v,str) else v['sha256']
 def item(record,path):
  table=record.get('files',{});return value(table.get(str(path),table.get(path.relative_to(root).as_posix(),{}))) if str(path) in table or path.relative_to(root).as_posix() in table else None
 def subset(record,expected):
  for name,h in expected.items():
   p=pathlib.Path(name);p=p if p.is_absolute() else root/p
   demand(item(record,p)==h,'Required preflight source/build member missing: '+name)
 expected={**data['study_freeze']['files'],**data['study_sources']['source_files'],**data['profile_freeze']['files']}
 for role,key in [('tool_receipt','binary_files'),('sdk_receipt','sdk_files')]:
  demand(len(data[role].get(key,{}))==ANCHORS['expected_inventory_counts'][role],'Incomplete tools/SDK inventory')
  inventory(data[role],root)
 supplement=data['wasm_tool_supplement']
 demand(supplement.get('binary_files')==data['tool_receipt']['binary_files'] and supplement.get('tools_receipt_sha256')==pins['tool_receipt']['sha256'] and supplement.get('build_operation_sha256')==pins['wasm_build_operation']['sha256'] and supplement.get('build_postverified_tools_before_collector') is True,'Wasm tools supplement not cross-bound')
 inventory(supplement,root)
 demand(data['sdk_receipt']['v5_freeze_sha256']==pins['study_freeze']['sha256'] and data['sdk_receipt']['native_post_sha256']==pins['native_post']['sha256'],'SDK provenance identity differs')
 for backend in ['native','wasm']:
  pre=data[backend+'_pre'];post=data[backend+'_post'];build=data[backend+'_build'];linked=data[backend+'_linked'];status=data[backend+'_status']
  for role in [backend+'_build',backend+'_linked']:
   demand(len(data[role]['files'])==ANCHORS['expected_inventory_counts'][role],'Incomplete build/linked inventory: '+role)
  subset(pre,expected)
  # Native preflight binds the complete target inventory by its exact receipt hash.
  # Wasm additionally records a flat inventory, which remains required unchanged.
  if backend=='wasm':subset(pre,{str((root/n) if not pathlib.Path(n).is_absolute() else pathlib.Path(n)):value(v) for n,v in build['files'].items()})
  buildhash=pre.get('native_build_inventory_sha256') if backend=='native' else pre.get('build_inventory_sha256')
  demand(buildhash==pins[backend+'_build']['sha256'],'Preflight build receipt differs')
  if backend=='wasm':
   demand(pre.get('linked_inventory_sha256')==pins['wasm_linked']['sha256'] and pre.get('sdk_cache_preparation_sha256')==pins['sdk_receipt']['sha256'],'Wasm preflight linked/SDK identity differs')
   subset(pre,{str(root/n):value(v) for n,v in linked['files'].items()})
   for role,field in [('module_mjs','module_sha256'),('wasm','wasm_sha256'),('wasm_metadata','generated_metadata_sha256')]:demand(pre.get(field)==pins[role]['sha256'],'Wasm preflight artifact differs')
  for kind in ['configure','build']:
   operation=data[backend+'_'+kind+'_operation']
   demand(operation.get('returncode')==0 and operation.get('preverified') is True and operation.get('postverified') is True and operation.get('cwd')==str(root),'Build operation failed/unverified')
   demand(operation.get('source_freeze_sha256')==pins['profile_freeze']['sha256'] and operation.get('tools_sha256')==pins['tool_receipt']['sha256'] and operation.get('recorder_sha256')==pins['operation_recorder']['sha256'] and operation.get('log_sha256')==pins[backend+'_'+kind+'_log']['sha256'],'Build operation source/tool/log differs')
  demand(status.get('returncode')==0 and status.get('preflight_sha256')==pins[backend+'_pre']['sha256'] and status.get('log_sha256')==pins[backend+'_log']['sha256'],'Collection status/preflight/log differs')
  for role in [backend+'_status',backend+'_log']:
   demand(post['outputs'].get(paths[role].name)==pins[role]['sha256'],'Post does not bind collection status/log')
  if backend=='native':
   binary={'path':str(paths['native_binary']),'sha256':pins['native_binary']['sha256']}
   demand(pre.get('binary')==post.get('binary')==binary,'Native pre/build/post binary chain differs')
   demand(item(build,paths['native_binary'])==binary['sha256'],'Native executable not actual build member')
   demand(status.get('argv')==['python3','-B',str(paths['assessor']),'native','--solver',str(paths['native_binary']),'--raw',str(paths['native_raw'])],'Native collector used another solver/assessor/raw')
   demand(linked.get('binary_preobserved_sha256')==binary['sha256'] and linked.get('completed_case_rows_at_capture')==28,'Native during-collection supplement timing/identity differs')
  else:
   demand(status.get('argv')==['node',str(paths['collector']),str(paths['module_mjs']),str(paths['cases']),str(paths['wasm_raw'])] and status.get('cwd')==str(root),'Wasm collector/module/cases/raw differs')
   demand(status.get('recorder_sha256')==pins['wasm_recorder']['sha256'] and status.get('source_postverified') is True and status.get('error') is None,'Wasm recorder/source postcheck failed')
   demand(post['outputs'].get(paths['parity_report'].name)==pins['parity_report']['sha256'],'Post omits exact parity')
 demand(pins['native_metadata']['sha256']==pins['wasm_metadata']['sha256']==pins['normal_metadata']['sha256'],'Backend/catalogue metadata differs')
 demand(pins['native_header']['sha256']==pins['wasm_header']['sha256']==pins['normal_header']['sha256'],'Backend normal header differs')

def compose(spec,study_root,release_root,destination):
 study_root=pathlib.Path(study_root).resolve();release_root=pathlib.Path(release_root).resolve();dest=None if destination is None else pathlib.Path(destination)
 if dest is not None:demand(not dest.exists() and not dest.is_symlink(),'Refusing existing staging destination')
 demand(set(spec)=={'inputs'} and set(spec['inputs'])==ROLES,'Exact required input roles needed')
 paths={};pins={};data={};roots={};review_paths={}
 for role,item in spec['inputs'].items():
  demand(set(item)=={'root','path','review_path','sha256'} and item['root'] in ['study','release'],'Malformed input pin')
  anchor=ANCHORS['inputs'][role];demand(item['root']==anchor['root'] and item['path']==anchor['path'],'Wrong anchored role root/path: '+role)
  if anchor['sha256'] is not None:demand(item['sha256']==anchor['sha256'],'Accepted anchor differs: '+role)
  relative(item['review_path']);root=study_root if item['root']=='study' else release_root;p=resolve(root,item['path'])
  demand(re.fullmatch('[0-9a-f]{64}',item['sha256']) and sha(p.read_bytes())==item['sha256'],'Input changed: '+role)
  previous=review_paths.get(item['review_path']);demand(previous is None or previous==item['sha256'],'Conflicting review-path pins');review_paths[item['review_path']]=item['sha256']
  paths[role]=p;pins[role]={'path':item['review_path'],'sha256':item['sha256']};roots[role]=root
  if role not in ['module_js','module_mjs','wasm']:data[role]=json.loads(p.read_text()) if p.suffix=='.json' else None
 demand(pins['source_receipts']['path']==SOURCE_RECEIPT,'Source receipt must retain packaging convention')
 definition=data['definition'];demand(definition.get('id')==MODEL and definition.get('schema_version')=='0.3','Wrong model')
 # Source candidate is immutable: installed model must equal original source-v1 candidate.
 candidate=resolve(study_root,'docs/ingestion/bingham-comsol63/source-v1/candidate.json')
 demand(candidate.read_bytes()==paths['definition'].read_bytes(),'Definition differs from original candidate')
 demand(pins['study_freeze']['sha256']==ANCHORS['source_freeze'] and pins['profile_freeze']['sha256']==ANCHORS['profile_freeze'] and pins['definition']['sha256']==ANCHORS['candidate'],'Accepted scientific identity differs')
 demand(data['study_freeze']['source_bindings_sha256']==pins['study_sources']['sha256'],'Source bindings not exact frozen identity')
 frozen=data['study_freeze'];demand(frozen.get('cases')==136 and frozen.get('repeats_per_case')==2 and frozen.get('before_new_v5_compiled_calls') is True,'Wrong v5 freeze')
 for role in ['cases','assessor','oracle','collector','parity_source']:
  key=paths[role].relative_to(study_root).as_posix();demand(frozen['files'].get(key)==pins[role]['sha256'],'Helper/cases not frozen: '+role)
 for role in ['study_sources','profile_freeze','study_freeze','native_pre','native_build','native_linked','wasm_pre','wasm_build','wasm_linked']:
  demand(inventory(data[role],roots[role])>0,'Empty inventory: '+role)
 profile_path=study_root/'runtimes/physical-time-v2/include/atlas/schedule.hpp';profile=sha(profile_path.read_bytes())
 demand(data['study_sources']['profile_freeze']['sha256']==pins['profile_freeze']['sha256'],'Profile freeze binding differs')
 for backend in ['native','wasm']:
  report=data[backend+'_report'];post=data[backend+'_post'];build=data[backend+'_build']
  demand(report.get('passed') is True and report.get('cases')==136 and report.get('raw_calls')==272 and report.get('numeric_comparisons')==7771,'Incomplete '+backend+' assessment')
  demand(post.get('passed') is True and post.get('errors')==[],'Failed post-inventory: '+backend)
  demand(post.get('summary')=={k:report[k] for k in ['passed','cases','raw_calls','numeric_comparisons']},'Post summary differs')
  for role in [backend+'_raw',backend+'_report']:
   demand(post['outputs'].get(paths[role].name)==pins[role]['sha256'],'Post output pin differs')
  if backend=='native':
   binary=post.get('binary',{});bp=pathlib.Path(binary.get('path',''));demand(bp.is_file() and sha(bp.read_bytes())==binary.get('sha256'),'Native post binary missing/changed')
  for role in [backend+'_pre',backend+'_build',backend+'_linked']:
   demand(post['inventories'].get(paths[role].name,{}).get('sha256')==pins[role]['sha256'],'Post provenance pin differs')
  demand(build.get('versioned_schedule_sha256')==profile and build.get('schedule_required') is True,'Wrong profile in build')
  demand(build.get('actual_schedule_headers')==[str(profile_path)],'Wrong schedule selection')
  deps=[study_root/n for n in build['files'] if n.endswith('/cpp/main.cpp.o.d')]
  flags=[study_root/n for n in build['files'] if n.endswith('atlas_bingham_solver.dir/flags.make')]
  demand(deps and flags,'Dependency/flag proof absent')
  for dep in deps:
   tokens=shlex.split(dep.read_text().replace('\\\n',' '));demand(str(profile_path) in tokens and str(study_root/'cpp/include/atlas/schedule.hpp') not in tokens,'Actual dependency selection differs')
  for flag in flags:
   text=flag.read_text()
   for response in re.findall(r'@([^\s]+)',text):
    rp=flag.parents[2]/response;key=rp.relative_to(study_root).as_posix();demand(key in build['files'],'Unpinned response file');demand(sha(rp.read_bytes())==(build['files'][key] if isinstance(build['files'][key],str) else build['files'][key]['sha256']),'Response file changed');text+=' '+rp.read_text()
   a=text.find(str(profile_path.parents[1]));b=text.find(str(study_root/'cpp/include'));demand(a>=0 and b>a,'Include order not proved')
 parity=data['parity_report'];demand(parity.get('passed') is True and parity.get('cases')==136 and parity.get('relative_budget')==2e-10,'Parity incomplete')
 verify_chain(paths,pins,data,study_root,release_root)
 pure_numerics(paths)
 js=paths['module_js'].read_bytes();mjs=paths['module_mjs'].read_bytes();wasm=paths['wasm'].read_bytes();metadata=paths['wasm_metadata'].read_bytes()
 demand(js==mjs,'Original js and compatibility mjs differ')
 demand(wasm.startswith(b'\0asm'),'Invalid Wasm magic')
 demand(metadata==paths['native_metadata'].read_bytes() and paths['native_header'].read_bytes()==paths['wasm_header'].read_bytes(),'Backend generated bytes differ')
 demand(metadata==paths['normal_metadata'].read_bytes(),'Normal release generator metadata differs')
 normal=data['normal_generation'];sources=data['normal_sources']
 demand(normal.get('identity')=='bingham-current-release-normal-generator-metadata-equivalence-v1' and normal.get('returncode')==0 and normal.get('source_unchanged') is True,'Normal release generation proof required')
 demand(normal.get('source_count')==len(sources) and len(sources)>0 and normal.get('source_before_sha256')==pins['normal_sources']['sha256'],'Normal generator source inventory differs')
 for name,h in sources.items():demand(sha(resolve(release_root,name).read_bytes())==h,'Normal release source changed: '+name)
 demand(normal.get('argv') and normal.get('compiler_log_sha256')==pins['normal_log']['sha256'],'Normal generator command/log proof missing')
 demand(paths['normal_header'].read_bytes()==paths['native_header'].read_bytes(),'Normal release generated header differs')
 for name,h in [('models.json',sha(metadata)),('models.hpp',pins['normal_header']['sha256'])]:
  demand(normal['comparison'][name]=={'generated_sha256':h,'tested_engine_generated_sha256':h,'byte_equal':True},'Normal generator comparison differs: '+name)
 # Pin tested native generated header and both metadata inventories to the compared bytes.
 for backend,roles in [('native',['native_header','native_metadata']),('wasm',['wasm_header','wasm_metadata'])]:
  for role in roles:
   key=paths[role].relative_to(study_root).as_posix();item=data[backend+'_build']['files'].get(key);actual=item if isinstance(item,str) else (item or {}).get('sha256')
   demand(actual==pins[role]['sha256'],'Compared generated asset not build-bound: '+backend+'/'+role)
 # Bind selected actual assets to Wasm build inventory, not merely independent input pins.
 for role in ['module_js','wasm','wasm_metadata']:
  key=paths[role].relative_to(study_root).as_posix();item=data['wasm_build']['files'].get(key);actual=item if isinstance(item,str) else (item or {}).get('sha256')
  demand(actual==pins[role]['sha256'],'Selected asset not bound to actual Wasm build: '+role)
 members={'bingham.mjs':mjs,'bingham.wasm':wasm,'generated/models.json':metadata}
 demand(all(len(v)<=LIMIT for v in members.values()),'Asset exceeds limit')
 stream=io.BytesIO()
 with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for name,value in sorted(members.items()):
   info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,value)
 archive=stream.getvalue();demand(len(archive)<=LIMIT,'Archive exceeds limit')
 index={'model':MODEL,'status':'passed','files':{k:sha(v) for k,v in members.items()},'archive':{'path':ARCHIVE,'sha256':sha(archive)}}
 receipt={'kind':'bingham-qualified-engine-build-v1','model':{'id':MODEL,'sha256':pins['definition']['sha256']},'artifacts':{'module':{'path':spec['inputs']['module_mjs']['path'],'sha256':sha(mjs)},'wasm':{'path':spec['inputs']['wasm']['path'],'sha256':sha(wasm)},'metadata':{'path':spec['inputs']['wasm_metadata']['path'],'sha256':sha(metadata)}},'study':'execution-v5/versioned-physical-time-v2','evidence':pins,'approval_state':'candidate-awaiting-independent-E5','runtime_source_capsule':data['study_sources'],'normal_release_generation':pins['normal_generation'],'asset_index':INDEX,'asset_archive':ARCHIVE}
 # All qualification/identity checks precede any staged output. No canonical install here.
 if dest is None:return {'validated':True,'input_roles':len(paths),'files_written':0,'native':{k:data['native_report'][k] for k in ['passed','cases','raw_calls','numeric_comparisons']},'wasm':{k:data['wasm_report'][k] for k in ['passed','cases','raw_calls','numeric_comparisons']},'parity_passed':data['parity_report']['passed'],'E5_acceptance_claimed':False}
 dest.mkdir(parents=True)
 for name,value in [(RECEIPT,(json.dumps(receipt,indent=2)+'\n').encode()),(INDEX,(json.dumps(index,indent=2)+'\n').encode()),(ARCHIVE,archive)]:
  p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
 return {'candidate_only':True,'receipt':RECEIPT,'index':INDEX,'archive':ARCHIVE,'hashes':{p:sha((dest/p).read_bytes()) for p in [RECEIPT,INDEX,ARCHIVE]}}

def verify_approved(release_root,review_path):
 """After independent E5 and coordinator installation; no mutation/provisioning."""
 root=pathlib.Path(release_root).resolve();relative(review_path)
 from atlas.agent_review import validate_review,approval_entry
 review=validate_review(root/review_path,root=root,for_approval=True);approval=approval_entry(root/review_path,root=root)
 registry=json.loads((root/'catalogue/approved-models.json').read_text())['models']
 demand([x for x in registry if x['model_id']==MODEL]==[approval],'Registry differs from exact E5 approval')
 demand(review['model']['id']==MODEL,'Wrong accepted review model')
 pins={i['path']:i['sha256'] for i in review['artifacts']}
 receipt=json.loads(resolve(root,RECEIPT).read_text());index=json.loads(resolve(root,INDEX).read_text());raw=resolve(root,ARCHIVE).read_bytes()
 demand(receipt.get('kind')=='bingham-qualified-engine-build-v1' and receipt.get('model',{}).get('id')==MODEL and set(receipt.get('artifacts',{}))=={'module','wasm','metadata'},'Invalid reviewed build receipt')
 demand(len(raw)<=LIMIT,'Reviewed archive exceeds size limit')
 for p in [RECEIPT,INDEX,ARCHIVE]:demand(pins.get(p)==sha(resolve(root,p).read_bytes()),'E5 does not bind '+p)
 for item in receipt['evidence'].values():demand(pins.get(item['path'])==item['sha256'],'E5 omits exact evidence '+item['path'])
 demand(receipt['model']['sha256']==review['model']['sha256'],'Accepted definition differs')
 demand(index['archive']=={'path':ARCHIVE,'sha256':sha(raw)} and index['model']==MODEL and index['status']=='passed','Index archive differs')
 with zipfile.ZipFile(io.BytesIO(raw)) as z:
  demand(len(z.infolist())==3 and set(z.namelist())==MEMBERS and set(index['files'])==MEMBERS,'Archive must contain three exact members')
  for i in z.infolist():demand(not i.is_dir() and i.file_size<=LIMIT and (i.external_attr>>16)&0o170000!=0o120000 and sha(z.read(i))==index['files'][i.filename],'Unsafe/changed archive member')
 for role,name in [('module','bingham.mjs'),('wasm','bingham.wasm'),('metadata','generated/models.json')]:demand(receipt['artifacts'][role]['sha256']==index['files'][name],'Receipt/archive asset mismatch')
 return {'accepted_E5_and_registry_exact':True,'provisioning_not_performed':True}
if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='action',required=True)
 for action in ['compose','validate']:
  c=sub.add_parser(action);c.add_argument('--spec',type=pathlib.Path,required=True);c.add_argument('--study-root',type=pathlib.Path,required=True);c.add_argument('--release-root',type=pathlib.Path,required=True)
  if action=='compose':c.add_argument('--output',type=pathlib.Path,required=True)
 v=sub.add_parser('verify-approved');v.add_argument('--release-root',type=pathlib.Path,required=True);v.add_argument('--review-path',required=True);a=p.parse_args()
 if a.action=='verify-approved':result=verify_approved(a.release_root,a.review_path)
 else:result=compose(json.loads(a.spec.read_text()),a.study_root,a.release_root,a.output if a.action=='compose' else None)
 print(json.dumps(result,indent=2))
