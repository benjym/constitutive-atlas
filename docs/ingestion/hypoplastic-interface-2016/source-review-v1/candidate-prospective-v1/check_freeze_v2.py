"""Read-only exact pre-build input checks."""
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016/implementation-v1';E=ROOT/'docs/ingestion/hypoplastic-interface-2016/execution-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
assert sha(P/'manifest.json')=='7747199d17a8a3d9e6b324dde8ce731054e316babd5482696a6cafa3ba194c3e'
m=read(P/'manifest.json')
for f in m['files']+[m['candidate']]:
 p=Path(f['path']);assert sha(p)==f['sha256'] and p.stat().st_size==f['bytes']
plan=read(E/'execution-plan-v2.json');freeze=read(E/'source-freeze-v2.json');snap=Path(freeze['snapshot'])
assert {k:v for k,v in plan.items() if k!='runner_sha256'}==freeze
assert plan['runner_sha256']==sha(E/'run_stage_v2.py')=='05783578394077f48f28ac8d929f40f9803cd039760dc86862fc9711153ae0aa'
assert plan['target']=='atlas_path_capability' and plan['parallel']==1
for p,h in freeze['source_closure'].items():assert sha(ROOT/p)==sha(snap/p)==h
for p,h in (freeze['cases']|freeze['transport_sources']).items():assert sha(ROOT/p)==h
for p in freeze['transport_sources']:assert 'check_backend_results.py' not in p
v1=read(E/'source-freeze.json')
assert v1['source_closure']==freeze['source_closure'] and v1['cases']==freeze['cases']
assert v1['parity_scaled_absolute']==freeze['parity_scaled_absolute']==1e-10
meta=read(P/'generated/path_catalogue.json');assert len(meta['models'])==1 and meta['models'][0]==read(P/'backend-requests.json')['metadata']
bindings={str(p.relative_to(ROOT)):sha(p) for p in [P/'manifest.json',P/'CONTRACT_CLARIFICATION.md',P/'check_backend_results_v2.py',P/'test_checker_v2.py',E/'source-freeze.json',E/'execution-plan.json',E/'run_stage.py',E/'source-freeze-v2.json',E/'execution-plan-v2.json',E/'run_stage_v2.py',E/'prepare.py']}
result=dict(accepted_for_bounded_serial_E4_launch=True,source_files_verified=len(freeze['source_closure']),evidence_and_transport_pins_verified=len(freeze['cases']|freeze['transport_sources']),implementation_manifest_members=len(m['files'])+1,unchanged_cases_thresholds_model_sources=True,only_V2_assessor_in_active_plan=True,model_count=1,source_snapshot=str(snap),native_Wasm_parity_scaled_bound=1e-10,reviewer_compiled_material_calls=0,bindings=bindings)
(OUT/'freeze-v2-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))
