"""Synthetic transport receipts only. No artifact is executed."""
import copy,gzip,importlib.util,json,shutil,struct,sys
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent;A=P/'legacy-runtime-v8';sys.path.insert(0,str(A));spec=importlib.util.spec_from_file_location('review_raw',A/'check_raw.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pre=m.load('runtime-rebind-v5/preflight.py');br=P/'build-native-v4/build-receipt.json';artifact=json.loads(br.read_text())['artifact_path'];sha=m.sha
class Synthetic:
 def __init__(self,folder):self.folder=folder;self.calls=0;self.records=[]
 def call(self,req,log):
  self.calls+=1
  # Deliberately no constitutive law: fail all operations except the AD parent
  # prefix needed to exercise all24 frozen special calls. Source gates must fail.
  ok=req.get('chain_index')is not None and req.get('coordinate',1)<=.0005 and self.current==plan['special']['ad_parent_case']
  response={'ok':ok,'state':req['initial'],'message':'SYNTHETIC REVIEW ONLY'}
  if req['mode']in['run','run-controls']:response={'ok':False,'points':[{'control':0.,'state':req['initial'],'strain':[0.]*6}],'message':'SYNTHETIC REVIEW ONLY'}
  record={'call_index':self.calls,'request':req,'argv':m.argv_for(req,artifact,self.folder,self.calls),'returncode':0 if ok else 1,'elapsed_seconds':0.,'raw_stdout':json.dumps(response,allow_nan=False),'stderr':'','response':response}
  if req['mode']=='run-controls':
   controls=self.folder/'controls';controls.mkdir(exist_ok=True);(controls/('call-'+str(self.calls)+'.txt')).write_text(','.join(req['controls_bits']))
  log.write(json.dumps(record)+'\n');self.records.append(record);return response

def metadata(folder,study,report,calls):
 folder.joinpath('report.json').write_text(json.dumps(report)+'\n')
 binding=pre.check();binding.update(pre.build_binding(br,'native',artifact));original=P/('execution-v3/run_native.py'if study=='legacy-md'else 'ordinary-regression-v7/run.py')
 binding.update(identity='md1997-legacy-runtime-binding-v8',study=study,delegate_path=str(A/'collect.py'),delegate_sha256=sha(A/'collect.py'),delegate_command=[sys.executable,'-B',str(A/'collect.py'),'--study',study,'--solver',artifact,'--output',str(folder)],subset=[],original_harness_path=str(original),original_harness_sha256=sha(original),raw_link_manifest_sha256=sha(A/'manifest.json'),v5_preflight_identity='md1997-control-runtime-rebind-v5',delegate_returncode=0,report_sha256=sha(folder/'report.json'))
 (folder/'runtime-binding.json').write_text(json.dumps(binding));(folder/'coordinator-build-receipt.json').write_bytes(br.read_bytes())
 (folder/'transport.json').write_text(json.dumps({'identity':'md1997-legacy-raw-transport-v8','backend':'native','artifact_path':artifact,'artifact_sha256':sha(artifact),'original_call_sha256':sha(P/'execution-v3/run_native.py'),'collector_sha256':sha(A/'collect.py'),'worker':None,'closed':True,'call_count':calls}))

folder=D/'synthetic-full-md';folder.mkdir(exist_ok=False);base=P/'execution-v3';plan=json.loads((base/'requests.json').read_text());module=m.load('execution-v3/run_native.py');backend=Synthetic(folder)
ident={'backend':'native','artifact_path':artifact,'artifact_sha256':sha(artifact),'model_sha256':plan['model_sha256'],'requests_sha256':sha(base/'requests.json'),'policy_sha256':sha(base/'POLICY.md'),'manifest_sha256':sha(base/'manifest.json'),'harness_only_no_constitutive_kernel':True};report={'identity':ident,'cases':{}}
(folder/'identity.json').write_text(json.dumps(ident))
for case in plan['cases']:
 backend.current=case['id']
 with gzip.open(folder/(case['id']+'.jsonl.gz'),'wt')as log:report['cases'][case['id']]=module.run_case(plan,case,backend,log)
with gzip.open(folder/'special.jsonl.gz','wt')as log:report['special']=module.special(plan,backend,log,report['cases'])
report['call_count']=backend.calls;assert len(report['cases'])==35 and len(report['special'])==24
metadata(folder,'legacy-md',report,backend.calls);checks=[{'name':'full35cases24special positive native synthetic','result':m.verify(folder,'legacy-md')}]
folder2=D/'synthetic-full-ordinary';folder2.mkdir(exist_ok=False);policy=json.loads((P/'ordinary-regression-v7/policy.json').read_text());cases=[]
for i,c in enumerate(policy['cases'],1):
 old=Path('/private/tmp/atlas-predictor-constraints-v1/ordinary-native-v6')/(c['model']+'.jsonl.gz')
 with gzip.open(old,'rt')as f:record=json.loads(next(f))
 req={'mode':'run','model':c['model'],'parameters':c['parameters'],'initial':c['initial'],'settings':c['integration_settings'],'protocol':c['protocol'],'target':c['target'],'steps':c['steps'],'cycles':c['cycles']}
 assert record['request']==req;record['call_index']=i;record['argv']=m.argv_for(req,artifact,folder2,i)
 with gzip.open(folder2/(c['model']+'.jsonl.gz'),'wt')as f:f.write(json.dumps(record)+'\n')
 cases.append(m.ordinary_case(c,record['response']))
report2={'identity':'md1997-ordinary-regression-v7','backend':'native','artifact_sha256':sha(artifact),'policy_sha256':sha(P/'ordinary-regression-v7/policy.json'),'manifest_sha256':sha(P/'ordinary-regression-v7/manifest.json'),'cases':cases,'passed':all(c['passed']for c in cases)}
metadata(folder2,'ordinary',report2,16);checks.append({'name':'full16ordinary positive native synthetic','result':m.verify(folder2,'ordinary')})
# Each corruption starts from an accepted complete synthetic fixture. A temporary
# backup is restored after every rejected mutation; outputs describe the mutation.
def reject(name,files,mutate,study='legacy-md',folder=folder):
 saved={f:f.read_bytes()for f in files}
 try:
  mutate()
  try:m.verify(folder,study)
  except Exception as ex:checks.append({'name':name,'rejected':True,'error':type(ex).__name__+': '+str(ex)})
  else:raise AssertionError('false acceptance: '+name)
 finally:
  for f,b in saved.items():f.write_bytes(b)
def rewrite_raw(path,change):
 with gzip.open(path,'rt')as f:rows=[json.loads(x)for x in f]
 change(rows)
 with gzip.open(path,'wt')as f:
  for row in rows:f.write(json.dumps(row)+'\n')
raw=folder/(plan['cases'][0]['id']+'.jsonl.gz')
reject('missing raw call',[raw],lambda:rewrite_raw(raw,lambda r:r.clear()))
reject('extra raw call',[raw],lambda:rewrite_raw(raw,lambda r:r.append(copy.deepcopy(r[0]))))
reject('contradictory raw stdout',[raw],lambda:rewrite_raw(raw,lambda r:r[0].update(raw_stdout='{"ok":true}')))
reject('wrong request initial parent',[raw],lambda:rewrite_raw(raw,lambda r:r[0]['request']['initial'].__setitem__(0,999)))
reject('wrong actual argv artifact',[raw],lambda:rewrite_raw(raw,lambda r:r[0]['argv'].__setitem__(0,'/synthetic/wrong')))
reject('wrong logical rejection returncode',[raw],lambda:rewrite_raw(raw,lambda r:r[0].update(returncode=0)))
reject('nonfinite overflow stdout',[raw],lambda:rewrite_raw(raw,lambda r:r[0].update(raw_stdout='{"ok":false,"x":1e999}')))
reject('duplicate key stdout',[raw],lambda:rewrite_raw(raw,lambda r:r[0].update(raw_stdout='{"ok":false,"ok":true}')))
transport=folder/'transport.json'
reject('unclosed transport',[transport],lambda:transport.write_text(json.dumps(dict(json.loads(transport.read_text()),closed=False))))
rp=folder2/'report.json';bp=folder2/'runtime-binding.json'
def falseordinary():
 r=json.loads(rp.read_text());r['cases'][0]['checks']=[];rp.write_text(json.dumps(r));b=json.loads(bp.read_text());b['report_sha256']=sha(rp);bp.write_text(json.dumps(b))
reject('ordinary missing original decision checks',[rp,bp],falseordinary,'ordinary',folder2)
(D/'full-synthetic-checks.json').write_text(json.dumps({'compiled_calls':0,'synthetic_not_actual':True,'checks':checks},indent=2)+'\n');print('checks',len(checks),'md calls',backend.calls,'special',len(report['special']))
