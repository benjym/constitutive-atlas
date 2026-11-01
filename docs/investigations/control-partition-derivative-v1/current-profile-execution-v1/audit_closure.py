"""Prospective seven-collector source/literal closure; no imports or execution."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent;S=Path('/private/tmp/atlas-control-partition-support-v3/source');B='3873a48b256ed37cbc78378ee6b41d73139676f8';sha=lambda b:hashlib.sha256(b).hexdigest();rows=json.loads((D/'plan.json').read_text())['profiles'];inventory={};missing=[]
literals={
'power-creep':['tools/power_creep_study.py','docs/ingestion/power-creep-itasca900/execution-v1/refinement-v2/study.json','docs/ingestion/power-creep-itasca900/execution-v1/refinement-v2/freeze.json'],
'burgers':['docs/ingestion/burgers-itasca900/integration-v1/'+n for n in ['reference.py','requests.json','references.json','acceptance.json','wasm_host.mjs']],
'sls':['docs/ingestion/sls-comsol63/execution-v1/'+n for n in ['cases.json','study.py']],
'j2':['tools/run_j2.py','tools/study_j2.py','docs/ingestion/j2-linear-hardening/delivery-v1/preset-references.json']+['docs/ingestion/j2-linear-hardening/execution-v2/'+n for n in ['references.json','default-references.json','paths.json','check_paths.py']],
'orthotropic':['tools/orthotropic_reference.py','docs/ingestion/orthotropic-ogs/execution-v1/references.json','docs/ingestion/orthotropic-ogs/execution-v1/freeze-v2.json'],
'maxwell':['tools/build_maxwell_laboratory.py','tools/check_maxwell_ci.py','tools/collect_maxwell.mjs','docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json']+['examples/maxwell/'+n+'.json'for n in ['relaxation','creep','oedometer','load-hold-reverse']],
'norsand':['tools/build_controlled_path_web.py','tools/generate_controlled_path.py','docs/ingestion/norsand-1993/e2-v3/backend-requests-v2.json','models/research/norsand/norsand-jefferies-1993-active-axial.json','tests/fixtures/controlled-path/synthetic-curved.json','tests/fixtures/controlled-path/synthetic-model.json']}
# tools/collect_maxwell.mjs is not a selected command; use the actual exact collector.
literals['maxwell'].remove('tools/collect_maxwell.mjs')
for row in rows:
 name=row['profile'];roots=set(S/p for p in literals[name]);roots.update(Path(a)for step in row['steps']for a in step['argv']if Path(a).is_absolute()and (a.endswith('.py')or a.endswith('.mjs')or a.endswith('.json'))and not a.startswith('/private/tmp/atlas-control-partition-profile-execution-v1'))
 # Generation source closure: exact CMake files, compiler modules, schema trees,
 # scalar implementation and every source file actually present in their matchers.
 roots.update(S/p for p in json.loads((D.parent/'qualification-support-v4/patched-source-manifests.json').read_text())['profiles']['maxwell']['files'])
 roots.add(S/'CMakeLists.txt'if name=='power-creep'else S/'cmake'/('controlled-path'if name=='norsand'else name)/'CMakeLists.txt');roots.add(S/'cmake/AtlasScalarFunctions.cmake')
 todo=list(roots);seen=set();unresolved=[]
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  if not p.is_file():
   unresolved.append(str(p));continue
  inventory[str(p)]=sha(p.read_bytes())
  if p.suffix=='.py':
   try:t=ast.parse(p.read_text())
   except UnicodeDecodeError:continue
   imports=[]
   for n in ast.walk(t):
    if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
    elif isinstance(n,ast.ImportFrom)and n.module:imports.append(n.module)
   for module in imports:
    q=Path(*module.split('.'));candidates=[p.parent/(str(q)+'.py'),S/(str(q)+'.py'),S/q/'__init__.py',S/'tools'/(str(q)+'.py')]
    if module=='reference':candidates.insert(0,S/'docs/ingestion/burgers-itasca900/integration-v1/reference.py')
    # The Burgers path adapter deliberately supplies study.py first.
    if module=='study'and name=='burgers':candidates.insert(0,D/'adapters/study.py')
    found=next((x for x in candidates if x.is_file()),None)
    if found:todo.append(found)
    elif module.split('.')[0]in ['atlas','tools','tests']:unresolved.append('local import '+module+' from '+str(p))
  elif p.suffix in ['.mjs','.js']:
   for rel in re.findall(r"(?:from|import)\s*['\"](\.[^'\"]+)['\"]",p.read_text()):todo.append(p.parent/rel)
 row['static_closure_files']=len(seen);row['unresolved_static_inputs']=unresolved
 for path in unresolved:
  if path.startswith(str(S)):
   rel=str(Path(path).relative_to(S))
   try:b=subprocess.check_output(['git','show',B+':'+rel],stderr=subprocess.DEVNULL)
   except subprocess.CalledProcessError:b=None
   missing.append(dict(profile=name,path=rel,sha256=sha(b)if b is not None else None,available_exact=b is not None,git_source=B+':'+rel))
  else:missing.append(dict(profile=name,path=path,available_exact=False))
# All93 Power freeze files are actual executed preconditions, even though none
# supplies the new compiled runtime. Do not alter the accepted matcher sets.
for x in json.loads((D/'literal-gaps.json').read_text())['power_missing']:missing.append(dict(profile='power-creep',**x))
unique={x['path']:x for x in missing}
result=dict(identity='seven-profile-executed-input-closure-v1',source_directory=str(S),profiles=[dict(profile=r['profile'],static_closure_files=r['static_closure_files'],unresolved_static_inputs=r['unresolved_static_inputs'])for r in rows],files=inventory,missing=list(unique.values()),scope='Static exact command/import/literal and freeze-loop closure. Future build outputs/environment/toolchain imports are external runtime preconditions, not present source files. No collector, assessment main, generator or artifact executed.',compiled_calls=0)
(D/'collector-closure.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(pinned_files=len(inventory),unique_missing=len(unique),unavailable=sum(not x['available_exact']for x in unique.values()),missing_nonpower=[x['path']for x in unique.values()if x['profile']!='power-creep'],compiled_calls=0)))
