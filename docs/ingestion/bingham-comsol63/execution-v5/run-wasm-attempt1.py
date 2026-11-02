"""Coordinator transport only: unchanged collector, one owned process group, retained status."""
import datetime,hashlib,json,os,pathlib,signal,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[4]
BASE=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
pre=BASE/'actual-pre-wasm-attempt1.json'
for p,h in json.loads(pre.read_text())['files'].items():assert sha(pathlib.Path(p))==h,p
log=BASE/'wasm-attempt1.log';status=BASE/'wasm-attempt1-status.json';raw=BASE/'wasm-attempt1.json'
assert not any(p.exists() for p in [log,status,raw])
argv=['node',str(BASE/'collect_wasm.mjs'),str(ROOT/'build-bingham-wasm/bingham.mjs'),str(BASE/'cases.json'),str(raw)]
data={'argv':argv,'cwd':str(ROOT),'start':utc(),'preflight_sha256':sha(pre),'recorder_sha256':sha(pathlib.Path(__file__)),'timeout_seconds':3600}
proc=None;code=125;error=None
try:
 with log.open('w') as output:
  proc=subprocess.Popen(argv,cwd=ROOT,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
  data['pid']=proc.pid
  code=proc.wait(timeout=3600)
except BaseException as exc:
 error=repr(exc)
finally:
 if proc is not None:
  try:os.killpg(proc.pid,signal.SIGTERM)
  except ProcessLookupError:pass
  if proc.poll() is None:
   try:proc.wait(timeout=2)
   except subprocess.TimeoutExpired:pass
  try:os.killpg(proc.pid,signal.SIGKILL)
  except ProcessLookupError:pass
  proc.wait()
 data.update(end=utc(),returncode=code,error=error,log_sha256=sha(log))
 data['source_postverified']=all(sha(pathlib.Path(p))==h for p,h in json.loads(pre.read_text())['files'].items())
 status.write_text(json.dumps(data,indent=2)+'\n')
print('Wasm collector returncode',code,'error',error,'postverified',data['source_postverified'])
raise SystemExit(code if error is None and data['source_postverified'] else 125)
