"""Source-only receipt semantics, closed view and original811 transition checks."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,tempfile
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):assert v,n;checks.append(n)
def rejects(fn,n):
 try:fn()
 except (ValueError,AssertionError,KeyError,FileNotFoundError):checks.append(n);return
 raise AssertionError('accepted '+n)
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
delta=json.loads((HERE/'source-delta.json').read_text())['files'];proof=json.loads((HERE/'proof.json').read_text());byname={r['path']:r for r in delta}
for r in delta:
 p=HERE/r['proposal'];ok(sha(p)==r['sha256']and p.stat().st_size==r['bytes'],'proposal exact '+r['path'])
 if r['preimage_sha256']is not None:ok(sha(ROOT/r['path'])==r['preimage_sha256'],'current install preimage '+r['path'])
for p in [*HERE.glob('*.py'),*(HERE/'proposed/tools').glob('*.py')]:ast.parse(p.read_text());checks.append('syntax '+p.name)
for n in ('tools/profile_source_compatibility.py','tools/profile_source_compatibility_baseline.py','tools/build_controlled_time_web.py'):
 text=(HERE/'proposed'/n).read_text().replace('from tools.package_final_source_view_v2 import','from tools.package_final_source_view_v1 import')
 ok(text==(HERE/'originals'/n).read_text(),'entire existing hook inverse '+n)
for n in ('tools/build_interface2016_web.py','tools/build_interface2016_baseline_web.py'):
 text=(HERE/'proposed'/n).read_text();expression="source_closure=(json.loads(compatibility['compatibility_bytes'])['source_files'] if compatibility is not None else closure)"
 ok(text.count(expression)==1 and text.replace(expression,'source_closure=closure')==(HERE/'originals'/n).read_text(),'only Interface receipt expression changes '+n)
 tree=ast.parse(text);bundle=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='bundle');block=next(x for x in bundle.body if isinstance(x,ast.If)and ast.unparse(x.test)=='refresh is not None')
 historical={'solver':'historical-digest'};rawcurrent={'solver':'current-digest','proof':'current-proof'}
 q={'binding':{'source_closure':historical,'artifacts':{'engine.mjs':'js','engine.wasm':'wasm'},'generated':{'path_catalogue.json':'catalogue'}}}
 for compatible in (True,False):
  compatibility={'sources':rawcurrent,'qualification':q,'compatibility_bytes':json.dumps({'source_files':historical}).encode()}if compatible else None
  namespace={'compatibility':compatibility,'refresh':{'qualification':q},'sha':lambda _: 'inert','definition':Path('/inert/definition'),'build':Path('/inert/build'),'json':json}
  exec(compile(ast.Module(body=block.body,type_ignores=[]),'<exact-original-receipt-block>','exec'),namespace)
  ok(namespace['receipt']['source_closure']==historical,'real extracted receipt historical map '+n+' '+str(compatible))
  ok(namespace['closure']==(rawcurrent if compatible else historical),'raw final stability variable preserved '+n+' '+str(compatible))
  ok(q['binding']['source_closure']==historical,'qualification binding untouched '+n+' '+str(compatible))
 ok("if any(sha(ROOT/name) != digest for name,digest in closure.items())"in text,'existing blocking final raw guard remains '+n)
for n in ('tools/test_interface2016_package.mjs','tools/test_interface2016_baseline_package.mjs','cpp/include/atlas/solver.hpp','atlas/compiler.py','CMakeLists.txt'):
 ok(n not in byname,'no checker/math/compiler change '+n)
with tempfile.TemporaryDirectory(prefix='closed-source-view-',dir=HERE)as td:
 root=Path(td).resolve();required={*proof['ancestors'],*[v['archive']for v in proof['aliases'].values()],*proof['implementation'],'cpp/include/atlas/solver.hpp'}
 for n in required:
  q=root/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((HERE/byname[n]['proposal']if n in byname else ROOT/n).read_bytes())
 pname='docs/delivery/unheld-finalisation-20261105-v1/interface-receipt-source-closure-v1/proof.json';q=root/pname;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((HERE/'proof.json').read_bytes())
 contract=json.loads((HERE/'consumer-review-contract.json').read_text());decision=copy.deepcopy(contract['required_decision']);decision['reviewer_run']='manufactured-noncanonical-independent-fixture';rp=root/contract['canonical_path'];rp.parent.mkdir(parents=True,exist_ok=True);rp.write_text(json.dumps(decision))
 view=module('_new_closed_source_view',root/'tools/package_final_source_view_v2.py');ok(view.authority(root)['implementation']==proof['implementation'],'real seven-file closed authority positive')
 for n,row in proof['aliases'].items():
  ok(view.historical_bytes(root,n,(root/n).read_bytes())==(root/row['archive']).read_bytes(),'exact immutable historical alias '+n)
 rawmap=view.current_snapshot(root,{view.SOURCE:view.OLD});ok(rawmap[view.SOURCE]==view.NEW,'raw current snapshot C unchanged')
 ok(set(proof['implementation'])|{view.PROOF,view.REVIEW}<=set(rawmap),'snapshot covers both helpers/builders/newproof/review')
 for n in proof['implementation']:
  p=root/n;b=p.read_bytes();p.write_bytes(b+b' ');rejects(lambda:view.authority(root),'unknown implementation drift rejects '+n);p.write_bytes(b)
 b=rp.read_bytes();r=json.loads(b);r['reviewer_run']='/root/baseline_migration';rp.write_text(json.dumps(r));rejects(lambda:view.authority(root),'self review rejects');rp.write_bytes(b)
 archive=root/proof['aliases']['tools/build_interface2016_baseline_web.py']['archive'];b=archive.read_bytes();archive.write_bytes(b+b' ');rejects(lambda:view.authority(root),'old exact builder archive drift rejects');archive.write_bytes(b)
 ok(all(sha(root/n)==h for n,h in rawmap.items()),'raw stability snapshot initially valid')
 rp.write_bytes(rp.read_bytes()+b' ');ok(any(sha(root/n)!=h for n,h in rawmap.items()),'final raw map detects authority change')
refs=json.loads((HERE/'continuation-authorities.json').read_text())
for row in refs.values():ok(sha(Path(row['path']))==row['sha256']and Path(row['path']).stat().st_size==row['bytes'],'unchanged historical authority '+row['path'])
pre=json.loads(Path(refs['source_freeze']['path']).read_text());original={r['path']:r for r in pre['source_inventory']};qualified=json.loads((HERE/'qualified-preimages.json').read_text());continuation=module('_new_continuation',HERE/'continuation.py')
retained=next(r for r in json.loads(Path(refs['previous_packaging_delta']['path']).read_text())['files']if r['path']=='tools/package_final_source_view_v1.py');byname[retained['path']]=retained
after=copy.deepcopy(original)
for n in continuation.CHANGED|continuation.ADDED:after[str(ROOT/n)]={'path':str(ROOT/n),'sha256':byname[n]['sha256'],'bytes':byname[n]['bytes']}
continuation.validate_transition(original,after,byname,ROOT,qualified);ok(len(original)==811 and len(after)==813,'exact original811 to fivechanged plus twoadded vector')
for n in continuation.CHANGED:
 ok(qualified[n]==original[str(ROOT/n)],'qualified preimage derived from genuine original811 '+n)
 if 'build_interface2016'not in n:ok(qualified[n]['sha256']!=byname[n]['preimage_sha256'],'qualified versus install preimage explicitly distinct '+n)
ok(str(ROOT/'tools/package_final_source_view_v1.py')not in original and retained['preimage_sha256']is None,'retained v1 helper added relative811 but not newly installed')
for n in ('cpp/include/atlas/solver.hpp','atlas/compiler.py','models/linear-elastic.json','schemas/model.schema.json','CMakeLists.txt','tools/generate_controlled_path.py'):
 bad=copy.deepcopy(after);bad[str(ROOT/n)]['sha256']='0'*64;rejects(lambda:continuation.validate_transition(original,bad,byname,ROOT,qualified),'any compiled/nonpackaging drift rejects '+n)
bad=copy.deepcopy(after);bad[str(ROOT/'tools/arbitrary.py')]={'path':'extra','sha256':'0'*64,'bytes':0};rejects(lambda:continuation.validate_transition(original,bad,byname,ROOT,qualified),'unlisted added tool rejects')
bad=copy.deepcopy(qualified);n='tools/profile_source_compatibility.py';bad[n]['sha256']=byname[n]['preimage_sha256'];rejects(lambda:continuation.validate_transition(original,after,byname,ROOT,bad),'current install preimage cannot replace original qualified preimage')
with tempfile.TemporaryDirectory(prefix='continuation-failure-',dir=HERE)as td:
 primary=KeyboardInterrupt('manufactured original');calls=[]
 def guard(*args):
  calls.append(True)
  if len(calls)==2:raise ValueError('manufactured final')
  return {'inert':True}
 def fail():raise primary
 with patch.object(continuation,'guard',guard):
  try:continuation.observe(fail,ROOT,'fixture',Path(td)/'report.json')
  except KeyboardInterrupt as e:ok(e is primary and e.packaging_post_errors==["ValueError('manufactured final')"],'primary plus final error retained')
  else:raise AssertionError('failure lost')
 r=json.loads((Path(td)/'report.json').read_text());ok(not r['passed']and 'KeyboardInterrupt'in r['traceback'],'durable primary traceback no false pass')
ok(not list(HERE.glob('closed-source-view-*'))and not list(HERE.glob('continuation-failure-*')),'owned temporary contexts removed')
(HERE/'checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'actual_artifact_compiler_material_browser_network_Git':False,'fixture_decisions_manufactured_noncanonical':True,'actual_guard_not_executed':True,'temporary_contexts_removed':True},indent=2)+'\n')
print(json.dumps({'status':'PASS','checks':len(checks)}))
