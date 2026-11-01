"""One explicitly named build target, serialized by the coordinating parent."""
import argparse,datetime,hashlib,json,shutil,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent
STAGE=Path('/private/tmp/atlas-occ-execution-v1')
a=argparse.ArgumentParser();a.add_argument('backend',choices=['native','wasm']);x=a.parse_args()
manifest=json.loads((B/'freeze-manifest.json').read_text())
for p,digest in manifest['files'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==digest,p
if not (STAGE/'source').exists():shutil.copytree(B/'source-snapshot',STAGE/'source')
for p in (B/'source-snapshot').rglob('*'):
 if p.is_file():assert (STAGE/'source'/p.relative_to(B/'source-snapshot')).read_bytes()==p.read_bytes()
cmd=['cmake','-S',str(STAGE/'source'),'-B',str(STAGE/f'build-{x.backend}'),'-DCMAKE_BUILD_TYPE=Release']
if x.backend=='wasm':cmd=['emcmake']+cmd
commands=[cmd,['cmake','--build',str(STAGE/f'build-{x.backend}'),'--target','atlas_occ_solver','--parallel','1']]
logs=[]
for cmd in commands:
 r=subprocess.run(cmd,capture_output=True,text=True)
 logs.append(dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 (B/f'{x.backend}-build.json').write_text(json.dumps(dict(backend=x.backend,time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),commands=logs),indent=2)+'\n')
 print(' '.join(cmd),'exit',r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
for p in (STAGE/f'build-{x.backend}').glob('occ.*' if x.backend=='wasm' else 'atlas_occ_solver'):
 print(p,hashlib.sha256(p.read_bytes()).hexdigest())
