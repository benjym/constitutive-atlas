"""Read-only compact archive integrity and installed binding replay."""
import hashlib,json,sys,tarfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[4];sha=lambda b:hashlib.sha256(b).hexdigest()
a=json.loads((B/'artifact.json').read_text());assert sha((B/'preservation-plan.tar.gz').read_bytes())==a['archive_sha256'];assert sha((B/'members.json').read_bytes())==a['members_sha256'];members=json.loads((B/'members.json').read_text());payload={}
with tarfile.open(B/'preservation-plan.tar.gz','r:gz')as t:
 for m in t.getmembers():
  assert m.isfile()and not Path(m.name).is_absolute()and '..'not in Path(m.name).parts and m.name not in payload;payload[m.name]=t.extractfile(m).read()
assert set(payload)==set(members);assert all(sha(payload[p])==h for p,h in members.items());assert sha(payload['plan.json'])==a['plan_sha256'];assert payload['plan.json']==(B/'plan.json').read_bytes();p=json.loads(payload['plan.json']);sys.path.insert(0,str(R));from atlas.evidence import checked_receipt,verify_manifest_files
for row in p['required_edges']:
 assert sha((R/row['document']).read_bytes())==row['document_sha256'];checked_receipt(R,row['document'],row['original_path'],row['sha256'])
verify_manifest_files(R,str((B/'receipt.json').relative_to(R)))
print('PASS compact archive',len(payload),'members;',len(p['required_edges']),'original bindings; installation manifest')
