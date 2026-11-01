import copy,gzip,importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent;A=P/'raw-link-v6';sys.path.insert(0,str(A));spec=importlib.util.spec_from_file_location('review_raw_extra',A/'check_raw.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);f=D/'synthetic-full-md';checks=[]
def reject(name,mutate,restore):
 try:
  mutate()
  try:m.verify(f,'md')
  except Exception as e:checks.append({'name':name,'rejected':True,'error':str(e)})
  else:raise AssertionError('false accept '+name)
 finally:restore()
raw=next(f.glob('undrained*.gz'));rawbytes=raw.read_bytes();missing=raw.with_suffix('.missing')
reject('missing raw file',lambda:raw.rename(missing),lambda:missing.rename(raw))
extra=f/'extra.jsonl.gz';reject('extra raw filename',lambda:extra.write_bytes(rawbytes),lambda:extra.unlink())
control=next((f/'controls').iterdir());old=control.read_bytes();reject('corrupted control wire',lambda:control.write_text('wrong'),lambda:control.write_bytes(old))
report=f/'report.json';binding=f/'runtime-binding.json';oldr=report.read_bytes();oldb=binding.read_bytes()
def badreport():
 r=json.loads(oldr);case=next(iter(r['cases']));r['cases'][case]['points'][0]['state'][0]+=123;report.write_text(json.dumps(r));b=json.loads(oldb);b['report_sha256']=m.sha(report);binding.write_text(json.dumps(b))
reject('contradictory report despite updated hash',badreport,lambda:(report.write_bytes(oldr),binding.write_bytes(oldb)))
def badbinding():
 b=json.loads(oldb);b['delegate_path']=str(P/'runtime-rebind-v5/run_bound.py');binding.write_text(json.dumps(b))
reject('misclaimed old actual collector',badbinding,lambda:binding.write_bytes(oldb))
# Verify actual-worker metadata gate independently with synthetic text module only.
w=D/'synthetic-worker';w.mkdir();artifact=w/'mock.mjs';artifact.write_text('SYNTHETIC REVIEW TEXT NEVER EXECUTED');stderr=w/'worker-stderr.txt';stderr.write_text('retained synthetic stderr');worker={'command':['node',str(P/'resolution-study-v4/run_wasm.mjs'),'--worker','--engine',str(artifact)],'pid':42,'ready_wire':'{"ready":true}\n','exit_code':0,'stderr_path':str(stderr),'stderr_sha256':m.sha(stderr)}
audit={'identity':'md1997-raw-transport-v6','backend':'wasm','artifact_path':str(artifact),'artifact_sha256':m.sha(artifact),'original_call_sha256':m.sha(P/'execution-v3/run_native.py'),'collector_sha256':m.sha(A/'collect.py'),'worker':worker,'closed':True,'call_count':24};path=w/'transport.json';path.write_text(json.dumps(audit));m.verify_transport(w,'md','wasm',str(artifact),24);checks.append({'name':'positive complete synthetic worker audit','passed':True})
for name,mut in [('late-worker-exit',lambda x:x['worker'].update(exit_code=9)),('wrong-worker-command',lambda x:x['worker']['command'].__setitem__(0,'wrong')),('bad-ready',lambda x:x['worker'].update(ready_wire='{"ready":false}')),('wrong-stderr-hash',lambda x:x['worker'].update(stderr_sha256='0'*64)),('wrong-callcount',lambda x:x.update(call_count=25)),('wrong-worker-artifact',lambda x:x.update(artifact_sha256='0'*64))]:
 x=copy.deepcopy(audit);mut(x);path.write_text(json.dumps(x))
 try:m.verify_transport(w,'md','wasm',str(artifact),24)
 except Exception as e:checks.append({'name':name,'rejected':True,'error':str(e)})
 else:raise AssertionError('false accept '+name)
path.write_text(json.dumps(audit));(D/'additional-checks.json').write_text(json.dumps({'compiled_calls':0,'checks':checks},indent=2)+'\n');print(len(checks))
