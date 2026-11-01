from pathlib import Path
import hashlib,json,sys,subprocess
r=Path('/private/tmp/atlas-occ-release-v1');site=Path('/private/tmp/atlas-occ-release-v1-site');d=r/'docs/ingestion/original-cam-clay/finish-checklist-v1/release-host-fixes-v1';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files={str(p.relative_to(site)):h(p) for p in sorted(site.rglob('*')) if p.is_file()}; source={}
for p in (r/'web').iterdir():
 if p.is_file() and (site/p.name).is_file():source[str(p.relative_to(r))]={'source':h(p),'packaged':h(site/p.name)}
assert all(v['source']==v['packaged'] for v in source.values())
for n in ['atlas.js','atlas.wasm']:assert h(site/n)==h(Path('/private/tmp/atlas-occ-integration-v1/build-wasm')/n)
# User-facing catalogue corrections alter catalogue.json, not immutable generated metadata identity.
assert h(site/'models.json')==h(Path('/private/tmp/atlas-occ-integration-v1/build-wasm/generated/models.json'))
assert not [p for p in site.rglob('*') if p.is_file() and (p.suffix.lower()=='.pdf' or '.local' in p.parts or '__pycache__' in p.parts)]
(d/'final-package-manifest.json').write_text(json.dumps({'package_path':str(site),'files':files,'web_source_equality':source,'model_sha256':h(r/'models/original-cam-clay-sw-electronic-log-recovery-v1.json'),'review_sha256':h(r/'catalogue/agent-reviews/original-cam-clay-sw-electronic-log-recovery-agent-v1.json'),'catalogue_hash':json.loads((site/'models.json').read_text())['sha256']},indent=2)+'\n')
# Actual browser inventory observed these local resource URLs; bind their exact served files.
observed=['app.js','style.css','laboratory-support.mjs','models.json','catalogue.json','evidence.json','worker.js','laboratory-worker.mjs','atlas.js','experiments/index.json','laboratory-control-support.json','applicability.json']
(d/'browser-observed-assets.json').write_text(json.dumps({'origin':'http://127.0.0.1:18767','method':'IAB pageAssets.list observed fetched resource URLs after final reload; hashes bind dedicated loopback server files. Wasm indirectly confirmed by successful freshly reloaded worker/export catalogue and server GET; no browser-response-body digest API claimed.','assets':{p:files[p] for p in observed}},indent=2)+'\n')
print(len(files),'files; all available web source files and common Wasm/generated metadata identical')
