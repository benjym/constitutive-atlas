"""Pure generation and source comparison; no compiled execution/network/subprocess."""
from pathlib import Path
import sys,json,hashlib,re
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
def deny(event,args):
 if event.startswith(('subprocess.','socket.','ctypes.')):raise RuntimeError('Process/network/native load forbidden')
sys.addaudithook(deny)
from atlas.compiler import generate
sha=lambda data:hashlib.sha256(data).hexdigest()
load=lambda p:json.loads(p.read_bytes())
base=ROOT/'docs/ingestion/manzari-dafalias-1997/delivery-v1'
row=load(base/'direct-profile-compatibility-implementation-v1/bindings.json')['interface2016']
changed={n:dict(qualified=h,current=sha((ROOT/n).read_bytes())) for n,h in row['source_files'].items() if sha((ROOT/n).read_bytes())!=h}
expected={'models/drucker-prager.json','models/hypoplastic-sand-igs97.json','models/hypoplastic-sand-vw96.json','models/linear-elastic.json','models/modified-cam-clay.json','tests/test_state_contract.py','tools/qualify_controlled_path_refresh.py'}
assert set(changed)==expected
out=OUT/'generated-interface2016';out.mkdir(exist_ok=False)
generate(out,[ROOT/'models/research/interface2016/hvwe2016-reconciled-fixed-local.json'])
generated={}
for n in ['path_api.cpp','path_models.hpp','path_catalogue.json']:
 actual=(out/n).read_bytes();reference=(base/'direct-profile-compatibility-v1/generated/interface2016'/n).read_bytes()
 assert actual==reference,n
 assert actual==(ROOT/'web/engines/current17-compatible/interface2016/generated'/n).read_bytes(),n
 generated[n]=sha(actual)
seen={};todo=[out/'path_api.cpp']
while todo:
 p=todo.pop()
 if p in seen:continue
 data=p.read_bytes();key=('generated/'+p.name) if p.is_relative_to(out) else p.relative_to(ROOT).as_posix()
 seen[p]=dict(path=key,sha256=sha(data))
 if p.is_relative_to(ROOT) and not p.is_relative_to(out):
  assert p.relative_to(ROOT).as_posix() in row['source_files'],str(p)
  assert row['source_files'][p.relative_to(ROOT).as_posix()]==sha(data),str(p)
 for target in re.findall(rb'^\s*#\s*include\s*"([^\"]+)"',data,re.M):
  n=target.decode();candidates=[p.parent/n,out/n,ROOT/'cpp/include'/n];found=next((x.resolve() for x in candidates if x.is_file()),None)
  assert found is not None,(str(p),n)
  todo.append(found)
assert not any(p.name=='solver.hpp' for p in seen)
compile_inputs={n:h for n,h in row['source_files'].items() if n.startswith(('cpp/','cmake/','models/research/interface2016/')) or n.startswith('tools/generate')}
assert all(sha((ROOT/n).read_bytes())==h for n,h in compile_inputs.items())
result=dict(identity='interface2016-baseline-five-source-equivalence-v1',source_only=True,compiled_calls=0,passed=True,reviewer_run='/root/md1997_upstream_merge_review',original_row_file='web/engines/current17-compatible/interface2016/source-compatibility.json',original_row_sha256=sha((ROOT/'web/engines/current17-compatible/interface2016/source-compatibility.json').read_bytes()),original_bindings_sha256=sha((base/'direct-profile-compatibility-implementation-v1/bindings.json').read_bytes()),changed_source_pins=changed,generated_exact=generated,transitive_quoted_include_closure=sorted(seen.values(),key=lambda x:x['path']),unchanged_compile_input_pins=compile_inputs,limitations=['Source-only equivalence: no new compilation or numerical/material execution.','System/standard-library includes retain prior toolchain evidence, not independently recompiled here.','Seven changed broad receipt pins do not enter selected interface generation or actual quoted C++ include closure.'])
(OUT/'interface-source-equivalence.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: 7 broad-only deltas, 3 exact generated files, '+str(len(seen))+' transitive quoted source files, '+str(len(compile_inputs))+' unchanged compile input pins')
