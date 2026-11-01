from pathlib import Path
import json,hashlib,sys,tempfile,subprocess
H=Path(__file__).resolve().parent;R=H.parents[5];sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
P=R/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/profile-count-fix-v1'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=load(P/'SOURCE_FREEZE.json');assert sha(P/'SOURCE_FREEZE.json')=='7f54923b8c99907de3438ed1f1c2092fd291a4ffb6e9d737b18cc1758fa61b26'
for row in f['files']:assert sha(R/row['original_path'])==row['old_sha256']
p=load(P/'PROPOSAL.json');before=(P/'test-before.mjs').read_bytes();after=(P/'test-proposed.mjs').read_bytes()
assert before.count(b'complete thirteen model')==1 and before.count(b'.cases.length,35)')==2
assert after==before.replace(b'complete thirteen model',b'complete fourteen model').replace(b'.cases.length,35)',b'.cases.length,36)')
assert sha(R/p['source']['original_path'])==p['source']['old_sha256']
policy=load(R/'catalogue/laboratory-profile-policy.json');assert policy['case_count']==len(load(R/policy['cases']['path']))==36 and len(list((R/'models').glob('*.json')))==14
text=after.decode().replace("from'../tools/laboratory_profile_policy.mjs'",'from'+json.dumps((R/'tools/laboratory_profile_policy.mjs').as_uri())).replace("const root=resolve(import.meta.dirname,'..')",'const root='+json.dumps(str(R)))
assert text==(P/'test-harness.mjs').read_text();(H/'harness.mjs').write_text(text)
r=subprocess.run(['node','--test',str(H/'harness.mjs')],capture_output=True,text=True,timeout=30);(H/'node.log').write_text(r.stdout+r.stderr);assert r.returncode==0
virtual={p['source']['original_path']:P/p['source']['future_copy']}
for row in p['maps']:
 live=R/row['original_path'];assert (sha(live) if live.exists() else None)==row['old_sha256'];candidate=P/row['candidate'];assert sha(candidate)==row['new_sha256'];virtual[row['original_path']]=candidate
 if live.exists():
  old=load(live);new=load(candidate);assert all(new['documents'].get(k)==v for k,v in old['documents'].items());assert all(e in new['entries'] for e in old['entries'])
for row in p['archives']:
 candidate=P/row['snapshot'];assert sha(candidate)==row['old_sha256'];virtual[row['canonical_archive']]=candidate
with tempfile.TemporaryDirectory(dir=H) as d:
 d=Path(d)
 def copy(name):
  dest=d/name
  if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(virtual.get(name,R/name).read_bytes())
 for row in p['checks']:
  assert row['outcome']=='passed';doc=row['document'];name=row['original_path'];digest=row['old_sha256'];copy(doc)
  side=str(Path(doc).parent/'source-archive-map.json')
  if side in virtual or (R/side).exists():
   copy(side);m=load(d/side);matches=[e for e in m['entries'] if e['original_path']==name and e['sha256']==digest]
   selected=matches[0]['archived_path'] if matches else name
  else:selected=name
  copy(selected);checked_receipt(d,doc,name,digest)
assert len(p['checks'])==123 and len(p['maps'])==len(p['archives'])==8
(H/'RESULTS.json').write_text(json.dumps(dict(status='passed',exact_positive_tokens=3,pure_node_tests=16,preservation_checks=123,maps=8,archives=8,scope='Prospective source/metadata review; no production installation or numerical gate changes'),indent=2)+'\n')
print('PASS exact tokens,16 pure tests,123 actual receipt checks')
