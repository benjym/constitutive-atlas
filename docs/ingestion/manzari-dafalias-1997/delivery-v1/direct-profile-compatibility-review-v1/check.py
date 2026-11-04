from pathlib import Path
import hashlib,json,sys,tarfile,re
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent;P=Q.parent/'direct-profile-compatibility-v1';R=Q.parents[4]
S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source');OLD=Path('/private/tmp/atlas-md1997-final-native-source-v1/source')
def h(x):return hashlib.sha256(x).hexdigest()
def read(p):return json.loads(p.read_bytes())
checks=0
def ck(x,label):
 global checks
 assert x,label
 checks+=1
m=read(P/'manifest.json');ck(h((P/'manifest.json').read_bytes())=='e156545f0e04bf9f9e29fa93afd99086444e2e94d53e7d9186952a5f686f6abf','subject')
for n,v in m['files'].items():ck(h((P/n).read_bytes())==v,n)
b=read(P/'proposed-bindings.json');r=read(P/'results.json')
ck(b['status']=='pending-independent-review' and b['actual_observations_performed'] is False,'honest proposal')
with tarfile.open(R/'.local/private-evidence/md1997-current-package-v7/complete-output.tar.gz') as t:
 nq=json.load(t.extractfile('site/engine-path/qualification.json'));mq=json.load(t.extractfile('site/engine-maxwell/qualification.json'));mm=json.load(t.extractfile('site/engine-maxwell/source-manifest.json'))
 for label,q in [('norsand',nq),('maxwell',mq)]:
  bp=b['profiles'][label];binding=bp['proposed_binding'];old=q['binding']
  ck(bp['prior_actual_gates_inherited_only'] is True and bp['new_actual_gates'] is False,'inherited gates')
  for k,v in old.items():
   if k not in ('sources','source_manifest_sha256'):ck(binding[k]==v,(label,k))
  inv=bp['complete_source_manifest'];ck(inv==r[label]['proposed_complete_current_sources'],'complete map')
  ck(h(json.dumps(inv,sort_keys=True,separators=(',',':')).encode())==bp['source_inventory_sha256'],'canonical inventory')
  for n,v in inv.items():ck(h((S/n).read_bytes())==v,n)
  oldmap=old['sources'] if label=='norsand' else mm['files']
  for n,v in oldmap.items():
   if n.startswith(('cpp/','cmake/','models/','tests/fixtures/','tools/generate')):ck(h((S/n).read_bytes())==v,('compile input',n))
# Preserve all four original formulation branches, not merely their count.
a=read(OLD/'schemas/model-v0.3.schema.json');z=read(S/'schemas/model-v0.3.schema.json');ck(a['oneOf']==z['oneOf'][:4] and len(z['oneOf'])==5,'schema branches')
# Only source generation below: no native library, subprocess, or network.
def deny(event,args):
 if event.startswith(('subprocess.','socket.','ctypes.')):raise RuntimeError(event)
sys.addaudithook(deny);sys.path.insert(0,str(S))
from atlas.compiler import generate
cases={'norsand':['models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'],'maxwell':['models/research/maxwell/maxwell-itasca900-zero-spin-ode.json'],'interface2016':['models/research/interface2016/hvwe2016-reconciled-fixed-local.json']}
iq=read(S/'docs/ingestion/hypoplastic-interface-2016/execution-v1/build-receipt.json');counts={};generated={}
for label,models in cases.items():
 g=Q/'generated'/label;generate(g,[S/n for n in models]);files=sorted(g.iterdir());ck(len(files)==(2 if label=='maxwell' else 3),'generated cardinality')
 for f in files:
  ck(f.read_bytes()==(P/'generated'/label/f.name).read_bytes(),('fresh generation',label,f.name))
  want=next(v for n,v in iq['artifacts'].items() if n.endswith('/generated/'+f.name)) if label=='interface2016' else r[label]['generated'][f.name]['expected']
  ck(h(f.read_bytes())==want,('qualified generation',label,f.name))
 generated[label]={f.name:h(f.read_bytes()) for f in files}
 todo=[S/'cpp/main.cpp'] if label=='maxwell' else [g/'path_api.cpp'];seen={}
 oldmap=iq['source_closure'] if label=='interface2016' else (nq['binding']['sources'] if label=='norsand' else mm['files'])
 while todo:
  f=todo.pop().resolve()
  if str(f) in seen:continue
  data=f.read_bytes();seen[str(f)]=h(data)
  if f.is_relative_to(S):ck(oldmap[f.relative_to(S).as_posix()]==h(data),('include byte',str(f)))
  for name in re.findall(rb'^\s*#\s*include\s*"([^"]+)"',data,re.M):
   options=[f.parent/name.decode(),g/name.decode(),S/'cpp/include'/name.decode()];found=next((x for x in options if x.is_file()),None);ck(found is not None,('include resolution',name));todo.append(found)
 ck(not any(n.endswith('/solver.hpp') for n in seen) if label!='maxwell' else any(n.endswith('/solver.hpp') for n in seen),'solver reachability');counts[label]=len(seen)
# Current dedicated CMake explicitly compiles these actual entry points.
ck('add_executable(atlas_path_capability "${ATLAS_GENERATED}/path_api.cpp")' in (S/'cmake/controlled-path/CMakeLists.txt').read_text(),'path compile entry')
ck('add_executable(atlas_maxwell_solver EXCLUDE_FROM_ALL "${ATLAS_ROOT}/cpp/main.cpp")' in (S/'cmake/maxwell/CMakeLists.txt').read_text(),'maxwell compile entry')
ck(counts=={'norsand':9,'maxwell':16,'interface2016':9},'include counts')
ck(b['profiles']['interface2016']['operationally_authorized'] is False,'interface integration remains open')
# Deliberate saved corruption must fail exact byte commitments, not approximate equality.
for label,files in generated.items():
 for name,digest in files.items():ck(h((Q/'generated'/label/name).read_bytes()+b'\n')!=digest,('extra byte refusal',label,name))
print(json.dumps({'passed':True,'checks':checks,'independent_generated':generated,'include_counts':counts,'executed_engines':0,'compiled_calls':0},indent=2))
