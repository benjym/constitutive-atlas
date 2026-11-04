from pathlib import Path
import ast,hashlib,importlib.util,json,runpy,sys,tempfile
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;P=R.parent/'current16-qualification-plan-v1';checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ck('exact author manifest',sha(P/'manifest.json')=='87174e56906f54413e09693288ffbdc91722a42c3ab3ea2b2119a70217b3023d')
m=json.loads((P/'manifest.json').read_text())
ck('exclusive23 members',len(m['files'])==23 and {x.name for x in P.iterdir() if x.is_file()}=={x['path'] for x in m['files']}|{'manifest.json'})
for r in m['files']:ck('member '+r['path'],sha(P/r['path'])==r['sha256'] and (P/r['path']).stat().st_size==r['bytes'])
# Strict author replay: only temp fixture location is redirected, never author writes.
original=tempfile.TemporaryDirectory
class OwnedTemporary(original):
 def __init__(self,*a,**kw):kw['dir']=R;super().__init__(*a,**kw)
tempfile.TemporaryDirectory=OwnedTemporary
sys.path.insert(0,str(P))
import contextlib,io
s=io.StringIO()
try:
 with contextlib.redirect_stdout(s):runpy.run_path(str(P/'check.py'),run_name='__main__')
finally:tempfile.TemporaryDirectory=original
(R/'author-replay.stdout.json').write_text(s.getvalue())
a=json.loads(s.getvalue());ck('strict exact32 author replay',a==json.loads((P/'check-final.stdout.json').read_text()) and a['count']==32)
build=ast.parse((P/'build.py').read_text());fn=next(n for n in build.body if isinstance(n,ast.FunctionDef) and n.name=='compiler')
import re
ns={'Path':Path,'re':re};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<frozen compiler resolver>','exec'),ns)
with original(dir=R,prefix='independent-') as tmp:
 root=Path(tmp);f=root/'metadata'
 for name,value in [('good','set(CMAKE_CXX_COMPILER "/inert/clang++")\n'),('duplicate','set(CMAKE_CXX_COMPILER "/a")\nset(CMAKE_CXX_COMPILER "/a")\n'),('missing',''),('trailing','set(CMAKE_CXX_COMPILER "/a") # comment\n'),('multiline','set(CMAKE_CXX_COMPILER "/a\nb")\n'),('wrong','set(CMAKE_C_COMPILER "/a")\n')]:
  f.write_text(value)
  try:result=ns['compiler'](f,'CXX')
  except AssertionError:ck('resolver rejects '+name,name!='good')
  else:ck('resolver accepts only unique exact literal '+name,name=='good' and str(result)=='/inert/clang++')
 # Real unchanged observer, inert executable bytes + fake child; no actual process.
 observer=Path(json.loads((P/'reused-inputs.json').read_text())['files'][4]['path'])
 spec=importlib.util.spec_from_file_location('real_observer',observer);o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
 executable=root/'inert';executable.write_bytes(b'inert-not-executed')
 class Child:
  pid=123456789
  def __init__(self,status):self.status=status;self.waits=0
  def wait(self,timeout):self.waits+=1;return self.status
 for status in (0,17):
  child=Child(status);calls=[];kills=[]
  def popen(argv,**kw):calls.append((argv,kw));return child
  output=root/str(status)
  result=o.observe([str(executable),'--manufactured'],str(root),output,env={'ONLY':'closed'},timeout=1800,_popen=popen,_killpg=lambda p,s:kills.append((p,s)))
  receipt=json.loads((output/'receipt.json').read_text())
  ck('real observer pin/raw/reap '+str(status),receipt['executable']['sha256']==sha(executable) and receipt['mandatory_reap'] is True and receipt['returncode']==status and child.waits==2 and calls[0][1]['start_new_session'] is True and calls[0][1]['env']=={'ONLY':'closed'} and (output/'stdout.raw').read_bytes()==b'' and (output/'stderr.raw').read_bytes()==b'')
  ck('failure group cleanup '+str(status),bool(kills)==(status!=0))
 # Adapter exact routing/environment/timeout and nonzero stop; injected module only.
 import observe_phase as adapter
 import types
 original_spec=adapter.importlib.util.spec_from_file_location;original_module=adapter.importlib.util.module_from_spec
 seen=[]
 fake=types.SimpleNamespace(observe=lambda *args,**kw:(seen.append((args,kw)) or types.SimpleNamespace(returncode=0)))
 adapter.importlib.util.spec_from_file_location=lambda *a:types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda m:None))
 adapter.importlib.util.module_from_spec=lambda s:fake
 try:
  pre={'repo':str(adapter.C.SOURCE),'compiled_observations':False,'python':{'path':str(executable)},'node':{'path':'/inert/node'}}
  adapter.observe_phase(pre,'build')
  ck('adapter exact observer invocation',seen[0][0][0]==adapter.C.phase_argv(pre)['build'] and seen[0][1]=={'env':adapter.closed_environment(),'timeout':1800})
  fake.observe=lambda *a,**kw:types.SimpleNamespace(returncode=19)
  try:adapter.observe_phase(pre,'native')
  except AssertionError:ck('adapter rejects real nonzero result',True)
  else:raise AssertionError('adapter accepted nonzero')
 finally:
  adapter.importlib.util.spec_from_file_location=original_spec;adapter.importlib.util.module_from_spec=original_module
ck('no disposable fixture remains',not any(x.is_dir() for x in R.iterdir()))
print(json.dumps({'status':'PASS','checks':checks,'count':len(checks),'actual_process_tool_source_sdk_calls':0,'author_replay_checks':32},indent=2))
