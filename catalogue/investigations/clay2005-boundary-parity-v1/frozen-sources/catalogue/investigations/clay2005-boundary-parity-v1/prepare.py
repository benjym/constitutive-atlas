"""Freeze unchanged109case diagnostic; no material/reference evaluation."""
import copy,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'clay2005-rates-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prepare():
 original=json.loads((PRIOR/'protocol.json').read_text());protocol=copy.deepcopy(original)
 protocol.update(study='clay2005-boundary-parity-v1',model_file=str((HERE/'model.json').relative_to(ROOT)))
 names=[HERE/p for p in ('model.json','README.md','prepare.py','run_build.py','verify_study.py')]
 names += [PRIOR/p for p in ('protocol.json','comparison.json','prospective-freeze.json','diagnostic-notes-v1.json','manifest.json')]
 for p in names:protocol['files'][str(p.relative_to(ROOT))]=sha(p)
 assert (HERE/'model.json').read_bytes()==(PRIOR/'model.json').read_bytes()
 protocol['diagnostic']={'changed_factor':'CMAKE_CXX_FLAGS=-ffp-contract=off for native and Wasm','all109literal_cases_and_budgets_unchanged':True,'boundary_source_accuracy_claim':False}
 return protocol
if __name__=='__main__':
 p=HERE/'protocol.json';s=json.dumps(prepare(),indent=2,allow_nan=False)+'\n'
 if '--check'in sys.argv:assert p.read_text()==s,'frozen diagnostic protocol changed'
 else:
  assert not p.exists(),'fresh protocol required';p.write_text(s)
