from pathlib import Path
import json,hashlib,ast,sys,re,copy
from unittest.mock import patch
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent;P=Q.parent/'direct-controlled-time-compatibility-v1';F=Q.parent/'direct-controlled-time-package-fix-v1';S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source');B=S/'web/engines/controlled-time'
h=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_bytes());count=0

def ck(v,n):
 global count
 assert v,n
 count+=1
for p,w in [(P,'09611947bbf983f4423a6ecd48de9d202ebb0a8f73f05f363f7faa3e5aa94426'),(F,'23d6e2d94ba5d48989ad0bd3037d7c90ceb11f07e2d3d25e81bd6a1908ab4879')]:
 ck(h((p/'manifest.json').read_bytes())==w,'manifest')
 for n,v in read(p/'manifest.json')['files'].items():ck(h((p/n).read_bytes())==v,n)
proof=read(P/'proof.json');receipt=read(B/'public-qualification.json');ck(proof['source_files']==len(proof['source_inventory'])==94,'94 source rows')
for row,pin in zip(proof['source_inventory'],receipt['source_files']):
 ck(pin==dict(path=row['path'],sha256=row['qualified']),'exact old row');ck(h((S/row['path']).read_bytes())==row['current'],'current row')
ck([x for x in proof['source_inventory'] if x['qualified']!=x['current']]==proof['changed'],'only fixed delta')
ck(proof['changed']==[dict(path='cpp/include/atlas/solver.hpp',qualified='b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e',current='05e6cc0c9dd6b6774597e07de0abe2beb7d9128383423d22b34c2e1d0a4d9218')],'exact allowed pair')
ck(h((S/proof['historical_solver']['path']).read_bytes())==proof['historical_solver']['sha256'],'historical snapshot')
seen={};todo=[B/'generated/controlled_time_api.cpp']
while todo:
 f=todo.pop().resolve();name=f.relative_to(S).as_posix()
 if name in seen:continue
 data=f.read_bytes();seen[name]=h(data)
 for inc in re.findall(rb'^\s*#\s*include\s*"([^"]+)"',data,re.M):
  opts=[f.parent/inc.decode(),S/'cpp/include'/inc.decode(),B/'generated'/inc.decode()];found=next((x for x in opts if x.is_file()),None);ck(found is not None,'include resolved');todo.append(found)
ck(seen==proof['compile_dependency_files'] and len(seen)==11 and 'cpp/include/atlas/solver.hpp' not in seen,'actual compile closure')
for name,pin in proof['unlisted_dependency_headers'].items():
 ck(pin['qualification_receipt_pin_present'] is False,'historical coverage limitation explicit');ck(h((S.parent/'baseline16-source'/name).read_bytes())==pin['original02ad_baseline_sha256']==seen[name],'unlisted baseline header exact')
for name,v in receipt['artifacts'].items():ck(h((B/name).read_bytes())==v,'actual retained engine byte')
ck(h((B/'public-qualification.json').read_bytes())==proof['qualification_sha256'] and (B/'public-qualification.json').read_bytes()==(S/receipt['root_receipt_path']).read_bytes(),'original qualification/root identical')
registry=read(S/'catalogue/approved-models.json')['models'];ck(proof['approval'] in registry,'actual approval retained')
for name in ['examples','public_results']:ck(h((S/receipt[name]['path']).read_bytes())==receipt[name]['sha256'],'examples/results pin')
cmake=(S/'cmake/controlled-time/CMakeLists.txt').read_text();ck('add_executable(atlas_controlled_time_capability "${ATLAS_GENERATED}/controlled_time_api.cpp")' in cmake,'actual dedicated compile entry')
def deny(e,a):
 if e.startswith(('subprocess.','socket.','ctypes.')):raise RuntimeError(e)
