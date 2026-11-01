"""Read-only exact prospective-plan binding audit; no collection mains."""
import json,hashlib
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';A=C/'native-decimal-ci-dispatch-plan-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,b):
 if not b:raise RuntimeError(n)
 checks.append(n)
ck('exact author manifest',sha(A/'manifest.json')=='15348d2183e2f4d14d4a32d1102397ad3d44a3cb1ae33b2a055f4647396bc952')
for n,v in read(A/'manifest.json')['files'].items():ck('author file '+n,sha(A/n)==v)
pins=read(A/'inputs.json')
for n,v in pins['files'].items():ck('input '+n,sha(Path(n))==v)
print(json.dumps({'identity':'independent-native-decimal-ci-plan-bindings-v1','checks':len(checks),'check_names':checks,'builds':0,'compiled_calls':0},indent=2))
