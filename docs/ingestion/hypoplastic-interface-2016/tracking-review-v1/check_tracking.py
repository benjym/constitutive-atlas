"""Pure saved tracking/archive closure check."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016';OUT=Path(__file__).parent
receipt=json.loads((P/'integration-v1/tracking-preservation-receipt.json').read_text());R=Path(receipt['isolated_release']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(R));from atlas.evidence import checked_receipt
pairs=0
for change in receipt['map_changes']:
 checked_receipt(R,change['document'],change['source'],change['source_sha256']);pairs+=1
 if change['old_map_archive']:
  path=R/change['old_map_archive'];assert sha(path)==Path(change['old_map_archive']).parts[2]
for name,digest in receipt['source_preimages'].items():
 snapshot=R/'catalogue/source-snapshots'/digest/name
 if snapshot.exists():assert sha(snapshot)==digest
oldfreeze=json.loads((P/'integration-v1/integration-source-freeze.json').read_text())
for name,digest in oldfreeze['files'].items():assert sha(R/name)==digest
q=json.loads((R/'docs/ingestion/hypoplastic-interface-2016/execution-v1/qualification.json').read_text())
for name,digest in q['binding']['source_closure'].items():assert sha(R/name)==digest
review=R/'catalogue/agent-reviews/hvwe2016-reconciled-fixed-local-agent-v1.json';assert sha(review)==oldfreeze['E5_record_sha256']
result={'passed':True,'tracking_receipt_sha256':sha(P/'integration-v1/tracking-preservation-receipt.json'),'checked_changed_receipt_pairs':pairs,'original_tracking_preimages':receipt['source_preimages'],'unchanged_integration_files':len(oldfreeze['files']),'unchanged_qualified_source_files':len(q['binding']['source_closure']),'unchanged_E5_sha256':sha(review),'package_browser_live_claim':False}
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
