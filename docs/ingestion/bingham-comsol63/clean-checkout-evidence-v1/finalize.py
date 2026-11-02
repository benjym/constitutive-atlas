"""Seal owned packet only; never install or mutate Git."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();save=lambda n,o:(H/n).write_text(json.dumps(o,indent=2)+'\n')
i=json.loads((H/'INSTALLATION.json').read_text());assert len(i['files'])==10
for n,v in i['files'].items():assert sha(R/n)==sha(H/v['candidate'])==v['sha256']
for n in ['INTEGRITY.json','PURE-TESTS.json','REGISTRY-PATHS.json','SUPPLEMENTARY-RECEIPTS.json','TRACKED-AFTER-TEN.json']:assert json.loads((H/n).read_text())['passed']
assert not json.loads((H/'TRACKED-BEFORE.json').read_text())['passed']
pins=['.gitignore','catalogue/approved-models.json','catalogue/agent-reviews/source-archive-map.json','catalogue/agent-reviews/bingham-comsol63-agent-v1.json','docs/ingestion/bingham-comsol63/execution-v1/build-receipt.json','docs/ingestion/bingham-comsol63/execution-v1/source-archive-map.json','docs/ingestion/bingham-comsol63/asset-provision-v1/qualified-assets.zip','docs/ingestion/bingham-comsol63/live-release-v1/CI-TERMINAL.json','docs/ingestion/bingham-comsol63/live-release-v1/FIRST-ATTEMPT-FAILED-STEPS.log','docs/ingestion/bingham-comsol63/live-release-v1/FAILURE-SUMMARY.json','atlas/evidence.py','atlas/agent_review.py','atlas/review_export.py','atlas/research.py','tools/build_evidence.py']
save('SOURCE-BINDINGS.json',{'baseline_commit':i['baseline_commit'],'files':{n:sha(R/n) for n in pins},'existing_tracked_identity_changes':0,'compiled_module_or_material_calls':0})
files={p.relative_to(H).as_posix():sha(p) for p in H.rglob('*') if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts};save('MANIFEST.json',{'identity':'bingham-clean-checkout-evidence-v1','status':'prospective-source-only-review-request','files':files,'installation_sha256':sha(H/'INSTALLATION.json'),'scope_split':{'active_export':7,'existing_mapped_asset_receipts':3},'independent_acceptance_claimed':False});print(json.dumps({'manifest_sha256':sha(H/'MANIFEST.json'),'files':len(files),'canonical_additions':len(i['files'])},indent=2))
