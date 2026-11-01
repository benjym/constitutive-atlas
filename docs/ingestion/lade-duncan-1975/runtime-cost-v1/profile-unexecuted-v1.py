from pathlib import Path
import json,subprocess,time,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];p=json.loads((HERE/'POLICY.json').read_text());local=ROOT/'.local/lade-runtime-cost-v1'
assert hashlib.sha256(Path(p['command'][0]).read_bytes()).hexdigest()==p['exe_sha256']
started=time.monotonic()
with (local/'response.json').open('wb') as out,(local/'request.stderr').open('wb') as err:
 child=subprocess.Popen(p['command'],stdout=out,stderr=err)
 time.sleep(p['sample_after_seconds'])
 sample=subprocess.run([p['sample_executable'],str(child.pid),str(p['sample_duration_seconds']),str(p['sampling_interval_ms']),'-file',str(local/'sample.txt')],capture_output=True,timeout=20)
 (local/'sample.stdout').write_bytes(sample.stdout);(local/'sample.stderr').write_bytes(sample.stderr)
 timedout=False
 try:child.wait(timeout=max(.001,p['timeout_seconds']-(time.monotonic()-started)))
 except subprocess.TimeoutExpired:timedout=True;child.kill();child.wait()
report={'diagnostic_only':True,'not_qualification':True,'command':p['command'],'exe_sha256':p['exe_sha256'],'returncode':child.returncode,'sample_returncode':sample.returncode,'timeout':timedout,'elapsed_seconds':time.monotonic()-started,'files':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in local.iterdir() if x.is_file()}}
(HERE/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
