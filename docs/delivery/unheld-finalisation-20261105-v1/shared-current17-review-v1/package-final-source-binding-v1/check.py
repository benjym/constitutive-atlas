from pathlib import Path
import ast,hashlib,json,types,tempfile,copy
O=Path(__file__).resolve().parent;N=O.parents[1];A=N/'package-final-source-binding-v1';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def h(b):return hashlib.sha256(b).hexdigest()
def ok(x,n):assert x,n;checks.append(n)
def rejected(f,n):
 try:f()
 except (ValueError,KeyError,FileNotFoundError):checks.append(n)
 else:raise AssertionError('accepted '+n)
ok(h((A/'manifest.json').read_bytes())=='f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9','exact frozen author manifest')
manifest=json.loads((A/'manifest.json').read_text())
for r in manifest['files']:ok(h((A/r['path']).read_bytes())==r['sha256'] and (A/r['path']).stat().st_size==r['bytes'],'manifest '+r['path'])
delta=json.loads((A/'source-delta.json').read_text())['files'];proof=json.loads((A/'proof.json').read_text());contract=json.loads((A/'consumer-review-contract.json').read_text());review=contract['required_decision'];review['reviewer_run']='/root/publication_operations_review'
for r in delta:
 ok(h((A/r['proposal']).read_bytes())==r['sha256'],'payload '+r['path'])
 if r['preimage_sha256']:ok(h((A/'originals'/r['path']).read_bytes())==r['preimage_sha256'],'retained preimage '+r['path'])
module=types.ModuleType('inert_source_view');exec(compile((A/'proposed/tools/package_final_source_view_v1.py').read_text(),'helper','exec'),module.__dict__)
# Literal bounded source bytes only; no artifacts, imports of material kernels or processes.
data={module.PROOF:(A/'proof.json').read_bytes(),module.REVIEW:(json.dumps(review)+'\n').encode()}
for name in proof['implementation']:data[name]=(A/'proposed'/name).read_bytes()
for name in [module.SOURCE,*proof['ancestors'],*[r['archive'] for r in proof['aliases'].values()]]:data[name]=((A/'proposed'/name)if(A/'proposed'/name).is_file()else W/name).read_bytes()
physical_regular=module.regular
with tempfile.TemporaryDirectory(dir=O,prefix='nofollow-')as td:
 root=Path(td);(root/'file').write_bytes(b'inert');(root/'link').symlink_to(root/'file')
 ok(physical_regular(root,'file')==b'inert','physical regular source read')
 for name in ['link','../escape','/absolute']:
  rejected(lambda:physical_regular(root,name),'reject unsafe physical path '+name)
base=copy.deepcopy(data);module.regular=lambda root,name:data[str(name)]
ok(module.authority(W)==proof,'genuine exact source authority closure')
for name,row in proof['aliases'].items():ok(h(module.historical_bytes(W,name,data[name]))==row['predecessor_sha256'],'historical alias '+name)
ok(module.historical_bytes(W,'unknown/name',b'unchanged')==b'unchanged','unknown path cannot be aliased')
for name in [*proof['implementation'],module.SOURCE,*proof['ancestors'],*[r['archive']for r in proof['aliases'].values()]]:
 old=data[name];data[name]=old+b'corrupt';rejected(lambda:module.authority(W),'reject authority drift '+name);data[name]=old
for key,value in [('reviewer_run',''),('reviewer_run',review['author_run']),('decision','pending'),('unresolved_blockers',['x']),('proof_sha256','0'*64),('extra',1)]:
 bad=dict(review);bad[key]=value;data[module.REVIEW]=json.dumps(bad).encode();rejected(lambda:module.authority(W),'reject closed review '+key+str(value))
