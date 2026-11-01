"""Pure installed profile/source/compiler/artifact check; no compiled calls."""
from pathlib import Path
import hashlib,json,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[5]
sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
from tools.generate_implicit_path import regenerate
from tools.build_implicit_path_laboratory import runtime_manifest
A=ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1';F=ROOT/'docs/ingestion/lade-duncan-1975/fused-linear-v1'
read=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=read(A/'EXPECTED_F_BINDING.json');installed=read(A/'profile-install-v1/coordinator-install-v1/INSTALLED.json');plan=read(A/'profile-install-v1/revision-v2/PLAN.json')
assert installed['status']=='passed' and installed['old_binding_checks']==218 and len(installed['writes'])==26
assert installed['runtime']==runtime_manifest()==expected['expected_runtime']
for name,pin in expected['expected_runtime']['files'].items():assert sha(ROOT/'cpp/profiles/implicit-path-v1'/name)==pin
for row in plan['combined_overlay_checks']:checked_receipt(ROOT,row['document'],row['original_path'],row['old_sha256'])
for row in read(F/'legacy-prerequisite-recovery-v1/RECOVERY.json')['records']:assert sha(ROOT/row['original_path'])==row['current_full_sha256']
generated=regenerate(OUT/'generated')
assert generated['outputs']==expected['binding']['generated'] and generated['ordered_inputs']==expected['binding']['ordered_inputs']
model=ROOT/expected['binding']['ordered_inputs'][0]['path'];assert sha(model)==expected['binding']['model_sha256']
review=read(F/'independent-review/qualified-build-v1/build-review.json');qualification=read(A/'qualified-assets-v1/implicit-path-qualification.json')
assert review['binding']==qualification['binding']==expected['binding'] and review['gates']==qualification['gates'] and len(review['gates'])==11 and all(x is True for x in review['gates'].values())
assert review['status']=='accepted' and review['reviewer_run']=='/root/lade_source_review' and review['reviewer_run']!=qualification['implementation_run']
for name,key in [('lade-domain.mjs','module_sha256'),('lade-domain.wasm','wasm_sha256')]:assert sha(ROOT/'.local/lade-fused-linear-v1/wasm-build'/name)==expected['binding'][key]
source=ROOT/'.local/private-sources/lade-duncan-1975/original-1975-supplied.pdf';assert sha(source)=='bdebd928dbe9e4bac47c0a0328ed0bab79ab3e440a25390f1d646e9ed3749fc5'
result={'passed':True,'runtime_files':29,'runtime_sha256':runtime_manifest()['sha256'],'old_binding_checks':218,'current_full_raws':57,'normal_compiler_generated':generated,'binding':expected['binding'],'source_pdf_sha256':sha(source),'scope':'Pure installed/source/compiler identity check; no compiled/material, actual provisioning/browser or remote calls'}
(OUT/'binding-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'runtime_sha256':runtime_manifest()['sha256'],'old_bindings':218}))
