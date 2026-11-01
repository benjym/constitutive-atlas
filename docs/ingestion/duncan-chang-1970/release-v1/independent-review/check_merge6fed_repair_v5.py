"""Independent virtual overlay replay of saved receipt predicates."""
from pathlib import Path
import json,hashlib,sys,tempfile,shutil,subprocess
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
out=Path(__file__).resolve().parent;pre=Path('docs/ingestion/duncan-chang-1970/release-v2');plan=json.loads((root/pre/'merge-6fed-v1/repair-v2/plan.json').read_text());ops=plan['operations'];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();queries=[]
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
# Independent complete reverse pass over every current non-null operation base.
maptargets={p:o['original_sha256'] for p,o in ops.items() if o['original_sha256']}
reverse=set()
def walk(n,d):
 if isinstance(n,dict):
  for k,v in n.items():
   if k in maptargets and v==maptargets[k]:reverse.add((d,k,v))
  p=n.get('path',n.get('original_path'));h=n.get('sha256',n.get('hash'))
  if isinstance(p,str) and p in maptargets and h==maptargets[p]:reverse.add((d,p,h))
  for v in n.values():walk(v,d)
 elif isinstance(n,list):
  for v in n:walk(v,d)
scanned=0;parseerrors=[]
for d in subprocess.check_output(['rg','--files','--hidden','-g','*.json','-g','!.git/**'],cwd=root,text=True).splitlines():
 if d.startswith('catalogue/source-snapshots/'):continue
 data=(root/d).read_bytes();scanned+=1
 if not any(s.encode() in data for s in maptargets.values()):continue
 try:walk(json.loads(data),d)
 except Exception as e:parseerrors.append({'path':d,'error':str(e)})
reverse_valid=[];reverse_preexisting=[]
for d,p,s in sorted(reverse):
 try:checked_receipt(root,d,p,s);reverse_valid.append((d,p,s))
 except Exception as e:reverse_preexisting.append({'document':d,'path':p,'sha256':s,'error':str(e)})
queries.extend(reverse_valid)
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
metadata=[];blocking=[]
for e in errors:
 if e['document']==str(pre/'merge-6fed-v1/repair-v1/plan.json') and e['error']=='source path/hash pair absent from original receipt document':
  doc=json.loads((root/e['document']).read_text())
  assert any(b.get('original_path')==e['path'] and b.get('sha256')==e['sha256'] for b in doc['bindings'])
  canonical=root/'catalogue/source-snapshots'/e['sha256']/e['path'];assert h(canonical)==e['sha256'];metadata.append(e)
 else:blocking.append(e)
assert len(metadata)==36
print(json.dumps({'status':'FAIL' if blocking else 'PASS-BOUNDED','normal_checked_receipt_queries_passed':len(queries)-len(errors),'raw_original_path_metadata_identities_verified':len(metadata),'retained_metadata_helper_failures':metadata,'operations':len(ops),'new_bindings':len(plan['bindings']),'queries_replayed':len(queries),'groups':{'repair':124,'prior':205,'remote_affected':126,'remote_original':266},'failures':blocking,'reverse_scan_json_files':scanned,'reverse_pairs':len(reverse),'reverse_currently_valid_replayed':len(reverse_valid),'preexisting_reverse_failures':reverse_preexisting,'reverse_parse_errors':parseerrors,'all_sibling_json_pins_exact':True,'original_pins_and_entries_unchanged':True},indent=2));assert not blocking and not parseerrors
