"""Adversarial manufactured receipt checks; source-only and self-cleaning."""
from pathlib import Path
import tempfile,json,hashlib,sys
W=Path('/private/tmp/atlas-vibe2026-controlled-time-v1');O=Path(__file__).resolve().parent
sys.path.insert(0,str(W))
from atlas.evidence import checked_receipt
hash=lambda b:hashlib.sha256(b).hexdigest();checks=[]
with tempfile.TemporaryDirectory(prefix='resolver-review-',dir=O) as tmp:
 r=Path(tmp);doc='catalogue/agent-reviews/example.json';original='docs/source.md';raw=b'exact historical bytes\n';pin=hash(raw)
 p=r/doc;p.parent.mkdir(parents=True);p.write_text(json.dumps({'artifacts':[{'path':original,'sha256':pin}]}))
 live=r/original;live.parent.mkdir(parents=True);live.write_bytes(raw)
 archive='catalogue/source-snapshots/'+pin+'/'+original;a=r/archive;a.parent.mkdir(parents=True);a.write_bytes(raw)
 m=p.parent/'source-archive-map.json';mapping={'version':'immutable-source-archive-map-0.1','documents':{doc:hash(p.read_bytes())},'entries':[{'original_path':original,'sha256':pin,'archived_path':archive}]};m.write_text(json.dumps(mapping))
 assert checked_receipt(r,doc,original,pin)==a;checks.append('valid exact archive selected')
 def refused(label,func):
  try:func()
  except ValueError:checks.append(label);return
  raise AssertionError(label+' unexpectedly accepted')
 a.write_bytes(b'corrupt');refused('corrupt archive rejected despite correct live file',lambda:checked_receipt(r,doc,original,pin));a.unlink();refused('missing archive rejected despite correct live file',lambda:checked_receipt(r,doc,original,pin));a.write_bytes(raw)
 refused('wrong expected hash absent from original document rejected',lambda:checked_receipt(r,doc,original,'0'*64))
 before=p.read_bytes();p.write_bytes(before+b'\n');refused('altered original review document rejected',lambda:checked_receipt(r,doc,original,pin));p.write_bytes(before)
 mapping['documents'].clear();m.write_text(json.dumps(mapping));refused('unlisted new review receives no historical privilege',lambda:checked_receipt(r,doc,original,pin))
(O/'resolver-results.json').write_text(json.dumps(dict(checks=checks,count=len(checks),compiled_calls=0,cleanup='Manufactured temporary fixture removed after all checks; no evidence source was modified.'),indent=2)+'\n')
print('Resolver negative checks:',len(checks))
