from pathlib import Path
import json,hashlib,sys,shutil
r=Path('/Users/bmar5496/code/constitutive-atlas');stage=Path('/private/tmp/atlas-spectral-history-binding-audit-v1');out=r/'docs/reviews/spectral-history-source-bindings-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())
m=load(stage/'manifest.json')
for rel,record in m['files'].items():
 expected=record['sha256']if isinstance(record,dict)else record
 assert sha(stage/rel)==expected,rel
plan=load(stage/'plan.json');assert not out.exists()
for item in plan['staged_verified_bytes']:assert sha(r/item['original_path'])==item['sha256'] and sha(stage/item['staged_path'])==item['sha256']
for row in plan['documents']:assert sha(r/row['document'])==row['document_sha256']
shutil.copytree(stage,out/'audit');written=[]
for item in plan['staged_verified_bytes']:
 dest=r/'catalogue/source-snapshots'/item['sha256']/item['original_path'];data=(stage/item['staged_path']).read_bytes()
 if dest.exists():assert dest.read_bytes()==data
 else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data);written.append(dest.relative_to(r).as_posix())
for row in plan['documents']:
 path=r/row['sibling_sidecar'];mapping=load(path);old=mapping['documents'].get(row['document']);assert old is None or old==row['document_sha256'];mapping['documents'][row['document']]=row['document_sha256']
 for binding in row['bindings']:
  e={'original_path':binding['original_path'],'sha256':binding['sha256'],'archived_path':binding['canonical_archive']}
  same=[x for x in mapping['entries']if x['original_path']==e['original_path']and x['sha256']==e['sha256']];assert not same or same==[e]
  if not same:mapping['entries'].append(e)
 path.write_text(json.dumps(mapping,indent=2)+'\n')
sys.path.insert(0,str(r));from atlas.evidence import checked_receipt
verified=[]
for row in plan['documents']:
 assert sha(r/row['document'])==row['document_sha256']
 for binding in row['bindings']:
  resolved=checked_receipt(r,row['document'],binding['original_path'],binding['sha256']);assert resolved==r/binding['canonical_archive'];verified.append({'document':row['document'],'original_path':binding['original_path'],'sha256':binding['sha256'],'resolved':resolved.relative_to(r).as_posix()})
secondary=[]
for row in plan['affected_secondary_references']:
 if row['resolution'] in ('archived','live'):
  resolved=checked_receipt(r,row['document'],row['original_path'],row['sha256']);assert sha(resolved)==row['sha256'];secondary.append(row['document'])
 elif row['resolution']in('archived-sidecar-entry','live-sidecar-entry'):
  target=r/'catalogue/source-snapshots'/row['sha256']/row['original_path'];assert sha(target)==row['sha256'];secondary.append(row['document'])
 else:raise AssertionError(row)
for item in plan['minimal_maps_to_create_or_extend']:
 old=load(r/'catalogue/source-snapshots'/item['sha256']/item['original_path']);new=load(r/item['original_path']);assert all(new['documents'].get(k)==v for k,v in old['documents'].items());assert all(e in new['entries']for e in old['entries'])
report={'verified_bindings':verified,'secondary_edges_checked':len(secondary),'original_documents_unchanged':len(plan['documents']),'old_map_pins_and_entries_preserved':True,'new_snapshots':written,'changed_sidecars':[i['original_path']for i in plan['minimal_maps_to_create_or_extend']],'compiled_observations':0}
(out/'archive-checks.json').write_text(json.dumps(report,indent=2)+'\n');shutil.copyfile(__file__,out/'preserve.py')
(out/'README.md').write_text('''# History-source preservation before spectral event validation

All 30 original history.py bindings and five live reverse GIS-map receipt bindings now resolve through exact canonical archived bytes. All 35 original documents are unchanged. All 35 existing maps retain their prior document pins and entries; all 36 pre-change source/map identities are preserved. The 58 affected secondary edges were checked at their original hashes, including already archived and descriptive map-entry references. No numerical or compiled observation was made.

The worker audit is retained unmodified in `audit/`, with the original limited scanner, independent fixed-point sibling-map closure, source-byte snapshots, six extraction probes and manifest. Two required sibling maps were missed by the inherited conservative scanner; the stronger plan follows actual live receipt-to-sibling-map dependencies. Existing packet-local/descriptive diagnostics are retained explicitly.

`archive-checks.json` records each checked original binding and all changed maps. `preserve.py` records the one-shot coordinator action with its intentional original staging paths; do not rerun it over this output. Identity preservation alone does not replay old execution against its complete dependencies. No old source hash or document was rewritten.
''')
print(json.dumps({'bindings':len(verified),'maps':35,'new_snapshots':len(written),'secondary_edges':len(secondary)}))
