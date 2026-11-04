"""Prospective local package launcher; default describes, never launches."""
from pathlib import Path
import argparse,hashlib,json,os,sys,time,traceback,importlib.util
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;B=P.parents[1]/'unheld-finalisation-20261102-v1';ROOT=P.parents[3]
POLICY=json.loads((P/'POLICY.json').read_text())
POLICY_SHA='5d31c92507dd330493b59777225be02ec56d4113809cdaf09c4dd7c0e4398151'
ADDENDUM_SHA='cdcfbbc9d82abac9efa6f8b9c0474bc914afdcee30cc8638422c5dc68bcaf1c1'
ACTUAL_DIR=B/'baseline-five-export-source-successor-actual-review-v1'
ACTUAL_SHA='c7e6c3dae53b5096fea876194d0c3c64d7661b77e2a1d3dc0edb95d2c9fb2a1c'
ACTUAL_MANIFEST='72cdf061669052b5d82d589aa671cf527325d6c6d2916b4d801b6e775c56ad0a'
TOOL_PATH='/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
def require(ok,message):
 if not ok:raise ValueError(message)
def safe(path):
 path=Path(path).absolute();require('..'not in path.parts and not any(p.is_symlink()for p in[path,*path.parents]),'unsafe path');return path
def raw(path):return safe(path).read_bytes()
def sha(path):return hashlib.sha256(raw(path)).hexdigest()
def pin(ref):
 b=raw(ref['path']);require(hashlib.sha256(b).hexdigest()==ref['sha256']and len(b)==ref['bytes'],'authority pin changed');return json.loads(b)
def members(m):
 require(('members'in m)!=('files'in m),'ambiguous manifest');return m.get('members',m.get('files'))
def verify_manifest(ref):
 m=pin(ref);rows=members(m);require(len({r['path']for r in rows})==len(rows),'duplicate members');root=Path(ref['path']).parent
 for r in rows:
  part=Path(r['path']);require(not part.is_absolute()and '..'not in part.parts,'unsafe member');require(sha(root/part)==r['sha256']and(root/part).stat().st_size==r['bytes'],'member drift')
 return m
def independent(authority,proposal):
 m=verify_manifest(authority['manifest']);r=pin(authority['decision']);path=Path(authority['decision']['path']);require(path.parent==Path(authority['manifest']['path']).parent and any(x['path']==path.name and x['sha256']==authority['decision']['sha256']for x in members(m)),'unbound decision')
 require(r.get('decision')=='accepted'and r.get('unresolved_blockers')==[]and r.get('author_run')and r.get('reviewer_run')and r['reviewer_run']!=r.get('author_run')and r.get('proposal_manifest_sha256')==proposal,'independent exact acceptance required');return r

def commands(python=None):
 python=sys.executable if python is None else python;root=Path(POLICY['source']);temp=Path(POLICY['runner_temp'])
 return {'producer':[python,'-B',str(root/'tools/baseline_prepare_ci_input_v2.py'),'--root',str(root),'--prepare-source-input'],'wrapper_prefix':[python,'-B',str(root/'tools/baseline_ci_package_portable_host_v3.py'),'--root',str(root),'--output',str(temp/'baseline-portable-site'),'--observations',str(temp/'baseline-portable-observations'),'--spec',str(temp/'baseline-portable-input-spec.json')],'cwd':str(root)}
def output_guard(source,temp,execution):
 paths=[safe(x)for x in[source,temp,execution]]
 for i,x in enumerate(paths):
  for y in paths[i+1:]:require(x!=y and not x.is_relative_to(y)and not y.is_relative_to(x),'output/input overlap')
 require(not paths[1].exists()and not paths[2].exists(),'unique never-existing outputs required');return paths

def closed_environment(temp):
 temp=Path(temp)
 return {'PATH':TOOL_PATH,'HOME':str(temp/'env-home'),'XDG_CONFIG_HOME':str(temp/'env-xdg'),'TMPDIR':str(temp/'env-tmp'),'LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1','PYTHONHASHSEED':'0','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_SYSTEM':'/dev/null','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_COUNT':'0','GIT_ATTR_NOSYSTEM':'1','GIT_NO_REPLACE_OBJECTS':'1','GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0','GITHUB_SHA':POLICY['revision'],'RUNNER_TEMP':str(temp)}

