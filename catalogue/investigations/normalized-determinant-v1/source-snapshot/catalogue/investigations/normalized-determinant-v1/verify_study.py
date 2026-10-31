"""Reproduce the frozen determinant study and validate all retained file hashes."""
import hashlib,json
from pathlib import Path
from assess import assess
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 manifest=json.loads((HERE/'manifest.json').read_text())
 for name,pin in manifest['files'].items():assert sha(HERE/name)==pin,name
 root=HERE.parents[2];freeze=json.loads((HERE/'prospective-freeze.json').read_text())
 for name,pin in freeze['files'].items():assert sha(HERE/'source-snapshot'/name)==pin,name
 actual=assess();saved=json.loads((HERE/'assessment.json').read_text());assert actual==saved
 assert saved['outcome']in('passed','failed');print(json.dumps({'outcome':saved['outcome'],'ordered_calls_per_backend':saved['ordered_calls_per_backend'],'derivative_columns':38,'rejection_recovery_pairs':saved['rejection_recovery_pairs'],'retained_assessment_identical':True}))
if __name__=='__main__':verify()
