"""Pure generation and source-byte comparisons; never run an engine."""
from pathlib import Path
import sys,json,hashlib,tarfile,difflib
P=Path(__file__).resolve().parent
S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
OLD=Path('/private/tmp/atlas-md1997-final-native-source-v1/source')
R=P.parents[4]
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def deny(event,args):
 if event.startswith(('subprocess.','socket.','ctypes.')):raise RuntimeError('Process/network/native load forbidden')
sys.addaudithook(deny)
sys.path.insert(0,str(S))
from atlas.compiler import generate
archive=R/'.local/private-evidence/md1997-current-package-v7/complete-output.tar.gz'
with tarfile.open(archive) as t:
 nq=json.load(t.extractfile('site/engine-path/qualification.json'))
 mq=json.load(t.extractfile('site/engine-maxwell/qualification.json'))
 mm=json.load(t.extractfile('site/engine-maxwell/source-manifest.json'))
 receipt=read(R/'docs/ingestion/manzari-dafalias-1997/delivery-v1/current-qualified-profile-copies-v1/receipt.json')
 oldmaps={'norsand':nq['binding']['sources'],'maxwell':mm['files']}
 result={}
 for label,files in oldmaps.items():
  unchanged=[];changed=[]
  for n,h in files.items():
   data=(S/n).read_bytes()
   if sha(data)==h:unchanged.append(n)
   else:
    before=(OLD/n).read_bytes();assert sha(before)==h,(label,n,'old preimage mismatch')
    changed.append(n)
    out=P/'diffs'/n;out.parent.mkdir(parents=True,exist_ok=True)
    out.with_suffix(out.suffix+'.diff').write_text(''.join(difflib.unified_diff(before.decode().splitlines(True),data.decode().splitlines(True),fromfile='qualified/'+n,tofile='current/'+n)))
  compileinputs=[n for n in files if n.startswith(('cpp/','cmake/','models/','tests/fixtures/')) or n.startswith('tools/generate')]
  assert all(n in unchanged for n in compileinputs)
  result[label]={'qualified_entries':len(files),'changed':changed,'unchanged_compile_inputs':{n:files[n] for n in compileinputs},'current_sources':{n:sha((S/n).read_bytes()) for n in files}}
 cases={'norsand':['models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json'],'maxwell':['models/research/maxwell/maxwell-itasca900-zero-spin-ode.json']}
 expected={'norsand':receipt['profiles']['norsand']['original_inventory'],'maxwell':receipt['profiles']['maxwell']['original_inventory']}
 for label,paths in cases.items():
  dest=P/'generated'/label;dest.mkdir(parents=True,exist_ok=True);generate(dest,[S/n for n in paths])
  names=['path_api.cpp','path_models.hpp','path_catalogue.json'] if label=='norsand' else ['models.hpp','models.json']
  rows={}
  for n in names:
   h=sha((dest/n).read_bytes());want=expected[label]['generated/'+n];rows[n]={'sha256':h,'expected':want,'equal':h==want};assert h==want,(label,n)
  result[label]['generated']=rows
  result[label]['artifact_binding']=nq['binding'] if label=='norsand' else mq['binding']
 iq=read(S/'docs/ingestion/hypoplastic-interface-2016/execution-v1/build-receipt.json')
 mismatches=[n for n,h in iq['source_closure'].items() if sha((S/n).read_bytes())!=h]
 result['interface2016']={'baseline_receipt_source_mismatches':mismatches,'reuse_proven':False,'reason':'solver.hpp differs; old interface binary dependency equivalence not established'}
 write('results.json',result)
 print('PASS NorSand/Maxwell compile-input bytes and all five generated files identical; Interface2016 unresolved solver.hpp')
# Direct include closure, with unresolved repository includes rejected.
import re

def includes(start,generated):
 seen={};queue=list(start)
 while queue:
  p=queue.pop();key=str(p)
  if key in seen:continue
  data=p.read_bytes();seen[key]=sha(data)
  for target in re.findall(rb'^\s*#\s*include\s*"([^"]+)"',data,re.M):
   n=target.decode();candidates=[p.parent/n,generated/n,S/'cpp/include'/n]
   found=next((x for x in candidates if x.is_file()),None)
   assert found is not None,(p,n)
   queue.append(found)
 return seen
idata=read(S/'docs/ingestion/hypoplastic-interface-2016/execution-v1/build-receipt.json')
dest=P/'generated/interface2016';dest.mkdir(parents=True,exist_ok=True)
generate(dest,[S/'models/research/interface2016/hvwe2016-reconciled-fixed-local.json'])
ig={}
for p in dest.iterdir():
 want=next(h for n,h in idata['artifacts'].items() if n.endswith('/generated/'+p.name));assert sha(p.read_bytes())==want
 ig[p.name]=want
closures={}
for label in ['norsand','interface2016','maxwell']:
 g=P/'generated'/label
 starts=[g/'path_api.cpp'] if label!='maxwell' else [S/'cpp/main.cpp']
 cl=includes(starts,g)
 expected=oldmaps[label] if label in oldmaps else idata['source_closure']
 for n,h in cl.items():
  p=Path(n)
  if p.is_relative_to(S):assert expected[p.relative_to(S).as_posix()]==h,(label,n)
 assert not any(n.endswith('/solver.hpp') for n in cl) if label!='maxwell' else True
 closures[label]=cl
result['interface2016'].update(generated=ig,recursive_include_closure=closures['interface2016'],reuse_proven_at_source_level=True,reason='Changed solver.hpp is not in actual transitive quoted-include closure; all included repository bytes and all three generated outputs match exact qualified original Interface artifact binding.')
result['recursive_include_closures']=closures
for label in ['norsand','maxwell']:
 current=dict(result[label]['current_sources'])
 dirs=[('atlas',{'.py'}),('schemas',{'.json'}),('cpp/include/atlas',{'.hpp'})] if label=='norsand' else [('atlas',{'.py'}),('schemas',{'.json'}),('cpp',{'.cpp','.hpp'})]
 for directory,suffixes in dirs:
  for p in (S/directory).rglob('*'):
   if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts:current[p.relative_to(S).as_posix()]=sha(p.read_bytes())
 result[label]['added_inventory_paths']=sorted(set(current)-set(result[label]['current_sources']))
 result[label]['proposed_complete_current_sources']=current
write('results.json',result)
print('PASS Interface three generated bytes, complete local quoted-include closures; solver.hpp excluded for both path engines')
