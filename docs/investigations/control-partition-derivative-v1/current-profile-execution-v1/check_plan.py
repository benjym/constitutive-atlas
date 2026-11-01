"""Read-only prospective plan/source/adapters proof; never launches a process."""
import ast,hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;S=Path('/private/tmp/atlas-control-partition-support-v3/source');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());p=read(D/'plan.json');f=read(D.parent/'qualification-support-v4/source-freeze.json');files=f.get('files',f.get('source_files'));assert len(files)==2628
for n,h in files.items():assert sha(S/n)==h,n
assert sorted(files)==sorted(str(p.relative_to(S))for p in S.rglob('*')if p.is_file())
for n,h in read(D/'preparation-inputs.json').items():assert sha(Path(n))==h,n
for name,entry in read(D/'adapter-proof.json').items():
 if 'replacements'in entry:
  original=Path(entry['source']).read_text();new=(D/'adapters'/name).read_text();assert hashlib.sha256(original.encode()).hexdigest()==entry['source_sha256'];assert hashlib.sha256(new.encode()).hexdigest()==entry['adapter_sha256'];reverse=new
  for r in reversed(entry['replacements']):reverse=reverse.replace(r['replacement'],r['original'])
  assert reverse==original,name
 elif entry.get('exact_reuse'):assert sha(D/'adapters'/name)==entry['sha256']
closure=read(D/'collector-closure.json');assert len(closure['missing'])==94 and all(x['available_exact']for x in closure['missing']);assert sum(x['profile']=='power-creep'for x in closure['missing'])==93
for name,h in closure['files'].items():assert sha(Path(name))==h,name
for path in D.rglob('*.py'):ast.parse(path.read_text())
for row in p['profiles']:
 for step in row['steps']:
  assert step['cwd']==str(S)and step['env']['ATLAS_QUALIFICATION_SOURCE']==str(S)
  if '--build'in step['argv']:assert step['argv'][-2:]==['--parallel','1']and step['argv'].count('--target')==1
assert [r['profile']for r in p['profiles']]==['power-creep','burgers','sls','j2','orthotropic','maxwell','norsand'];assert len(p['profiles'])==7
assert read(D.parent/'qualification-support-v2/j2-paths-with-public-preset.json')==read(S/'docs/ingestion/j2-linear-hardening/execution-v2/paths.json')+[read(S/'docs/ingestion/j2-linear-hardening/delivery-v1/preset-references.json')]
sets=read(D.parent/'qualification-support-v4/patched-source-manifests.json')['profiles'];matcher={}
for name,data in sets.items():
 current={n:sha(S/n)for n in data['files']};assert current==data['files'];digest=hashlib.sha256(json.dumps(current,sort_keys=True,separators=(',',':')).encode()).hexdigest();matcher[name]=dict(files=len(current),sha256=digest)
assert matcher['maxwell']['files']==149 and matcher['norsand']['files']==121
result=dict(identity='current-profile-plan-source-checks-v1',passed=True,source_files=2628,profile_commands=sum(len(x['steps'])for x in p['profiles']),source_inputs=len(closure['files']),missing_exact_available=94,power_missing=93,burgers_missing_host=1,matchers=matcher,compiled_calls=0,source_mutations=0,independent_plan_review_required=True)
(D/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
