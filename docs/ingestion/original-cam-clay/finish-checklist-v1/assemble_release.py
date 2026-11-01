from pathlib import Path
import shutil,json
src=Path(__file__).resolve().parents[4];dst=Path('/private/tmp/atlas-occ-release-v1');mid='original-cam-clay-sw-electronic-log-recovery-v1'
def cp(p):
 a=src/p;b=dst/p;b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b)
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
packet='docs/ingestion/original-cam-clay'
shutil.copytree(src/packet,dst/packet,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
for p in [f'models/{mid}.json',f'docs/models/{mid}.md',f'catalogue/agent-reviews/{mid.replace("-v1","-agent-v1")}.json']:
 if (src/p).exists():cp(p)
cp('catalogue/agent-reviews/original-cam-clay-sw-electronic-log-recovery-agent-v1.json')
for p in ['catalogue/laboratory-control-support.json','catalogue/laboratory-package-policy.json','catalogue/laboratory-profile-policy.json','tests/test_occ_ingestion.py','tests/test_laboratory_support.mjs','tests/test_laboratory_profile_policy.mjs','tests/test_solver.cpp','tests/test_recorded.cpp','tests/test_historical_generation.py','tests/fixtures/current-thirteen-occ-v1.json','tools/laboratory_profile_policy.mjs','tools/test_wasm.mjs','tools/test_browser_loading.mjs','web/laboratory-support.mjs','protocols/gis2024-small-drained-thirteen-occ-v1.json']:
 cp(p)
# Merge only OCC rows; concurrent model assignments remain in their own checkout.
for f,key,identity in [('catalogue/manifest.json','models',mid),('catalogue/approved-models.json','models','original-cam-clay-sw-electronic-log-recovery-agent-v1')]:
 a=read(dst/f);b=read(src/f);rows=[x for x in b[key] if x.get('id')==identity or (f.endswith('approved-models.json') and x.get('model_id')==mid)];assert len(rows)==1
 a[key]=[x for x in a[key] if x.get('id')!=rows[0]['id']]+rows;write(dst/f,a)
f='catalogue/laboratory-examples.json';write(dst/f,read(src/f))
f='catalogue/applicability/kfs-development-v1.json';a=read(dst/f);b=read(src/f)
for k,v in b.items():
 if isinstance(v,list) and any(isinstance(x,dict) and mid in str(x.get('model_id',x.get('model',''))) for x in v):
  rows=[x for x in v if mid in str(x.get('model_id',x.get('model','')))];a[k]=a[k]+rows
write(dst/f,a)
# Use the qualified simplified-site UI, before unrelated timed-laboratory edits.
site=Path('/private/tmp/atlas-occ-current-site-v1/site')
for f in ['app.js','index.html']:shutil.copyfile(site/f,dst/'web'/f)
# Preserve HEAD's intentional page removal; add only generic OCC support/dossier packaging.
p=dst/'tools/build_web.py';s=p.read_text().replace("'laboratory-examples-view.mjs','formulation-view.mjs'","'laboratory-examples-view.mjs','laboratory-support.mjs','formulation-view.mjs'")
current=(src/'tools/build_web.py').read_text();start=current.index('    import hashlib\n    support=');end=current.index('    bundle_applicability(dest)',start);s=s.replace('    bundle_applicability(dest)',current[start:end]+'    bundle_applicability(dest)');p.write_text(s)
# Separate numerical covariance and recorded restart profiles in CI.
p=dst/'.github/workflows/verify.yml';s=p.read_text();s=s.replace('run: ctest --test-dir build --output-on-failure\n','run: |\n          ctest --test-dir build --output-on-failure -E atlas_recorded\n          ATLAS_NATIVE_FIXTURES=explicit-gis20-occ-restart-v4 ctest --test-dir build --output-on-failure -R "^atlas_recorded$"\n');s=s.replace('run: ctest --test-dir build --output-on-failure -E atlas_python\n','run: |\n          ctest --test-dir build --output-on-failure -E "atlas_python|atlas_recorded"\n          ATLAS_NATIVE_FIXTURES=explicit-gis20-occ-restart-v4 ctest --test-dir build --output-on-failure -R "^atlas_recorded$"\n');s=s.replace('ATLAS_NATIVE_FIXTURES: explicit-gis20-v2','ATLAS_NATIVE_FIXTURES: explicit-gis20-occ-v3');p.write_text(s)
# Preserve old browser sources through immutable existing archive mechanism.
mp='catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json';cp(mp)
for e in read(src/mp)['entries']:
 p=e['archived_path']
 if not (dst/p).exists():cp(p)
print('Prepared isolated OCC inputs; no compilation or staging')
