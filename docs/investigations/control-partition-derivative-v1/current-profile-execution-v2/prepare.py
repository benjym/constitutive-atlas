"""Source-only reversible rebind. No child processes or artifact calls."""
from pathlib import Path
import json,hashlib,os,shutil
D=Path(__file__).resolve().parent; C=D.parent; V=C/'current-profile-execution-v1'; S=Path('/private/tmp/atlas-control-partition-support-v4/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n')
replacements=[('/private/tmp/atlas-control-partition-support-v3/source',str(S)),('atlas-control-partition-profile-execution-v1','atlas-control-partition-profile-execution-v2'),('current-profile-execution-v1','current-profile-execution-v2')]
proof={}
selected=['RECEIPTS.md','assess_pairs.py','assess_maxwell_presets.py','prepare_maxwell_identity.py','burgers-original-verify.py']+[str(p.relative_to(V))for p in (V/'adapters').glob('*.py')]
for n in selected:
 old=(V/n).read_text();new=old
 for a,b in replacements:new=new.replace(a,b)
 out=D/n;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(new);rev=new
 for a,b in reversed(replacements):rev=rev.replace(b,a)
 assert rev==old
 proof[n]=dict(old_sha256=sha(V/n),new_sha256=sha(out),reverse_exact=True)
p=read(V/'plan.json');old=json.dumps(p)
for a,b in replacements:old=old.replace(a,b)
p=json.loads(old)
p['source_freeze']=str(C/'profile-build-support-v5/source-freeze.json');p['source_files']=2722
path=os.environ['PATH']
env={'PATH':path,'EMCC_CORES':'1','EM_CACHE':'/private/tmp/atlas-predictor-constraints-v1/em-cache-v1'}
# Explicitly suppress ambient compiler/config overrides; collector checks these absent.
for row in p['profiles']:
 row['status']='prospective; closure complete; independent v2 plan review and stage receipts required'
 for step in row['steps']:step['env'].update(env)
for step in p['post_independent_build_review_only']:
 name=step['profile'];step['env']={**env,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(S),'ATLAS_QUALIFICATION_SOURCE':str(S),'ATLAS_QUALIFICATION_OUTPUT':p['execution_base']+'/'+name+'/evidence'}
p['stage_receipts']={'required':'pre and post every stage including failures; source/toolchain/environment exact checks; retain exit status and stdout/stderr separately','collector':str(D/'stage_receipt.py'),'output':'<profile evidence>/stage-receipts/<stage>.<pre|post>.json','independent_review_before_execution':True}
write(D/'plan.json',p)
# Prove all original plan content restores exactly after ONLY declared metadata/env updates.
rev=json.loads(json.dumps(p))
rev.pop('stage_receipts');rev['source_freeze']=read(V/'plan.json')['source_freeze'];rev['source_files']=2628
for i,row in enumerate(rev['profiles']):
 row['status']=read(V/'plan.json')['profiles'][i]['status']
 for st in row['steps']:
  for k in env:st['env'].pop(k)
for st in rev['post_independent_build_review_only']:st.pop('env')
t=json.dumps(rev)
for a,b in reversed(replacements):t=t.replace(b,a)
assert json.loads(t)==read(V/'plan.json')
write(D/'rebind-proof.json',dict(old_manifest=sha(V/'manifest.json'),replacements=replacements,files=proof,plan_restores_exact=True,allowed_metadata=['source_freeze','source_files','profile status','stage env PATH/EMCC_CORES/EM_CACHE','post-review env','stage_receipts']))
f=read(C/'profile-build-support-v5/source-freeze.json')['files'];assert len(f)==2722
assert {str(x.relative_to(S)):sha(x)for x in S.rglob('*')if x.is_file()}==f
oldf=read(C/'qualification-support-v4/source-freeze.json')['files'];assert len(oldf)==2628 and all(f[n]==h for n,h in oldf.items())
cl=read(V/'collector-closure.json');acquired=[]
for x in cl['missing']:assert sha(S/x['path'])==x['sha256'];acquired.append(x)
assert len(acquired)==94
for n,h in cl['files'].items():
 for a,b in replacements:n=n.replace(a,b)
 assert sha(Path(n))==h,n
cl['identity']='seven-profile-executed-input-closure-v2';cl['source_directory']=str(S);cl['files']={n.replace(replacements[0][0],str(S)):h for n,h in cl['files'].items()};cl['missing']=[];cl['resolved_exact']=acquired
for row in cl['profiles']:row['unresolved_static_inputs']=[]
write(D/'collector-closure.json',cl)
sets=read(C/'qualification-support-v4/patched-source-manifests.json')['profiles'];match={}
for name,data in sets.items():
 assert {n:sha(S/n)for n in data['files']}==data['files'];match[name]={'files':len(data['files']),'sha256':hashlib.sha256(json.dumps(data['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()}
write(D/'source-checks.json',dict(passed=True,source_files=2722,preserved_old_files=2628,exact_additions=94,missing=0,matchers=match,compiled_calls=0,source_mutations=0))
write(D/'input-pins.json',{str(x):sha(x)for x in [V/'manifest.json',C/'profile-build-support-v5/manifest.json',C/'profile-build-support-v5/source-freeze.json',C/'profile-build-support-v5/addition-receipt.json',C/'qualification-support-v4/patched-source-manifests.json']})
print('PASS: 2722 source files, 94 additions, zero missing; exact reverse plan/adapters')