def handoff_guard(claim,process,handoff,resource,now):
 require(claim.get('identity')=='baseline-publication-local-package-serial-claim-v1'and claim.get('owner')=='/root'and claim.get('state')=='claimed-before-launch'and claim.get('source_revision')==POLICY['revision'],'coordinator serial claim required')
 authority=POLICY['prior_owner_authority']
 require(handoff.get('identity')=='baseline-package-prior-owner-fresh-verification-v3'and handoff.get('verified_by')=='/root'and handoff.get('prior_owner')==authority['owner']and handoff.get('state')=='released-after-mandatory-reap'and handoff.get('all_children_reaped')is True and handoff.get('no_newer_active_owner')is True,'fresh verified actual prior-owner release required')
 require(handoff.get('terminal_sha256')==authority['terminal']['sha256']and handoff.get('reap_sha256')==authority['reap']['sha256']and handoff.get('historical_child_ended_ns')==authority['historical_child_ended_ns'],'wrong immutable terminal/reap authority')
 require(process.get('identity')=='baseline-publication-local-package-process-guard-v1'and process.get('full_ps_argv')==['ps','-axo','pid,ppid,pgid,stat,etime,args']and process.get('active_model_build_package_browser_processes')==[],'fresh complete process guard required')
 times=[handoff['verified_epoch'],process['captured_epoch'],resource['captured_epoch'],claim['claimed_epoch']]
 require(all(isinstance(t,(int,float))and 0<=now-t<=300 for t in times)and times[0]<=times[1]<=times[3]and times[2]<=times[3],'fresh ordered verification/process/resource/claim required')
 require(resource['source_revision']==POLICY['revision']and resource['committed_logical_bytes']==POLICY['source_logical_bytes'],'exact saved source size required')
 required=2*resource['committed_logical_bytes']+7*1024**3
 require(resource['available_bytes']>=required,'fresh disk budget insufficient; no source export authorized')
 return required

def authorization_guard(auth,manifest_sha,now):
 require(sha(P/'POLICY.json')==POLICY_SHA and auth.get('identity')=='baseline-publication-local-package-authorization-v1','policy/authorization identity')
 own=auth['plan_manifest'];require(own['path']==str(P/'manifest.json')and own['sha256']==manifest_sha,'wrong plan manifest');verify_manifest(own)
 review=independent(auth['plan_review'],manifest_sha)
 require(review.get('identity')=='baseline-publication-local-package-plan-independent-review-v1','wrong plan review identity')
 actual=auth['actual_source_review'];require(actual['manifest']['path']==str(ACTUAL_DIR/'manifest.json')and actual['manifest']['sha256']==ACTUAL_MANIFEST and actual['decision']['sha256']==ACTUAL_SHA and actual['decision']['path']==str(ACTUAL_DIR/'decision.json'),'exact actual source review required')
 r=independent(actual,'7da70569af80739894518761f67a60de0ef132d60782054188901416d3124528')
 require(r['actual_status']=='passed-local-source-only' and r['actual_operation_exit_code']==0 and r['actual_revision']==POLICY['revision']and r['tree']==POLICY['tree']and r['counts']['candidate_members']==41456,'genuine exact actual source facts required')
 a=json.loads(raw(P/'PRESERVATION-ADDENDUM.json'));require(a['source_tree_raw']==r['current_tree_raw']and[a['candidate_index_sha256'],a['candidate_index_bytes']]==[r['current_metadata']['candidate_index']['sha256'],r['current_metadata']['candidate_index']['bytes']]and[a['candidate_raw_HEAD_sha256'],a['candidate_raw_HEAD_bytes']]==[r['current_metadata']['candidate_raw_HEAD']['sha256'],r['current_metadata']['candidate_raw_HEAD']['bytes']]and r['current_metadata']['candidate_ref']['path']==str(Path(POLICY['source'])/'.git'/a['candidate_ref']),'exact actual preservation pins required')
 terminal=pin(r['actual_terminal']);receipt=pin(r['runtime_receipt']);require(terminal['exit_code']==0 and receipt['revision']==POLICY['revision']and receipt['tree']==POLICY['tree']and receipt['physical_members']==41456,'actual terminal/source receipt mismatch')
 require(receipt['committed']is True and receipt['four_bundle_recovery']is True and receipt['package_executed']is False,'genuine completed source-only successor required')
 process=pin(auth['process_guard']);handoff=pin(auth['prior_owner_handoff']);claim=pin(auth['serial_claim']);resource=pin(auth['resource_assessment'])
 ps=process['full_ps_raw'];require(sha(ps['path'])==ps['sha256']and Path(ps['path']).stat().st_size==ps['bytes'],'full ps snapshot not retained')
 authority=POLICY['prior_owner_authority'];terminal_release=pin(authority['terminal']);reap=pin(authority['reap'])
 require(terminal_release.get('serial_slot')=='RELEASED'and terminal_release.get('owned_group_absent')is True and isinstance(terminal_release.get('completion',{}).get('exit_code'),int),'genuine explicit terminal/release required')
 require(reap.get('child_completed')is True and reap.get('owned_group_absent_after_reap')is True and reap.get('ended_ns')==authority['historical_child_ended_ns']and reap.get('child_pid')==terminal_release.get('child_pid'),'genuine same-child completed/reap authority required')
 required=handoff_guard(claim,process,handoff,resource,now)
 require(claim['prior_owner_verification_sha256']==auth['prior_owner_handoff']['sha256'],'claim must bind exact fresh verification')
 require(claim['plan_manifest_sha256']==manifest_sha and claim['actual_source_review_sha256']==ACTUAL_SHA,'claim must bind exact authorities')
 output_guard(POLICY['source'],POLICY['runner_temp'],ROOT/POLICY['durable_execution_directory'])
 return {'required_available_bytes':required,'claim':claim}

