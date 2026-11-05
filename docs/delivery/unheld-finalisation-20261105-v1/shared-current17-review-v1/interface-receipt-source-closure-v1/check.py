from pathlib import Path
import ast,hashlib,json,types,tempfile,copy
O=Path(__file__).resolve().parent;N=O.parents[1];A=N/'interface-receipt-source-closure-v1';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def h(b):return hashlib.sha256(b).hexdigest()
def ok(x,n):assert x,n;checks.append(n)
def rejected(f,n):
 try:f()
 except (ValueError,KeyError,FileNotFoundError):checks.append(n)
 else:raise AssertionError('accepted '+n)
ok(h((A/'manifest.json').read_bytes())=='eecdec42938c4dc633ee74ece56b219e06c289b490eda1c8a500c28c1f122fbf','exact frozen author manifest')
manifest=json.loads((A/'manifest.json').read_text())
for r in manifest['files']:ok(h((A/r['path']).read_bytes())==r['sha256'] and (A/r['path']).stat().st_size==r['bytes'],'manifest '+r['path'])
delta=json.loads((A/'source-delta.json').read_text())['files'];proof=json.loads((A/'proof.json').read_text());contract=json.loads((A/'consumer-review-contract.json').read_text());review=contract['required_decision'];review['reviewer_run']='/root/publication_operations_review'
for r in delta:
 ok(h((A/r['proposal']).read_bytes())==r['sha256'],'payload '+r['path'])
 if r['preimage_sha256']:ok(h((A/'originals'/r['path']).read_bytes())==r['preimage_sha256'],'retained preimage '+r['path'])
module=types.ModuleType('inert_source_view');exec(compile((A/'proposed/tools/package_final_source_view_v2.py').read_text(),'helper','exec'),module.__dict__)
# Literal bounded source bytes only; no artifacts, imports of material kernels or processes.
data={module.PROOF:(A/'proof.json').read_bytes(),module.REVIEW:(json.dumps(review)+'\n').encode()}
for name in proof['implementation']:data[name]=((A/'proposed'/name)if(A/'proposed'/name).is_file()else W/name).read_bytes()
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
# The three hooks change only versioned helper imports; both final raw guards remain exact.
for name in ['profile_source_compatibility.py','profile_source_compatibility_baseline.py','build_controlled_time_web.py']:
 old=(A/'originals/tools'/name).read_text();new=(A/'proposed/tools'/name).read_text();ok(new.replace('tools.package_final_source_view_v2','tools.package_final_source_view_v1')==old,'hook entire inverse exact '+name)
for name in ['build_interface2016_web.py','build_interface2016_baseline_web.py']:
 old=(A/'originals/tools'/name).read_text();new=(A/'proposed/tools'/name).read_text();oldexpr='source_closure=closure, refresh_qualification_sha256';newexpr="source_closure=(json.loads(compatibility['compatibility_bytes'])['source_files'] if compatibility is not None else closure), refresh_qualification_sha256"
 ok(new.replace(newexpr,oldexpr)==old,'builder entire inverse exact '+name)
 ok("closure = compatibility['sources']"in new and 'for name,digest in closure.items()'in new,'raw stability unchanged '+name)
 tree=ast.parse(new);expr=next(n.value for n in ast.walk(tree)if isinstance(n,ast.keyword)and n.arg=='source_closure');closure={'solver':'current-raw','authority':'raw-proof'};historical={'solver':'historical-qualified'}
 for compat in [{'compatibility_bytes':json.dumps({'source_files':historical}).encode(),'sources':closure},None]:
  result=eval(compile(ast.Expression(expr),'receipt-expression','eval'),{'json':json,'compatibility':compat,'closure':closure})
  ok(result==(historical if compat is not None else closure),'actual receipt AST expression semantic '+name+str(compat is None))
 for compat in [{'compatibility_bytes':b'not-json'},{'compatibility_bytes':b'{}'}]:rejected(lambda:eval(compile(ast.Expression(expr),'bad','eval'),{'json':json,'compatibility':compat,'closure':closure}),'malformed historical receipt input rejects '+name)
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
refs=json.loads((A/'continuation-authorities.json').read_text())
for key,row in refs.items():ok(h(Path(row['path']).read_bytes())==row['sha256']and Path(row['path']).stat().st_size==row['bytes'],'exact metadata authority '+key)
pre=json.loads(Path(refs['source_freeze']['path']).read_text());original={r['path']:r for r in pre['source_inventory']}
for name,row in json.loads((A/'qualified-preimages.json').read_text()).items():ok(original[str(W/name)]==row,'genuine original qualified preimage '+name)
byname={r['path']:r for r in delta};previous=json.loads((N/'package-final-source-binding-v1/source-delta.json').read_text())['files'];retained=next(r for r in previous if r['path']=='tools/package_final_source_view_v1.py');byname[retained['path']]=retained;qualified=json.loads((A/'qualified-preimages.json').read_text());before={str(W/n):dict(qualified[n])for n in c.CHANGED}
for name in ['atlas/a.py','cpp/a.cpp','models/a.json','schemas/a.json','CMakeLists.txt','tools/generator.py','tools/unknown.py']:before[str(W/name)]={'path':str(W/name),'sha256':'a'*64,'bytes':2}
after=copy.deepcopy(before)
for name in c.CHANGED|c.ADDED:after[str(W/name)]={'path':str(W/name),'sha256':byname[name]['sha256'],'bytes':byname[name]['bytes']}
c.validate_transition(before,after,byname,W,qualified);ok(True,'exact changed5 added2 accepted')
for name in before:
 bad=copy.deepcopy(after);bad[name]['sha256']='b'*64;rejected(lambda:c.validate_transition(before,bad,byname,W,qualified),'reject nonreviewed delta '+name)
for change in ['added','missing']:
 bad=copy.deepcopy(after)
 if change=='added':bad[str(W/'tools/new.py')]={'path':'extra','sha256':'a'*64,'bytes':1}
 else:bad.pop(str(W/'tools/package_final_source_view_v2.py'))
 rejected(lambda:c.validate_transition(before,bad,byname,W,qualified),'reject namespace '+change)
s=(A/'continuation.py').read_text();ok("if current!=expected:raise ValueError"in s and 'only literal five changed plus one newly installed packaging tool allowed'in s,'exact namespace and literal delta gates');ok("*f['artifacts'].values()"in s and "*f['candidates'].values()"in s and "verify(launch['plan_review'])"in s,'original artifacts candidates and launch review gates retained')
previous=N/'package-final-source-binding-v1';ok(h((previous/'manifest.json').read_bytes())=='f2cb57305fe5c16a2ced23ffe3bb1f6010791a7d9e9e36bc2f7d1352bc2161b9','prior source packet unchanged')
for row in json.loads((previous/'manifest.json').read_text())['files']:ok(h((previous/row['path']).read_bytes())==row['sha256'],'prior member unchanged '+row['path'])
for row in json.loads((O/'preliminary-contract-observation.json').read_text())['sources']:
 if 'test_interface' in row['path']:ok(h((W/row['path']).read_bytes())==row['sha256'],'original checker unchanged '+row['path'])
(O/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'actual_execution':False,'fixtures_removed':True},indent=2)+'\n');print(json.dumps({'passed':True,'count':len(checks)}))
