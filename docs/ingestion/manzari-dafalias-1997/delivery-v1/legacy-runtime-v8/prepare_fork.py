"""Exact path/identity-only fork of accepted raw-link-v7; no artifact execution."""
import ast,difflib,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;P=D.parent;OLD=P/'raw-link-v7'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
replacements=[('resolution-study-v4','execution-v3'),('md1997-raw-transport-v7','md1997-legacy-raw-transport-v8'),('md1997-raw-link-runtime-binding-v7','md1997-legacy-runtime-binding-v8'),('md1997-raw-link-verification-v7','md1997-legacy-raw-verification-v8'),('md1997-raw-link-freeze-v7','md1997-legacy-runtime-freeze-v8'),('md1997-raw-link-structure-tests-v7','md1997-legacy-structure-tests-v8'),("'md'","'legacy-md'")]
proof=[];patches=[]
for name in ['frozen_logic.py','collect.py','run_bound.py','check_raw.py','check_freeze.py','test_structure.py']:
 original=(OLD/name).read_text();adapted=original;used=[]
 for old,new in replacements:
  count=adapted.count(old)
  if count:
   positions=[];start=0
   while True:
    at=adapted.find(old,start)
    if at<0:break
    positions.append(at);start=at+len(old)
   adapted=adapted.replace(old,new);used.append(dict(original=old,replacement=new,count=count,original_positions=positions))
 ast.parse(adapted);restored=adapted
 # Reverse indexed substitutions, distinguishing preexisting destination strings.
 for step in reversed(used):
  old,new=step['original'],step['replacement'];positions=[pos+i*(len(new)-len(old))for i,pos in enumerate(step['original_positions'])]
  for pos in reversed(positions):
   assert restored[pos:pos+len(new)]==new;restored=restored[:pos]+old+restored[pos+len(new):]
 assert restored==original,name
 (D/'originals').mkdir(exist_ok=True);(D/'originals'/name).write_text(original);(D/name).write_text(adapted)
 proof.append(dict(file=name,original_sha256=sha(OLD/name),retained_original_sha256=sha(D/'originals'/name),fork_sha256=sha(D/name),substitutions=used,forward_exact=True,reverse_exact=True))
 patches+=list(difflib.unified_diff(original.splitlines(True),adapted.splitlines(True),fromfile='raw-link-v7/'+name,tofile='legacy-runtime-v8/'+name))
(D/'fork.diff').write_text(''.join(patches))
inputs=json.loads((OLD/'inputs.json').read_text())
for directory in ['raw-link-v7','execution-v3','parity-v6']:
 manifest=P/directory/'manifest.json';inputs[directory+'/manifest.json']=sha(manifest)
 for name,h in json.loads(manifest.read_text()).items():
  path=(manifest.parent/name).resolve();relative=path.relative_to(P).as_posix();assert sha(path)==h
  inputs[relative]=h
# Original parity reads the byte-identical v1 plan.
inputs['execution-v1/requests.json']=sha(P/'execution-v1/requests.json')
for name,h in json.loads((P/'execution-v3/requests.json').read_text())['source_inputs'].items():assert sha(P/name)==h;inputs[name]=h
(D/'inputs.json').write_text(json.dumps(inputs,indent=2,sort_keys=True)+'\n')
(D/'fork-proof.json').write_text(json.dumps(dict(identity='legacy-runtime-v8-path-identity-fork-proof',accepted_original_manifest_sha256=sha(OLD/'manifest.json'),files=proof,allowed_changes='Literal original MD module path; study/transport/binding/check/freeze identity labels only. All data/algorithms/branches/calls/error gates retained.',compiled_calls=0),indent=2)+'\n')
print(json.dumps(dict(files=len(proof),input_pins=len(inputs),original_harnesses_byte_identical=sha(P/'execution-v3/run_native.py')==sha(P/'resolution-study-v4/run_native.py'))))
