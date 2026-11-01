"""Replay failed synthetic preflight; this does not pass the readiness gate."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
p=Path(__file__).resolve().parent;root=p.parents[2];sys.path.insert(0,str(root))
from atlas.evidence import checked_receipt
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
for n,h in read(p/'manifest.json')['files'].items():assert sha(p/n)==h,n
pin=p/'source-pins.json'
for n,h in read(pin)['sources'].items():assert sha(checked_receipt(root,pin.relative_to(root).as_posix(),n,h))==h,n
for f in (p/'frozen-web').glob('*.mjs'):assert sha(f)==read(pin)['sources']['web/'+f.name]
a,b=read(p/'mc-draft.json'),read(p/'prior-mc.json');assert {k for k in set(a)|set(b) if a.get(k)!=b.get(k)}<={'name','description','status'}
assert read(p/'generation.json')['exit_code']==0 and len(read(p/'catalogue.json')['models'])==12
ref=read(root/'docs/reviews/mc-browser-loading-paths-v1/source-input.json');contracts=read(p/'contracts.json');assert len(contracts)==14
for c,x in zip(contracts,ref['paths']):assert c['id']==x['id'] and c['specification']['loading']['controls_bits']==x['controls_bits']
claim=read(p/'claim.json');assert sha(root/claim['archived_path'])==claim['board_sha256']
with tempfile.TemporaryDirectory() as d:
 out=Path(d)/'replay.json';subprocess.run(['node',str(p/'check_consumer.mjs'),str(out)],check=True);assert read(out)==read(p/'consumer-results.json')
r=read(p/'consumer-results.json');assert not r['passed'] and len(r['false_passes'])==28 and r['negative_checks']==70 and r['constitutive_calls']==0
result=subprocess.run([sys.executable,'-B',str(p/'readiness.py')],capture_output=True,text=True);assert result.returncode==1
print('REPRODUCED FAILED PREFLIGHT: 14 synthetic paths/834 points,70 rejections,28 parser false passes. Readiness remains blocked; no material execution.')
