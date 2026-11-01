"""Saved-source/hash/archive diagnostics only; no builds, generator or material calls."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import sys
import tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
from tools.build_maxwell_laboratory import source_manifest
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
packet=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-v2'
old=read(packet/'observations/inputs.json')['source_manifest'];current=source_manifest()
changes=[dict(path=n,old=old['files'].get(n),current=current['files'].get(n)) for n in sorted(set(old['files'])|set(current['files'])) if old['files'].get(n)!=current['files'].get(n)]
profile='cpp/profiles/implicit-path-v1/include/atlas/solver.hpp'
fused='docs/ingestion/lade-duncan-1975/fused-linear-v1/proposed-native-source/include/atlas/solver.hpp'
p=(ROOT/profile).read_bytes();q=(ROOT/fused).read_bytes()
newfiles=dict(current['files']);newfiles[profile]=sha(q)
future=dict(files=newfiles,sha256=sha(json.dumps(newfiles,sort_keys=True,separators=(',',':')).encode()))
comparison=dict(retained=old,current=current,current_drift=changes,prospective=future,future_single_change=dict(path=profile,old=sha(p),future=sha(q)),changed_physical_lines=[dict(line=i+1,old=a,future=b) for i,(a,b) in enumerate(zip(p.decode().splitlines(),q.decode().splitlines())) if a!=b])
(HERE/'closure-comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
(HERE/'prospective-profile-solver.diff').write_text(''.join(difflib.unified_diff(p.decode().splitlines(True),q.decode().splitlines(True),fromfile=profile,tofile=fused)))
qualification=read(packet/'maxwell-qualification.json');review=read(packet/'independent-review/final-v1/build-review.json');provenance=read(packet/'provenance.json')
archive=packet/'compiled-closure-v1.tar.gz'
with tarfile.open(archive) as t:
 members=[dict(path=m.name,bytes=m.size,sha256=sha(t.extractfile(m).read())) for m in t.getmembers() if m.isfile()]
constants={}
for node in ast.parse((ROOT/'tools/provision_maxwell_assets.py').read_text()).body:
 if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ['ARCHIVE_SHA256','QUALIFICATION_SHA256','REVIEW_SHA256']:
  constants[node.targets[0].id]=ast.literal_eval(node.value)
archive_result=dict(archive_sha256=sha(archive.read_bytes()),members=members,provider_constants=constants,qualification_sha256=sha((packet/'maxwell-qualification.json').read_bytes()),review_sha256=sha((packet/'independent-review/final-v1/build-review.json').read_bytes()))
assert archive_result['archive_sha256']==constants['ARCHIVE_SHA256'];assert archive_result['qualification_sha256']==constants['QUALIFICATION_SHA256'];assert archive_result['review_sha256']==constants['REVIEW_SHA256']
assert {x['path']:x['sha256'] for x in members}==provenance['archive_members']
assert qualification['binding']==review['binding'];assert qualification['binding']['source_manifest_sha256']==old['sha256']
(HERE/'archive-verification.json').write_text(json.dumps(archive_result,indent=2)+'\n')
sources={};deps=[]
for side in ['native','wasm']:
 audit_path=ROOT/f'docs/reviews/common-scalar-functions-v1/consumer-results-v1/{side}/maxwell/build-audit.json';audit=read(audit_path);sources[str(audit_path.relative_to(ROOT))]=sha(audit_path.read_bytes())
 build=Path(audit['commands'][0]['directory']);source_root=Path('/private/tmp/atlas-common-scalar-functions-v1/consumer-source-v1')
 files=list(build.rglob('*.d'));assert len(files)==13
 relevant={};external={}
 for dep in files:
  text=dep.read_text();external[str(dep)]=sha(dep.read_bytes())
  saved=HERE/'saved-build-metadata'/side/dep.relative_to(build);saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(dep.read_bytes())
  assert 'cpp/profiles/' not in text
  for token in text.replace('\\\n',' ').split():
   path=Path(token)
   if path.is_relative_to(source_root) and path.is_file():
    relative=path.relative_to(source_root).as_posix();relevant[relative]=dict(retained=sha(path.read_bytes()),current=sha((ROOT/relative).read_bytes()))
 assert all(x['retained']==x['current'] for x in relevant.values())
 assert all('cpp/profiles/' not in json.dumps(command) for command in audit['commands'])
 actual_commands=read(build/'compile_commands.json');assert actual_commands==audit['commands']
 (HERE/'saved-build-metadata'/side/'compile_commands.json').write_bytes((build/'compile_commands.json').read_bytes())
 # Snapshot only source/dependency/command metadata, never execute artifact bytes.
 generated={name:sha((build/'generated'/name).read_bytes()) for name in ['models.hpp','models.json']}
 assert generated['models.json']==qualification['binding']['catalogue_file_sha256']
 deps.append(dict(backend=side,compile_commands=13,dependency_files=external,source_dependency_hashes=relevant,generated=generated,profile_references=0))
 sources[str((build/'compile_commands.json'))]=sha((build/'compile_commands.json').read_bytes())
for n in ['tools/build_maxwell_laboratory.py','tools/provision_maxwell_assets.py','cmake/maxwell/CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','cpp/main.cpp','atlas/compiler.py','atlas/model.py','atlas/dsl.py','atlas/stress.py','atlas/structure.py',profile,fused,'docs/reviews/common-scalar-functions-v1/dependent-independent-review/profile-provenance-bindings-v2.json','docs/reviews/common-scalar-functions-v1/dependent-independent-review/build-local-v2/maxwell/profile-provenance-delta.json','docs/reviews/common-scalar-functions-v1/dependent-independent-review/FINAL_REVIEW_V1.md']:
 sources[n]=sha((ROOT/n).read_bytes())
for path in [packet/'observations/inputs.json',packet/'maxwell-qualification.json',packet/'independent-review/final-v1/build-review.json',packet/'compiled-closure-v1.tar.gz',packet/'provenance.json']:
 sources[str(path.relative_to(ROOT))]=sha(path.read_bytes())
(HERE/'dependency-verification.json').write_text(json.dumps(dict(scope='actual retained commands and source .d files; no execution',backends=deps),indent=2)+'\n')
(HERE/'source-pins.json').write_text(json.dumps(dict(files=sources),indent=2)+'\n')
assert not changes;assert len(comparison['changed_physical_lines'])==2
print(json.dumps(dict(current_drift=changes,retained_manifest_files=len(old['files']),current_sha256=current['sha256'],prospective_sha256=future['sha256'],changed_physical_lines=len(comparison['changed_physical_lines']),archive_members=len(members),native_and_wasm_dependency_checks='passed',scope='saved sources and hashes only; no acceptance or material execution'),indent=2))
