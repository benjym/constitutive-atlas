"""Pure prospective source/freeze validation. No configure/build/material call."""
import hashlib,importlib.util,json,re,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'docs/ingestion/maxwell-itasca900/atlas-build-v1';f=json.loads((BASE/'freeze.json').read_text());D=Path(f['source_root'])
sha=lambda b:hashlib.sha256(b).hexdigest()
rows={e['path']:e for e in f['files']};assert len(rows)==len(f['files'])==114
actual={str(p.relative_to(D)) for p in D.rglob('*') if p.is_file()};assert actual==set(rows)
for n,e in rows.items():
 p=D/n;assert not p.is_symlink();b=p.read_bytes();assert sha(b)==e['sha256'] and len(b)==e['bytes'],n
manifest=f['runtime_source_manifest'];assert len(manifest['files'])==101
assert sha(json.dumps(manifest['files'],sort_keys=True,separators=(',',':')).encode())==manifest['sha256']=='f03b7fd76aa0d275f29e05f96b4484f67195a6c71e7d3678e8f76b5b37b03852'
for n,h in manifest['files'].items():assert rows[n]['sha256']==h and sha((ROOT/n).read_bytes())==h,n
# Walk the dedicated target's reachable quoted headers. The generated model
# header has the compiler's fixed trace/expression/exponential support includes.
includes=0;pending=['cpp/main.cpp','cpp/include/atlas/expm.hpp','cpp/include/atlas/checked_trace.hpp','cpp/include/atlas/checked_expression.hpp'];visited=set()
while pending:
 n=pending.pop()
 if n in visited:continue
 visited.add(n);assert n in rows;npath=D/n
 for name in re.findall(r'^\s*#\s*include\s*"([^"]+)"',npath.read_text(),re.M):
  if name=='models.hpp':continue
  options=[npath.parent/name,D/'cpp/include'/name,D/'cpp'/name]
  found=next((x for x in options if x.is_file() and str(x.relative_to(D)) in rows),None)
  assert found is not None,(n,name)
  pending.append(str(found.relative_to(D)));includes+=1
# Dedicated CMake's model wildcard has the same exact singleton on each side.
assert sorted(p.name for p in (ROOT/'models/research/maxwell').glob('*.json'))==sorted(p.name for p in (D/'models/research/maxwell').glob('*.json'))==['maxwell-itasca900-zero-spin-ode.json']
# One recorded path-only patch is the only source/driver delta.
patches=f['driver_path_patches'];assert len(patches)==1
patch=patches[0];old=(BASE/'original-drivers/check_transactions.py').read_bytes();new=(D/patch['path']).read_bytes()
assert sha(old)==patch['original_sha256'] and sha(new)==patch['frozen_sha256']
assert old==(ROOT/patch['path']).read_bytes()
assert old.count(b'/private/tmp/atlas-maxwell-execution-v1/cli')==1
assert new==old.replace(b'/private/tmp/atlas-maxwell-execution-v1/cli',b'/private/tmp/atlas-maxwell-current-v1/cli')
for n in rows:
 if n not in manifest['files'] and n!=patch['path']:assert (ROOT/n).read_bytes()==(D/n).read_bytes(),n
refs=json.loads((D/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json').read_text());assert len(refs['cases'])==24
assert sha((D/'docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json').read_bytes())=='f29bf379737a1cfa98c4345660f938561412a181e83e89e7411efceff28e0e96'
assert sha((D/'tests/test_maxwell.py').read_bytes())=='57868b967d9f992b723d08944c6c5a4d1dee545a621a7d33ce9199c0c6a9c643'
assert sha((D/'tools/test_maxwell_wasm.mjs').read_bytes())=='4cb432c65709dea50ae3b10316e5f8f90960542afb0b6bee48bfd183943e150f'
# Historical parity-v2 and reference budgets remain byte-identical.
for n in ['compare_backends_v2.py','PLAN.md']:
 name='docs/ingestion/maxwell-itasca900/integration-v1/'+n;assert (ROOT/name).read_bytes()==(D/name).read_bytes()
assert sum(not c['ok'] for c in refs['cases'])==6
assert sum(c['ok'] and c['kind']=='direct' for c in refs['cases'])==11
assert sum(c['ok'] and c['kind']=='schedule' for c in refs['cases'])==7
assert all(c['tolerance']==.05 for c in refs['cases'] if c['ok'] and c['kind']=='direct')
assert all(c['tolerance']==(1000 if c['id']=='refine-coarse' else 15) and c['strain_tolerance']==2e-7 for c in refs['cases'] if c['ok'] and c['kind']=='schedule')
commands=json.loads((BASE/'prospective-commands.json').read_text())
for key in ['native_build','wasm_build']:
 c=commands['commands'][key];assert c[c.index('--target')+1]=='atlas_maxwell_solver' and c[c.index('--parallel')+1]=='1'
assert commands['cwd']==str(D)
for key in ['native_main','native_transactions','wasm_main','wasm_analytical_assess','wasm_transactions','parity','assess_native_presets']:
 assert key in commands['commands'],key
mapping={'relaxation':'relaxation-schedule','creep':'creep-schedule','oedometer':'oedometer','load-hold-reverse':'load-hold-reverse'}
assert commands['preset_mapping']==mapping
for name,cid in mapping.items():
 assert json.loads((D/'examples/maxwell'/f'{name}.json').read_text())==next(c['specification'] for c in refs['cases'] if c['id']==cid)
 assert 'native_preset_'+name in commands['commands']
supp=json.loads((BASE/'supplemental-driver-freeze.json').read_text())
assert sha((ROOT/supp['path']).read_bytes())==supp['sha256']==commands['new_assessor_sha256']
identity=json.loads((BASE/'source-closure-identity.json').read_text());archive=ROOT/identity['path']
assert sha(archive.read_bytes())==identity['sha256'] and archive.stat().st_size==identity['bytes']
with tarfile.open(archive,'r:gz') as tf:
 members=tf.getmembers(); assert len(members)==117 and all(m.isfile() and not m.name.startswith('/') and '..' not in Path(m.name).parts for m in members)
 for m in members:
  expected=(D/m.name) if m.name in rows else (ROOT/m.name)
  assert tf.extractfile(m).read()==expected.read_bytes(),m.name
assert f['compiled_calls']==0
print(json.dumps({'passed':True,'mirror_files':len(rows),'runtime_source_files':len(manifest['files']),'runtime_source_manifest_sha256':manifest['sha256'],'resolved_project_header_includes':includes,'unchanged_main_cases':24,'prospective_supplementary_cases':14,'prospective_calls_per_backend':76,'only_delta':'one documented temporary CLI directory replacement','builds':0,'compiled_calls':0},indent=2))
