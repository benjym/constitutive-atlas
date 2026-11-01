"""Source-only v3 authoring: identity, environment and receipt hardening only."""
if not __debug__: raise RuntimeError('Unoptimized Python is required')
from pathlib import Path
import json,hashlib,difflib
D=Path(__file__).resolve().parent;V=D.parent/'current-profile-execution-v2'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n')
repl=[('current-profile-execution-v2','current-profile-execution-v3'),('atlas-control-partition-profile-execution-v2','atlas-control-partition-profile-execution-v3')]
proof={}
for n in ['RECEIPTS.md','assess_pairs.py','assess_maxwell_presets.py','prepare_maxwell_identity.py','burgers-original-verify.py','collector-closure.json','source-checks.json']+[str(p.relative_to(V))for p in (V/'adapters').glob('*.py')]:
 t=(V/n).read_text()
 for a,b in repl:t=t.replace(a,b)
 out=D/n;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(t);r=t
 for a,b in reversed(repl):r=r.replace(b,a)
 assert r==(V/n).read_text();proof[n]=dict(old_sha256=sha(V/n),new_sha256=sha(out),reverse_exact=True)
p=read(V/'plan.json');t=json.dumps(p)
for a,b in repl:t=t.replace(a,b)
p=json.loads(t)
for row in p['profiles']:
 for st in row['steps']:st['env']['PYTHONOPTIMIZE']='0'
for st in p['post_independent_build_review_only']:st['env']['PYTHONOPTIMIZE']='0'
p['stage_receipts']['required']='pre and post every stage including failures; exact source/toolchain/environment/pre identity; post passed requires exit status zero; retain stdout/stderr and nonzero status before failure'
write(D/'plan.json',p)
r=json.loads(json.dumps(p));r['stage_receipts']['required']=read(V/'plan.json')['stage_receipts']['required']
for row in r['profiles']:
 for st in row['steps']:st['env'].pop('PYTHONOPTIMIZE')
for st in r['post_independent_build_review_only']:st['env'].pop('PYTHONOPTIMIZE')
t=json.dumps(r)
for a,b in reversed(repl):t=t.replace(b,a)
assert json.loads(t)==read(V/'plan.json')
tool=read(V/'toolchain.json');tool['identity']='profile-toolchain-source-freeze-v3';tool['environment']['PYTHONOPTIMIZE']='0';write(D/'toolchain.json',tool)
pins=read(V/'input-pins.json')
for q in [V/'manifest.json',D.parent/'current-profile-execution-review-v2/manifest.json',D.parent/'current-profile-execution-review-v2/RECEIPT-ADDENDUM.md']:pins[str(q)]=sha(q)
write(D/'input-pins.json',pins)
write(D/'rebind-proof.json',dict(old_manifest=sha(V/'manifest.json'),replacements=repl,files=proof,plan_restores_exact=True,allowed=['identity/paths','PYTHONOPTIMIZE=0','receipt pre/post/optimizer checks','precondition documentation']))
