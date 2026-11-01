from pathlib import Path
import json,hashlib,sys,tempfile
R=Path('/Users/bmar5496/code/constitutive-atlas');P=Path(__file__).parent
sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(P/'installation-plan-v1.json')
assert sha(P/'independent-review/receipt.json')=='844b3eb6c9086e49fd167f757e0e9b6bff9f503de9f973b26894f424709500e2'
for n,h in plan['prior_paths'].items():assert sha(R/n)==h,n
for n,h in plan['map_before'].items():assert (sha(R/n) if (R/n).exists() else None)==h,n
for n,h in plan['unchanged_original_documents'].items():assert sha(R/n)==h,n
for n,item in plan['replacements'].items():assert sha(R/item['candidate'])==item['sha256'],n
for row in plan['redirected_pairs']:assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256']
for n,node in plan['maps'].items():
 if (R/n).exists():
  old=read(R/n);assert all(node['documents'].get(k)==v for k,v in old['documents'].items());assert all(e in node['entries'] for e in old['entries'])
with tempfile.TemporaryDirectory(prefix='atlas-deeplink-dry-') as t:
 v=Path(t)
 def put(n,data):
  f=v/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 for n,h in plan['prior_paths'].items():put(str(Path('catalogue/source-snapshots')/h/n),(R/n).read_bytes())
 for n in plan['unchanged_original_documents']:put(n,(R/n).read_bytes())
 for n,node in plan['maps'].items():put(n,(json.dumps(node,indent=2)+'\n').encode())
 for n,item in plan['replacements'].items():put(n,(R/item['candidate']).read_bytes())
 for row in plan['redirected_pairs']:assert sha(checked_receipt(v,row['document'],row['original_path'],row['sha256']))==row['sha256']
print('PASS: virtual installation preserves all23 affected historical source bindings.')
if '--apply' not in sys.argv:sys.exit(0)
for n,h in plan['prior_paths'].items():
 data=(R/n).read_bytes()
 for dest in [R/'catalogue/source-snapshots'/h/n,P/'prior-source'/n]:
  dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert dest.read_bytes()==data,dest
  else:dest.write_bytes(data)
for n,node in plan['maps'].items():
 dest=R/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(node,indent=2)+'\n')
for n,item in plan['replacements'].items():(R/n).write_bytes((R/item['candidate']).read_bytes())
for n,h in plan['unchanged_original_documents'].items():assert sha(R/n)==h
for row in plan['redirected_pairs']:assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256']
report={'passed':True,'plan_sha256':sha(P/'installation-plan-v1.json'),'script_sha256':sha(Path(__file__)),'original_documents_unchanged':len(plan['unchanged_original_documents']),'redirected_pairs_verified':len(plan['redirected_pairs']),'prior_paths_archived':plan['prior_paths'],'installed_files':{n:sha(R/n) for n in [*plan['replacements'],*plan['maps']]},'scope':'Exact independently reviewed navigation/test bytes and additive archival only; normal package and actual installed browser verification pending. No model/numerical/remote claim.'}
(P/'installation-result-v1.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