def load_tree_guard(path,expected):
 require(sha(path)==expected,'accepted complete-tree helper drift')
 spec=importlib.util.spec_from_file_location('package_accepted_tree_guard',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def parse_tree(data,tree,count,T):
 entries={}
 require(data.endswith(b'\0'),'unterminated saved tree')
 for record in data[:-1].split(b'\0'):
  meta,name=record.split(b'\t',1);mode,kind,oid=meta.decode().split(' ');name=os.fsdecode(name)
  require(kind=='blob'and name not in entries,'duplicate/nonblob saved member');entries[name]=[mode,oid]
 require(len(entries)==count and T.tree_oid(entries)==tree,'saved complete tree identity');return entries

def check_checkout(source,entries,T,metadata):
 source=safe(source);actual=T.physical_members(source)
 require(set(actual)==set(entries),'complete checkout namespace drift')
 for name,info in actual.items():require(list(T.blob_identity(source/name,info))==entries[name],'complete checkout mode/blob drift: '+name)
 for name,expected in metadata.items():
  data=raw(source/'.git'/name);require((hashlib.sha256(data).hexdigest(),len(data))==tuple(expected),'checkout Git metadata drift: '+name)
 return {'physical_members':len(actual),'nofollow':True}

def source_guard():
 require(sha(P/'PRESERVATION-ADDENDUM.json')==ADDENDUM_SHA,'preservation policy drift');a=json.loads(raw(P/'PRESERVATION-ADDENDUM.json'))
 source=Path(POLICY['source']);T=load_tree_guard(source/'tools/baseline_portable_tree_v1.py',a['tree_guard_sha256'])
 ref=a['source_tree_raw'];data=raw(ref['path']);require(hashlib.sha256(data).hexdigest()==ref['sha256']and len(data)==ref['bytes'],'saved complete-tree authority drift')
 entries=parse_tree(data,POLICY['tree'],41456,T)
 refbytes=(POLICY['revision']+'\n').encode()
 metadata={'index':[a['candidate_index_sha256'],a['candidate_index_bytes']],'HEAD':[a['candidate_raw_HEAD_sha256'],a['candidate_raw_HEAD_bytes']],a['candidate_ref']:[hashlib.sha256(refbytes).hexdigest(),len(refbytes)]}
 return lambda:check_checkout(source,entries,T,metadata)

def run_children(out,temp,env,observe,source_reader=raw,guard=lambda:None):
 """Explicit observer injection enables manufactured tests without any subprocess."""
 out=Path(out);temp=Path(temp);cmd=commands();result={'identity':'baseline-publication-local-package-observation-v1','revision':POLICY['revision'],'status':'failed-retained','children':[],'remote_calls':0};active=None
 try:
  for phase in['producer','wrapper']:
   guard()
   if phase=='producer':argv=cmd['producer']
   else:
    sp=temp/'baseline-portable-input-spec.json';data=source_reader(sp);spec=json.loads(data)
    require(spec['revision']==POLICY['revision']and spec['root']==str(temp/'baseline-portable-source')and spec['site']==str(temp/'baseline-portable-site')and spec['observations']==str(temp/'baseline-portable-host-dispatch'),'producer actual runtime output mismatch')
    argv=cmd['wrapper_prefix']+['--spec-sha256',hashlib.sha256(data).hexdigest()]
   child=observe(argv,cmd['cwd'],out/phase,env=env,timeout=1800)
   result['children'].append({'phase':phase,'argv':argv,'returncode':child.returncode})
   require(child.returncode==0,'first child failure: '+phase+'; closed raw evidence retained')
  result['status']='full-package-pass-not-browser-or-live-qualified'
 except BaseException as error:
  active=error;result['error']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};raise
 finally:
  post=None
  try:guard()
  except BaseException as error:
   post=error;result['status']='failed-retained';result['source_post_guard_error']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
   if active is not None:active.source_post_guard_errors=getattr(active,'source_post_guard_errors',[])+[result['source_post_guard_error']]
  try:
   with(out/'receipt.json').open('x')as stream:json.dump(result,stream,indent=2);stream.write('\n')
  except BaseException as error:
   if active is None and post is None:raise
   primary=active if active is not None else post;primary.package_receipt_errors=getattr(primary,'package_receipt_errors',[])+[{'type':type(error).__name__,'message':str(error)}]
  if active is None and post is not None:raise post
 return result

