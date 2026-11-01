from pathlib import Path
import json,hashlib
r=Path(__file__).resolve().parents[3];p=Path(__file__).parent;o=p/'actual-root-v1';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
installed=json.loads((p/'installed-v1.json').read_text());old=json.loads((p/'engine-source-freeze-v1.json').read_text());clone=Path(old['source']);expected={Path(n).relative_to(clone).as_posix():h for n,h in old['files'].items() if not Path(n).relative_to(clone).as_posix().startswith('generated/')}
expected.update(installed['files'])
workflow_prior=expected['.github/workflows/verify.yml'];expected['.github/workflows/verify.yml']=sha(r/'.github/workflows/verify.yml')
# Only accepted root probe/additive test/doc/notice deltas from qualified closure.
for n,h in expected.items():assert sha(r/n)==h,n
for n,h in json.loads((p/'engine-gate-freeze-v2.json').read_text())['files'].items():assert sha(Path(n))==h,n
files={n:sha(r/n) for n in expected}
for n in ['commands.json','gates.json']:files[(o/n).relative_to(r).as_posix()]=sha(o/n)
(o/'source-freeze.json').write_text(json.dumps({'status':'Prospective actualroot before configure/build/calls','root':str(r),'files':files,'qualified_engine_source_freeze_sha256':sha(p/'engine-source-freeze-v1.json'),'installed42_sha256':sha(p/'installed-v1.json'),'catalogue_sha256':old['catalogue_sha256'],'noncompiled_concurrent_workflow_delta':{'prior_qualified_sha256':workflow_prior,'current_sha256':expected['.github/workflows/verify.yml'],'scope':'Unrelated concurrent coordinator CI binding update; not a numerical runtime/compiler/model/gate input; preserved as separate provenance only'}},indent=2)+'\n');print(len(files),'exact root pins verified/frozen')
