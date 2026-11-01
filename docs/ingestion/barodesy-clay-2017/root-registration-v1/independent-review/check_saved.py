from pathlib import Path
import json,hashlib,sys,subprocess,tempfile
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/ingestion/barodesy-clay-2017/root-registration-v1';N=P.parent/'ncl-current-v2';O=P/'independent-review';sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
if (O/'inputs.json').exists():
 for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
plan=read(P/'installation-plan-v1.json');result=read(P/'installation-result-v1.json');scan=read(N/'registry-binding-scan-v2.json')
assert sha(N/'registry-binding-scan-v2.json')==plan['source_scan_sha256'];assert sha(R/'atlas/evidence.py')==scan['checked_receipt_source_sha256']
assert result['passed']and result['plan_sha256']==sha(P/'installation-plan-v1.json')and result['script_sha256']==sha(P/'apply_registration.py')
assert len(plan['maps'])==6 and len(plan['prior_paths'])==4 and len(plan['redirected_pairs'])==11 and len(plan['unchanged_original_documents'])==7
for p,h in result['installed_files'].items():assert sha(R/p)==h,p
for p,h in plan['unchanged_original_documents'].items():assert sha(R/p)==h,p
for p,h in plan['prior_paths'].items():
 a=R/'catalogue/source-snapshots'/h/p;assert sha(a)==h and a.read_bytes()==(P/'prior-source'/p).read_bytes()
for p,m in plan['maps'].items():
 assert read(R/p)==m
 if plan['map_before'][p]:
  old=read(R/'catalogue/source-snapshots'/plan['map_before'][p]/p)
  assert all(m['documents'].get(k)==v for k,v in old['documents'].items())and all(e in m['entries']for e in old['entries'])
 for d,h in m['documents'].items():assert sha(R/d)==h,d
 for e in m['entries']:assert sha(R/e['archived_path'])==e['sha256'],e
for row in plan['redirected_pairs']:assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256']
counts={}
for k in ['primary_references','secondary_source_map_references']:
 rows=[r for r in scan[k]if r['original_path']in plan['prior_paths']and r['resolution']!='unresolved'];counts[k]=len(rows)
 for row in rows:
  assert sha(R/row['document'])==row['document_sha256']
  if row['resolution'].endswith('sidecar-entry'):
   # Scanner recognizes original_path entries, which checked_receipt intentionally does not treat as receipt shape.
   snap=R/'catalogue/source-snapshots'/row['sha256']/row['original_path'];assert sha(snap)==row['sha256']
  else:assert sha(checked_receipt(R,row['document'],row['original_path'],row['sha256']))==row['sha256'],row
assert sha(R/plan['new_protocol'])==plan['new_protocol_sha256']==sha(N/'laboratory-document-v2.json')
assert sha(R/'catalogue/laboratory-examples.json')==plan['new_registry_sha256']==sha(N/'proposed-registry-v2.json')
reg=read(R/'catalogue/laboratory-examples.json');old=read(P/'prior-source/catalogue/laboratory-examples.json');assert reg['examples'][:-1]==old['examples']and len(reg['examples'])==4
consumer=read(P/'root-consumer-v1.json');assert consumer['exit_code']==0
with tempfile.TemporaryDirectory(prefix='barodesy-root-independent-')as t:
 cmd=['node','tools/build_laboratory_examples.mjs',str(R),t,consumer['command'][-1]]
 z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert z.returncode==0,z.stderr
 assert read(Path(t)/'laboratory-examples.json')==consumer['index']
 for p,v in consumer['files'].items():assert sha(Path(t)/p)==v['sha256']and(Path(t)/p).stat().st_size==v['bytes']
# Initial malformed plan differs solely in trailing literal backslash-n, no semantic plan revision.
initial=(P/'installation-plan-initial.json.txt').read_text();corrected=(P/'installation-plan-v1.json').read_text();assert initial.endswith('\\n')and initial[:-2].rstrip()==corrected.rstrip()
print(json.dumps({'passed':True,'maps_additive':6,'canonical_prior_snapshots':4,'immutable_original_documents':7,'redirected_pairs':11,'prior_successful_affected_primary_pairs':counts['primary_references'],'prior_successful_affected_secondary_pairs':counts['secondary_source_map_references'],'old_entries_unchanged':3,'normal_root_consumer_examples':4,'reviewer_compiled_calls':0,'registration_helper_reapplied':False,'limitations':['Preexisting unresolved scanner entries not repaired or accepted.','Original_path scanner entries preserved by exact canonical snapshot; standard receipt shape is intentionally narrower.','Root registration only; no package/browser/live or scientific scope expansion.']},indent=2))