sys.addaudithook(deny);sys.path.insert(0,str(S))
from atlas.controlled_time_compiler import generate
generate(Q/'generated',[S/proof['current_model']['path']])
for name,v in proof['generated'].items():ck(h((Q/'generated'/name).read_bytes())==v and (Q/'generated'/name).read_bytes()==(B/'generated'/name).read_bytes(),'fresh generated exact')
packager=S/'tools/build_controlled_time_web.py';ck(h(packager.read_bytes())=='02b1dd6e36c2c23ca91a78d321c4af5060dd7b68dbf8385e142061f4149a4758','actual packager exact')
a=ast.parse((F/'before.py').read_bytes());z=ast.parse(packager.read_bytes())
for name in ['sha','source_pin']:
 left=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==name);right=next(n for n in z.body if isinstance(n,ast.FunctionDef) and n.name==name);ck(ast.dump(left,include_attributes=False)==ast.dump(right,include_attributes=False),'original guard unchanged '+name)
# Execute only unchanged sha/source_pin plus new compatibility validator; never bundle.
ns=dict(Path=Path,json=json,hashlib=hashlib,ROOT=S,__file__=str(packager))
parts=[n for n in z.body if (isinstance(n,ast.FunctionDef) and n.name in ['sha','source_pin','reviewed_source_compatibility']) or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id.startswith('COMPATIBILITY_') for t in n.targets))]
exec(compile(ast.Module(body=parts,type_ignores=[]),'<exact extracted compatibility guard>','exec'),ns)
fn=ns['reviewed_source_compatibility'];original_sha=ns['sha'];text=Path.read_text;overrides={};decision={'status':'accepted','reviewer_run':'/root/md1997_profile_review_resume','blocking_findings':[],'source_sha256':h(packager.read_bytes()),'proof_sha256':h((P/'proof.json').read_bytes()),'scope':'controlled-time-unused-solver-pin-package-only-v1'}
# This dictionary exists only in the manufactured fixture, never on disk or in ROOT.
def readtext(p,*a,**k):
 if p==S/ns['COMPATIBILITY_PROOF']:return (P/'proof.json').read_text()
 if p==S/ns['COMPATIBILITY_REVIEW']:
  if decision is None:raise FileNotFoundError('manufactured absent acceptance')
  return json.dumps(decision)
 return text(p,*a,**k)
def sha(p):
 p=Path(p)
 if str(p) in overrides:return overrides[str(p)]
 if p==S/ns['COMPATIBILITY_PROOF']:return h((P/'proof.json').read_bytes())
 return original_sha(p)
ns['sha']=sha
neg=0
def refuse(r=receipt):
 global count,neg
 try:fn(B,r)
 except (ValueError,FileNotFoundError):count+=1;neg+=1
 else:raise AssertionError('bad compatibility accepted')
with patch.object(Path,'read_text',readtext):
 ck(fn(B,receipt) is not None,'manufactured guard positive')
 for key,bad in [('status','passed'),('reviewer_run','author'),('blocking_findings',['x']),('source_sha256','0'*64),('proof_sha256','0'*64),('scope','whole-CI')]:
  old=decision[key];decision[key]=bad;refuse();decision[key]=old
 old=decision;decision=None;refuse();decision=old
 for p in [packager,S/ns['COMPATIBILITY_PROOF'],S/proof['historical_solver']['path'],B/'public-qualification.json',*[B/'generated'/n for n in proof['generated']],*[S/n for n in proof['compile_dependency_files']],S/'atlas/controlled_time.py']:
  overrides[str(p)]='0'*64;refuse();overrides.clear()
 for key,bad in [('model_id','other'),('definition_sha256','0'*64),('artifacts',{}),('source_files',receipt['source_files'][:-1])]:
  r=copy.deepcopy(receipt);r[key]=bad;refuse(r)
 # Original exact-source route returns None and does not require a compatibility decision.
 decision=None
 for pin in receipt['source_files']:overrides[str(S/pin['path'])]=pin['sha256']
 ck(fn(B,receipt) is None,'old strict route unchanged');overrides.clear()
print(json.dumps({'passed':True,'checks':count,'validator_refusals':neg,'generated_exact':3,'source_inventory':94,'actual_compile_closure':11,'compiled_models_or_bundle_executed':0,'unlisted_header_coverage_limitation_preserved':True},indent=2))
