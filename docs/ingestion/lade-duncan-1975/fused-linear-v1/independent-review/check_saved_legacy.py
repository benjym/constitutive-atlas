"""Replay frozen checker logic against saved responses only; no artifact invocation.
subprocess.run is replaced by an exact-command saved-response dispatcher; every
checker write is intercepted and compared with retained bytes/JSON. No root writes.
"""
from pathlib import Path
import contextlib,io,json,hashlib,runpy,subprocess,sys,types,math
D=Path(__file__).resolve().parent;B=D.parent;ROOT=D.parents[4];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sys.dont_write_bytecode=True;sys.path.insert(0,str(B))
f=json.loads((B/'freeze-v3.json').read_text())
for p,h in f['files'].items():assert sha(ROOT/p)==h,p
build=json.loads((B/'native-build-receipt.json').read_text())
for p,h in build['files'].items():assert sha(ROOT/p)==h,p
jobs=[('check_native_legacy.py','native-legacy-results.json')]
rows_total=0;raws=0;outcomes=[]
for script,reportname in jobs:
 report=json.loads((B/reportname).read_text());assert report['passed'];rows=report.get('requests',[]);payloads=[]
 for row in rows:
  assert row['command'][0]==str(ROOT/'.local/lade-fused-linear-v1/native-build/atlas_lade_domain_candidate')
  if 'raw_path' in row:
   p=ROOT/row['raw_path'];assert sha(p)==row['raw_sha256'];text=p.read_text();raws+=1
  else:text=json.dumps(row['response'])
  payloads.append(text)
 index=0;writes=0;original_run=subprocess.run;original_write=Path.write_text;original_mkdir=Path.mkdir
 def saved_run(cmd,*args,**kwargs):
  global index
  assert index<len(rows),(script,'extra request',cmd)
  assert cmd==rows[index]['command'],(script,index,'command mismatch',cmd,rows[index]['command'])
  assert kwargs.get('timeout')==120,(script,'deadline mismatch')
  result=types.SimpleNamespace(stdout=payloads[index],stderr='',returncode=rows[index]['returncode']);index+=1;return result
 def intercepted_write(path,text,*args,**kwargs):
  global writes
  assert path.exists(),('unexpected new write',path)
  existing=path.read_text()
  if path==B/reportname:assert json.loads(text)==json.loads(existing),(script,'recomputed aggregate mismatch')
  else:assert text==existing,(script,'raw byte mismatch',path)
  writes+=1;return len(text)
 def existing_mkdir(path,*args,**kwargs):assert path.is_dir(),('unexpected directory',path)
 subprocess.run=saved_run;Path.write_text=intercepted_write;Path.mkdir=existing_mkdir
 try:
  with contextlib.redirect_stdout(io.StringIO()):
   try:runpy.run_path(str(B/script),run_name='__main__')
   except SystemExit as e:assert e.code in (0,None),(script,'gate failure',e.code)
 finally:subprocess.run=original_run;Path.write_text=original_write;Path.mkdir=original_mkdir
 assert index==len(rows),(script,'unconsumed requests',index,len(rows));assert writes>=1
 outcomes.append({'checker':script,'report':reportname,'saved_requests':len(rows),'checks':len(report.get('checks',report.get('cases',[]))),'all_recomputed_report_fields_identical':True});rows_total+=len(rows)

out={'passed':True,'saved_requests':rows_total,'raws':raws,'checker_replays':outcomes,'compiled_execution':False}
(D/'saved-native-legacy-replay-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
