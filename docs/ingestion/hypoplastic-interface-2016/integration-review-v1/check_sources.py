"""Read-only source and saved receipt audit; no compiled/module/material calls."""
from pathlib import Path
import json,hashlib,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016';OUT=Path(__file__).parent
freeze=json.loads((P/'integration-v1/integration-source-freeze.json').read_text());R=Path(freeze['release_root']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
for name,digest in freeze['files'].items():assert sha(R/name)==digest
review='catalogue/agent-reviews/hvwe2016-reconciled-fixed-local-agent-v1.json';assert sha(R/review)==freeze['E5_record_sha256']
sys.path.insert(0,str(R));from atlas.agent_review import validate_review,approval_entry
from atlas.evidence import checked_receipt
validate_review(R/review,root=R,for_approval=True)
registry=read(R/'catalogue/approved-models.json');selected=[a for a in registry['models'] if a['model_id']=='hvwe2016-reconciled-fixed-local'];assert selected==[approval_entry(R/review,root=R)]
q=read(R/'docs/ingestion/hypoplastic-interface-2016/execution-v1/qualification.json')
for name,digest in q['binding']['source_closure'].items():assert sha(R/name)==digest
base='54f409b37deaed0ab82a85cdac9f489bc65e1309'
old=lambda n:subprocess.check_output(['git','show',base+':'+n],cwd=ROOT)
for filename,key,identity in [('catalogue/manifest.json','models','id'),('catalogue/approved-models.json','models','model_id')]:
 before=json.loads(old(filename))[key];after=read(R/filename)[key]
 for entry in before:assert entry in after,(filename,entry[identity])
assert len(read(R/'catalogue/manifest.json')['models'])==len(json.loads(old('catalogue/manifest.json'))['models'])+1
app=(R/'web/app.js').read_text();before=old('web/app.js').decode()
import re
controllers=lambda s:re.findall(r'setup\w+Laboratory\(\{',s)
assert set(controllers(before)).issubset(controllers(app))
wf=(R/'.github/workflows/verify.yml').read_text();oldwf=old('.github/workflows/verify.yml').decode()
assert all(line in wf for line in oldwf.splitlines())
assert 'check_parity_v2.py path-results/interface2016/native.json path-results/interface2016/wasm.json path-results/interface2016/parity.json' in wf
pres=read(P/'integration-v1/preservation-receipt-v2.json');checked=0
for change in pres['map_changes']:
 doc=change['document'];source=change['source'];digest=change['source_sha256'];assert sha(R/doc)==sha(ROOT/doc) if (ROOT/doc).exists() else True
 checked_receipt(R,doc,source,digest);checked+=1
 if change['old_map_archive']:
  archive=R/change['old_map_archive'];assert sha(archive)==Path(change['old_map_archive']).parts[2]
for name,digest in pres['source_preimages'].items():
 assert hashlib.sha256(old(name)).hexdigest()==digest
 snapshot=R/'catalogue/source-snapshots'/digest/name
 if any(c['source']==name for c in pres['map_changes']):assert sha(snapshot)==digest
receipt=read(P/'integration-v1/database-preservation.json');assert receipt['passed'] and len(receipt['tables'])==9 and all(v['all_old_rows_preserved'] for v in receipt['tables'].values())
manifest=read(R/'catalogue/manifest.json');entry=next(x for x in manifest['models'] if x['id']=='hvwe2016-reconciled-fixed-local');assert entry['path_laboratory']=='index.html' and not entry.get('timed_laboratory')
result={'passed':True,'release_root':str(R),'base':base,'frozen_integration_files':len(freeze['files']),'scientific_source_closure':len(q['binding']['source_closure']),'exact_E5_record':freeze['E5_record_sha256'],'old_catalogue_and_approval_entries_preserved':True,'old_controller_hooks_preserved':True,'old_workflow_lines_preserved':True,'checked_changed_receipt_pairs':checked,'base_preimages_verified':len(pres['source_preimages']),'database_preservation_saved_receipt':receipt,'no_build_or_compiled_material_browser_remote_calls':True}
(OUT/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='database_preservation_saved_receipt'})
