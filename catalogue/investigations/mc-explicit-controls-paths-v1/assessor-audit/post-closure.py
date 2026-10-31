from pathlib import Path
import ast,json,datetime,os
P=Path(__file__).parent;s=(P/'revised/post_checks.py').read_text();m=ast.parse(s);loop=m.body[-1]
class FakePath:
 def __truediv__(self,x):return self
 def exists(self):return False
 def write_text(self,x):pass
class FakeSubprocess:
 def run(self,*a,**k):return type('Result',(),{'returncode':1,'stdout':'synthetic failure','stderr':''})()
scope={'s':FakePath(),'commands':[('synthetic-failure',['not-executed'])],'datetime':datetime,'subprocess':FakeSubprocess(),'os':os,'json':json,'print':lambda *a,**k:None}
try:exec(compile(ast.Module(body=[loop],type_ignores=[]),'<copied revised loop>','exec'),scope)
except RuntimeError as e:assert str(e)=='synthetic-failure failed; original receipt retained'
else:raise AssertionError('nonzero child exit ignored')
checks={'hard_failure_after_receipt':True,'backend_role_required':"receipt['backend']!=backend"in s,'manifest_binding':"receipt['manifest_sha256']"in s,'artifact_set_exact':"set(receipt['artifacts'])!=expected"in s,'artifact_bytes_hashed':"Path(artifact['path']).read_bytes()"in s,'candidate_calls':0}
assert all(v for k,v in checks.items()if k!='candidate_calls')
(P/'post-closure-checks.json').write_text(json.dumps({'passed':True,'checks':checks},indent=2)+'\n')
print('Revised mandatory post-check failure propagation and artifact binding pass source-only checks')
