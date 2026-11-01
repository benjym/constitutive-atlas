from pathlib import Path
import json,subprocess,time,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];p=json.loads((HERE/'POLICY.json').read_text());local=ROOT/'.local/lade-runtime-cost-v1';local.mkdir(exist_ok=True)
assert hashlib.sha256(Path(p['command'][0]).read_bytes()).hexdigest()==p['exe_sha256']
started=time.monotonic();child=None
report={'diagnostic_only':True,'not_qualification':True,'command':p['command'],'exe_sha256':p['exe_sha256'],'timeout':False}
try:
 with (local/'response.json').open('wb') as out,(local/'request.stderr').open('wb') as err:
  child=subprocess.Popen(p['command'],stdout=out,stderr=err)
  try:
   time.sleep(p['sample_after_seconds'])
   if child.poll() is not None:report['sample_skipped']='child exited before attachment'
   else:
    try:
     sample=subprocess.run([p['sample_executable'],str(child.pid),str(p['sample_duration_seconds']),str(p['sampling_interval_ms']),'-file',str(local/'sample.txt')],capture_output=True,timeout=20)
     (local/'sample.stdout').write_bytes(sample.stdout);(local/'sample.stderr').write_bytes(sample.stderr);report['sample_returncode']=sample.returncode
    except subprocess.TimeoutExpired as e:
     report['sample_error']='sample timeout20s';(local/'sample.stdout').write_bytes(e.stdout or b'');(local/'sample.stderr').write_bytes(e.stderr or b'')
    except Exception as e:report['sample_error']=str(e)
  finally:
   try:child.wait(timeout=max(.001,p['timeout_seconds']-(time.monotonic()-started)))
   except subprocess.TimeoutExpired:report['timeout']=True;child.kill();child.wait()
except Exception as e:report['driver_error']=str(e)
finally:
 if child is not None:
  if child.poll() is None:child.kill();child.wait()
  report['returncode']=child.returncode
 report['elapsed_seconds']=time.monotonic()-started
 report['files']={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in local.iterdir() if x.is_file()}
 (HERE/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
