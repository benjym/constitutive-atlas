"""Independent saved-evidence closure; no network, builds or compiled calls."""
from pathlib import Path
import hashlib,json,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];P=ROOT/'docs/ingestion/hill-abaqus2025/delivery-v1/live-v1';REV='3873a48b256ed37cbc78378ee6b41d73139676f8'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
run=read(P/'run-identity.json');assert run['headSha']==REV and run['databaseId']==41343952906 and run['status']=='completed' and run['conclusion']=='success'
ci=read(P/'ci-terminal.json');assert ci['status']=='completed' and ci['conclusion']=='success'
assert len(ci['jobs'])==6 and all(j['conclusion']=='success' for j in ci['jobs'])
assert ci['url'].endswith('/41343952906')
u=read(P/'tested-upload-receipt.json');assert u['revision']==REV and u['run']==41343952906
assert sha(Path(u['private_local_tar']).read_bytes())==u['sha256']
actual=Path(u['extracted_path'])
for path in ['web/app.js','web/hill-contract.mjs','web/hill-laboratory.mjs']:
 assert (actual/Path(path).name).read_bytes()==subprocess.check_output(['git','show',REV+':'+path],cwd=ROOT)
assert read(actual/'catalogue.json')==json.loads(subprocess.check_output(['git','show',REV+':catalogue/manifest.json'],cwd=ROOT))
assets=read(P/'asset-comparison.json');assert assets['revision']==REV and assets['all_exact'] and assets['complete']
assert len(assets['assets'])==26
for a in assets['assets']:
 assert a['status']==200 and a['exact']
 assert a['expected_sha256']==a['live_sha256']==sha((actual/a['path']).read_bytes())
manifest=read(actual/'material-point-hill/package-manifest.json');assert len(manifest)==15
for p,h in manifest.items():assert sha((actual/p).read_bytes())==h
assert manifest==read(ROOT/'docs/ingestion/hill-abaqus2025/review-v1/catalogue-route-fix-v1/closure-v1/package-manifest.json')
b=read(P/'browser-result.json');assert len(b['checks'])==28 and all(v is True for v in b['checks'].values())
assert b['url']=='https://benjym.github.io/constitutive-atlas/index.html#laboratory?model=hill-abaqus2025-perfect-be'
assert not b['page_errors'] and not b['console_errors'] and not b['request_failures']
assert b['identity']==read(actual/'material-point-hill/identity.json')
raw=(P/'browser-raw.txt').read_text();assert json.loads(raw.split('### Result\n',1)[1].split('\n### Ran Playwright code',1)[0])==b
s=(P/'browser-script.js').read_text();assert s.index("page.on('pageerror'")<s.index("page.goto('https://")
assert read(OUT/'independent-export-results.json')['state_comparisons']==119
assert not subprocess.check_output(['git','diff','--name-only',REV,'ec47f3e47b41d01a51c0cd1ef0bfecb344def694','--','web','tools','.github','models','catalogue/manifest.json','catalogue/approved-models.json'],cwd=ROOT).strip()
bindings={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in P.iterdir() if p.is_file()}
for p in [ROOT/'docs/ingestion/hill-abaqus2025/source-v1/check_algebra.py',ROOT/'docs/ingestion/hill-abaqus2025/delivery-v1/catalogue-route-fix-v1/browser-v6/check_saved_exports.py']:
 bindings[str(p.relative_to(ROOT))]=sha(p.read_bytes())
result=dict(accepted=True,E8='closed for observed exact release and bounded approved scope',revision=REV,run=41343952906,ci_jobs_passed=6,live_assets_exact=26,strict_Hill_manifest_files=15,live_browser_checks=28,independent_state_comparisons=119,compiled_calls_by_reviewer=0,unchanged_concurrent_production=True,bindings=bindings)
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))
