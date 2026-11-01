"""Hash and source-text checks only; no compilation/material execution."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];OLD=P.with_name('outer-reuse-v1')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=P/'freeze-v1.json';assert h(f)=='88357c5be26b54d44624f376eb90b72bfd2373fbfb7f87c59af9c7063d183e2b'
d=json.loads(f.read_text());assert len(d['files'])==75
for n,s in d['files'].items():assert h(P/n)==s,n
for n in ['model.json','POLICY.json','SUPPLEMENT_POLICY.json','triaxial-policy.json','triaxial-reference-results.json','check_wasm_source.py']:
 assert (P/n).read_bytes()==(OLD/n).read_bytes(),n
for n in ['check_domain_supplement.py','check_native_domain.py','check_native_legacy.py','check_native_lifecycle.py','check_native_triaxial.py','check_native_triaxial_fixed.py','check_wasm_bounded.mjs','check_wasm_chains_bounded.mjs','check_wasm.mjs','check_wasm_chains.mjs']:
 assert (P/n).read_text().replace('outer-predictor-v1','outer-reuse-v1')==(OLD/n).read_text(),n
r={'passed':True,'scope':'75-pin closure, model/reference/policy identity and unchanged scientific checker bodies; source review separate; no compiled execution','freeze_sha256':h(f),'files':d['files']}
(P/'independent-review/prospective-check-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='files'}))