def execute(auth_path,manifest_sha):
 require(POLICY.get('execution_permitted')is True,'execution blocked: '+POLICY['execution_blocker'])
 auth=json.loads(raw(auth_path));authorization_guard(auth,manifest_sha,time.time())
 source=Path(POLICY['source']);temp=Path(POLICY['runner_temp']);out=ROOT/POLICY['durable_execution_directory']
 guard=source_guard();guard()
 require(sha(source/'tools/baseline_observe_child_v3.py')==POLICY['observer_sha256'],'original observer drift')
 temp.mkdir();out.mkdir();env=closed_environment(temp);active=None;pipeline=False;record={'identity':'baseline-publication-local-package-launch-v1','status':'failed-retained','plan_manifest_sha256':manifest_sha,'authorization_sha256':sha(auth_path),'source_revision':POLICY['revision'],'environment':env}
 try:
  for name in['env-home','env-xdg','env-tmp']:(temp/name).mkdir()
  with(out/'authorization.json').open('x')as stream:json.dump(auth,stream,indent=2)
  proof=out/'handoff-proof';proof.mkdir()
  for key in['process_guard','prior_owner_handoff','serial_claim','resource_assessment']:
   ref=auth[key];pin(ref)
   with(proof/(key+'.json')).open('xb')as stream:stream.write(raw(ref['path']))
  ps=pin(auth['process_guard'])['full_ps_raw']
  with(proof/'full-ps.raw').open('xb')as stream:stream.write(raw(ps['path']))
  # No model/SDK/compiler imports; only the unchanged process owner after gates.
  sys.path.insert(0,str(source/'tools'));from baseline_observe_child_v3 import observe
  pipeline=True;result=run_children(out,temp,env,observe,guard=guard);record['status']=result['status'];return result
 except BaseException as error:
  active=error;record['exception']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};raise
 finally:
  post=None
  if not pipeline:
   try:guard()
   except BaseException as error:
    post=error;record['source_post_guard_error']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    if active is not None:active.source_post_guard_errors=getattr(active,'source_post_guard_errors',[])+[record['source_post_guard_error']]
  try:
   with(out/'launch-receipt.json').open('x')as stream:json.dump(record,stream,indent=2);stream.write('\n')
  except BaseException as error:
   if active is None and post is None:raise
   active=active if active is not None else post
   active.package_launch_receipt_errors=getattr(active,'package_launch_receipt_errors',[])+[{'type':type(error).__name__,'message':str(error)}]

  if active is None and post is not None:raise post

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--execute-reviewed-local-package',action='store_true');a.add_argument('--authorization',type=Path);a.add_argument('--manifest-sha256');args=a.parse_args()
 if not args.execute_reviewed_local_package:print(json.dumps({'policy':POLICY,'commands':commands(),'readiness':'requires exact accepted plan review and fresh runtime handoff/claim'},indent=2))
 else:
  require(args.authorization is not None and args.manifest_sha256 is not None,'actual authorization/plan pins required');print(json.dumps(execute(args.authorization,args.manifest_sha256),indent=2))
