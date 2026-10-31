"""Freeze retained source literals and generic transport; never evaluate a material."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
PACKET=ROOT/'docs/ingestion/hypoplastic-clay-2005/compiled-plan-v3'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare():
 corpus=json.loads((PACKET/'corpus.json').read_text());model=json.loads((HERE/'model.json').read_text())
 assert sha(HERE/'model.json')==corpus['model_sha256']
 sources=set(p for p in PACKET.iterdir()if p.is_file())
 for pattern in ('atlas/*.py','schemas/*.json','cpp/include/atlas/*.hpp'):
  sources.update(ROOT.glob(pattern))
 sources.update(HERE/p for p in ('model.json','README.md','prepare.py','run_build.py','verify_study.py'))
 sources.update(ROOT/p for p in ('cmake/research-v3/CMakeLists.txt','tests/research_rate_driver_v3.cpp','tools/research_rate_observations_v3.py','tools/collect_research_rates_wasm_v3.mjs','tools/research_rate_parity_v3.py','docs/reviews/generic-rate-collection-v3/CONTRACT.md','docs/reviews/generic-rate-collection-v3/source-pins.json','docs/reviews/tagged-rate-transport-review-v3/manifest.json','docs/reviews/tagged-rate-transport-review-v3/observations-final.json'))
 return {'version':'research-instantaneous-rate-protocol-0.3','study':'clay2005-rates-v3','model_file':str((HERE/'model.json').relative_to(ROOT)),'model_definition':model,'files':{str(p.relative_to(ROOT)):sha(p)for p in sorted(sources)},'cases':corpus['cases'],'finite_only_parity':{'norm':'scaled_component_max','budget':corpus['parity_policy']['finite_only_scaled_budget']},'policy':{'source':corpus['source_policy'],'parity':corpus['parity_policy'],'counts':corpus['counts'],'failure':'Retain failures; do not refit or remove rows after compiled observation.','scope':'Instantaneous strain-path rates; no integration/tangent/admission/experimental claim.'}}
if __name__=='__main__':
 path=HERE/'protocol.json';text=json.dumps(prepare(),indent=2,allow_nan=False)+'\n'
 if '--check'in sys.argv:assert path.read_text()==text,'frozen assembly changed'
 else:
  assert not path.exists(),'fresh protocol required';path.write_text(text)
