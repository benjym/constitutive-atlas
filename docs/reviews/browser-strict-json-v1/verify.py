"""Verify the bounded parser repair and synthetic transport replay."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
p=Path(__file__).resolve().parent;r=p.parents[2];sys.path.insert(0,str(r))
from atlas.evidence import checked_receipt
read=lambda f:json.loads(f.read_text())
for n,h in read(p/'manifest.json')['files'].items():assert hashlib.sha256((r/n).read_bytes()).hexdigest()==h,n
for e in read(p/'archive.json')['edges']:checked_receipt(r,e['document'],e['original_path'],e['sha256'])
with tempfile.TemporaryDirectory() as d:
 out=Path(d)/'report.json'
 subprocess.run(['node',str(r/'docs/reviews/mc-current-contract-preflight-v2/live-check_consumer.mjs'),str(out)],check=True)
 assert read(out)==read(p/'current-mc-preflight.json')
x=read(p/'current-mc-preflight.json');assert x['passed'] and x['negative_checks']==98 and x['constitutive_calls']==0
print('Verified strict browser repair:14 synthetic paths/98 corruption rejections; historical receipt edges intact. No material execution.')
