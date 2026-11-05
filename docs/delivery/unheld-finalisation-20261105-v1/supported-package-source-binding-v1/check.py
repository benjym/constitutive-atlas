from pathlib import Path
import ast,hashlib,importlib.util,json,shutil,subprocess,tempfile
P=Path(__file__).resolve().parent;ROOT=P.parents[3];W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def require(value,name):
 assert value,name
 checks.append(name)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
delta=load(P/'source-delta.json')['files'];current=(P/delta[0]['proposal']).read_text();old=(P/'original.mjs').read_text();helper=(P/'helper-source.txt').read_text()
reverse=current.replace('existsSync,readdirSync,lstatSync,realpathSync}','existsSync,readdirSync}').replace(helper,'').replace('\n let packagerSnapshot=null,packagerExpected=null;','').replace('  packagerExpected=decision.source_sha256;packagerSnapshot=controlledTimePackagerSources(repository,packagerExpected);',"  assert.equal(hash(readFileSync(join(repository,'tools/build_controlled_time_web.py'))),decision.source_sha256,'Changed accepted controlled-time packager');").replace(" if(packagerSnapshot!==null)assert.deepEqual(controlledTimePackagerSources(repository,packagerExpected),packagerSnapshot,'Packager source view changed during membership validation');\n",'')
require(reverse==old,'exact full checker inverse; every original assertion preserved')
for r in delta:
 b=(P/r['proposal']).read_bytes();require(sha(b)==r['sha256']and len(b)==r['bytes'],'delta '+r['path'])
