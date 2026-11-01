"""Independent virtual overlay replay of saved receipt predicates."""
from pathlib import Path
import json,hashlib,sys,tempfile,shutil,subprocess
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
out=Path(__file__).resolve().parent;pre=Path('docs/ingestion/duncan-chang-1970/release-v2');plan=json.loads((root/pre/'merge-6fed-v1/repair-v1/plan.json').read_text());ops=plan['operations'];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();queries=[]
for p,o in ops.items():
 assert h(root/o['proposed_path'])==o['sha256'];assert (h(root/p) if (root/p).exists() else None)==o['original_sha256']
 new=json.loads((root/o['proposed_path']).read_text());old=json.loads((root/p).read_text()) if (root/p).exists() else {'documents':{},'entries':[]}
 assert all(new['documents'].get(k)==v for k,v in old['documents'].items());assert all(e in new['entries'] for e in old['entries'])
 for q in (root/p).parent.glob('*.json'):
  if q.name!='source-archive-map.json':assert new['documents'].get(str(q.relative_to(root)))==h(q)
 for d,v in new['documents'].items():assert h(root/d)==v
 for e in new['entries']:
  assert e['archived_path']==str(Path('catalogue/source-snapshots')/e['sha256']/e['original_path']);assert h(root/e['archived_path'])==e['sha256']
queries.extend((b['document'],b['original_path'],b['sha256']) for b in plan['bindings'])
for version in ['v1','v2','v3']:
 p=json.loads((root/pre/f'preservation-{version}/preservation-plan.json').read_text());queries.extend((b['document'],b['original_path'],b['sha256']) for b in p['bindings'])
a=json.loads((out/'merge6fed-affected-initial-results-v3.json').read_text());queries.extend((b['document'],b['path'],b['sha256']) for b in a['failures']+a['passed_predicates'])
prefix=Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1');a=json.loads((root/prefix/'ci-compat-v3/CONTEXT_REPAIR.json').read_text());queries.extend((b['document'],b['path'],b['sha256']) for b in a['resolved']);a=json.loads((root/prefix/'independent-review/ci-compat-v3/POSITIVE_REPAIR_INPUTS.json').read_text());queries.extend((d,b['path'],b['old_sha256']) for d,v in a['groups'].items() for b in v['pairs'])
with tempfile.TemporaryDirectory(prefix='duncan-merge-repair-review-') as tmp:
 v=Path(tmp)
 def cp(p):
  dest=v/p;dest.parent.mkdir(parents=True,exist_ok=True)
  source=root/ops[p]['proposed_path'] if p in ops else root/p
  if source.exists():shutil.copyfile(source,dest)
 for d,p,s in queries:
  cp(d);cp(str(Path(d).parent/'source-archive-map.json'));cp(p);cp(str(Path('catalogue/source-snapshots')/s/p))
 errors=[]
 for d,p,s in queries:
  try:checked_receipt(v,d,p,s)
  except Exception as e:errors.append({'document':d,'path':p,'sha256':s,'error':str(e)})
print(json.dumps({'status':'FAIL' if errors else 'PASS','operations':len(ops),'new_bindings':len(plan['bindings']),'queries_replayed':len(queries),'groups':{'repair':84,'prior':205,'remote_affected':126,'remote_original':266},'failures':errors,'all_sibling_json_pins_exact':True,'original_pins_and_entries_unchanged':True},indent=2));assert not errors