data[module.REVIEW]=base[module.REVIEW]
sources={module.SOURCE:module.OLD};snap=module.current_snapshot(W,sources);ok(snap[module.SOURCE]==module.NEW and module.PROOF in snap and module.REVIEW in snap,'current snapshot raw solver plus authorities')
data['unknown/source']=b'actual';rejected(lambda:module.current_snapshot(W,{'unknown/source':h(b'expected')}),'unknown source mismatch blocks snapshot')
# Exact inverse of the narrow three original hook edits; all old validation blocks retained.
for name in ['profile_source_compatibility.py','profile_source_compatibility_baseline.py']:
 old=(A/'originals/tools'/name).read_text();new=(A/'proposed/tools'/name).read_text();inverse=new.replace('from tools.package_final_source_view_v1 import historical_bytes','from tools.rate_restoration_source_view_v2 import historical_bytes').replace(' from tools.package_final_source_view_v1 import current_snapshot\n current_sources=current_snapshot(root,sources)\n','').replace(" require(current_snapshot(root,sources)==current_sources,'Current source/authority changed during compatibility validation')\n",'').replace('sources=current_sources','sources=sources');ok(inverse==old,'all historical guards inverse exact '+name)
 ok(new.index('current_sources=current_snapshot')<new.index('for n,h in sources.items()')<new.index('require(current_snapshot(root,sources)==current_sources'),'raw pre/post surrounds complete historical validation '+name)
old=(A/'originals/tools/build_controlled_time_web.py').read_text();new=(A/'proposed/tools/build_controlled_time_web.py').read_text();ok(new.replace('from tools.package_final_source_view_v1 import historical_bytes','from tools.rate_restoration_source_view_v2 import historical_bytes')==old,'controlled-time only closed-view import changes')
# Inert continuation lifecycle: operation failures and postguard failures both retained.
c=types.ModuleType('inert_continuation');c.__file__=str(A/'continuation.py');exec(compile((A/'continuation.py').read_text(),'continuation','exec'),c.__dict__)
for scenario in ['pass','primary','post','both']:
 with tempfile.TemporaryDirectory(dir=O,prefix='fixture-') as d:
  count=[0]
  def guard(*args):
   count[0]+=1
   if count[0]==2 and scenario in ['post','both']:raise ValueError('post failure')
   return {'same':'binding'}
  def operation():
   if scenario in ['primary','both']:raise ValueError('primary failure')
   return 7
  c.guard=guard;out=Path(d)/'receipt.json'
  try:value=c.observe(operation,W,'inert',out)
  except (ValueError,RuntimeError) as e:ok(scenario!='pass','failure propagated '+scenario)
  else:ok(value==7 and scenario=='pass','positive lifecycle')
  receipt=json.loads(out.read_text());ok(count[0]==2 and receipt['passed']==(scenario=='pass'),'pre/final receipt '+scenario);ok(bool(receipt['primary'])==(scenario in ['primary','both']) and bool(receipt['post_errors'])==(scenario in ['post','both']),'primary/post truthful '+scenario)
  rejected(lambda:c.observe(operation,W,'inert',out),'never overwrite '+scenario)
byname={r['path']:r for r in delta};before={str(W/n):{'path':str(W/n),'sha256':byname[n]['preimage_sha256'],'bytes':1}for n in c.CHANGED}
for name in ['atlas/a.py','cpp/a.cpp','models/a.json','schemas/a.json','CMakeLists.txt','tools/generator.py','tools/unknown.py']:before[str(W/name)]={'path':str(W/name),'sha256':'a'*64,'bytes':2}
after=copy.deepcopy(before)
for name in c.CHANGED|c.ADDED:after[str(W/name)]={'path':str(W/name),'sha256':byname[name]['sha256'],'bytes':byname[name]['bytes']}
c.validate_transition(before,after,byname,W);ok(True,'exact changed3 added1 accepted')
for name in before:
 bad=copy.deepcopy(after);bad[name]['sha256']='b'*64;rejected(lambda:c.validate_transition(before,bad,byname,W),'reject nonreviewed delta '+name)
for change in ['added','missing']:
 bad=copy.deepcopy(after)
 if change=='added':bad[str(W/'tools/new.py')]={'path':'extra','sha256':'a'*64,'bytes':1}
 else:bad.pop(str(W/'tools/package_final_source_view_v1.py'))
 rejected(lambda:c.validate_transition(before,bad,byname,W),'reject namespace '+change)
s=(A/'continuation.py').read_text();ok("if current!=expected:raise ValueError"in s and 'only literal packaging tool transition allowed'in s,'exact namespace and literal delta gates');ok("*f['artifacts'].values()"in s and "*f['candidates'].values()"in s and "verify(launch['plan_review'])"in s,'original artifacts candidates and launch review gates retained')
(O/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'actual_execution':False,'fixtures_removed':True},indent=2)+'\n');print(json.dumps({'passed':True,'count':len(checks)}))