require(delta[0]['preimage_sha256']==sha(old.encode()),'exact install preimage')
for q in P.glob('*.py'):ast.parse(q.read_text());require(True,'syntax '+q.name)
proofpath='docs/delivery/unheld-finalisation-20261105-v1/interface-receipt-source-closure-v1/proof.json';reviewpath='docs/delivery/unheld-finalisation-20261105-v1/shared-current17-review-v1/interface-receipt-source-closure-v1/source-view-decision.json';proof=load(ROOT/proofpath)
pins={**proof['implementation'],**proof['ancestors'],**{n:a['current_sha256']for n,a in proof['aliases'].items()},**{a['archive']:a['predecessor_sha256']for a in proof['aliases'].values()},proofpath:'54f68390c72d71374799e3ecd427f93e3d9384df72a4c030e8ceee0a08bc6edd',reviewpath:'4fec2a1da7ee05f253f7c5f5cb3c98dc69d545fd014de212fa2cef6e4174f970'}
with tempfile.TemporaryDirectory(prefix='supported-source-pure-')as td:
 t=Path(td).resolve();ctx=t/'current';ctx.mkdir()
 for name,digest in pins.items():
  candidates=[W/name,ROOT/name];source=next(q for q in candidates if q.is_file()and sha(q.read_bytes())==digest);q=ctx/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(source.read_bytes())
 node="import assert from 'node:assert/strict';import {readFileSync,lstatSync,realpathSync,writeFileSync,unlinkSync,symlinkSync,mkdirSync}from'node:fs';import{join,resolve}from'node:path';import{createHash}from'node:crypto';\nconst hash=b=>createHash('sha256').update(b).digest('hex');const strictJSON=JSON.parse;\n"+helper+"\nconst root=process.argv[2],names=JSON.parse(readFileSync(process.argv[3]));let count=0;const ok=(v)=>{assert.ok(v);count++;};const expected='02b1dd6e36c2c23ca91a78d321c4af5060dd7b68dbf8385e142061f4149a4758';const a=controlledTimePackagerSources(root,expected);ok(Object.keys(a).length===names.length);ok(JSON.stringify(a)===JSON.stringify(controlledTimePackagerSources(root,expected)));assert.throws(()=>controlledTimePackagerSources(root,'0'.repeat(64)));count++;for(const name of names){const p=join(root,name),b=readFileSync(p);writeFileSync(p,Buffer.concat([b,Buffer.from(' ')]));assert.throws(()=>controlledTimePackagerSources(root,expected));count++;writeFileSync(p,b);}const direct=root+'-historical';mkdirSync(join(direct,'tools'),{recursive:true});writeFileSync(join(direct,'tools/build_controlled_time_web.py'),readFileSync(join(root,'catalogue/source-snapshots/'+expected+'/tools/build_controlled_time_web.py')));ok(Object.keys(controlledTimePackagerSources(direct,expected)).length===1);const p=join(root,'tools/build_controlled_time_web.py'),b=readFileSync(p);unlinkSync(p);symlinkSync(join(direct,'tools/build_controlled_time_web.py'),p);assert.throws(()=>controlledTimePackagerSources(root,expected));count++;unlinkSync(p);writeFileSync(p,b);console.log(JSON.stringify({status:'PASS',checks:count}));"
 (t/'test.mjs').write_text(node);(t/'pins.json').write_text(json.dumps(list(pins)));run=subprocess.run(['node',str(t/'test.mjs'),str(ctx),str(t/'pins.json')],capture_output=True,text=True);(P/'node.stdout').write_text(run.stdout);(P/'node.stderr').write_text(run.stderr);require(run.returncode==0,'pure actual helper Node checks');nodechecks=json.loads(run.stdout)
 spec=importlib.util.spec_from_file_location('continuation',P/'continuation.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
 previous=P.parent/'interface-receipt-source-closure-v1';rows=load(previous/'source-delta.json')['files']+delta;by={r['path']:r for r in rows};v1=next(r for r in load(P.parent/'package-final-source-binding-v1/source-delta.json')['files']if r['path']=='tools/package_final_source_view_v1.py');by[v1['path']]=v1;refs=load(P/'continuation-authorities.json');original={r['path']:r for r in load(Path(refs['source_freeze']['path']))['source_inventory']};qualified=load(P/'qualified-preimages.json');require(delta[0]['preimage_sha256']==qualified['tools/test_web_package.mjs']['sha256'],'new checker preimage exactly original qualified811');expected=dict(original)
 for n in c.CHANGED|c.ADDED:expected[str(c.ROOT/n)]={'path':str(c.ROOT/n),'sha256':by[n]['sha256'],'bytes':by[n]['bytes']}
 c.validate_transition(original,expected,by,c.ROOT,qualified);require(len(original)==811 and len(expected)==813 and len(c.CHANGED)==6,'exact811→sixchanged+twoadded813')
 for n in ['cpp/include/atlas/solver.hpp','tools/test_web_package.mjs','tools/unknown.mjs']:
  corrupt=dict(expected);corrupt[str(c.ROOT/n)]={'sha256':'0'*64}
  try:c.validate_transition(original,corrupt,by,c.ROOT,qualified)
  except ValueError:require(True,'transition rejects '+n)
  else:raise AssertionError(n)
 site=t/'tiny-site';site.mkdir();(site/'a').write_bytes(b'a');before=c.physical_site(site);require(len(before)==1,'physical scan tiny regular');(site/'a').write_bytes(b'b');require(c.physical_site(site)!=before,'physical scan detects bytes');(site/'extra').write_bytes(b'a');require(c.physical_site(site)!=before,'physical scan detects namespace');(site/'link').symlink_to(site/'a')
 try:c.physical_site(site)
 except ValueError:require(True,'physical scan rejects link')
 else:raise AssertionError('symlink')
 review={'identity':'supported-package-source-binding-independent-review-v1','accepted':True,'author_run':'/root/baseline_migration','reviewer_run':'/root/publication_operations_review','proposal_manifest_sha256':'fixture','unresolved_blockers':[]};c.validate_review(review,'fixture');require(True,'exact independent authority fixture')
 for key in review:
  bad=dict(review);bad.pop(key)
  try:c.validate_review(bad,'fixture')
  except ValueError:require(True,'missing review field rejects '+key)
  else:raise AssertionError(key)
 calls=[]
 def guard(*a):
  calls.append(True)
  if len(calls)>1:raise ValueError('postguard')
  return {'fixture':True}
 c.guard=guard;primary=KeyboardInterrupt('primary')
 try:c.observe(lambda:(_ for _ in()).throw(primary),c.ROOT,'fixture',t/'receipt.json')
 except KeyboardInterrupt as e:require(e is primary and e.packaging_post_errors==["ValueError('postguard')"],'primary and finalerror retained')
 require('KeyboardInterrupt' in load(t/'receipt.json')['traceback'],'durable original traceback')
checks.extend(['Node '+str(i+1)for i in range(nodechecks['checks'])]);(P/'checks.json').write_text(json.dumps({'status':'PASS','checks':checks,'count':len(checks),'compiled_calls':0,'temporary_contexts_removed':True},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
