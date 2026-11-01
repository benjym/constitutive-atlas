"""Read-only functional review hash checks. Never runs compiled artifacts."""
import argparse,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--candidate-root',type=Path,default=ROOT);p.add_argument('--site',type=Path);a=p.parse_args()
m=json.loads((B/'manifest.json').read_text());s=json.loads((B/'source-bindings.json').read_text())
for path,h in m['evidence_sha256'].items():assert sha(ROOT/path)==h,path
for path,h in m['review_sha256'].items():assert sha(B/path)==h,path
for path,h in s['source_sha256'].items():assert sha(a.candidate_root/path)==h,path
if a.site:
 for path,h in s['package_sha256'].items():assert sha(a.site/path)==h,path
 assert not(a.site/'sls.html').exists()
base=ROOT/'docs/ingestion/sls-comsol63/main-atlas-v1/browser'
read=lambda n:json.loads((base/(n+'.json')).read_text())
assert read('default')==read('reset')==read('replayed')==read('final-v3-default')
print('PASS: finalv3 source/package/evidence/review hashes and exact actual-browser reset/replay; no engine execution.')
