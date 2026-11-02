"""Read/hash local source and retained assets only; never import repository code or provision."""
from pathlib import Path
import gzip, hashlib, io, json, stat, zipfile
R=Path('/private/tmp/atlas-bingham-release-v3')
OLD=Path('/private/tmp/atlas-bingham-release-v2')
OUT=Path(__file__).resolve().parent
D=R/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1'
def sha(b): return hashlib.sha256(b).hexdigest()
def encode(x): return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()
def save(n,x): (OUT/n).write_bytes(encode(x))
def gz(n,x): (OUT/n).write_bytes(gzip.compress(encode(x),mtime=0))
def info(p):
    if not p.is_file(): return {'path':str(p),'present':False}
    assert not p.is_symlink(),str(p)
    return {'path':str(p),'present':True,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
groups={
'wasm-dir':['atlas.js','atlas.wasm','generated/models.json'],
'burgers-wasm-dir':['burgers.mjs','burgers.wasm','generated/models.json'],
'hill-wasm-dir':['hill.js','hill.wasm','generated/models.json'],
'j2-wasm-dir':['j2.js','j2.wasm','generated/models.json'],
'kelvin-voigt-wasm-dir':['kv.mjs','kv.wasm','generated/models.json'],
'orthotropic-wasm-dir':['orthotropic.js','orthotropic.wasm','generated/models.json'],
'power-creep-wasm-dir':['power-creep.js','power-creep.wasm','power-creep-generated/models.json'],
'sls-wasm-dir':['sls.mjs','sls.wasm','generated/models.json']}
allowed=[]
for group,names in sorted(groups.items()):
 for n in names:
    p=OLD/'.local/current-prior-engines'/group/n
    assert p.is_file() and not any(q.is_symlink() for q in [p,*p.parents])
    allowed.append(dict(flag='--'+group,source=str(p),destination='.local/e7-qualified-assets/'+group+'/'+n,bytes=p.stat().st_size,sha256=sha(p.read_bytes())))
assert len(allowed)==24
save('ASSET-COPY-ALLOWLIST.json',{'identity':'bingham-e7-retained-assets-v3','scope':'Copy plan only; not permission to skip current package guards/material qualification. Never overwrite existing destinations.','files':allowed})
archives=[]
for indexrel,archive_name,base in [
 ('asset-provision-v1/INDEX.json','qualified-assets.zip',None),
 ('current-engine-equivalence-v1/qualified-packaging-v1/INDEX.json','qualified-engines.zip',OLD/'.local/current-prior-engines-v2')]:
 p=R/'docs/ingestion/bingham-comsol63'/indexrel; idx=json.loads(p.read_bytes()); archive=p.parent/archive_name
 rows=[]
 with zipfile.ZipFile(io.BytesIO(archive.read_bytes())) as z:
  zi=z.infolist(); assert len(zi)==len(idx['files']) and {x.filename for x in zi}==set(idx['files'])
  for m in zi:
   assert not m.is_dir() and not Path(m.filename).is_absolute() and '..' not in Path(m.filename).parts
   assert stat.S_IFMT(m.external_attr>>16)!=stat.S_IFLNK
   b=z.read(m); assert sha(b)==idx['files'][m.filename]
   if base: assert (base/m.filename).read_bytes()==b
   rows.append(dict(path=m.filename,sha256=sha(b),bytes=len(b)))
 expected=idx['archive']['sha256'] if isinstance(idx['archive'],dict) else idx['archive_sha256']
 assert sha(archive.read_bytes())==expected
 archives.append(dict(index=info(p),archive=info(archive),members=sorted(rows,key=lambda x:x['path']),compared_to_retained_directory=bool(base)))
save('ARCHIVES.json',archives)
imports={}
for name in ['current-engine-equivalence-v1','current-engine-equivalence-review-v1','current-dependency-provision-v1','current-dependency-provision-review-v1']:
 root=R/'docs/ingestion/bingham-comsol63'/name
 imports[name]=[info(p) for p in sorted(root.rglob('*')) if p.is_file()]
gz('imported-dependency-context.json.gz',imports)
composition=json.loads((D/'COMPOSITION.json').read_bytes())
selected=[]
for name,expected in composition['candidate_files'].items():
 p=D/'candidates'/name; assert sha(p.read_bytes())==expected
 selected.append(dict(relative=name,candidate=info(p),current=info(R/name)))
save('SELECTED-CANDIDATES.json',selected)
refs=['tools/build_web.py','tools/build_evidence.py','tools/build_experiments.py','tools/build_ensemble_web.py','tools/build_database.py','atlas/public_data.py','atlas/agent_review.py','atlas/evidence.py','tools/build_controlled_path_web.py','tools/build_maxwell_laboratory.py','tools/build_implicit_path_laboratory.py','tools/provision_implicit_path_assets.py','tools/provision_maxwell_assets.py','tools/test_supported_package.mjs','tools/test_experiments.mjs','tools/test_ensemble_wasm.mjs','tools/test_implicit_path_public_presets.mjs','tools/check_model_profiles.mjs','.github/workflows/verify.yml','CMakeLists.txt','data/curated/index.json','data/sources.json','data/public_sources.json','data/experiment_releases.json','docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/MANIFEST.json','docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/COMPOSITION.json','docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/baseline-public-records.json','docs/ingestion/bingham-comsol63/execution-v1/build-receipt.json','docs/ingestion/bingham-comsol63/source-v1/source-receipts.json','docs/ingestion/bingham-comsol63/interface-v3/POLICY.json','catalogue/agent-reviews/bingham-comsol63-agent-v1.json','models/research/bingham/bingham-comsol63-mises-perfect-zero-spin-ode.json']
for n in ['sls_laboratory','burgers_web','kelvin_voigt_laboratory','power_creep_web','orthotropic_laboratory','j2_laboratory','hill_laboratory']:refs.append('tools/build_'+n+'.py')
lade='docs/ingestion/lade-duncan-1975/atlas-integration-v1/'
for n in ['asset-provision-v1/INDEX.json','asset-provision-v1/compiled-assets-v1.tar.gz','maxwell-unit-alias-v1/compiled-closure-v1.tar.gz','maxwell-unit-alias-v1/maxwell-qualification.json','maxwell-unit-alias-v1/independent-review/build-review.json','live-release-v1/restore_interface_request.py','live-release-v1/interface-request.json']:refs.append(lade+n)
refs+=['tools/generate_implicit_path.py', 'models/research/implicit-path/lade-duncan-1975-midpoint-elastic-eq19-gap-v4.json', 'tests/fixtures/implicit-path-v1/baseline-v2.json', 'tests/fixtures/implicit-path-v1/hypoplastic-sand-vw96.json', 'tests/fixtures/implicit-path-v1/linear-elastic.json', 'catalogue/agent-reviews/lade-duncan-1975-midpoint-elastic-eq19-gap-v4-agent-v1.json', 'docs/ingestion/bingham-comsol63/execution-v1/cases.json']
refs+=['web/assets/'+n+'.webp' for n in ['constitutive-cover','home-laboratory','home-catalogue','home-methods']]
refs+=['docs/benchmarks/kfs-tmd2-research-range-v1/results/reproduction.png']
save('SOURCE-REFS.json',[info(R/n) for n in sorted(set(refs))])
existing_context={}
for name in ['asset-provision-v1','maxwell-unit-alias-v1']:
 root=R/lade/name; existing_context[name]=[info(p) for p in sorted(root.rglob('*')) if p.is_file()]
gz('current-main-provision-context.json.gz',existing_context)
control=R/lade/'live-release-v1/qualified-norsand-unit-alias-v1'
controlrows=[info(p) for p in sorted(control.rglob('*')) if p.is_file()]
save('CURRENT-CONTROLLED-PATH.json',{'selected_path':str(control.relative_to(R)),'files':controlrows,'binary_and_generated_match_retained_v2':all((control/n).read_bytes()==(OLD/'.local/current-prior-engines-v2/norsand'/n).read_bytes() for n in ['atlas_path_capability.mjs','atlas_path_capability.wasm','generated/path_api.cpp','generated/path_catalogue.json','generated/path_models.hpp']),'qualification_and_review_are_distinct':all((control/n).read_bytes()!=(OLD/'.local/current-prior-engines-v2/norsand'/n).read_bytes() for n in ['controlled-path-qualification.json','build-review.json'])})
cur=json.loads((R/'data/curated/index.json').read_bytes())['records']; curated=[]
for rec in cur:
 p=R/'data/curated'/rec['path']; assert p.is_file() and sha(p.read_bytes())==rec['sha256']
 curated.append(info(p))
gz('curated-inventory.json.gz',curated)
baseline=json.loads((D/'baseline-public-records.json').read_bytes())
ordinary=OLD/'.local/current-prior-engines/wasm-dir/generated/models.json'
assert sha(ordinary.read_bytes())==baseline['ordinary_catalogue_sha256']
# Reproduce only source enumeration/hash logic, without importing or running bundle guards.
paths={R/'cmake/maxwell/CMakeLists.txt',R/'cmake/AtlasScalarFunctions.cmake',R/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'}
paths.update(p for p in (R/'cpp/scalar-functions').rglob('*') if p.is_file())
for directory,suffixes in [('atlas',{'.py'}),('cpp',{'.cpp','.hpp'}),('schemas',{'.json'})]:
 paths.update(p for p in (R/directory).rglob('*') if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts)
maxfiles={p.relative_to(R).as_posix():sha(p.read_bytes()) for p in sorted(paths)}
maxhash=sha(json.dumps(maxfiles,sort_keys=True,separators=(',',':')).encode())
maxq=json.loads((OLD/'.local/current-prior-engines-v2/maxwell/maxwell-qualification.json').read_bytes())
assert maxhash==maxq['binding']['source_manifest_sha256']
norq=json.loads((control/'controlled-path-qualification.json').read_bytes())
norfiles=norq['binding']['sources']
required={p.relative_to(R).as_posix() for p in (R/'cpp/include/atlas').rglob('*.hpp')}
required.update(p.relative_to(R).as_posix() for p in (R/'cpp/scalar-functions').rglob('*') if p.is_file())
required.update(p.relative_to(R).as_posix() for p in (R/'atlas').rglob('*.py') if '__pycache__' not in p.parts)
required.update(p.relative_to(R).as_posix() for p in (R/'schemas').rglob('*.json'))
required.update(('cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'))
assert set(norfiles)==required and all(sha((R/n).read_bytes())==h for n,h in norfiles.items())
implicit=[p for p in (R/'cpp/profiles/implicit-path-v1').rglob('*') if p.is_file()]
gz('guard-source-context.json.gz',{'scope':'Source enumeration/hash comparison only, not guard execution or material qualification','maxwell':maxfiles,'norsand':norfiles,'implicit_profile':[info(p) for p in sorted(implicit)]})
reviewpath=R/'catalogue/agent-reviews/bingham-comsol63-agent-v1.json'
review=json.loads(reviewpath.read_bytes()) if reviewpath.is_file() else None
pins={v['path']:v['sha256'] for v in review['artifacts']} if review else {}
assetpins={}
for a in archives:
 for role in ['index','archive']:
  v=a[role]; relative=str(Path(v['path']).relative_to(R)); assetpins[relative]=dict(actual_sha256=v['sha256'],review_pin=pins.get(relative),equal=v['sha256']==pins.get(relative))
registered=[x for x in json.loads((R/'catalogue/approved-models.json').read_bytes())['models'] if x.get('model_id')=='bingham-comsol63-mises-perfect-zero-spin-ode']
save('ADMISSION-SNAPSHOT.json',{'scope':'Read-only point-in-time observation, not validate_review or approval decision','review':info(reviewpath),'review_status':review.get('status') if review else None,'review_artifact_count':len(pins),'archive_index_pins':assetpins,'registry_matches':len(registered),'registry':info(R/'catalogue/approved-models.json')})
summary={'task':'PREP-bingham-package-inputs-v3','source_only':True,'compiled_calls':0,'provision_calls':0,'shared_edits':0,'maxwell_enumerated_source_files':len(maxfiles),'maxwell_source_manifest_sha256':maxhash,'norsand_pinned_source_files':len(norfiles),'source_hash_comparisons_match':True,'allowed_asset_files':len(allowed),'allowed_asset_groups':len(groups),'allowed_asset_bytes':sum(x['bytes'] for x in allowed),'imported_dependency_files':sum(map(len,imports.values())),'archive_members':[len(x['members']) for x in archives],'selected_candidate_files':len(selected),'candidate_currently_absent':sum(not x['current']['present'] for x in selected),'curated_records':len(curated),'release_grants':len(json.loads((R/'data/experiment_releases.json').read_bytes())['grants']),'ordinary_count':len(baseline['ordinary_catalogue']['models']),'ordinary_metadata_matches_current_baseline':True,'current_counts':baseline['counts'],'prospective_counts':composition['prospective_counts'],'canonical_e5_present':(R/'catalogue/agent-reviews/bingham-comsol63-agent-v1.json').is_file(),'final_complete_imported_tree_preservation_proven':False,'integration_or_scientific_approval_claimed':False}
save('SUMMARY.json',summary)
print(json.dumps(summary,indent=2))
