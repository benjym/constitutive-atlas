from pathlib import Path
import json,hashlib,io,tarfile,zipfile,tempfile,ast
import transform as T
P=Path(__file__).resolve().parent;checks=[]
def ck(n,b):assert b,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except (AssertionError,ValueError):checks.append(n)
 else:raise AssertionError('accepted '+n)
policy=json.loads((P/'POLICY.json').read_text())
for pin in policy['inputs']:
 raw=Path(pin['path']).read_bytes();ck('sourcepin '+pin['path'],len(raw)==pin['bytes']and hashlib.sha256(raw).hexdigest()==pin['sha256'])
uploader=(P/'uploader/action.yml').read_text();ck('exact hidden default/source option', 'default: "false"'in uploader and "--exclude=.[^/]*"in uploader and "if: runner.os == 'Linux'"in uploader)
build=Path(next(x['path']for x in policy['inputs']if x['path'].endswith('/tools/build_web.py'))).read_text();ck('source-generated report only',"check_report=Path(tempfile.mkdtemp(prefix='build-',dir=check_root))/'report.json'"in build and "check_root=dest/'implicit-path-package-checks'"in build and "str(ROOT/'tools/test_implicit_path_package.py')"in build)
workflow=Path(next(x['path']for x in policy['inputs']if x['path'].endswith('/.github/workflows/pages.yml'))).read_text();ck('actual Linux default uploader no hidden override','runs-on: ubuntu-latest'in workflow and 'actions/upload-pages-artifact@v5'in workflow and 'include-hidden-files'not in workflow)
old='implicit-path-package-checks/build-fixture_original/report.json';new='implicit-path-package-checks/build-other_random/report.json';expected=['asset','.nojekyll',old]
proof=T.qualified_names(expected,['asset',new]);ck('source-derived transform accepts new generated component',proof['hidden_exclusions']==['.nojekyll']and proof['uploaded_members']==2)
ck('hidden exclusion derives nested component',T.qualified_names(expected+['docs/.hidden/data'],['asset',new])['hidden_exclusions']==['.nojekyll','docs/.hidden/data'])
for n,actual in [('meaningful missing',[new]),('meaningful extra',['asset','newasset',new]),('hidden unexpectedly uploaded',['asset','.nojekyll',new]),('missing report',['asset']),('two reports',['asset',new,old]),('wrong report location',['asset','elsewhere/build-other/report.json']),('non-generated report',['asset','implicit-path-package-checks/fixed/report.json'])]:reject(n,lambda actual=actual:T.qualified_names(expected,actual))
raw=(P/'reference/original-implicit-path-report.json').read_bytes();report=json.loads(raw);semantic=T.validate_report(raw);ck('all106 gates +24 sourcecritical',semantic['checks']==106 and len(semantic['source_literal_gate_names'])==24)
reordered={**report,'checks':list(reversed(report['checks']))};ck('only report order can vary',T.validate_report(json.dumps(reordered).encode())['checks']==106)
for label,change in [('false gate',lambda x:x['checks'][0].update(passed=False)),('missing gate',lambda x:x['checks'].pop()),('duplicate omission',lambda x:x['checks'].__setitem__(0,x['checks'][1])),('false pass numeric',lambda x:x['checks'][0].update(passed=1)),('extra field',lambda x:x.update(extra='unreviewed')),('scope changed',lambda x:x.update(scope='different')),('status failed',lambda x:x.update(status='failed'))]:
 altered=json.loads(raw);change(altered);reject(label,lambda altered=altered:T.validate_report(json.dumps(altered).encode()))
with tempfile.TemporaryDirectory(dir=P,prefix='owned-fixture-')as tmp:
 root=Path(tmp)
 for label,entries,accept in [('good',[('asset',b'asset','file'),(new,raw,'file')],True),('duplicate',[('asset',b'asset','file'),('asset',b'x','file'),(new,raw,'file')],False),('traversal',[('../asset',b'asset','file'),(new,raw,'file')],False),('symlink',[('asset',b'','link'),(new,raw,'file')],False),('badreport',[('asset',b'asset','file'),(new,b'{"status":"passed"}','file')],False)]:
  data=io.BytesIO()
  with tarfile.open(fileobj=data,mode='w')as tar:
   for name,value,kind in entries:
    member=tarfile.TarInfo(name);member.size=len(value)
    if kind=='link':member.type=tarfile.SYMTYPE;member.linkname='/outside'
    tar.addfile(member,io.BytesIO(value))
  archive=root/(label+'.zip')
  with zipfile.ZipFile(archive,'w')as z:z.writestr('artifact.tar',data.getvalue())
  if accept:
   members,captured=T.verify_archive(archive,expected,set());ck('manufactured ZIP allgates streaming',set(members)=={'asset',new}and T.verify_archive.last_proof['report']['checks']==106)
  else:reject('manufactured archive '+label,lambda:T.verify_archive(archive,expected,set()))
ck('own temporary removed',not root.exists())
print(json.dumps({'status':'PASS_SOURCE_MANUFACTURED_ONLY','count':len(checks),'checks':checks,'new_actual_CI_ZIP_HTTP_browser_compiled_calls':0,'temporary_contexts_remaining':0},indent=2))
