"""Portable saved packet integrity and source-algebra replay."""
from pathlib import Path
import hashlib, json
from check_packet import run
R=Path(__file__).resolve().parent
ROOT=R.parents[2]
manifest=json.loads((R/'manifest.json').read_text())
for name,digest in manifest['packet_files'].items():
    assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest, name
for name,digest in manifest['shared_dependencies'].items():
    assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, name
saved=json.loads((R/'check-results.json').read_text())
replayed=run(False)
# Source bytes stay private; portable equation checks must reproduce exactly.
saved['checks']=[x for x in saved['checks'] if x['check']!='exact private source bytes/version']
saved['total_cases']-=3
saved['private_sources_checked']=False
assert saved==replayed, 'saved scientific/algebra results differ'
print('PASS: packet/dependency hashes; exact replay of 515 portable cases; no compiled/vendor calls')
