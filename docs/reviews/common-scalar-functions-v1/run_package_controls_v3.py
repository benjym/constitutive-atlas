"""Real bundle functions; isolated copies; software-only mutations, no compiled calls."""
from pathlib import Path
import os,sys,json,hashlib,shutil,importlib.util,subprocess,copy
r=Path(__file__).resolve().parents[3];p=Path(__file__).parent;o=p/'package-controls-v3';o.mkdir(exist_ok=False);v=Path('/private/tmp/atlas-common-scalar-functions-v1/package-controls-root-v3');v.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for f in r.iterdir():
 if f.name in ['cpp','cmake','atlas','schemas','models','tests','tools']:shutil.copytree(f,v/f.name,ignore=shutil.ignore_patterns('__pycache__'))
 elif f.name in ['docs','catalogue']:shutil.copytree(f,v/f.name,copy_function=os.link)
 elif f.name not in ['.git','.local','.codex-attachments']: (v/f.name).symlink_to(f,target_is_directory=f.is_dir())
os.environ['GITHUB_SHA']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();sys.path.insert(0,str(r));mods={};builds={};rows=[]
for name,script,b in [('maxwell','build_maxwell_laboratory.py',Path('/private/tmp/atlas-common-scalar-functions-v1/consumers-wasm-v1/maxwell')),('norsand','build_controlled_path_web.py',Path('/private/tmp/atlas-common-scalar-functions-v1/dependents-v1/norsand-wasm'))]:
 spec=importlib.util.spec_from_file_location('control_'+name,p/'package-proposal-v4/tools'/script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=v;mods[name]=m;dst=o/(name+'-build');shutil.copytree(b,dst);builds[name]=dst
 for f in (p/'dependent-independent-review/build-local-v1'/name).iterdir():shutil.copyfile(f,dst/f.name)
def call(name,label,fail=False,hook=None):
 dest=o/(name+'-'+label);error=None
 try:
  if hook:hook()
  mods[name].bundle(dest,builds[name])
 except (ValueError,KeyError,TypeError,FileNotFoundError,json.JSONDecodeError) as e:error=type(e).__name__+': '+str(e)
 assert bool(error)==fail,(name,label,error,fail)
 if not fail:
  engine=dest/('engine-maxwell' if name=='maxwell' else 'engine-path');mf=json.loads((engine/'package-manifest.json').read_text())
  for n,h in mf['files'].items():assert sha(dest/n)==h,n
  q=json.loads((engine/'qualification.json').read_text());rr=q['independent_review'];assert sha(engine/rr['path'])==rr['sha256'];assert (engine/rr['path']).read_bytes()==(builds[name]/rr['path']).read_bytes()
 rows.append({'model':name,'control':label,'expected_rejection':fail,'passed':True,'error':error});(o/'results-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
def bytechange(name,label,path):
 b=path.read_bytes()
 try:path.write_bytes(b+b'\n ');call(name,label,True)
 finally:path.write_bytes(b)
def jsonchange(name,label,path,fn):
 b=path.read_bytes();d=json.loads(b)
 try:fn(d);path.write_text(json.dumps(d));call(name,label,True)
 finally:path.write_bytes(b)
for name in mods:
 call(name,'positive')
 for path in ['cpp/scalar-functions/pow.c','cpp/scalar-functions/libm.h','cpp/scalar-functions/COPYRIGHT','cpp/scalar-functions/NOTICES.txt','cmake/AtlasScalarFunctions.cmake','cpp/include/atlas/tensor.hpp','cpp/include/atlas/solver.hpp','cpp/include/atlas/numerics/symmetric_spectral.hpp','atlas/compiler.py','schemas/model-v0.3.schema.json','cmake/'+('maxwell' if name=='maxwell' else 'controlled-path')+'/CMakeLists.txt']:
  bytechange(name,'source-'+path.replace('/','_'),v/path)
 for directory,suffix in [('cpp/include/atlas','.hpp'),('cpp/scalar-functions','.c'),('atlas','.py'),('schemas','.json')]:
  f=v/directory/('unreviewed'+suffix)
  try:f.write_text('{}\n' if suffix=='.json' else '\n');call(name,'extra-'+suffix[1:],True)
  finally:f.unlink()
 for f in [('maxwell.js' if name=='maxwell' else 'atlas_path_capability.mjs'),('maxwell.wasm' if name=='maxwell' else 'atlas_path_capability.wasm')]:bytechange(name,'artifact-'+f,builds[name]/f)
 for f in (['models.json'] if name=='maxwell' else ['path_catalogue.json','path_api.cpp','path_models.hpp']):bytechange(name,'generated-'+f,builds[name]/'generated'/f)
 q=builds[name]/('maxwell-qualification.json' if name=='maxwell' else 'controlled-path-qualification.json');review=builds[name]/'build-review.json'
 for field,value in [('status','failed'),('model','wrong'),('schema_version','wrong'),('implementation_run','   '),('implementation_run',{'nonstring':True})]:jsonchange(name,'qualification-'+field+'-'+str(value),q,lambda d,k=field,x=value:d.update({k:x}))
 for key in ['binding','gates']:jsonchange(name,'missing-'+key,q,lambda d,k=key:d.pop(k))
 jsonchange(name,'gate-changed',q,lambda d:d['gates'].update({next(iter(d['gates'])):False}))
 jsonchange(name,'review-hash',q,lambda d:d['independent_review'].update(sha256='0'*64))
 for field,value in [('status','failed'),('reviewer_run','/root'),('reviewer_run','  '),('reviewer_run',[1])]:
  qb=q.read_bytes();rb=review.read_bytes();d=json.loads(rb);d[field]=value;review.write_text(json.dumps(d));qd=json.loads(qb);qd['independent_review']['sha256']=sha(review);q.write_text(json.dumps(qd))
  try:call(name,'review-'+field+'-'+str(value),True)
  finally:q.write_bytes(qb);review.write_bytes(rb)
 for path in ['../build-review.json','/private/tmp/review.json','missing.json']:
  jsonchange(name,'unsafe-review-'+path.replace('/','_'),q,lambda d,x=path:d['independent_review'].update(path=x))
 # Capture check: mutate input artifacts only once package destination is made,
 # after real guards captured bytes; no guard is replaced.
 from unittest.mock import patch
 original=Path.mkdir;changed={};expected={}
 for f in [('maxwell.js' if name=='maxwell' else 'atlas_path_capability.mjs'),('maxwell.wasm' if name=='maxwell' else 'atlas_path_capability.wasm')]:expected[f]=(builds[name]/f).read_bytes()
 fired=[False]
 def mkdir(self,*args,**kwargs):
  if not fired[0] and self.is_relative_to(o/(name+'-capture')):
   fired[0]=True
   for f,b in expected.items():(builds[name]/f).write_bytes(b+b'corrupt-after-capture')
  return original(self,*args,**kwargs)
 try:
  with patch.object(Path,'mkdir',mkdir):call(name,'capture')
  engine=o/(name+'-capture')/('engine-maxwell' if name=='maxwell' else 'engine-path')
  for f,b in expected.items():assert (engine/(('maxwell.mjs' if f.endswith('.js') else f) if name=='maxwell' else ('engine.mjs' if f.endswith('.mjs') else 'engine.wasm'))).read_bytes()==b
 finally:
  for f,b in expected.items():(builds[name]/f).write_bytes(b)
 # Current runtime must reject missing current receipt via historical guard.
 if name=='norsand':
  saved=q.read_bytes();q.unlink()
  try:call(name,'current-runtime-historical-fallback',True)
  finally:q.write_bytes(saved)
(o/'summary.json').write_text(json.dumps({'status':'passed','scope':'Software controls only; real bundle guards, isolated source/build copies; no compiled calls','controls':rows,'count':len(rows)},indent=2)+'\n');print(len(rows),'realguardcontrols PASS')
