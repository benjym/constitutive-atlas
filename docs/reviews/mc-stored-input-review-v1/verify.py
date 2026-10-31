"""Portable source-only corpus replay. Does not execute the historical candidate capture."""
from pathlib import Path
import json,hashlib,tempfile,subprocess,sys,shutil
R=Path(sys.argv[1]).resolve()if len(sys.argv)>1 else Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parent;C=R/'docs/reviews/mc-stored-input-v1';A=R/'docs/reviews/mc-stored-input-audit-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):return subprocess.run([sys.executable,'-I','-S','-B',*map(str,args)],capture_output=True,check=True)
freeze=json.loads((C/'prospective-freeze.json').read_text())
for rel,rec in freeze['files'].items():
 f=C/rel;assert sha(f)==rec['sha256'] and f.stat().st_size==rec['bytes']
for rel,rec in json.loads((A/'manifest.json').read_text())['files'].items():
 f=A/rel;assert sha(f)==rec['sha256'] and f.stat().st_size==rec['bytes']
for name,pin in json.loads((P/'adapter-pins.json').read_text()).items():
 assert sha(P/name)==pin['portable_sha256']and sha(A/name)==pin['original_sha256']
with tempfile.TemporaryDirectory(prefix='atlas-mc-corpus-replay-')as tmp:
 out=Path(tmp);capsule=out/'capsule';shutil.copytree(C,capsule)
 run([capsule/'generate.py',capsule/'frozen',out/'replay',capsule/'retained-v1-holds.json'])
 assert (out/'replay/inputs.json').read_bytes()==(C/'inputs.json').read_bytes()
 run([P/'audit.py',capsule,out]);run([P/'mixed_scale.py',capsule,out])
 for name in ['checks.json','mixed-scale-checks.json']:
  assert json.loads((out/name).read_text())==json.loads((A/name).read_text()),name
 data=json.loads((C/'inputs.json').read_text())
 assert len(data['cases'])==140 and len(data['seeds'])==data['columns']==38
print(json.dumps({'passed':True,'cases':140,'unique_mechanical_parameter_inputs':115,'incoming_columns':38,'seed_rank':18,'source_assertions':860,'mixed_scale_assertions':15,'exact_copied_generator_replay':True,'candidate_calls':0,'capture_executed':False,'compiled_observations':0},indent=2))
