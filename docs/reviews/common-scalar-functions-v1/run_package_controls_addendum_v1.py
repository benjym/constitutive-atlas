"""Supplemental real-guard software controls; no compiled calls or shared edits."""
from pathlib import Path
import json,hashlib,importlib.util,sys,os,subprocess,shutil
from unittest.mock import patch
r=Path(__file__).resolve().parents[3];p=Path(__file__).parent;o=p/'package-controls-addendum-v1';o.mkdir(exist_ok=False);v=Path('/private/tmp/atlas-common-scalar-functions-v1/package-controls-root-v5');sys.path.insert(0,str(v));os.environ['GITHUB_SHA']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();rows=[];mods={};builds={};sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for name,script in [('maxwell','build_maxwell_laboratory.py'),('norsand','build_controlled_path_web.py')]:
 spec=importlib.util.spec_from_file_location('addendum_'+name,p/'package-proposal-v4/tools'/script);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=v;mods[name]=m;builds[name]=p/'package-controls-v5'/(name+'-build')
def call(name,label,fail=False):
 error=None;dest=o/(name+'-'+label)
 try:mods[name].bundle(dest,builds[name])
 except (ValueError,KeyError,TypeError,FileNotFoundError,json.JSONDecodeError) as e:error=type(e).__name__+': '+str(e)
 assert bool(error)==fail,(name,label,error)
 rows.append(dict(model=name,control=label,expected_rejection=fail,passed=True,error=error));(o/'progress.json').write_text(json.dumps(rows,indent=2)+'\n');return dest
def bytechange(name,label,f):
 b=f.read_bytes()
 try:f.write_bytes(b+b' ');call(name,label,True)
 finally:f.write_bytes(b)
def jsonchange(name,label,f,fn):
 b=f.read_bytes();d=json.loads(b)
 try:fn(d);f.write_text(json.dumps(d));call(name,label,True)
 finally:f.write_bytes(b)
for name in mods:
 build=builds[name];q=build/('maxwell-qualification.json' if name=='maxwell' else 'controlled-path-qualification.json');review=build/'build-review.json';qb=q.read_bytes();rb=review.read_bytes()
 model=v/('models/research/maxwell/maxwell-itasca900-zero-spin-ode.json' if name=='maxwell' else 'models/research/norsand/norsand-jefferies-1993-active-axial.json');bytechange(name,'approved-model',model)
 if name=='norsand':bytechange(name,'synthetic-fixture',v/'tests/fixtures/controlled-path/synthetic-model.json')
 else:
  # The reference lives in read-only hardlinked evidence; detach isolated copy
  # before mutation so no original scientific evidence can be modified.
  ref=v/mods[name].REFERENCE;b=ref.read_bytes();ref.unlink();ref.write_bytes(b);bytechange(name,'reference-policy',ref)
 f=v/'cpp/scalar-functions/pow.c';b=f.read_bytes();f.unlink()
 try:call(name,'required-source-missing',True)
 finally:f.write_bytes(b)
 for field in (['source_manifest_sha256','module_sha256','reference_policy_sha256'] if name=='maxwell' else ['sources','artifacts','generated']):jsonchange(name,'bad-binding-'+field,q,lambda d,k=field:d['binding'].update({k:'changed'}))
 if name=='norsand':
  for field in ['native_successes','wasm_rejections','source_analytical','parity']:jsonchange(name,'count-or-sourcegate-'+field,q,lambda d,k=field:d['gates'].update({k:0}))
 for f in [q,review]:
  b=f.read_bytes()
  try:
   f.unlink();call(name,'missing-'+f.name,True);f.write_bytes(b'{malformed');call(name,'malformed-'+f.name,True)
  finally:f.write_bytes(b)
 # Authentic copied review altered only as a negative input; qualification
 # original binding unchanged, review SHA recomputed to isolate binding guard.
 d=json.loads(rb);d['binding']={};review.write_text(json.dumps(d));d=json.loads(qb);d['independent_review']['sha256']=sha(review);q.write_text(json.dumps(d))
 try:call(name,'changed-reviewed-binding',True)
 finally:q.write_bytes(qb);review.write_bytes(rb)
 external=o/(name+'-outside-review.json');external.write_bytes(rb);review.unlink();review.symlink_to(external.resolve())
 try:call(name,'canonical-review-symlink-escape',True)
 finally:review.unlink();review.write_bytes(rb)
 # Change source after the real first guard. Existing full final guard must fail.
 f=v/'cpp/scalar-functions/pow.c';b=f.read_bytes();fired=[False];origread=Path.read_text;origmkdir=Path.mkdir
 def read(self,*a,**kw):
  value=origread(self,*a,**kw)
  if name=='maxwell' and self==v/'docs/reviews/maxwell-checklist-v2/README.md' and not fired[0]:fired[0]=True;f.write_bytes(b+b' ')
  return value
 def mkdir(self,*a,**kw):
  if name=='norsand' and self.is_relative_to(o/(name+'-late-source')) and not fired[0]:fired[0]=True;f.write_bytes(b+b' ')
  return origmkdir(self,*a,**kw)
 try:
  with patch.object(Path,'read_text',read),patch.object(Path,'mkdir',mkdir):call(name,'late-source',True)
  assert fired[0]
 finally:f.write_bytes(b)
 # Captured qualification/review bytes must survive subsequent input drift.
 fired=[False]
 def mkdir_capture(self,*a,**kw):
  if self.is_relative_to(o/(name+'-capture-records')) and not fired[0]:fired[0]=True;q.write_text('changed after capture');review.write_text('changed after capture')
  return origmkdir(self,*a,**kw)
 try:
  with patch.object(Path,'mkdir',mkdir_capture):dest=call(name,'capture-records')
  engine=dest/('engine-maxwell' if name=='maxwell' else 'engine-path');assert fired[0];assert (engine/'qualification.json').read_bytes()==qb;assert (engine/'build-review.json').read_bytes()==rb
 finally:q.write_bytes(qb);review.write_bytes(rb)
# Historical fallback under its original exact source/artifact identity.
name='norsand';old=json.loads((r/'docs/ingestion/norsand-1993/shared-integration-v1/target-source-freeze-v2.json').read_text());saved={}
for n,h in old['files'].items():
 if n.startswith('cpp/include/atlas/') or n=='cmake/controlled-path/CMakeLists.txt':
  f=v/n;saved[n]=f.read_bytes();archive=r/'catalogue/source-snapshots'/h/n;source=archive if archive.is_file() else r/n;assert sha(source)==h,n;f.write_bytes(source.read_bytes())
current=builds[name];historical=o/'historical-build';shutil.copytree(r/'docs/ingestion/norsand-1993/shared-integration-v1/wasm-v2',historical);builds[name]=historical
try:
 call(name,'historical-positive');bytechange(name,'historical-source-change',v/'cpp/include/atlas/tensor.hpp');bytechange(name,'historical-artifact-change',historical/'atlas_path_capability.wasm')
finally:
 builds[name]=current
 for n,b in saved.items():(v/n).write_bytes(b)
(o/'summary.json').write_text(json.dumps({'status':'passed','scope':'Supplemental software controls only; no compiled calls','count':len(rows),'controls':rows},indent=2)+'\n');print(len(rows),'supplemental realguardcontrols PASS')
