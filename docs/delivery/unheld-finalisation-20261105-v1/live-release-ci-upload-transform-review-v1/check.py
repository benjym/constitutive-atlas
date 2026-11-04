from pathlib import Path
import json,hashlib,importlib.util,sys,ast,io,tempfile,tarfile,zipfile,types
H=Path(__file__).resolve().parent;N=H.parent;P=N/'live-release-ci-upload-transform-v1';checks=[]
def h(b):return hashlib.sha256(b).hexdigest()
def ok(n,b=True):assert b,n;checks.append(n)
def rejects(n,fn):
 try:fn()
 except (AssertionError,ValueError):ok(n)
 else:raise AssertionError('Unexpected acceptance '+n)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
manifest=(P/'manifest.json').read_bytes();ok('Exact frozen source manifest',h(manifest)=='465633fe1ec35dd3d921d36f8bd80bc38a66dda89f774b6981e17751f1a97d92')
for row in json.loads(manifest)['files']:
 b=(P/row['path']).read_bytes();ok('Frozen member '+row['path'],h(b)==row['sha256']and len(b)==row['bytes'])
policy=json.loads((P/'POLICY.json').read_text())
for row in policy['inputs']:
 b=Path(row['path']).read_bytes();ok('Input '+row['path'],h(b)==row['sha256']and len(b)==row['bytes'])
# Prior accepted namespace/API/revision and HTTP source authority preserved byte-exact.
for name,sha in [('manifest.json','342c878025ab331dfe7c62667efe4cb2eeace71c81b7d4d75c42025f8b986d0d'),('browser-validator-v1.manifest.json','bde302f9c8e341ca9adc47d40ec30e764ec7959f1b4fb750dddfab74b5d55f47'),('manifest-v2.json','62e7dea099f881bc6b0a32d0b781dc0319e590ef35828883cc2b6da209757f9e')]:
 q=N/'live-release-artifact-plan-v1';raw=(q/name).read_bytes();ok('Unchanged predecessor '+name,h(raw)==sha)
 for row in json.loads(raw)['files']:ok('Unchanged predecessor member '+row['path'],h((q/row['path']).read_bytes())==row['sha256'])
T=module('reviewed_transform',P/'transform.py');inventory=json.loads((N/'package-inventory-v1.json').read_text());expected=[r['path']for r in inventory['files']];hidden=[n for n in expected if T.hidden(n)];ok('Only .nojekyll hidden in exact accepted package',hidden==['.nojekyll']);old=[n for n in expected if T.REPORT.fullmatch(n)];ok('Exactly one expected generated report',len(old)==1)
old=old[0];reference=(P/'reference/original-implicit-path-report.json').read_bytes();original=next(r for r in inventory['files']if r['path']==old);ok('Original report bytes derive exact accepted inventory',h(reference)==original['sha256']and len(reference)==original['bytes'])
uploader=(P/'uploader/action.yml').read_text();ok('Pinned Linux uploader hidden exclusion source',"if: runner.os == 'Linux'"in uploader and 'default: "false"'in uploader and '--exclude=.[^/]*'in uploader)
workflow=Path(next(r['path']for r in policy['inputs']if r['path'].endswith('/pages.yml'))).read_text();ok('Current Pages Ubuntu no hidden override','runs-on: ubuntu-latest'in workflow and 'actions/upload-pages-artifact@v5'in workflow and 'include-hidden-files'not in workflow)
build=Path(next(r['path']for r in policy['inputs']if r['path'].endswith('/build_web.py'))).read_text();ok('Generated component location source exact',"check_root=dest/'implicit-path-package-checks'"in build and "Path(tempfile.mkdtemp(prefix='build-',dir=check_root))/'report.json'"in build)
new='implicit-path-package-checks/build-independent_fixture/report.json';actual=[new if n==old else n for n in expected if not T.hidden(n)];proof=T.qualified_names(expected,actual);ok('1549 to1548 source policy',proof['expected_members']==1549 and proof['uploaded_members']==1548 and proof['hidden_exclusions']==['.nojekyll'])
for name in actual:
 if name!=new:rejects('Every meaningful asset mandatory: '+name,lambda name=name:T.qualified_names(expected,[n for n in actual if n!=name]))
