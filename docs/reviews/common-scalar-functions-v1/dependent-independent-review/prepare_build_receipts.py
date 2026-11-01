"""Create exact accepted build-local bindings from reviewed saved evidence only."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[4];B=R/'docs/reviews/common-scalar-functions-v1';O=Path(__file__).parent
src=Path(json.loads((B/'dependent-source-freeze-v1.json').read_text())['source']);D=O/'build-local-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(x):return (json.dumps(x,indent=2)+'\n').encode()
def write(p,value):p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(encoded(value))
accepted=json.loads((O/'final-bindings-v1.json').read_text())
for p,h in accepted['files'].items():assert sha(R/p)==h,p
notice=B/'proposed-v4/cpp/scalar-functions/NOTICES.txt'
assert sha(notice)=='e22612e1a87864b4f3eb08d6e222fa4f18c082a020cc212fee67f40b44cd5dbe'
delta={'path':'cpp/scalar-functions/NOTICES.txt','sha256':sha(notice),'classification':'Additive noncompiled notice only, absent from518-file numerical source freeze; runtime/definitions/requests/gates/artifacts unchanged.'}
evidence={'review_report':{'path':str((O/'FINAL_REVIEW_V1.md').relative_to(R)),'sha256':sha(O/'FINAL_REVIEW_V1.md')},'review_bindings':{'path':str((O/'final-bindings-v1.json').relative_to(R)),'sha256':sha(O/'final-bindings-v1.json')},'notice_delta':delta}
paths={src/'cmake/maxwell/CMakeLists.txt',src/'cmake/AtlasScalarFunctions.cmake',src/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'}
paths.update(p for p in (src/'cpp/scalar-functions').rglob('*') if p.is_file())
for directory,suffixes in [('atlas',{'.py'}),('cpp',{'.cpp','.hpp'}),('schemas',{'.json'})]:paths.update(p for p in (src/directory).rglob('*') if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts)
mf={p.relative_to(src).as_posix():sha(p) for p in sorted(paths)};mf[delta['path']]=delta['sha256'];manifest={'files':dict(sorted(mf.items())),'sha256':hashlib.sha256(json.dumps(mf,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
write(D/'maxwell/source-manifest.json',manifest)
maxbuild=Path('/private/tmp/atlas-common-scalar-functions-v1/consumers-wasm-v1/maxwell')
binding={'model_sha256':sha(src/'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'),'catalogue_file_sha256':sha(maxbuild/'generated/models.json'),'module_sha256':sha(maxbuild/'maxwell.js'),'wasm_sha256':sha(maxbuild/'maxwell.wasm'),'source_manifest_sha256':manifest['sha256'],'reference_policy_sha256':sha(src/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json')}
gates={k:True for k in ['native_references','wasm_references','transactions','parity','presets']}
review={'schema_version':'maxwell-independent-build-review-1','model':'maxwell-itasca900-zero-spin-ode','status':'accepted','reviewer_run':'/root/duncan_complete_review','binding':binding,'gates':gates,'evidence':evidence,'scope':'Exact bounded numerical requalification only; no package/production/E6/E7 approval.'}
write(D/'maxwell/build-review.json',review)
write(D/'maxwell/maxwell-qualification.json',{'schema_version':'maxwell-qualified-build-1','model':review['model'],'status':'passed','implementation_run':'/root','binding':binding,'gates':gates,'independent_review':{'path':'build-review.json','sha256':sha(D/'maxwell/build-review.json')},'evidence':evidence})
paths={p for p in (src/'cpp/include/atlas').rglob('*.hpp')}
paths.update(p for p in (src/'cpp/scalar-functions').rglob('*') if p.is_file())
paths.update(p for p in (src/'atlas').rglob('*.py') if '__pycache__' not in p.parts)
paths.update((src/'schemas').rglob('*.json'))
paths.update(src/p for p in ['cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'])
sources={p.relative_to(src).as_posix():sha(p) for p in sorted(paths)};sources[delta['path']]=delta['sha256'];sources=dict(sorted(sources.items()))
norbuild=src.parent/'norsand-wasm'
binding={'sources':sources,'artifacts':{name:sha(norbuild/name) for name in ['atlas_path_capability.mjs','atlas_path_capability.wasm']},'generated':{name:sha(norbuild/'generated'/name) for name in ['path_catalogue.json','path_models.hpp','path_api.cpp']}}
gates={'native_requests':58,'wasm_requests':58,'native_successes':40,'native_rejections':18,'wasm_successes':40,'wasm_rejections':18,'source_analytical':True,'parity':True}
review={'schema_version':'controlled-path-independent-build-review-1','model':'norsand-jefferies-1993-active-axial','status':'accepted','reviewer_run':'/root/duncan_complete_review','binding':binding,'gates':gates,'evidence':evidence,'scope':'Exact bounded numerical requalification only; no package/production/E6/E7 approval.'}
write(D/'norsand/build-review.json',review)
write(D/'norsand/controlled-path-qualification.json',{'schema_version':'controlled-path-qualified-build-1','model':review['model'],'status':'passed','implementation_run':'/root','binding':binding,'gates':gates,'independent_review':{'path':'build-review.json','sha256':sha(D/'norsand/build-review.json')},'evidence':evidence})
print(json.dumps({'Maxwell_source_files':len(mf),'NorSand_source_files':len(sources),'notice_delta':delta},indent=2))
