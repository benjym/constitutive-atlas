import subprocess, json, os, hashlib, time
from pathlib import Path
root=Path(__file__).resolve().parents[4]
packet=root/'docs/ingestion/perzyna-comsol63/package-v1'
prior=Path('/private/tmp/atlas-bingham-release-v3')
argv=['python3','-B','tools/build_web.py','--output','.local/perzyna-site-v1','--perzyna-wasm-dir','build-perzyna-public']
for name in ['wasm-dir','power-creep-wasm-dir','sls-wasm-dir','burgers-wasm-dir','j2-wasm-dir','orthotropic-wasm-dir','kelvin-voigt-wasm-dir','hill-wasm-dir']:
 argv+=['--'+name,str(prior/'.local/e7-qualified-assets'/name)]
for name,directory in [('bingham','build-bingham-public'),('controlled-path','build-controlled-path-public'),('maxwell','build-maxwell-wasm'),('implicit-path','build-implicit-path-wasm')]:
 argv+=['--'+name+'-wasm-dir',str(prior/directory)]
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
def pins():return {name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in tracked if name and (root/name).is_file()}
pre=pins();(packet/'source-pre.json').write_text(json.dumps(pre,indent=2)+'\n')
receipt={'argv':argv,'revision':revision,'cwd':str(root),'started_unix':time.time()}
(packet/'REQUEST.json').write_text(json.dumps(receipt,indent=2)+'\n')
with (packet/'build.log').open('wb') as log:
 process=subprocess.run(argv,cwd=root,env={**os.environ,'GITHUB_SHA':revision},stdout=log,stderr=subprocess.STDOUT)
post=pins();(packet/'source-post.json').write_text(json.dumps(post,indent=2)+'\n')
receipt.update(returncode=process.returncode,finished_unix=time.time(),source_unchanged=pre==post,log_sha256=hashlib.sha256((packet/'build.log').read_bytes()).hexdigest())
(packet/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt));raise SystemExit(process.returncode)