for label,names in [('extra meaningful',actual+['new.js']),('extra hidden',actual+['.hidden.js']),('missing report',[n for n in actual if n!=new]),('two reports',actual+[old]),('duplicate member',actual+[actual[0]]),('report path wrong',[n if n!=new else 'other/build-fixture/report.json'for n in actual])]:rejects(label,lambda names=names:T.qualified_names(expected,names))
report=json.loads(reference);p=T.validate_report(reference);ok('106exact gate rows and24literal source-critical gates',p['checks']==106 and len(p['source_literal_gate_names'])==24)
for i in range(len(report['checks'])):
 bad=json.loads(reference);bad['checks'].pop(i);rejects('Every original report row mandatory '+str(i),lambda bad=bad:T.validate_report(json.dumps(bad).encode()))
for label,mutate in [('False outcome',lambda r:r['checks'][0].update(passed=False)),('Numeric1 outcome',lambda r:r['checks'][0].update(passed=1)),('Duplicate replaces original',lambda r:r['checks'].__setitem__(0,r['checks'][1])),('Scope changed',lambda r:r.update(scope='unreviewed')),('Status changed',lambda r:r.update(status='failed')),('Extra field',lambda r:r.update(extra=True))]:
 bad=json.loads(reference);mutate(bad);rejects(label,lambda bad=bad:T.validate_report(json.dumps(bad).encode()))
reverse={**report,'checks':list(reversed(report['checks']))};ok('Only source-set order semantic equivalence',T.validate_report(json.dumps(reverse).encode())['checks']==106)
with tempfile.TemporaryDirectory(prefix='owned-',dir=H)as tmp:
 root=Path(tmp)
 def archive(label,entries):
  tarbytes=io.BytesIO()
  with tarfile.open(fileobj=tarbytes,mode='w')as tar:
   for name,b,kind in entries:
    t=tarfile.TarInfo(name);t.size=len(b)
    if kind=='link':t.type=tarfile.SYMTYPE;t.linkname='/unowned'
    tar.addfile(t,io.BytesIO(b))
  path=root/(label+'.zip')
  with zipfile.ZipFile(path,'w')as z:z.writestr('artifact.tar',tarbytes.getvalue())
  return path
 small=['.nojekyll','asset',old]
 good=archive('good',[('asset',b'asset','file'),(new,reference,'file')]);members,raw=T.verify_archive(good,small,{'asset'});ok('Streaming pure archive accepted exact generated report',len(members)==2 and raw['asset']==b'asset'and T.verify_archive.last_proof['report']['checks']==106)
 for label,entries in [('traversal',[('../asset',b'asset','file'),(new,reference,'file')]),('duplicate',[('asset',b'asset','file'),('asset',b'asset','file'),(new,reference,'file')]),('link',[('asset',b'','link'),(new,reference,'file')]),('missing asset',[(new,reference,'file')])]:
  path=archive(label,entries);rejects('Streaming rejects '+label,lambda path=path:T.verify_archive(path,small,set()))
# Wrapper source invokes literal unchanged frozen v2 main and only replaces archive callback.
tree=ast.parse((P/'verify-v3.py').read_text());main=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='main');assignments=[ast.unparse(x)for x in ast.walk(main)if isinstance(x,ast.Assign)];ok('Only v2 module callback assignment', [x for x in assignments if x.startswith('m.')]==['m.verify_archive = transform.verify_archive'])
ok('Unchanged v2 main actually invoked',any(isinstance(x,ast.Call)and ast.unparse(x.func)=='m.main'for x in ast.walk(main)))
failure=N/'live-release-actual-v1/artifact-preflight-namespace-failure.json';f=json.loads(failure.read_text());ok('Original namespace failure remains historical failure','exit1'in f['retained_failure']and f['expected']==1549 and f['actual']==1548)
(H/'failure-pin.json').write_text(json.dumps({'path':str(failure),'sha256':h(failure.read_bytes()),'bytes':failure.stat().st_size,'scope':'Preserved failure only; no actual artifact reopened'},indent=2)+'\n')
(H/'checks.json').write_text(json.dumps({'status':'PASS_SOURCE_MANUFACTURED_ONLY','checks':checks,'count':len(checks),'real_artifact_network_browser_compiled_calls':0,'temporary_resources_remaining':0},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
