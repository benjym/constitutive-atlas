from pathlib import Path
import importlib.util,io,json,tarfile,tempfile,zipfile
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('streaming_plan',P/'verify.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);checks=[]
with tempfile.TemporaryDirectory(prefix='owned-fixture-',dir=P)as tmp:
 root=Path(tmp)
 for label,entries,expected,accept in [('good',[('one.json',b'{}','file')],['one.json'],True),('duplicate',[('one.json',b'{}','file'),('one.json',b'{}','file')],['one.json'],False),('traversal',[('../one.json',b'{}','file')],['../one.json'],False),('link',[('one.json',b'','link')],['one.json'],False),('namespace',[('one.json',b'{}','file')],['other.json'],False)]:
  data=io.BytesIO()
  with tarfile.open(fileobj=data,mode='w')as tar:
   for name,raw,kind in entries:
    member=tarfile.TarInfo(name);member.size=len(raw)
    if kind=='link':member.type=tarfile.SYMTYPE;member.linkname='/outside'
    tar.addfile(member,io.BytesIO(raw))
  archive=root/(label+'.zip')
  with zipfile.ZipFile(archive,'w')as z:z.writestr('artifact.tar',data.getvalue())
  try:members,captured=m.verify_archive(archive,expected,{'one.json'}if label=='good'else set())
  except AssertionError:assert not accept;checks.append(label+' rejected')
  else:assert accept and captured['one.json']==b'{}';checks.append('good streaming no extraction')
assert not any(p.is_dir()for p in P.iterdir())
print(json.dumps({'status':'PASS_SOURCE_MANUFACTURED_ONLY','checks':checks,'actual_archive_http_ci_browser_or_compiled_calls':0,'temporary_fixture_trees_remaining':0}))
