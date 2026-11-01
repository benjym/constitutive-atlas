from pathlib import Path
import subprocess,json,hashlib
r=Path(__file__).resolve().parents[4];p=Path(__file__).resolve().parent
cmd=['python3','-B','tools/build_web.py','--wasm-dir','/private/tmp/atlas-common-scalar-functions-v1/actual-root-wasm-v1','--output','/private/tmp/atlas-duncan-closeout-site-v1']
for name in ['burgers','power-creep','sls','j2']:cmd+=['--'+name+'-wasm-dir','/private/tmp/atlas-duncan-integration-v2/retained-inputs/'+name]
cmd+=['--maxwell-wasm-dir','build-maxwell-wasm','--controlled-path-wasm-dir','docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/qualified-norsand']
files={str(f.relative_to(r)):hashlib.sha256(f.read_bytes()).hexdigest() for folder in ['atlas','schemas','models','cpp','cmake','tools','web','catalogue','protocols'] for f in (r/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts and not str(f.relative_to(r)).startswith(('web/dist/','web/preview/'))}
assert not (p/'package-source-freeze-v1.json').exists()
(p/'package-source-freeze-v1.json').write_text(json.dumps({'command':cmd,'source_root':str(r),'files':files,'gate':'Current remote UI and every existing package gate remain required; exact Duncan model/review/protocol and ordinary engine unchanged; reused qualified engine artifacts, no rebuilt-artifact claim'},indent=2)+'\n')
with (p/'package-v1.log').open('w') as log: result=subprocess.run(cmd,cwd=r,stdout=log,stderr=subprocess.STDOUT)
post=all((r/n).is_file() and hashlib.sha256((r/n).read_bytes()).hexdigest()==h for n,h in files.items())
(p/'package-process-v1.json').write_text(json.dumps({'command':cmd,'exit_code':result.returncode,'source_postcheck':post},indent=2)+'\n');print('package exit',result.returncode,'source postcheck',post)
