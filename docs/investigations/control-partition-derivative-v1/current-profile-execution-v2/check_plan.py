"""Source-only independent reversal/identity check. No child processes."""
import ast,hashlib,json,os,importlib.util
from pathlib import Path
D=Path(__file__).resolve().parent;V=D.parent/'current-profile-execution-v1'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(D/'plan.json');old=read(V/'plan.json');pr=read(D/'rebind-proof.json')
assert sha(V/'manifest.json')==pr['old_manifest']=='1c21734488ba4ec34c71653c8f532e2a935877de9273bddaab8fe8c6a6e035ab'
assert sha(D.parent/'profile-build-support-v5/manifest.json')=='dc12055af1fe54a8ea7f6ab0e14ae3808c1afa52b74341d7ea0f03e7eeece8bc'
for n,data in pr['files'].items():
 assert sha(V/n)==data['old_sha256'] and sha(D/n)==data['new_sha256'];t=(D/n).read_text()
 for a,b in reversed(pr['replacements']):t=t.replace(b,a)
 assert t==(V/n).read_text()
r=json.loads(json.dumps(p));r.pop('stage_receipts');r['source_freeze']=old['source_freeze'];r['source_files']=2628
for i,row in enumerate(r['profiles']):
 row['status']=old['profiles'][i]['status']
 for st in row['steps']:
  for k in ['PATH','EMCC_CORES','EM_CACHE']:st['env'].pop(k)
for st in r['post_independent_build_review_only']:st.pop('env')
t=json.dumps(r)
for a,b in reversed(pr['replacements']):t=t.replace(b,a)
assert json.loads(t)==old
spec=importlib.util.spec_from_file_location('receipt',D/'stage_receipt.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
env={**os.environ,**p['profiles'][0]['steps'][0]['env']};ident=m.verify(env)
# Adversarial environment changes must fail before accepting identity.
for key,val in [('PATH','/usr/bin'),('EMCC_CORES','2'),('EM_CACHE','/tmp/wrong'),('CXX','other')]:
 bad=dict(env);bad[key]=val
 try:m.verify(bad)
 except AssertionError:pass
 else:raise AssertionError('accepted '+key)
for path in D.rglob('*.py'):ast.parse(path.read_text())
assert sum(len(x['steps'])for x in p['profiles'])==65
assert read(D/'collector-closure.json')['missing']==[]
result=dict(identity='current-profile-execution-v2-source-checks',passed=True,**ident,reverse_plan=True,reverse_adapters=len(pr['files']),source_missing=0,environment_negative_checks=4,commands=65,compiled_calls=0,source_mutations=0,independent_review_required=True)
(D/'checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
