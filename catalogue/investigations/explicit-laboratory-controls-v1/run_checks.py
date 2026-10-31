from pathlib import Path
import subprocess,os,json,datetime,hashlib
root=Path('/Users/bmar5496/code/constitutive-atlas');stage=Path(__file__).parent
native='/private/tmp/atlas-explicit-controls-native-v1/atlas_solver';wasm='/private/tmp/atlas-explicit-controls-wasm-v1'
freeze=json.loads((stage/'prospective-freeze.json').read_text())
for name,digest in freeze['source_files'].items():
 if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('source changed '+name)
for name,digest in freeze['local_files'].items():
 if hashlib.sha256((stage/name).read_bytes()).hexdigest()!=digest:raise RuntimeError('study changed '+name)
for entry in freeze['baseline_artifacts'].values():
 if hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest()!=entry['sha256']:raise RuntimeError('baseline changed')
Path(wasm,'package.json').write_text('{"type":"module"}\n')
commands=[['node',str(stage/'check.mjs'),native,wasm,'/private/tmp/atlas-nine-model-native-v1/atlas_solver','/private/tmp/atlas-nine-model-wasm-v1',str(stage/'observations.json')],['node','tools/test_wasm.mjs','--wasm-dir',wasm,'--native',native],['python3','-B','-m','unittest','discover','-s','tests','-p','test_laboratory_controls.py','-v']]
for i,argv in enumerate(commands):
 receipt=stage/f'check-command-{i}.json'
 if receipt.exists():raise RuntimeError('preserve previous check')
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(argv,cwd=root,env={**os.environ,'ATLAS_SOLVER':native,'PYTHONDONTWRITEBYTECODE':'1'},text=True,capture_output=True)
 receipt.write_text(json.dumps({'argv':argv,'ATLAS_SOLVER':native,'started_utc':start,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
 print(i,r.returncode,r.stdout[-800:],r.stderr[-800:],flush=True)
