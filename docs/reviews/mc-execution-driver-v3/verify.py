from pathlib import Path
import hashlib,json
from execute import verify_inputs,P,C
freeze=verify_inputs()
manifest=json.loads((P/'audit/manifest.json').read_text())['files']
for n,h in manifest.items():assert hashlib.sha256((P/'audit'/n).read_bytes()).hexdigest()==h,n
assert freeze['compiled_calls_at_freeze']==0
print('Execution envelope verified: exact reviewed driver and collector bytes, source pins, compatibility baselines; numerical outcomes remain unproven.')
