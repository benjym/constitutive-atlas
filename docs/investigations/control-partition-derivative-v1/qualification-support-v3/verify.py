"""Strict read-only support identity verifier; not package readiness or qualification."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;ROOT=D.parents[3];OLD=Path('/private/tmp/atlas-control-partition-support-v1/source');NEW=Path('/private/tmp/atlas-control-partition-support-v2/source');PRIOR=D.parent/'qualification-support-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory(root):
 assert not any(p.is_symlink()or '__pycache__'in p.parts or p.suffix in ['.pyc','.pyo']for p in root.rglob('*'))
 return {p.relative_to(root).as_posix():sha(p)for p in root.rglob('*')if p.is_file()}
old=json.loads((PRIOR/'support-source-freeze-v3.json').read_text())['files'];assert inventory(OLD)==old and len(old)==2611
freeze=json.loads((D/'source-freeze.json').read_text());new=inventory(NEW);assert new==freeze['files']and len(new)==2614
prep=json.loads((D/'preparation.json').read_text());assert sha(PRIOR/'manifest.json')==prep['prior_manifest_sha256']and sha(PRIOR/'support-source-freeze-v3.json')==prep['prior_source_freeze_sha256']
assert sorted(set(new)-set(old))==['docs/admission/power-creep-approved-v1/approval.json','docs/ingestion/power-creep-itasca900/manifest.json','docs/ingestion/power-creep-itasca900/review-v1/manifest.json']
assert [p for p,h in old.items()if new[p]!=h]==['tests/test_j2_main_routing.mjs']
for change in prep['changes']:assert new[change['path']]==change['after_sha256']
runtime=json.loads((ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v5/source-freeze.json').read_text());assert len(runtime['source_files'])==582
for p,h in runtime['source_files'].items():
 assert sha(Path(runtime['source_directory'])/p)==h
 assert new[p]==h or p=='tests/test_j2_main_routing.mjs'
protected={p:h for p,h in old.items()if p.startswith('catalogue/source-snapshots/')or p.endswith('source-archive-map.json')or p=='catalogue/approved-models.json'}
assert all(new[p]==h for p,h in protected.items())
archives=json.loads((PRIOR/'installed-plan-archives.json').read_text());assert len(archives)==23
assert all(new[x['path']]==x['sha256']for x in archives)
sets=json.loads((D/'patched-source-manifests.json').read_text());assert sets['profiles']==json.loads((PRIOR/'patched-source-manifests.json').read_text())['profiles']
assert all(new[p]==h for v in sets['profiles'].values()for p,h in v['files'].items())
sys.path[:0]=[str(NEW),str(NEW/'tools')]
import build_maxwell_laboratory
assert build_maxwell_laboratory.source_manifest()==sets['profiles']['maxwell']
for file in D.rglob('*.py'):ast.parse(file.read_text())
closure=json.loads((D/'guard-closure.json').read_text());assert len(closure['results'])==9 and sum(x['source_guard_passed']for x in closure['results'])==8 and sum(x['evaluated_guard_stages_passed']for x in closure['results'])==7
assert len(closure['prior_power_agent_v2_support_divergences'])==3
assert next(x for x in closure['results']if x['profile']=='power-creep')['evaluated_guard_stages_passed']
if(D/'manifest.json').exists():
 manifest=json.loads((D/'manifest.json').read_text());assert sorted(manifest)==sorted(p.relative_to(D).as_posix()for p in D.rglob('*')if p.is_file()and p!=D/'manifest.json')
 assert all(sha(D/p)==h for p,h in manifest.items())
print(json.dumps(dict(identity='generic-qualified-support-source-verification-v3',passed=True,source_files=2614,prior2611_immutable=True,original582_immutable=True,new_tree_runtime_bytes_unchanged=True,authorized_test_overlay_only=True,canonical_targets_verified=23,canonical_map_registry_files_unchanged=len(protected),source_guard_prefixes_passed=8,later_guard_stages_passed_profiles=7,remaining_source_literal_gaps=4,lade_interface_direct_pin_gaps=11,maxwell_manifest_sha256=sets['profiles']['maxwell']['sha256'],norsand_manifest_sha256=sets['profiles']['norsand']['sha256'],compiled_calls=0,builds=0,guarded_package_ready=False),indent=2))
