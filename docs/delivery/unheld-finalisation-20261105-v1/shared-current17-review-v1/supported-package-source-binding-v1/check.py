from pathlib import Path
import hashlib,json,types,tempfile,copy,os
O=Path(__file__).resolve().parent;N=O.parents[1];A=N/'supported-package-source-binding-v1';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ok(v,n):assert v,n;checks.append(n)
def rejects(f,n):
 try:f()
 except (ValueError,KeyError,FileNotFoundError):checks.append(n)
 else:raise AssertionError('accepted '+n)
c=types.ModuleType('inert_continuation');c.__file__=str(A/'continuation.py');exec(compile((A/'continuation.py').read_text(),'continuation','exec'),c.__dict__)
refs=json.loads((A/'continuation-authorities.json').read_text())
for name,row in refs.items():ok(h(row['path'])==row['sha256']and Path(row['path']).stat().st_size==row['bytes'],'literal metadata authority '+name)
pre=json.loads(Path(refs['source_freeze']['path']).read_text());before={r['path']:r for r in pre['source_inventory']};qualified=json.loads((A/'qualified-preimages.json').read_text())
for n,r in qualified.items():ok(before[str(W/n)]==r,'genuine qualified preimage '+n)
prior=json.loads(Path(refs['previous_receipt_delta']['path']).read_text())['files'];new=json.loads((A/'source-delta.json').read_text())['files'];byname={r['path']:r for r in [*prior,*new]};retained=next(r for r in json.loads(Path(refs['previous_packaging_delta']['path']).read_text())['files']if r['path']=='tools/package_final_source_view_v1.py');byname[retained['path']]=retained
current=copy.deepcopy(before)
for n in c.CHANGED|c.ADDED:current[str(W/n)]={'path':str(W/n),'sha256':byname[n]['sha256'],'bytes':byname[n]['bytes']}
c.validate_transition(before,current,byname,W,qualified);ok(len(before)==811 and len(current)==813,'exact original811 to sixchanged plus twoadded813')
for name in ['cpp/include/atlas/solver.hpp','atlas/compiler.py','CMakeLists.txt','tools/test_web_package.mjs']:
 bad=copy.deepcopy(current);bad[str(W/name)]['sha256']='0'*64;rejects(lambda:c.validate_transition(before,bad,byname,W,qualified),'reject unreviewed current delta '+name)
bad=copy.deepcopy(current);bad[str(W/'tools/extra.mjs')]={'path':'extra','sha256':'0'*64,'bytes':0};rejects(lambda:c.validate_transition(before,bad,byname,W,qualified),'reject namespace expansion')
with tempfile.TemporaryDirectory(dir=O,prefix='site-fixture-')as td:
 root=Path(td);(root/'nested').mkdir();f=root/'nested/a';f.write_bytes(b'inert');f.chmod(0o644);first=c.physical_site(root);ok(first['nested/a']['sha256']==hashlib.sha256(b'inert').hexdigest()and first['nested/a']['mode']==0o644,'physical complete SHA mode size vector')
 f.chmod(0o600);ok(c.physical_site(root)!=first,'site mode drift detected');f.chmod(0o644);f.write_bytes(b'drift');ok(c.physical_site(root)!=first,'site content drift detected');f.write_bytes(b'inert');(root/'extra').write_bytes(b'new');ok(c.physical_site(root)!=first,'site extra member detected');(root/'extra').unlink();(root/'link').symlink_to(root/'nested',target_is_directory=True);rejects(lambda:c.physical_site(root),'site directory symlink rejects');(root/'link').unlink();f.unlink();f.symlink_to(root/'missing');rejects(lambda:c.physical_site(root),'site symlink file rejects')
# Pure retained-site callback fixtures: no real site path or asset reads.
from pathlib import PurePosixPath
class FixturePath(PurePosixPath):
 def resolve(self):return self
