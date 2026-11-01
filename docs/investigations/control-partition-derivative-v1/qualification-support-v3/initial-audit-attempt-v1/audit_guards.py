"""Execute only original source/document guards; no generator, bundle or artifact call."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast,copy,hashlib,importlib.util,json
D=Path(__file__).resolve().parent;SOURCE=Path('/private/tmp/atlas-control-partition-support-v2/source')
sys.path[:0]=[str(SOURCE),str(SOURCE/'tools')]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(name,data):(D/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def load(name):
 path=SOURCE/'tools'/name;spec=importlib.util.spec_from_file_location('source_only_'+path.stem,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def run_nodes(module,nodes):
 # This Python AST consists of exact original statements, stopping before generation.
 node=ast.FunctionDef(name='_source_only_guards',args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),body=copy.deepcopy(nodes)+[ast.Return(value=ast.Call(func=ast.Name(id='locals',ctx=ast.Load()),args=[],keywords=[]))],decorator_list=[])
 tree=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]));namespace=vars(module).copy();namespace.update(dest=SOURCE/'NEVER_WRITTEN',destination=SOURCE/'NEVER_WRITTEN',build=SOURCE/'NO_BUILD_OBSERVED')
 exec(compile(tree,str(module.__file__),'exec'),namespace);return namespace['_source_only_guards']()

BUILDERS={'power-creep':'build_power_creep_web.py','burgers':'build_burgers_web.py','sls':'build_sls_laboratory.py','j2':'build_j2_laboratory.py','orthotropic':'build_orthotropic_laboratory.py','maxwell':'build_maxwell_laboratory.py','norsand':'build_controlled_path_web.py','lade':'build_implicit_path_laboratory.py','hill':'build_hill_laboratory.py'}
LITERALS={
'power-creep':['docs/admission/power-creep-approved-v1/approval.json','docs/ingestion/power-creep-itasca900/manifest.json','docs/ingestion/power-creep-itasca900/review-v1/manifest.json','catalogue/agent-reviews/power-creep-agent-v2.json','docs/ingestion/power-creep-itasca900/review-v2/README.md',*['web/'+n for n in ['power-creep.html','power-creep-contract.mjs','recorded.mjs','numerics.mjs','loading.mjs']]],
'burgers':['tools/build_evidence.py','docs/models/burgers-main-laboratory-v1.md',*['web/'+n for n in ['timed-contract.mjs','timed-laboratory.mjs','timed-worker.mjs','recorded.mjs','numerics.mjs','loading.mjs']]],
'sls':['docs/reviews/sls-comsol63-scientific-v1/README.md'],
'j2':['tools/build_j2_web.py','web/j2-contract.mjs','web/j2-laboratory.mjs','docs/reviews/j2-scientific-v2/README.md','docs/ingestion/j2-linear-hardening/delivery-v1/PUBLIC_DELIVERY.md','docs/ingestion/j2-linear-hardening/delivery-v1/independent-review/README.md','docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/README.md','docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/sls-router-addendum/README.md','docs/ingestion/j2-linear-hardening/delivery-v2/independent-review/sls-router-addendum/catalogue-copy-followup/receipt.json'],
'orthotropic':['web/orthotropic-contract.mjs','web/orthotropic-laboratory.mjs','docs/ingestion/orthotropic-ogs/source-v1/README.md','docs/ingestion/orthotropic-ogs/scientific-review-v1/report.md'],
'maxwell':['docs/reviews/maxwell-checklist-v2/README.md','docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json'],
'norsand':['catalogue/path-examples/norsand-1993-loose-constant-cell.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json','docs/ingestion/norsand-1993/supplied-original-v2/source-receipt.json','docs/ingestion/norsand-1993/approval-v1/REPORT.md'],
'lade':['tools/generate_implicit_path.py','cmake/implicit-path-v1/CMakeLists.txt','docs/ingestion/lade-duncan-1975/atlas-integration-v1/check_interface.mjs','docs/ingestion/lade-duncan-1975/atlas-integration-v1/independent-review/MODEL_REVIEW.md'],
'hill':['web/hill-contract.mjs','docs/models/hill-abaqus2025.md',*['docs/ingestion/hill-abaqus2025/execution-v1/'+n for n in ['build-receipt.json','references.json','negative-requests.json','POLICY.md']]]}

def main():
 before={p.relative_to(SOURCE).as_posix():sha(p)for p in SOURCE.rglob('*')if p.is_file()};results=[];modules={}
 for profile,name in BUILDERS.items():
  module=load(name);modules[profile]=module;text=Path(module.__file__).read_text();body=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='bundle').body;prefix=[]
  for node in body:
   if isinstance(node,ast.With)or(profile=='power-creep'and isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='engine'for t in node.targets)):break
   prefix.append(node)
  item=dict(profile=profile,builder='tools/'+name,builder_sha256=sha(module.__file__),source_guard_lines=[prefix[0].lineno,prefix[-1].end_lineno],stop_before_generation_or_write=True)
  try:
   values=run_nodes(module,prefix);item['source_guard_passed']=True
   if profile=='power-creep':
    # Exact later legacy packager also validates agent-v2, independently of legacy approval.
    from atlas.agent_review import validate_review
    validate_review(SOURCE/'catalogue/agent-reviews/power-creep-agent-v2.json',for_approval=True);item['later_agent_review_passed']=True
   if profile in ['maxwell','lade']:
    start=next(i for i,n in enumerate(body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='components'for t in n.targets));end=next(i for i,n in enumerate(body[start:],start)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='source'for t in n.targets))
    run_nodes(module,body[start:end+1]);item['later_interface_guard_passed']=True
   if profile=='hill':
    start=next(i for i,n in enumerate(body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='contract'for t in n.targets));run_nodes(module,body[start:start+2]);item['browser_contract_identity_guard_passed']=True
  except Exception as error:item.update(source_guard_passed=False,error=type(error).__name__+': '+str(error))
  paths=set(LITERALS[profile]);paths.update('web/'+n for n in getattr(module,'COMPONENTS',[]))
  for attr in ['APPROVAL','REFERENCE','INTERFACE_REVIEW','INTERFACE']:
   if hasattr(module,attr):paths.add(getattr(module,attr))
  item['literal_source_inputs']=[dict(path=p,exists=(SOURCE/p).is_file(),sha256=sha(SOURCE/p)if(SOURCE/p).is_file()else None)for p in sorted(paths)]
  item['missing_literal_source_inputs']=[x['path']for x in item['literal_source_inputs']if not x['exists']]
  item['not_qualified']='Generated catalogues/artifacts, actual new numerical qualification, independent build reviews, packaging/browser remain separate.'
  results.append(item)
 # Preserve the v2 observation but distinguish an agent-v2 supporting set from actual Power legacy guard.
 registry=json.loads((SOURCE/'catalogue/approved-models.json').read_text())['models'];poweragent=next(a for a in registry if a['model_id']=='power-creep-itasca900-both-active-ode'and a.get('review',{}).get('kind')=='agent-model-review');divergences=[]
 for pin in poweragent['supporting_files']:
  if sha(SOURCE/pin['path'])!=pin['sha256']:divergences.append(dict(path=pin['path'],agent_v2_expected=pin['sha256'],actual=sha(SOURCE/pin['path']),actual_legacy_builder_requires_this_exact_pin=False))
 after={p.relative_to(SOURCE).as_posix():sha(p)for p in SOURCE.rglob('*')if p.is_file()};assert before==after,'source guard audit mutated tree'
 maxwell=modules['maxwell'].source_manifest();norsand={p for p in before if(p.startswith('atlas/')and p.endswith('.py')or p.startswith('cpp/include/atlas/')and p.endswith('.hpp')or p.startswith('schemas/')and p.endswith('.json')or p.startswith('cpp/scalar-functions/'))and '__pycache__'not in p.split('/')};norsand.update(['cmake/controlled-path/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tools/generate_controlled_path.py','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json']);mapping={p:before[p]for p in sorted(norsand)}
 sets={'source_directory':str(SOURCE),'profiles':{'maxwell':maxwell,'norsand':{'files':mapping,'sha256':hashlib.sha256(json.dumps(mapping,sort_keys=True,separators=(',',':')).encode()).hexdigest()}}};save('patched-source-manifests.json',sets)
 prior=json.loads((D.parent/'qualification-support-v2/patched-source-manifests.json').read_text());assert prior['profiles']==sets['profiles'],'runtime matcher unexpectedly changed'
 save('guard-closure.json',dict(identity='actual-nine-builder-source-guard-audit-v3',results=results,source_files_unchanged=True,prior_power_agent_v2_support_divergences=divergences,correction='Prior v2 three divergences are not actual build_power_creep_web.py legacy supporting-file failures. Legacy approval loop and later agent validator are separately evaluated.',compiled_calls=0,builds=0,guarded_package_ready=False))
 print(json.dumps({'source_guards_passed':sum(x['source_guard_passed']for x in results),'profiles':len(results),'missing_literal_paths':sum(len(x['missing_literal_source_inputs'])for x in results),'agent_v2_direct_divergences':len(divergences),'maxwell_sha256':maxwell['sha256'],'norsand_sha256':sets['profiles']['norsand']['sha256']}))
if __name__=='__main__':main()
