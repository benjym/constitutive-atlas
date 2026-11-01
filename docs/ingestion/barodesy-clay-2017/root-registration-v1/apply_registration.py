"""Apply only reviewed document/registry bytes, preserving old successful receipts."""
from pathlib import Path
import json,hashlib,sys,tempfile,shutil
R=Path('/Users/bmar5496/code/constitutive-atlas');P=Path(__file__).parent
sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(P/'installation-plan-v1.json')
old='catalogue/laboratory-examples.json'
current=P.parent/'ncl-current-v2'
assert sha(current/'laboratory-document-v2.json')==plan['new_protocol_sha256']
assert sha(current/'proposed-registry-v2.json')==plan['new_registry_sha256']
assert sha(R/old)==plan['prior_paths'][old]
assert not (R/plan['new_protocol']).exists()
assert sha(current/'independent-review/document-v1/receipt.json')=='7f2fb2b35ca0dd888697f847bf09f7970d9fa2ad6d99ecc068ef3a88aced707b'
for n,h in plan['map_before'].items():
 assert (sha(R/n) if (R/n).exists() else None)==h,n
for n,h in plan['unchanged_original_documents'].items():assert sha(R/n)==h,n
for row in plan['redirected_pairs']:
 assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256']
for n,node in plan['maps'].items():
 if (R/n).exists():
  oldmap=read(R/n)
  assert all(node['documents'].get(k)==v for k,v in oldmap['documents'].items())
  assert all(e in node['entries'] for e in oldmap['entries'])
# Pure virtual verification before touching any shared path.
with tempfile.TemporaryDirectory(prefix='atlas-barodesy-registry-dry-') as t:
 v=Path(t)
 def put(n,data):
  f=v/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 for n,h in plan['prior_paths'].items():
  put(str(Path('catalogue/source-snapshots')/h/n),(R/n).read_bytes())
 for n in plan['unchanged_original_documents']:put(n,(R/n).read_bytes())
 for n,node in plan['maps'].items():put(n,(json.dumps(node,indent=2)+'\n').encode())
 put(old,(current/'proposed-registry-v2.json').read_bytes())
 put(plan['new_protocol'],(current/'laboratory-document-v2.json').read_bytes())
 for row in plan['redirected_pairs']:
  selected=checked_receipt(v,row['document'],row['original_path'],row['sha256'])
  assert sha(selected)==row['sha256']
print('PASS: exact prior guards, six additive maps and eleven historical pairs in virtual root.')
if '--apply' not in sys.argv:sys.exit(0)
# All exact-byte archives precede mutable shared paths.
for n,h in plan['prior_paths'].items():
 data=(R/n).read_bytes()
 for dest in [R/'catalogue/source-snapshots'/h/n,P/'prior-source'/n]:
  dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert dest.read_bytes()==data,dest
  else:dest.write_bytes(data)
for n,node in plan['maps'].items():
 dest=R/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(node,indent=2)+'\n')
(R/plan['new_protocol']).write_bytes((current/'laboratory-document-v2.json').read_bytes())
(R/old).write_bytes((current/'proposed-registry-v2.json').read_bytes())
for n,h in plan['unchanged_original_documents'].items():assert sha(R/n)==h
for row in plan['redirected_pairs']:
 assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256']
report={'passed':True,'plan_sha256':sha(P/'installation-plan-v1.json'),'script_sha256':sha(Path(__file__)),'original_documents_unchanged':len(plan['unchanged_original_documents']),'redirected_pairs_verified':len(plan['redirected_pairs']),'prior_paths_archived':plan['prior_paths'],'installed_files':{n:sha(R/n) for n in [old,plan['new_protocol'],*plan['maps']]},'scope':'Exact reviewed model document/entry and additive preservation only; no model/runtime/build/browser/remote claim'}
(P/'installation-result-v1.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
