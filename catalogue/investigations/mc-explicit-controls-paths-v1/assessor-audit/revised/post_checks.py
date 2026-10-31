from pathlib import Path
import json,subprocess,hashlib,os,shutil,datetime
s=Path(__file__).resolve().parent
for name,pin in json.loads((s/'manifest.json').read_text()).items():
 if hashlib.sha256((s/name).read_bytes()).hexdigest()!=pin:raise RuntimeError(name)
for backend in ['native','wasm']:
 receipt=json.loads((s/backend/'receipt.json').read_text())
 if not receipt['completed'] or receipt['backend']!=backend:raise RuntimeError('backend incomplete')
 if receipt['manifest_sha256']!=hashlib.sha256((s/'manifest.json').read_bytes()).hexdigest():raise RuntimeError('backend freeze mismatch')
 expected={'atlas_laboratory_preview'}if backend=='native'else{'atlas-preview.js','atlas-preview.wasm'}
 if set(receipt['artifacts'])!=expected:raise RuntimeError('backend artifact set')
 for artifact in receipt['artifacts'].values():
  if hashlib.sha256(Path(artifact['path']).read_bytes()).hexdigest()!=artifact['sha256']:raise RuntimeError('backend artifact changed')
native='/private/tmp/atlas-mc-explicit-paths-native-v1/atlas_laboratory_preview';wasm=Path('/private/tmp/atlas-mc-explicit-paths-wasm-v1')
# Alias only for the unchanged generic regression tool. Module still loads its actual atlas-preview.wasm.
shutil.copyfile(wasm/'atlas-preview.js',wasm/'atlas.js');(wasm/'generated').mkdir(exist_ok=True);shutil.copyfile(s/'generated/models.json',wasm/'generated/models.json')
commands=[('parity',['python3','-B',str(s/'assess_parity.py'),str(s/'native/journal.json'),str(s/'wasm/journal.json')]),('legacy-regressions',['node',str(s/'regressions.mjs'),native,str(wasm),'/private/tmp/atlas-explicit-controls-native-v1/atlas_solver','/private/tmp/atlas-explicit-controls-wasm-v1',str(s/'legacy-regressions.json')]),('generic-regressions',['node',str(s/'frozen/tools/test_wasm.mjs'),'--wasm-dir',str(wasm),'--native',native])]
for label,argv in commands:
 receipt=s/f'{label}-command.json'
 if receipt.exists():raise RuntimeError('preserve previous result')
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();p=subprocess.run(argv,text=True,capture_output=True,timeout=180,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 receipt.write_text(json.dumps({'argv':argv,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
 print(label,p.returncode,p.stdout[-600:],p.stderr[-600:],flush=True)
 if p.returncode:raise RuntimeError(label+' failed; original receipt retained')
