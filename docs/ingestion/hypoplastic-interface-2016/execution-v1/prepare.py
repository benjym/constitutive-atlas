"""Freeze and copy actual common-engine inputs; no compiled execution."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
WORK=Path('/private/tmp/atlas-interface2016-delivery-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
names=set()
for rel,pattern in [('atlas','*.py'),('schemas','*.json'),('cpp/include/atlas','*.hpp'),('cpp/scalar-functions','*')]:
 names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/rel).rglob(pattern) if p.is_file() and '__pycache__' not in p.parts)
names.update(['cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/interface2016/hvwe2016-reconciled-fixed-local.json'])
files={n:sha(ROOT/n) for n in sorted(names)}
for n,h in files.items():
 target=WORK/'source'/n;target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert sha(target)==h,('refuse overwrite source',n)
 else:shutil.copyfile(ROOT/n,target)
 assert sha(target)==h and sha(ROOT/n)==h
cache=WORK/'em-cache'
if not cache.exists():shutil.copytree('/opt/homebrew/Cellar/emscripten/6.0.8/libexec/cache',cache)
plan={'model':'hvwe2016-reconciled-fixed-local','definition_sha256':files['models/research/interface2016/hvwe2016-reconciled-fixed-local.json'],'source_closure':files,'snapshot':str(WORK/'source'),'native_build':str(WORK/'native'),'wasm_build':str(WORK/'wasm'),'em_cache':str(cache),'target':'atlas_path_capability','parallel':1,'order':['native configure','native target build','native requests and check','wasm configure','wasm target build','wasm requests and check','native/Wasm fullstate and observables parity'],'cases':{n:sha(ROOT/n) for n in ['docs/ingestion/hypoplastic-interface-2016/implementation-v1/policy.json','docs/ingestion/hypoplastic-interface-2016/implementation-v1/backend-requests.json','docs/ingestion/hypoplastic-interface-2016/implementation-v1/backend-expectations.json','docs/ingestion/hypoplastic-interface-2016/implementation-v1/references.json']},'transport_sources':{n:sha(ROOT/n) for n in ['docs/ingestion/norsand-1993/e2-v3/run_native_requests_v2.py','docs/ingestion/norsand-1993/e2-v3/run_wasm_requests_v2.mjs','docs/ingestion/hypoplastic-interface-2016/implementation-v1/check_backend_results.py']},'parity_scaled_absolute':1e-10,'state_scales':[100000]*4+[1],'observable_scales':[100000]*7+[1],'material_calls_observed':0,'status':'frozen preparation; no build or material execution'}
(OUT/'source-freeze.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'inputs':len(files),'snapshot':str(WORK/'source'),'definition_sha256':plan['definition_sha256'],'material_calls':0},indent=2))
