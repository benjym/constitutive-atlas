"""Read-only prepared-tree and adapter verification; never calls compiled artifacts."""
import ast,hashlib,importlib.util,json,sys
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[3];SOURCE=Path('/private/tmp/atlas-control-partition-support-v1/source')
sys.dont_write_bytecode=True
sys.path.insert(0,str(SOURCE))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
freeze=json.loads((D/'support-source-freeze-v3.json').read_text())
actual={p.relative_to(SOURCE).as_posix():sha(p)for p in SOURCE.rglob('*')if p.is_file()}
assert actual==freeze['files']
old=json.loads((ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v5/source-freeze.json').read_text())
assert len(old['source_files'])==582
assert all(actual[p]==h and sha(Path(old['source_directory'])/p)==h for p,h in old['source_files'].items())
selected=json.loads((D.parent/'qualification-support-v1/support-selection.json').read_text())['files']
not_equal=[p for p,v in selected.items()if actual[p]!=v['sha256']]
assert sorted(not_equal)==['cpp/include/atlas/solver.hpp','tests/test_j2_main_routing.mjs']
# Evaluate only source_manifest(), not bundle() or generated code.
spec=importlib.util.spec_from_file_location('isolated_maxwell_manifest',SOURCE/'tools/build_maxwell_laboratory.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
expected=json.loads((D/'patched-source-manifests.json').read_text())
assert m.source_manifest()==expected['profiles']['maxwell']
proof=json.loads((D/'adapter-proof.json').read_text());j=proof['j2'];restored=(D/j['adapter']).read_text();assert sha(D/j['adapter'])==j['adapter_sha256']
for item in reversed(j['replacements']):
 assert restored.count(item['replacement'])==1
 restored=restored.replace(item['replacement'],item['original'])
assert hashlib.sha256(restored.encode()).hexdigest()==j['source_sha256']
for p,h in proof['v1_exact_reuse'].items():assert sha(ROOT/p)==h and sha(D/'adapters'/Path(p).name)==h
for p in list(D.glob('*.py'))+list((D/'adapters').glob('*.py')):ast.parse(p.read_text())
assets=json.loads((D/'retained-assets.json').read_text())
assert not assets['gaps']
for profile in ['hill','lade']:
 for item in assets[profile]:assert sha(item['retained_path'])==item['sha256']
combination=json.loads((D/'j2-path-combination.json').read_text())
assert sha(D/'j2-paths-with-public-preset.json')==combination['output_sha256']
assert all(sha(SOURCE/p)==h for p,h in combination['inputs'].items())
paths=json.loads((SOURCE/'docs/ingestion/j2-linear-hardening/execution-v2/paths.json').read_text())+[json.loads((SOURCE/'docs/ingestion/j2-linear-hardening/delivery-v1/preset-references.json').read_text())]
assert paths==json.loads((D/'j2-paths-with-public-preset.json').read_text())
closure=json.loads((D/'semantic-closure.json').read_text())
assert len(closure['review_validator_results'])==9 and all(x['passed']for x in closure['review_validator_results'])
assert not closure['missing_bytes'] and all(x['passed']for x in closure['checked_receipt_results'])
report=dict(identity='isolated-generic-support-source-only-check-v2',passed=True,compiled_calls=0,builds=0,source_files=len(actual),original582_files_verified=True,selected_inputs=len(selected),selected_baseline_matches=len(selected)-len(not_equal),preserved_source_overrides=sorted(not_equal),current_routing_test_substitution_authorized=False,review_validators_passed=9,canonical_plan_targets=23,maxwell_manifest_sha256=m.source_manifest()['sha256'],norsand_manifest_sha256=expected['profiles']['norsand']['sha256'],direct_current_guard_failures=len(closure['current_raw_supporting_failures']),guarded_package_ready=False)
if (D/'manifest.json').exists():assert all(sha(D/p)==h for p,h in json.loads((D/'manifest.json').read_text()).items())
print(json.dumps(report,indent=2))
