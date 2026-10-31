"""Verify frozen inputs, serial build receipts and raw reassessment without execution."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,tempfile,shutil
s=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((s/'manifest.json').read_text());freeze=json.loads((s/'prospective-freeze.json').read_text())
assert freeze['compiled_observations']==0 and freeze['manifest_sha256']==sha(s/'manifest.json')
for name,pin in manifest.items():assert sha(s/name)==pin,name
if (s/'evidence-manifest.json').exists():
 for name,pin in json.loads((s/'evidence-manifest.json').read_text()).items():assert sha(s/name)==pin,name
receipts={}
for role in ('native','wasm'):
 out=s/role;r=json.loads((out/'receipt.json').read_text());receipts[role]=r
 assert r['completed'] is True and r['backend']==role and r['manifest_sha256']==freeze['manifest_sha256']
 assert r['environment']['EMCC_CORES']=='1'
 assert sha(out/'journal.json')==r['journal_sha256']
 commands=r['commands'];assert all(c['returncode']==0 for c in commands)
 build=next(c for c in commands if c['label']=='build')['argv']
 assert build[-4:]==['--target','atlas_terracotta_study','--parallel','1']
 for row in r['artifacts'].values():assert sha(Path(row['path']))==row['sha256']
 journal=json.loads((out/'journal.json').read_text());assert len(journal)==9
 if role=='native':
  for i,row in enumerate(journal):assert row['raw']==(out/('request-'+str(i)+'.stdout.txt')).read_text()
assert receipts['native']['finished_utc']<=receipts['wasm']['started_utc']
assert freeze['utc']<=receipts['native']['started_utc']

# Reconstruct the exact cache-free source closure; do not execute compiled files.
with tempfile.TemporaryDirectory(prefix='atlas-terracotta-source-replay-') as tmp:
 clone=Path(tmp)
 for name in manifest:
  target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s/name,target)
 for role in ('native','wasm'):
  (clone/role).mkdir();shutil.copyfile(s/role/'journal.json',clone/role/'journal.json')
 subprocess.run([sys.executable,'-I','-B','-c',"import sys,runpy;sys.path.insert(0,sys.argv[1]);sys.argv=['atlas.compiler',sys.argv[2],sys.argv[3]];runpy.run_module('atlas.compiler',run_name='__main__')",str(clone/'frozen'),str(clone/'regenerated'),str(clone/'frozen/models/research')],check=True,capture_output=True)
 for name in ('models.hpp','models.json'):assert (clone/'regenerated'/name).read_bytes()==(clone/'generated'/name).read_bytes(),name
 subprocess.run([sys.executable,'-I','-B',str(clone/'assemble.py'),'--reference',str(clone/'reference/references.json'),'--model',str(clone/'frozen/models/research/terracotta-2024-fig1.json'),'--output',str(clone/'regenerated-requests.json')],check=True,capture_output=True)
 assert (clone/'regenerated-requests.json').read_bytes()==(clone/'requests.json').read_bytes()
 # Only the copied study's own adjacent assembler/assessor are importable.
 subprocess.run([sys.executable,'-I','-B','-c',"import sys,runpy;sys.path.insert(0,sys.argv[1]);runpy.run_path(sys.argv[2],run_name='__main__')",str(clone),str(clone/'evaluate.py')],check=True,capture_output=True)
 observed=json.loads((s/'assessment.json').read_text());replayed=json.loads((clone/'assessment.json').read_text())
 def physical_report(value):
  if isinstance(value,dict):return {k:physical_report(v) for k,v in value.items() if k!='traceback'}
  if isinstance(value,list):return [physical_report(v) for v in value]
  return value
 assert physical_report(replayed)==physical_report(observed),'Copied-source assessment differs'
 exact=(clone/'assessment.json').read_bytes()==(s/'assessment.json').read_bytes()
print(json.dumps({'evidence_verified':True,'status':observed['status'],'source_files':len(manifest),'exact_generated_bytes':True,'exact_requests':True,'exact_assessment_bytes':exact,'physical_assessment_equal':True,'compiled_execution':False,'artifact_bytes_rehashed':True}))
