"""Owned tiny manufactured fixtures only; no actual source/tools/processes."""
from pathlib import Path
import ast,copy,hashlib,json,sys,tempfile,os
from types import SimpleNamespace
import launcher as L
P=Path(__file__).resolve().parent;checks=[]
def check(name,ok):
 if not ok:raise AssertionError(name)
 checks.append({'name':name,'status':'PASS'})
def reject(name,fn):
 try:fn()
 except (ValueError,KeyError,FileNotFoundError):check(name,True);return
 raise AssertionError('not rejected: '+name)
def run():
 for f in [P/'launcher.py',P/'check.py']:ast.parse(f.read_text());check('parse '+f.name,True)
 check('policy frozen before launcher',L.sha(P/'POLICY.json')==L.POLICY_SHA)
 cmd=L.commands('/manufactured/python');check('two exact versioned entrypoints',cmd['producer'][2].endswith('/tools/baseline_prepare_ci_input_v2.py')and cmd['wrapper_prefix'][2].endswith('/tools/baseline_ci_package_portable_host_v3.py'))
 check('runtime source exact',cmd['cwd']==L.POLICY['source'])
 env=L.closed_environment(L.POLICY['runner_temp']);check('closed env no inherited injection',set(env)=={'PATH','HOME','XDG_CONFIG_HOME','TMPDIR','LC_ALL','TZ','PYTHONDONTWRITEBYTECODE','PYTHONNOUSERSITE','PYTHONHASHSEED','GIT_CONFIG_NOSYSTEM','GIT_CONFIG_SYSTEM','GIT_CONFIG_GLOBAL','GIT_CONFIG_COUNT','GIT_ATTR_NOSYSTEM','GIT_NO_REPLACE_OBJECTS','GIT_OPTIONAL_LOCKS','GIT_TERMINAL_PROMPT','GITHUB_SHA','RUNNER_TEMP'})
 check('runtime fixed revision/temp',env['GITHUB_SHA']==L.POLICY['revision']and env['RUNNER_TEMP']==L.POLICY['runner_temp'])
 now=1000;handoff={'identity':'baseline-package-prior-owner-fresh-verification-v3','verified_by':'/root','prior_owner':L.POLICY['prior_owner_authority']['owner'],'state':'released-after-mandatory-reap','all_children_reaped':True,'no_newer_active_owner':True,'verified_epoch':900,'terminal_sha256':L.POLICY['prior_owner_authority']['terminal']['sha256'],'reap_sha256':L.POLICY['prior_owner_authority']['reap']['sha256'],'historical_child_ended_ns':L.POLICY['prior_owner_authority']['historical_child_ended_ns']};process={'identity':'baseline-publication-local-package-process-guard-v1','full_ps_argv':['ps','-axo','pid,ppid,pgid,stat,etime,args'],'active_model_build_package_browser_processes':[],'captured_epoch':920};resource={'source_revision':L.POLICY['revision'],'committed_logical_bytes':L.POLICY['source_logical_bytes'],'available_bytes':22000000000,'captured_epoch':930};claim={'identity':'baseline-publication-local-package-serial-claim-v1','owner':'/root','state':'claimed-before-launch','source_revision':L.POLICY['revision'],'claimed_epoch':940}
 required=L.handoff_guard(claim,process,handoff,resource,now);check('exact tar/export+7GiBbudget',required==2*L.POLICY['source_logical_bytes']+7*1024**3)
 for kind in['owner','claimstate','revision','handoff','reap','ps','active','stale','future','order','disk','size']:
  c=copy.deepcopy(claim);p=copy.deepcopy(process);h=copy.deepcopy(handoff);r=copy.deepcopy(resource)
  if kind=='owner':c['owner']='/other'
  elif kind=='claimstate':c['state']='pending'
  elif kind=='revision':c['source_revision']='b'*40
  elif kind=='handoff':h['state']='active'
  elif kind=='reap':h['all_children_reaped']=False
  elif kind=='ps':p['full_ps_argv']=['ps']
  elif kind=='active':p['active_model_build_package_browser_processes']=['busy']
  elif kind=='stale':h['verified_epoch']=600
  elif kind=='future':p['captured_epoch']=1001
  elif kind=='order':h['verified_epoch']=950
  elif kind=='disk':r['available_bytes']=required-1
  else:r['committed_logical_bytes']=1
  reject('handoff rejects '+kind,lambda c=c,p=p,h=h,r=r:L.handoff_guard(c,p,h,r,now))
 with tempfile.TemporaryDirectory(prefix='atlas-package-plan-mock-')as tmp:
  root=Path(tmp).resolve();source=root/'source';source.mkdir()
  L.output_guard(source,root/'new-temp',root/'new-observation');check('new external outputs allowed',True)
  reject('nested source output',lambda:L.output_guard(source,source/'new',root/'out'))
  reject('same outputs',lambda:L.output_guard(source,root/'out',root/'out'))
  (root/'exists').mkdir();reject('existing output',lambda:L.output_guard(source,root/'exists',root/'out'))
  (root/'link').symlink_to(source);reject('symlink output',lambda:L.output_guard(source,root/'link',root/'out'))
  for kind in['pass','producer-nonzero','wrapper-nonzero','producer-interrupt','wrapper-interrupt','launch-error']:
   out=root/kind;out.mkdir();calls=[];temp=Path(L.POLICY['runner_temp']);raw=(json.dumps({'revision':L.POLICY['revision'],'root':str(temp/'baseline-portable-source'),'site':str(temp/'baseline-portable-site'),'observations':str(temp/'baseline-portable-host-dispatch')})+'\n').encode()
   primary=KeyboardInterrupt('manufactured')
   def observe(argv,cwd,output,**kwargs):
    phase='producer'if 'baseline_prepare_ci_input_v2.py'in argv[2]else'wrapper';calls.append({'phase':phase,'argv':argv,'cwd':cwd,'output':str(output),**kwargs})
    if kind==phase+'-interrupt':raise primary
    if kind=='launch-error':raise OSError('manufactured child launch failed')
    return SimpleNamespace(returncode=1 if kind==phase+'-nonzero'else 0)
   try:L.run_children(out,temp,env,observe,lambda _:raw)
   except BaseException as error:
    check('failure type/primary '+kind,(kind.endswith('interrupt')and error is primary)or(kind=='launch-error'and isinstance(error,OSError))or(kind.endswith('nonzero')and isinstance(error,ValueError)))
   else:check('success only pass',kind=='pass')
   receipt=json.loads((out/'receipt.json').read_text());check('closed receipt '+kind,receipt['status']==('full-package-pass-not-browser-or-live-qualified'if kind=='pass'else'failed-retained'))
   check('firstfailure no later child '+kind,len(calls)==(1 if kind.startswith('producer')or kind=='launch-error'else 2))
   check('actual observer closed env/1800 '+kind,all(c['env']==env and c['timeout']==1800 and c['cwd']==L.POLICY['source']for c in calls))
   if len(calls)==2:check('actual raw specSHA passed '+kind,calls[1]['argv'][-2:]==['--spec-sha256',hashlib.sha256(raw).hexdigest()])
 # Accepted nofollow functions on owned tiny fixtures only.
 T=L.load_tree_guard(L.B/'baseline-five-portable-host-context-v1/proposed/tools/baseline_portable_tree_v1.py','185d85ebdea492dd21b24cc09428f0e8e08b4fcaad70f38def3999bd9bb5de52')
 with tempfile.TemporaryDirectory(prefix='atlas-package-tree-mock-')as tmp:
  r=Path(tmp).resolve();(r/'.git/refs/heads').mkdir(parents=True);(r/'a').write_bytes(b'a');(r/'link').symlink_to('a')
  meta={}
  for name in['index','HEAD','refs/heads/test']:
   data=name.encode();(r/'.git'/name).write_bytes(data);meta[name]=[hashlib.sha256(data).hexdigest(),len(data)]
  entries={n:list(T.blob_identity(r/n,i))for n,i in T.physical_members(r).items()}
  L.check_checkout(r,entries,T,meta);check('complete tiny namespace including literal link',True)
  rows=b''.join((m+' blob '+oid+'\t'+name).encode()+b'\0'for name,(m,oid)in entries.items())
  check('saved raw tree derives exact tree',L.parse_tree(rows,T.tree_oid(entries),2,T)==entries)
  reject('wrong saved tree',lambda:L.parse_tree(rows,'0'*40,2,T))
  for kind in['bytes','mode','link','extra','missing','index','HEAD','refs/heads/test']:
   target=r/'a';original=target.read_bytes()
   if kind=='bytes':target.write_bytes(b'b')
   elif kind=='mode':target.chmod(0o755)
   elif kind=='link':(r/'link').unlink();(r/'link').symlink_to('else')
   elif kind=='extra':(r/'extra').write_bytes(b'x')
   elif kind=='missing':target.unlink()
   else:(r/'.git'/kind).write_bytes(b'changed')
   reject('fresh checkout rejects '+kind,lambda:L.check_checkout(r,entries,T,meta))
   if kind in['bytes','missing']:target.write_bytes(original)
   elif kind=='mode':target.chmod(0o644)
   elif kind=='link':(r/'link').unlink();(r/'link').symlink_to('a')
   elif kind=='extra':(r/'extra').unlink()
   else:(r/'.git'/kind).write_bytes(kind.encode())
  for fail in[False,True]:
   out=r/('failed'if fail else'success');out.mkdir();calls=[];primary=KeyboardInterrupt('original child')
   def observer(*args,**kwargs):
    calls.append('child')
    if fail:raise primary
    return SimpleNamespace(returncode=0)
   def guard():
    calls.append('guard')
    if calls.count('guard')==(2 if fail else 3):raise RuntimeError('post preservation failure')
   try:L.run_children(out,Path(L.POLICY['runner_temp']),env,observer,lambda _:raw,guard)
   except BaseException as error:
    check('postguard preserves primary '+str(fail),error is primary if fail else isinstance(error,RuntimeError))
    if fail:check('primary retains post error',error.source_post_guard_errors[0]['message']=='post preservation failure')
   else:raise AssertionError('post failure silently passed')
   check('post failure closes nonpass receipt '+str(fail),json.loads((out/'receipt.json').read_text())['status']=='failed-retained')
 check('nonempty author required in independent guard',"r.get('author_run')and r.get('reviewer_run')"in (P/'launcher.py').read_text())
 check('preservation addendum frozen',L.sha(P/'PRESERVATION-ADDENDUM.json')==L.ADDENDUM_SHA)
 # Saved metadata only; no candidate/base content or object access.
 decision=json.loads((L.ACTUAL_DIR/'decision.json').read_text());check('exact genuine actual review pin',L.sha(L.ACTUAL_DIR/'decision.json')==L.ACTUAL_SHA)
 check('actual source identity41456',decision['actual_revision']==L.POLICY['revision']and decision['tree']==L.POLICY['tree']and decision['counts']['candidate_members']==41456)
 check('original72 assertions preserved before exporter extension',len(checks)==72)
 from export_regression import run as exporter_checks
 exporter_checks(L,check)
 check('all original80 assertions before v3 extension',len(checks)==80)
 from handoff_regression import run as handoff_checks
 handoff_checks(L,check,reject,handoff,process,resource,claim,now)
 return {'identity':'baseline-publication-local-package-plan-source-checks-v1','status':'PASS','count':len(checks),'actual_operations':False,'candidate_source_git_tool_sdk_process_calls':0,'checks':checks}
if __name__=='__main__':print(json.dumps(run(),indent=2))
