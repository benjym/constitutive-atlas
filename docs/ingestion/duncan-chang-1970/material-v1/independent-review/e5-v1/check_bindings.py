"""Read-only E5 evidence/model/schema integrity audit; no compiled execution."""
from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parent;M=P.parents[1];ROOT=M.parents[3];E=M/'execution-v2'
sys.path.insert(0,str(ROOT))
from atlas.model import load
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(E/'candidate.json')=='452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'
load(E/'candidate.json')
r=json.loads((E/'material-receipt.json').read_text())
for name,h in r['files'].items():assert sha(ROOT/name)==h,name
for name in ['native_artifact','js_artifact','wasm_artifact']:
 for key in ['build_path','retained_path']:
  p=Path(r[name][key]);p=p if p.is_absolute() else ROOT/p
  assert sha(p)==r[name]['sha256'],str(p)
pre=json.loads((M/'integration-preflight-v1/result.json').read_text())
for name,row in pre['generated'].items():
 p=M/'integration-preflight-v1/generated'/name;f=E/'frozen/generated'/name
 assert p.read_bytes()==f.read_bytes() and sha(p)==row['sha256']==row['qualified_sha256']
for name,h in pre['current_dependencies'].items():assert sha(ROOT/name)==h,name
generic=json.loads((ROOT/'docs/reviews/bounded-partition-retry-v1/independent-review/final-bindings.json').read_text())
assert generic['decision']=='accepted-bounded-generic-runtime' and not generic['blocking_findings']
for name,h in generic['files'].items():assert sha(ROOT/name)==h,name
complete=json.loads((E/'E4_COMPLETE.json').read_text())
for name,h in complete['files'].items():assert sha(ROOT/name)==h,name
print(json.dumps({'final_generic_bindings_checked':len(generic['files']),'e4_complete_bindings_checked':len(complete['files']),'pass':True,'candidate_schema_valid':True,'material_receipt_pins_checked':len(r['files']),'durable_and_build_artifact_hashes_checked':6,'current_generator_outputs_identical_to_qualified_closure':True,'current_dependency_hashes_checked':len(pre['current_dependencies']),'compiled_calls':0},indent=2))
