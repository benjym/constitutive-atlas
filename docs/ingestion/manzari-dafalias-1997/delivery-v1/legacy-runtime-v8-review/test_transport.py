import hashlib,importlib.util,io,json,sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;A=D.parent/'legacy-runtime-v8';sys.path.insert(0,str(A));spec=importlib.util.spec_from_file_location('review_collector',A/'collect.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.STUDY='legacy-md';checks=[]
class Original:
 def call(self,*args):raise AssertionError('compiled transport forbidden in reviewer')
class Worker:
 def __init__(self,ready,code):self.stdin=io.StringIO();self.stdout=io.StringIO(ready);self.pid=12345;self.code=code
 def wait(self,timeout):return self.code
for name,ready,code,expected in [('valid','{"ready":true}\n',0,True),('late-exit','{"ready":true}\n',9,False),('bad-ready','{"ready":false}\n',0,False),('malformed-ready','broken\n',0,False)]:
 out=D/name;out.mkdir(exist_ok=False);artifact=out/'mock-module.mjs';artifact.write_text('review synthetic text only, never executed');args=SimpleNamespace(wasm_engine=str(artifact),solver=None)
 try:
  def popen(command,**kw):kw['stderr'].write('synthetic stderr\n');kw['stderr'].flush();return Worker(ready,code)
  with patch.object(m.subprocess,'Popen',side_effect=popen):
   cls=m.audited_factory(Original);assert cls.call is Original.call;b=cls(args,out);b.close()
  ok=True
 except Exception:ok=False
 assert ok==expected,name
 audit=json.loads((out/'transport.json').read_text());assert audit['closed'] is True and audit['worker']['exit_code']==code and audit['worker']['stderr_sha256']==hashlib.sha256((out/'worker-stderr.txt').read_bytes()).hexdigest(),name+' preservation'
 checks.append({'name':name,'expected_accept':expected,'passed':True})
(D/'transport-checks.json').write_text(json.dumps({'compiled_calls':0,'checks':checks},indent=2)+'\n');print(checks)
