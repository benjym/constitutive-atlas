"""One explicit configure/build/run phase; no automatic retries or parallel builds."""
from pathlib import Path
import sys,json,gzip,hashlib,subprocess,datetime,os
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def verify():
 freeze=json.loads((P/'prospective-freeze.json').read_text())
 for path,record in freeze['files'].items():
  p=P/path
  if sha(p)!=record['sha256'] or p.stat().st_size!=record['bytes']:raise RuntimeError('frozen input changed: '+path)
 return freeze

def main():
 phase,backend,build=sys.argv[1:];build=Path(build).resolve();assert backend in('native','wasm');assert phase in('configure','build','run');verify()
 out=P/backend;out.mkdir(exist_ok=True);recordpath=out/(phase+'-command.json');assert not recordpath.exists(),'retain previous attempt; no silent retry'
 if phase=='configure':
  command=['cmake','-S',str(P),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release']
  if backend=='wasm':command=['emcmake',*command]
 elif phase=='build':command=['cmake','--build',str(build),'--target','atlas_spectral_context','--parallel','1']
 else:command=[str(build/'atlas_spectral_context')]if backend=='native'else['node',str(build/'spectral-context.js')]
 env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
 if backend=='wasm':env['EMCC_CORES']='1'
 record={'phase':phase,'backend':backend,'command':command,'cwd':str(P),'started_at':now(),'EMCC_CORES':env.get('EMCC_CORES'),'freeze_sha256':sha(P/'prospective-freeze.json')}
 recordpath.write_text(json.dumps(record,indent=2)+'\n')
 data=gzip.decompress((P/'requests.txt.gz').read_bytes())if phase=='run'else None
 try:
  result=subprocess.run(command,cwd=P,env=env,input=data,capture_output=True,timeout=600 if phase!='run'else 180)
 except BaseException as exc:
  record.update(ended_at=now(),exception=repr(exc));recordpath.write_text(json.dumps(record,indent=2)+'\n');raise
 (out/(phase+'.stdout')).write_bytes(result.stdout);(out/(phase+'.stderr')).write_bytes(result.stderr)
 record.update(ended_at=now(),returncode=result.returncode,stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),stderr_sha256=hashlib.sha256(result.stderr).hexdigest())
 recordpath.write_text(json.dumps(record,indent=2)+'\n');verify();print(json.dumps(record))
 if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
