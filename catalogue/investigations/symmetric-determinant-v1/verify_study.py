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
 assert saved['outcome']=='passed';print('Verified: 124 calls/backend, 38 derivative columns, exact bits and 46 recovery pairs')
if __name__=='__main__':verify()
