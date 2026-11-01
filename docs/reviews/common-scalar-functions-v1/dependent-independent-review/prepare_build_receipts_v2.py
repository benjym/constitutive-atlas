"""Add only separately versioned, noncompiled profile source provenance."""
from pathlib import Path
import ast,hashlib,json,copy
R=Path(__file__).resolve().parents[4];B=R/'docs/reviews/common-scalar-functions-v1';O=Path(__file__).parent;D=O/'build-local-v2/maxwell'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=json.loads((O/'build-local-v1/maxwell/source-manifest.json').read_text())
# Execute only the exact pure source_manifest/digest function definitions.
p=B/'package-proposal-v4/tools/build_maxwell_laboratory.py';tree=ast.parse(p.read_text());functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ['source_manifest','digest']]
ns={'ROOT':R,'DEFINITION':'models/research/maxwell/maxwell-itasca900-zero-spin-ode.json','hashlib':hashlib,'json':json}
exec(compile(ast.Module(body=functions,type_ignores=[]),str(p),'exec'),ns);new=ns['source_manifest']()
assert all(new['files'].get(name)==h for name,h in old['files'].items())
extra={p:h for p,h in new['files'].items() if p not in old['files']}
assert len(old['files'])==120 and len(new['files'])==149 and len(extra)==29
assert all(p.startswith('cpp/profiles/implicit-path-v1/') and Path(p).suffix in {'.cpp','.hpp'} for p in extra)
checked={}
for p in ['cmake/maxwell/CMakeLists.txt','cpp/main.cpp',*[p for p in old['files'] if p.startswith('cpp/include/atlas/')]]:
    data=(R/p).read_text();assert 'cpp/profiles/' not in data and 'implicit-path-v1' not in data;checked[p]=sha(R/p)
cmake=(R/'cmake/maxwell/CMakeLists.txt').read_text();assert '"${ATLAS_ROOT}/cpp/main.cpp"' in cmake and '"${ATLAS_ROOT}/cpp/include"' in cmake and 'GLOB_RECURSE' not in cmake
for backend in ['native','wasm']:
    audit=json.loads((B/f'consumer-results-v1/{backend}/maxwell/build-audit.json').read_text())
    for command in audit['commands']:assert 'profiles/' not in command['command'] and 'implicit-path-v1' not in command['file']
    # Retained compiler dependencies provide a second independent route check.
    build=Path(audit['commands'][0]['directory']);deps=list(build.rglob('main.cpp.o.d'));assert deps
    for p in deps:assert 'cpp/profiles/' not in p.read_text();checked[str(p)]=sha(p)
delta={'kind':'noncompiled separately versioned profile source provenance only','files':extra,'basis':'Exact Maxwell CMake compiles cpp/main.cpp with cpp/include, never cpp/profiles/implicit-path-v1; qualified commands and dependency files contain no profile reference. No profile algorithm or scientific approval supplied.'}
D.mkdir(parents=True,exist_ok=True)
def write(name,d):p=D/name;p.write_text(json.dumps(d,indent=2)+'\n')
write('source-manifest.json',new);write('profile-provenance-delta.json',delta)
review=json.loads((O/'build-local-v1/maxwell/build-review.json').read_text());q=json.loads((O/'build-local-v1/maxwell/maxwell-qualification.json').read_text())
before=copy.deepcopy(review['binding']);review['binding']['source_manifest_sha256']=new['sha256'];q['binding']=review['binding'].copy()
review['evidence']['profile_provenance_delta']={'path':str((D/'profile-provenance-delta.json').relative_to(R)),'sha256':sha(D/'profile-provenance-delta.json')}
review['evidence']['prior_build_review']={'path':str((O/'build-local-v1/maxwell/build-review.json').relative_to(R)),'sha256':sha(O/'build-local-v1/maxwell/build-review.json')};q['evidence']=copy.deepcopy(review['evidence'])
assert {k:v for k,v in before.items() if k!='source_manifest_sha256'}=={k:v for k,v in review['binding'].items() if k!='source_manifest_sha256'}
write('build-review.json',review);q['independent_review']={'path':'build-review.json','sha256':sha(D/'build-review.json')};write('maxwell-qualification.json',q)
result={'status':'accepted additive noncompiled source provenance delta','old_files':120,'new_files':149,'added_files':29,'changed_original_files':[],'compiled_execution':False,'checked_dependency_routes':checked,'delta':delta}
(O/'profile-delta-results-v2.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['delta','checked_dependency_routes']},indent=2))