original_path=c.Path;original_verify=c.verify;original_load=c.load;original_physical=c.physical_site
phases=['fast-source-contracts','retained-source-guards','standard-web-package','package-engine-smoke','all994-built-dataset-transport','original-package-contracts'];failure={'phase_results':[{'phase':n,'returncode':0,'mandatory_reap':True}for n in phases],'files':[{'path':'/fake/physical-site-inventory.json'}]};inventory={'site':'/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v3','files':[{'path':str(i),'sha256':'a'*64,'size_bytes':1,'mode':420}for i in range(1565)]};actual={r['path']:dict(r)for r in inventory['files']}
c.Path=FixturePath;c.verify=lambda row:None;c.load=lambda path:inventory if str(path).endswith('physical-site-inventory.json')else failure;c.physical_site=lambda site:actual
ok(c.retained_site({'path':'/fake/failure.json'})['members']==1565,'complete synthetic1565-site/six-stage reuse positive')
for key,value in [('returncode',1),('mandatory_reap',False),('phase','wrong')]:
 old=failure['phase_results'][0][key];failure['phase_results'][0][key]=value;rejects(lambda:c.retained_site({'path':'/fake/failure.json'}),'reuse rejects stage '+key);failure['phase_results'][0][key]=old
for key,value in [('sha256','b'*64),('mode',384),('size_bytes',2)]:
 old=actual['0'][key];actual['0'][key]=value;rejects(lambda:c.retained_site({'path':'/fake/failure.json'}),'reuse rejects full-site '+key);actual['0'][key]=old
old=actual.pop('0');rejects(lambda:c.retained_site({'path':'/fake/failure.json'}),'reuse rejects missing site member');actual['0']=old
actual['extra']={'path':'extra'};rejects(lambda:c.retained_site({'path':'/fake/failure.json'}),'reuse rejects extra site member');actual.pop('extra')
c.Path=original_path;c.verify=original_verify;c.load=original_load;c.physical_site=original_physical
for scenario in ['pass','primary','post','both']:
 with tempfile.TemporaryDirectory(dir=O,prefix='lifecycle-')as td:
  calls=[0]
  def guard(*args):
   calls[0]+=1
   if calls[0]==2 and scenario in ['post','both']:raise ValueError('post failure')
   return {'same':'binding'}
  def operation():
   if scenario in ['primary','both']:raise ValueError('primary failure')
   return 7
  c.guard=guard;out=Path(td)/'receipt.json'
  try:result=c.observe(operation,W,'inert',out)
  except (ValueError,RuntimeError):ok(scenario!='pass','propagate failure '+scenario)
  else:ok(result==7 and scenario=='pass','positive observed return')
  record=json.loads(out.read_text());ok(calls[0]==2 and record['passed']==(scenario=='pass'),'pre/final record '+scenario);ok(bool(record['primary'])==(scenario in ['primary','both'])and bool(record['post_errors'])==(scenario in ['post','both']),'retain primary/post separately '+scenario)
  rejects(lambda:c.observe(operation,W,'inert',out),'reject overwrite '+scenario)
valid={'identity':'supported-package-source-binding-independent-review-v1','accepted':True,'author_run':'/root/baseline_migration','reviewer_run':'/root/publication_operations_review','proposal_manifest_sha256':'inert','unresolved_blockers':[]};c.validate_review(valid,'inert');ok(True,'exact review binding accepted')
for key,value in [('accepted',False),('author_run','other'),('reviewer_run','/root/baseline_migration'),('proposal_manifest_sha256','other'),('unresolved_blockers',['x'])]:
 bad=dict(valid);bad[key]=value;rejects(lambda:c.validate_review(bad,'inert'),'review binding rejects '+key)
source=(A/'continuation.py').read_text();ok("six genuine completed/reaped phases required"in source and 'len(actual)!=1565'in source,'complete genuine six-phase/site authority mandatory');ok("site=retained_site(refs['retained_site_failure'])"in source,'site checked within every pre/final guard');ok("*f['artifacts'].values()"in source and "verify(launch['plan_review'])"in source,'compiled artifacts and launch authority retained')
(O/'continuation-checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'actual_site_or_artifact_read':False,'fixtures_removed':True},indent=2)+'\n');print(json.dumps({'passed':True,'count':len(checks)}))
