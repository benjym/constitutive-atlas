"""Post-observation evidence verifier; never compiles or executes candidate binaries."""
from pathlib import Path
import json,gzip,hashlib,subprocess,sys,tempfile,shutil
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((P/'prospective-freeze.json').read_text())
for rel,r in freeze['files'].items():
 p=P/rel;assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes'],rel
last=freeze['frozen_at'];assessments={}
for backend in ('native','wasm'):
 for phase in ('configure','build','run'):
  r=json.loads((P/backend/(phase+'-command.json')).read_text())
  assert r['returncode']==0 and r['freeze_sha256']==sha(P/'prospective-freeze.json')
  assert last<r['started_at']<r['ended_at'];last=r['ended_at']
  for stream in ('stdout','stderr'):assert r[stream+'_sha256']==sha(P/backend/(phase+'.'+stream))
  if phase=='build':assert r['command'][-4:]==['--target','atlas_spectral_context','--parallel','1']
  if backend=='wasm':assert r['EMCC_CORES']=='1'
 result=subprocess.run([sys.executable,'-B',str(P/'assessor/assess.py'),str(P),str(P/backend/'run.stdout')],capture_output=True,check=True)
 report=json.loads(result.stdout);assert report==json.loads((P/backend/'assessment.json').read_text()) and report['passed'];assessments[backend]=report['counts']
requests=json.loads(gzip.decompress((P/'requests.json.gz').read_bytes()))
wire=[]
for r in requests:
 tokens=[r['id'],str(r['slot']),r['kind'],str(r['threshold']),*[str(int(r[k])) for k in ('initial','check_only','reset','scale','observe_scale','solver_fail')],*r['values'],*[v for seed in r['seeds'] for v in seed]]
 wire.append(' '.join(tokens))
assert ('\n'.join(wire)+'\n').encode()==gzip.decompress((P/'requests.txt.gz').read_bytes())
with tempfile.TemporaryDirectory(prefix='atlas-spectral-context-replay-') as tmp:
 t=Path(tmp);root=t/'root';shutil.copytree(P/'frozen',root);out=t/'out'
 subprocess.run([sys.executable,'-B',str(P/'generate.py'),str(root),str(out)],capture_output=True,check=True)
 paths=[*sorted((P/'models').glob('*.json')),*sorted((P/'generated').glob('*')),P/'requests.json.gz',P/'slots.json',P/'history.json',P/'policy.json',P/'wire.json']
 for p in paths:assert p.read_bytes()==(out/p.relative_to(P)).read_bytes(),str(p)
 # Static validators run against a copied package and its copied source root.
 for name in ('static_checks.py',):shutil.copyfile(P/name,out/name)
 r=subprocess.run([sys.executable,'-B',str(out/'static_checks.py')],capture_output=True,check=True)
 assert json.loads(r.stdout)==json.loads((P/'static-results.json').read_text())
native=[json.loads(s) for s in (P/'native/run.stdout').read_text().splitlines()];wasm=[json.loads(s) for s in (P/'wasm/run.stdout').read_text().splitlines()]
assert len(native)==len(wasm)==1589
assert all((a['id'],a['ok'])==(b['id'],b['ok']) for a,b in zip(native,wasm))
print(json.dumps({'passed':True,'frozen_inputs':len(freeze['files']),'source_replayed_files':len(paths),'literal_wire_exact':True,'static_checks':36,'backend_counts':assessments,'backend_status_agreement':1589,'different_output_rows':sum(a!=b for a,b in zip(native,wasm)),'artifact_execution':False,'scientific_admission':False},indent=2))
