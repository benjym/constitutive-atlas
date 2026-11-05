"""Source-only reversible-patch, genuine-validator tiny-context and lifecycle checks."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,tempfile,types
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):assert v,n;checks.append(n)
def rejects(fn,n):
 try:fn()
 except (ValueError,AssertionError,FileNotFoundError):checks.append(n);return
 raise AssertionError('accepted '+n)
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
delta=json.loads((HERE/'source-delta.json').read_text())['files'];proof=json.loads((HERE/'proof.json').read_text())
for row in delta:
 p=HERE/row['proposal'];ok(sha(p)==row['sha256']and p.stat().st_size==row['bytes'],'exact proposed '+row['path'])
 if row['preimage_sha256']is not None:ok(sha(ROOT/row['path'])==row['preimage_sha256'],'exact current preimage '+row['path'])
for p in [*HERE.glob('*.py'),*(HERE/'proposed/tools').glob('*.py')]:ast.parse(p.read_text());checks.append('syntax '+p.name)
for name in ('tools/profile_source_compatibility.py','tools/profile_source_compatibility_baseline.py','tools/build_controlled_time_web.py'):
 text=(HERE/'proposed'/name).read_text().replace('from tools.package_final_source_view_v1 import historical_bytes','from tools.rate_restoration_source_view_v2 import historical_bytes')
 if 'profile_source_compatibility'in name:
  text=text.replace('\n from tools.package_final_source_view_v1 import current_snapshot\n current_sources=current_snapshot(root,sources)','').replace(" require(current_snapshot(root,sources)==current_sources,'Current source/authority changed during compatibility validation')\n",'').replace('sources=current_sources,compatibility_bytes=raw','sources=sources,compatibility_bytes=raw')
 ok(text==(HERE/'originals'/name).read_text(),'entire old validator inverse '+name)
for name in ('tools/build_controlled_path_web.py','tools/build_interface2016_web.py','tools/build_interface2016_baseline_web.py','tools/build_maxwell_laboratory.py'):
 ok(not any(r['path']==name for r in delta),'existing final raw guard unchanged '+name)
with tempfile.TemporaryDirectory(prefix='source-validator-',dir=HERE)as td:
 root=Path(td).resolve()
 required={*proof['ancestors'],*[v['archive']for v in proof['aliases'].values()],*proof['implementation'],'cpp/include/atlas/solver.hpp'}
 byname={r['path']:HERE/r['proposal']for r in delta}
 for name in required:
  q=root/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((byname.get(name)or ROOT/name).read_bytes())
 pname='docs/delivery/unheld-finalisation-20261105-v1/package-final-source-binding-v1/proof.json';q=root/pname;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((HERE/'proof.json').read_bytes())
 contract=json.loads((HERE/'consumer-review-contract.json').read_text());review=copy.deepcopy(contract['required_decision']);review['reviewer_run']='manufactured-independent-source-fixture-only';rp=root/contract['canonical_path'];rp.parent.mkdir(parents=True,exist_ok=True);rp.write_text(json.dumps(review))
 view=module('_manufactured_real_view',root/'tools/package_final_source_view_v1.py')
 ok(view.authority(root)['implementation']==proof['implementation'],'real new source-view closed authority manufactured positive')
 source='cpp/include/atlas/solver.hpp';original=(root/source).read_bytes();old=(root/proof['aliases'][source]['archive']).read_bytes()
 ok(view.historical_bytes(root,source,original)==old,'same exact C bytes project to immutable640 solver bytes')
 rejects(lambda:view.historical_bytes(root,source,original+b' '),'unknown source argument rejects')
 snapshot=view.current_snapshot(root,{source:proof['source_delta']['predecessor_sha256']})
 ok(snapshot[source]==hashlib.sha256(original).hexdigest()and snapshot[source]!=hashlib.sha256(old).hexdigest(),'current snapshot stores raw C hash not historical hash')
 ok({view.PROOF,view.REVIEW,*view.IMPLEMENTATION}.issubset(snapshot),'snapshot includes explicit new helper/proof/review bytes')
 for variant in ('profile_source_compatibility.py','profile_source_compatibility_baseline.py'):
  v=module('_real_'+variant.replace('.','_'),HERE/'proposed/tools'/variant)
  # Tiny complete namespace with actual C source plus inert nonnumerical schema/compiler.
  for name in ('atlas/fixture.py','schemas/fixture.json'):
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('inert source')
  v.BINDINGS='fixture/bindings.json';v.DECISION='fixture/decision.json';v.SOURCE_DECISION='fixture/source-decision.json';v.PROOF='fixture/proof.json'
  def put(name,data):
   p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return p
  put(v.SOURCE_DECISION,b'{}');v.SOURCE_DECISION_SHA=sha(root/v.SOURCE_DECISION);put(v.PROOF,b'{}');v.PROOF_SHA=sha(root/v.PROOF)
  for name in v.TOOLS:
   if not(root/name).exists():put(name,b'inert unchanged packaging code')
  sources={source:proof['source_delta']['predecessor_sha256'],'atlas/fixture.py':sha(root/'atlas/fixture.py'),'schemas/fixture.json':sha(root/'schemas/fixture.json')}
  build=root/('build-'+variant);build.mkdir();q={'model':'fixture','status':'passed','binding':{'historical':'unchanged'},'gates':{'retained':True},'implementation_run':'fixture-author','independent_review':{'path':'review.json'}}
  oldreview={'status':'accepted','binding':q['binding'],'gates':q['gates'],'reviewer_run':'fixture-reviewer'};rawreview=json.dumps(oldreview).encode();q['independent_review']['sha256']=hashlib.sha256(rawreview).hexdigest();rawq=json.dumps(q).encode();(build/'qualification.json').write_bytes(rawq);(build/'review.json').write_bytes(rawreview)
  row={'identity':'current17-dedicated-profile-compatibility-v1','profile':'interface2016'if'baseline'in variant else'norsand','model':'fixture','proof_manifest_sha256':v.PROOF_SHA,'source_files':sources,'files':{'qualification.json':hashlib.sha256(rawq).hexdigest(),'review.json':hashlib.sha256(rawreview).hexdigest()},'qualification':'qualification.json','review':'review.json','old_binding':q['binding'],'gates':q['gates']}
  bindings={'interface2016':row}if'baseline'in variant else{'norsand':row,'maxwell':{},'interface2016':{}}
  bindingraw=json.dumps(bindings).encode();put(v.BINDINGS,bindingraw);(build/'source-compatibility.json').write_text(json.dumps(row))
  with patch.dict(sys.modules,{'tools.package_final_source_view_v1':view}):
   accepted={'identity':'current17-baseline-interface-implementation-review-v1'if'baseline'in variant else'current17-direct-profile-compatibility-implementation-review-v1','accepted':True,'proof_manifest_sha256':v.PROOF_SHA,'bindings_sha256':hashlib.sha256(bindingraw).hexdigest(),'implementation':{n:v.digest(v.regular(root,n))for n in v.TOOLS},'reviewer_run':'fixture-reviewer'};put(v.DECISION,json.dumps(accepted).encode())
   result=v.validate(root,build,row['profile'])
   ok(result['qualification']==q and result['qualification_bytes']==rawq and result['review_bytes']==rawreview and result['compatibility_bytes']==(build/'source-compatibility.json').read_bytes(),'historical qualification/receipt/binding bytes exact '+variant)
   ok(result['sources'][source]==hashlib.sha256(original).hexdigest(),'real validator returns current raw stability vector '+variant)
   saved=(root/'atlas/fixture.py').read_bytes();(root/'atlas/fixture.py').write_bytes(saved+b' ');rejects(lambda:v.validate(root,build,row['profile']),'nonaliased source drift rejects '+variant);(root/'atlas/fixture.py').write_bytes(saved)
   result['sources']['atlas/fixture.py']=sha(root/'atlas/fixture.py');(root/'atlas/fixture.py').write_bytes(saved+b' ');ok(any(sha(root/n)!=h for n,h in result['sources'].items()),'existing consumer final raw guard catches drift '+variant);(root/'atlas/fixture.py').write_bytes(saved)
   (build/'review.json').write_bytes(rawreview+b' ');rejects(lambda:v.validate(root,build,row['profile']),'historical review bytes drift rejects '+variant);(build/'review.json').write_bytes(rawreview)
 # Unknown current implementation, original archives, closed authority all reject.
 b=rp.read_bytes();r=json.loads(b);r['reviewer_run']='/root/baseline_migration';rp.write_text(json.dumps(r));rejects(lambda:view.authority(root),'self review rejects');rp.write_bytes(b)
 archive=root/proof['aliases'][source]['archive'];b=archive.read_bytes();archive.write_bytes(b+b' ');rejects(lambda:view.authority(root),'old scientific archive drift rejects');archive.write_bytes(b)
 for name in proof['implementation']:
  p=root/name;b=p.read_bytes();p.write_bytes(b+b' ');rejects(lambda:view.authority(root),'unknown implementation rejects '+name);p.write_bytes(b)
 # Existing current snapshot detects review change after validation as final guards do.
 ok(all(sha(root/n)==h for n,h in snapshot.items()),'real source/authority stability snapshot valid before mutation')
 rp.write_bytes(rp.read_bytes()+b' ');ok(any(sha(root/n)!=h for n,h in snapshot.items()),'review authority bytes drift detected by final snapshot')
continuation=module('_prospective_continuation',HERE/'continuation.py')
byname={r['path']:r for r in delta}
before={str(ROOT/n):{'path':str(ROOT/n),'sha256':byname[n]['preimage_sha256'],'bytes':1}for n in continuation.CHANGED}
for name in ('atlas/compiler.py','cpp/include/atlas/solver.hpp','schemas/model.schema.json','models/fixture.json','CMakeLists.txt','tools/generate_controlled_path.py','tools/unknown.py'):
 before[str(ROOT/name)]={'path':str(ROOT/name),'sha256':'a'*64,'bytes':2}
after=copy.deepcopy(before)
for name in continuation.CHANGED|continuation.ADDED:after[str(ROOT/name)]={'path':str(ROOT/name),'sha256':byname[name]['sha256'],'bytes':byname[name]['bytes']}
continuation.validate_transition(before,after,byname,ROOT);checks.append('only explicit three changed plus one added vector accepted')
for name in ('atlas/compiler.py','cpp/include/atlas/solver.hpp','schemas/model.schema.json','models/fixture.json','CMakeLists.txt','tools/generate_controlled_path.py','tools/unknown.py'):
 bad=copy.deepcopy(after);bad[str(ROOT/name)]['sha256']='b'*64;rejects(lambda:continuation.validate_transition(before,bad,byname,ROOT),'continuation unknown nonpackaging drift rejects '+name)
bad=copy.deepcopy(after);bad[str(ROOT/'tools/extra.py')]={'path':str(ROOT/'tools/extra.py'),'sha256':'a'*64,'bytes':1};rejects(lambda:continuation.validate_transition(before,bad,byname,ROOT),'arbitrary added tool rejects')
bad=copy.deepcopy(after);bad.pop(str(ROOT/'tools/package_final_source_view_v1.py'));rejects(lambda:continuation.validate_transition(before,bad,byname,ROOT),'missing new helper rejects')
bad=copy.deepcopy(before);bad[str(ROOT/'tools/profile_source_compatibility.py')]['sha256']='0'*64;rejects(lambda:continuation.validate_transition(bad,after,byname,ROOT),'unknown original packaging preimage rejects')
for path in [*(ROOT/'atlas').glob('*.py'),ROOT/'CMakeLists.txt',*(ROOT/'cmake').rglob('*.cmake')]:
 text=path.read_text();ok(all(n not in text for n in ('profile_source_compatibility','package_final_source_view','build_controlled_time_web')),'compiler/CMake does not import changed packaging helpers '+str(path.relative_to(ROOT)))
with tempfile.TemporaryDirectory(prefix='continuation-lifecycle-',dir=HERE)as td:
 calls=[];primary=KeyboardInterrupt('manufactured original failure')
 def guarded(*args):
  calls.append(True)
  if len(calls)==2:raise ValueError('manufactured final failure')
  return {'inert':True}
 def fail():raise primary
 with patch.object(continuation,'guard',guarded):
  try:continuation.observe(fail,ROOT,'fixture',Path(td)/'report.json')
  except KeyboardInterrupt as e:ok(e is primary and e.packaging_post_errors==["ValueError('manufactured final failure')"],'continuation preserves primary plus final failure')
  else:raise AssertionError('failure lost')
 record=json.loads((Path(td)/'report.json').read_text());ok(not record['passed']and 'KeyboardInterrupt'in record['traceback']and record['post_errors'],'continuation durable original traceback/posterrors')
ok(not list(HERE.glob('source-validator-*'))and not list(HERE.glob('continuation-lifecycle-*')),'all owned source fixtures removed')
(HERE/'checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'all_reviews_in_fixture_are_manufactured_noncanonical':True,'actual_compiled_modules_or_artifacts_read_executed':False,'actual_source_guard_or_package_executed':False,'fixtures_removed':True},indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks)}))
