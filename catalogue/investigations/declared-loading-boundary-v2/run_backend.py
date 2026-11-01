"""One serial backend build; immutable outputs and exact input recheck."""
from pathlib import Path
import datetime, hashlib, json, os, platform, subprocess, sys
p=Path(__file__).resolve().parent
backend=sys.argv[1];assert backend in ('native','wasm')
out=p/backend;assert not out.exists(), 'refusing to overwrite observations';out.mkdir()
freeze=json.loads((p/'pre-build-freeze.json').read_text())
for n,h in freeze['files'].items():assert hashlib.sha256((p/n).read_bytes()).hexdigest()==h,n
build=Path('/private/tmp/atlas-loading-boundary-v2-'+backend)
env=os.environ.copy();env.update(EMCC_CORES='1',EM_CACHE=str(p.parents[2]/'.cache/emscripten'))
receipt={'backend':backend,'host':platform.platform(),'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[],'artifacts':{}}
def run(label,argv):
    proc=subprocess.run(argv,cwd=p,env=env,capture_output=True)
    (out/(label+'.stdout.txt')).write_bytes(proc.stdout);(out/(label+'.stderr.txt')).write_bytes(proc.stderr)
    receipt['commands'].append({'label':label,'argv':argv,'exit_code':proc.returncode})
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(backend,label,proc.returncode,flush=True)
    if proc.returncode:raise SystemExit(proc.returncode)
argv=['cmake','-S',str(p),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release']
if backend=='wasm':argv=['/opt/homebrew/bin/emcmake']+argv
run('configure',argv)
run('build',['cmake','--build',str(build),'--target','atlas_loading_boundary','--parallel','1'])
artifacts=['atlas_loading_boundary']if backend=='native'else['atlas-loading-boundary.js','atlas-loading-boundary.wasm']
for name in artifacts:
    data=(build/name).read_bytes();receipt['artifacts'][name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
if backend=='native':run('observe',[str(build/'atlas_loading_boundary')])
else:
    script="import fs from 'node:fs'; import create from './atlas-loading-boundary.js'; await create({wasmBinary:fs.readFileSync(new URL('./atlas-loading-boundary.wasm',import.meta.url)),print:x=>process.stdout.write(x+'\\n'),printErr:x=>process.stderr.write(x+'\\n')});\n"
    # Write actual JS newline escape, not an extra literal backslash.
    script=script.replace('\\\\n','\\n')
    (build/'observe.mjs').write_text(script);(out/'observe.mjs').write_text(script)
    run('observe',['/opt/homebrew/bin/node',str(build/'observe.mjs')])
for n,h in freeze['files'].items():assert hashlib.sha256((p/n).read_bytes()).hexdigest()==h,n
receipt['frozen_inputs_unchanged_after_run']=True
receipt['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
