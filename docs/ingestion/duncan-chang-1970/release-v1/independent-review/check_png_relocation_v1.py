"""Prospective PNG relocation: saved-source maps and unmodified packet test only."""
from pathlib import Path
import json,hashlib,sys,tempfile,shutil,subprocess,importlib.util,unittest,io
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
out=Path(__file__).resolve().parent;pre=Path('docs/ingestion/duncan-chang-1970/release-v2');packet=pre/'ci-png-relocation-v1';plan=json.loads((root/packet/'preservation-v1/preservation-plan.json').read_text());proposal=json.loads((root/packet/'relocation-proposal.json').read_text());ops=plan['planned_sidecars'];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();removed=set();queries=[];preexisting_unpinned=[]
assert proposal['base']=='0cd28fc2a18dea9a496795ad149a58afed809930'
for e in proposal['images']:
 old=e.get('original_path',e['path']);removed.add(old);assert h(root/old)==h(root/e['archived_path'])==e['sha256'];assert (root/old).stat().st_size==e['bytes']
for e in proposal['original_proofs']:assert h(root/e['path'])==e['sha256']
for p,o in ops.items():
 assert h(root/o['proposed_path'])==o['proposed_sha256'];assert (h(root/p) if (root/p).exists() else None)==o['original_sha256']
 old=json.loads((root/p).read_text()) if (root/p).exists() else {'documents':{},'entries':[]};new=json.loads((root/o['proposed_path']).read_text());assert all(new['documents'].get(k)==v for k,v in old['documents'].items());assert all(e in new['entries'] for e in old['entries'])
 for d,v in new['documents'].items():assert h(root/d)==v
 for q in (root/p).parent.glob('*.json'):
  if q.name=='source-archive-map.json':continue
  if new['documents'].get(str(q.relative_to(root)))!=h(q):
   assert o['original_sha256'] is not None and old['documents'].get(str(q.relative_to(root)))!=h(q);preexisting_unpinned.append(str(q.relative_to(root)))
 for e in new['entries']:assert e['archived_path']==str(Path('catalogue/source-snapshots')/e['sha256']/e['original_path']) and h(root/e['archived_path'])==e['sha256']
assert not plan['document_pin_rollforwards']
queries.extend((e['document'],e['original_path'],e['sha256']) for e in plan['bindings'])
# All prior real normal predicates, filtering only explicitly retained unsupported raw metadata.
merge=json.loads((root/pre/'merge-6fed-v1/repair-v2/plan.json').read_text());queries.extend((e['document'],e['original_path'],e['sha256']) for e in merge['bindings'] if e['document']!=str(pre/'merge-6fed-v1/repair-v1/plan.json'))
for ver in ['v1','v2','v3']:
 a=json.loads((root/pre/f'preservation-{ver}/preservation-plan.json').read_text());queries.extend((e['document'],e['original_path'],e['sha256']) for e in a['bindings'])
a=json.loads((out/'merge6fed-affected-initial-results-v3.json').read_text());queries.extend((e['document'],e['path'],e['sha256']) for e in a['failures']+a['passed_predicates'])
pp=Path('docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1');a=json.loads((root/pp/'ci-compat-v3/CONTEXT_REPAIR.json').read_text());queries.extend((e['document'],e['path'],e['sha256']) for e in a['resolved']);a=json.loads((root/pp/'independent-review/ci-compat-v3/POSITIVE_REPAIR_INPUTS.json').read_text());queries.extend((d,e['path'],e['old_sha256']) for d,x in a['groups'].items() for e in x['pairs']);queries.extend((e['document'],e['path'],e['sha256']) for e in json.loads((out/'merge6fed-reverse-scan-v3.json').read_text())['missing_valid_edges'])
# Independent full current source reverse scan; check every baseline-valid pair after overlay.
targets={p:o['original_sha256'] for p,o in ops.items() if o['original_sha256']};targets.update({e.get('original_path',e['path']):e['sha256'] for e in proposal['images']});pairs=set();scanned=0;excluded=[]
def walk(n,d):
 if isinstance(n,dict):
  for k,v in n.items():
   if k in targets and isinstance(v,str) and v==targets[k]:pairs.add((d,k,v))
  p=n.get('path');s=n.get('sha256',n.get('hash'))
  if isinstance(p,str) and p in targets and s==targets[p]:pairs.add((d,p,s))
  for v in n.values():walk(v,d)
 elif isinstance(n,list):
  for v in n:walk(v,d)
for d in subprocess.check_output(['rg','--files','--hidden','-g','*.json','-g','!.git/**'],cwd=root,text=True).splitlines():
 if d.startswith('catalogue/source-snapshots/'):continue
 data=(root/d).read_bytes();scanned+=1
 if not any(v.encode() in data for v in targets.values()):continue
 try:walk(json.loads(data),d)
 except json.JSONDecodeError:raise
valid=[]
for d,p,s in sorted(pairs):
 try:checked_receipt(root,d,p,s);valid.append((d,p,s))
 except Exception as e:excluded.append({'document':d,'path':p,'sha256':s,'error':str(e)})
queries.extend(valid)
with tempfile.TemporaryDirectory(prefix='duncan-png-review-') as tmp:
 virtual=Path(tmp)
 def cp(p):
  if p in removed:return
  source=root/ops[p]['proposed_path'] if p in ops else root/p
  if source.exists():
   d=virtual/p;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,d)
 for d,p,s in queries:cp(d);cp(str(Path(d).parent/'source-archive-map.json'));cp(p);cp(str(Path('catalogue/source-snapshots')/s/p))
 errors=[]
 for d,p,s in queries:
  try:checked_receipt(virtual,d,p,s)
  except Exception as e:errors.append({'document':d,'path':p,'sha256':s,'error':str(e)})
 assert not errors,errors
 # Execute only unchanged pure source/extension gate in virtual packet layout.
 spec=importlib.util.spec_from_file_location('png_packet_gate',root/'tests/test_ingestion_packets.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 for model in mod.PACKETS:
  source=root/'docs/ingestion'/model;dest=virtual/'docs/ingestion'/model
  if model=='duncan-chang-1970':
   for q in source.rglob('*'):
    rel=q.relative_to(root)
    if q.is_file() and str(rel) not in removed:
     d=virtual/rel
     if not d.exists():d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(q)
  else:
   for q in source.rglob('*'):
    if q.is_file():
     d=virtual/q.relative_to(root)
     if not d.exists():d.parent.mkdir(parents=True,exist_ok=True);d.symlink_to(q)
 mod.ROOT=virtual;stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(unittest.TestSuite([mod.IngestionPackets('test_local_packet_receipts')]));assert result.wasSuccessful(),stream.getvalue()
print(json.dumps({'status':'PASS','maps':len(ops),'images_removed':len(removed),'new_bindings':len(plan['bindings']),'normal_queries_replayed':len(queries),'prior_normal_queries':689,'reverse_json_scanned':scanned,'baseline_valid_reverse_pairs_replayed':len(valid),'retained_preexisting_reverse_failures':excluded,'retained_preexisting_unpinned_siblings':preexisting_unpinned,'pure_unchanged_packet_gate':'PASS in virtual removed-image layout','no_compiled_calls':True,'historical_direct_path_replay':'Requires exact archived image materialization; originals/checkers unchanged'},indent=2))
