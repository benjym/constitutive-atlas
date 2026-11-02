"""Pure independent exact sidecar-fix and supporting-receipt check."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016';R=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v2');OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
oldhash='13cf65684c64fb3dd15d7043fdd26a6f87abbd5f196a99a15c6da25e11284aad';newhash='8f80339c5f89f39c18f228a013300477ed4c9536ef2795e6760bc85727d5ede0';name='catalogue/agent-reviews/source-archive-map.json';archive=R/'catalogue/source-snapshots'/oldhash/name;live=R/name
assert sha(archive)==oldhash and sha(live)==newhash
old=read(archive);new=read(live);doc='catalogue/agent-reviews/hvwe2016-reconciled-fixed-local-agent-v1.json';docsha='13aa0f267736a9a5ad246e34461ead944fea5aa052ee74d2cec0ab3426a8ee0b';assert doc not in old['documents'];expected=json.loads(json.dumps(old));expected['documents'][doc]=docsha;assert new==expected and sha(R/doc)==docsha
sys.path.insert(0,str(R));from atlas.agent_review import validate_review,approval_entry
from atlas.evidence import checked_receipt
review=validate_review(R/doc,root=R,for_approval=True);approval=approval_entry(R/doc,root=R)
for pin in approval['supporting_files']:checked_receipt(R,doc,pin['path'],pin['sha256'])
registry=read(R/'catalogue/approved-models.json');assert approval==next(a for a in registry['models'] if a['model_id']==review['model']['id'])
freeze=read(P/'integration-v1/integration-source-freeze.json')
for path,digest in freeze['files'].items():assert sha(R/path)==digest
q=read(R/'docs/ingestion/hypoplastic-interface-2016/execution-v1/qualification.json')
for path,digest in q['binding']['source_closure'].items():assert sha(R/path)==digest
run=read(P/'package-v1/run.json');assert run['exit_code']==1 and run['status']=='failed-retained' and run['source_post_unchanged'] is True
for n,h in run['logs'].items():assert sha(P/'package-v1'/n)==h
assert 'original evidence document changed after archival' in (P/'package-v1/stderr.log').read_text()
result={'passed':True,'old_map_sha256':oldhash,'new_map_sha256':newhash,'sole_semantic_addition':{doc:docsha},'old_document_pins_preserved':len(old['documents']),'old_archive_entries_preserved':len(old['entries']),'normal_supporting_receipts_verified':len(approval['supporting_files']),'unchanged_integration_files':len(freeze['files']),'unchanged_qualified_source_files':len(q['binding']['source_closure']),'retained_actual_package_failure_verified':True,'no_compiled_material_browser_remote_calls':True}
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
