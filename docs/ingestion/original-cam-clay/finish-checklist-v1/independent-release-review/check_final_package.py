"""Hash final package, source equality and existing browser/package evidence only."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
B=HERE.parent/'release-host-fixes-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bindings={}
def bind(p,digest=None):
    actual=sha(p)
    if digest is not None:assert actual==digest,str(p)
    bindings[str(p)]=actual
manifest_path=B/'final-package-manifest.json';bind(manifest_path)
m=json.loads(manifest_path.read_text());site=Path(m['package_path'])
assert len(m['files'])==838
assert {str(p.relative_to(site)) for p in site.rglob('*') if p.is_file()}==set(m['files'])
for name,digest in m['files'].items():bind(site/name,digest)
for name,comparison in m['web_source_equality'].items():
    assert comparison['source']==comparison['packaged']
    bind(ROOT/name,comparison['source']);bind(site/Path(name).name,comparison['packaged'])
for name,digest in [('atlas.js','108826ff7f6e796219b88c50a1eb7707dfa6c5f28dda25a9926de9e52c4e6cbc'),('atlas.wasm','1268a52764f2d7f7e9841999778d35b0cdfe275b20bfe0e2b3aa2b29168141cd'),('models.json','1e5e00c1ecd1739d13ea3f171894e87bd751f767ef75b114bddc906c4414b5d5')]:
    bind(site/name,digest)
    qualified=Path('/private/tmp/atlas-occ-integration-v1/build-wasm')
    bind(qualified/('generated/'+name if name=='models.json' else name),digest)
model=json.loads((site/'models.json').read_text())
assert model['sha256']==m['catalogue_hash']
assert len(model['models'])==13
asset_path=B/'browser-observed-assets.json';bind(asset_path)
assets=json.loads(asset_path.read_text())
for name,digest in assets['assets'].items():bind(site/name,digest)
support_path=B/'supported-package.json';bind(support_path)
s=json.loads(support_path.read_text());assert s['status']=='passed'
assert s['catalogue_hash']==model['sha256']
assert s['policy_sha256']==sha(ROOT/'catalogue/laboratory-package-policy.json')
assert len(s['ordinary'])==13 and len(s['named'])==1
positive=[x for x in s['ordinary'] if x['result']['ok']]
negative=[x for x in s['ordinary'] if not x['result']['ok']]
assert len(positive)==12 and len(negative)==1
assert negative[0]['id']=='research-hp-extracted-asbs-gis-2024-v03'
assert all(x['result']['ok'] for x in s['named'])
for name in ['browser-final.jpg','browser-response.jpg','canonical-exact-tests.json','canonical-exact-tests-v2.json']:
    bind(B/name)
exact=json.loads((B/'canonical-exact-tests-v2.json').read_text())
assert exact['returncode']==0 and 'Ran 31 tests' in exact['stderr'] and exact['stderr'].endswith('OK\n')
assert all(x.startswith('tests.') for x in exact['command'][4:-1])
result={'status':'pass','package_files':838,'source_equalities':len(m['web_source_equality']),'observed_asset_urls_bound_to_server_files':len(assets['assets']),'ordinary_successes':12,'retained_GIS_ordinary_failure':1,'named_successes':1,'canonical_exact_tests':31,'builds':0,'compiled_calls':0,'bindings':bindings}
(HERE/'final-package-check-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))
