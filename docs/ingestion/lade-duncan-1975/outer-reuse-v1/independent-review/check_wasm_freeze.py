"""Read-only supplemental/original closure and checker-diff audit."""
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent;B=D.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=B/'wasm-bounded-v1/freeze-v1.json'
assert sha(f)=='66849d59cfcc43c91fa2774c8bdfca8fd3d73b2a0f4515a4072f25f3bf5b555b'
s=json.loads(f.read_text())
for p,h in s['files'].items():assert sha(B/p)==h,p
original=json.loads((B/'freeze-v1.json').read_text())
for p,h in original['files'].items():assert sha(B/p)==h,p
for old,new,kind in [('check_wasm.mjs','check_wasm_bounded.mjs','literal'),('check_wasm_chains.mjs','check_wasm_chains_bounded.mjs','chains')]:
 text=(B/old).read_text();target=(B/new).read_text();expected="import {createBoundedModule} from './wasm-bounded-v1/runner.mjs';\n"+text
 expected=expected.replace("const {default:create}=await import(pathToFileURL(path.join(build,'lade-domain.mjs')));\nconst module=await create({wasmBinary:fs.readFileSync(path.join(build,'lade-domain.wasm'))});",f"const module=createBoundedModule(build,path.join(root,'.local/lade-outer-reuse-v1/wasm-bounded-{kind}'));")
 assert expected==target,new
h=B.parent/'hierarchical-seeds-v1/proposed-wasm-CMakeLists.txt';assert h.read_bytes()==(B/'wasm-bounded-v1/CMakeLists.txt').read_bytes()
out={'id':'REVIEW-lade-outer-wasm-bounded-closure-v1','supplement_freeze_sha256':sha(f),'verified_supplement_files':len(s['files']),'verified_unchanged_original_files':len(original['files']),'checker_changes':'module initialization only','historical_CMake_exact_copy':True,'compiled_execution':False,'Wasm_material_execution':False}
(D/'wasm-freeze-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
