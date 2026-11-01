"""Pure source/receipt mocks; no build, collector or Atlas calls."""
if not __debug__:raise RuntimeError('Unoptimized Python is required')
from pathlib import Path
import json,hashlib,ast,importlib.util,os,subprocess,sys
D=Path(__file__).resolve().parent;V=D.parent/'current-profile-execution-v2'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(D/'plan.json');old=read(V/'plan.json');pr=read(D/'rebind-proof.json');assert pr['old_manifest']==sha(V/'manifest.json')=='eebf5d8be93aa8d385fdf74d793d6dde22d6f571e21889f7a924fa2429455669'
for n,d in pr['files'].items():
 assert sha(V/n)==d['old_sha256']and sha(D/n)==d['new_sha256'];t=(D/n).read_text()
 for a,b in reversed(pr['replacements']):t=t.replace(b,a)
 assert t==(V/n).read_text()
r=json.loads(json.dumps(p));r['stage_receipts']['required']=old['stage_receipts']['required']
for row in r['profiles']:
 for st in row['steps']:
  assert st['env'].pop('PYTHONOPTIMIZE')=='0' and '-O'not in st['argv']and '-OO'not in st['argv']
for st in r['post_independent_build_review_only']:assert st['env'].pop('PYTHONOPTIMIZE')=='0'
t=json.dumps(r)
for a,b in reversed(pr['replacements']):t=t.replace(b,a)
assert json.loads(t)==old
assert read(D/'toolchain.json')['files']==read(V/'toolchain.json')['files']
assert read(D/'toolchain.json')['environment']['PYTHONOPTIMIZE']=='0'
spec=importlib.util.spec_from_file_location('receipt',D/'stage_receipt.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ident=m.verify({**os.environ,**p['profiles'][0]['steps'][0]['env']})
wanted=dict(identity='current-profile-stage-receipt-v3',phase='pre',profile='power-creep',stage='native-configure',packet_manifest_sha256='packet',command=p['profiles'][0]['steps'][0],**ident)
good={**wanted,'passed':True};m.validate_pre(good,wanted);negative=0
for k in wanted:
 bad=dict(good);bad[k]='wrong'
 try:m.validate_pre(bad,wanted)
 except ValueError:negative+=1
 else:raise AssertionError('accepted wrong '+k)
for value in [False,1,'yes',None]:
 bad={**good,'passed':value}
 try:m.validate_pre(bad,wanted)
 except ValueError:negative+=1
 else:raise AssertionError('accepted passed '+repr(value))
for k in wanted:
 bad=dict(good);bad.pop(k)
 try:m.validate_pre(bad,wanted)
 except ValueError:negative+=1
 else:raise AssertionError('accepted missing '+k)
for status in [1,7,-9,None,False]:
 result={'passed':False}
 try:m.finish_post(result,good,wanted,status,{'sha256':'out'},{'sha256':'err'},'pre')
 except ValueError:pass
 else:raise AssertionError('accepted nonzero/nonint')
 assert result['passed']is False and result['exit_status']==status and result['stdout']['sha256']=='out'and result['stderr']['sha256']=='err'
result={'passed':False};m.finish_post(result,good,wanted,0,{'sha256':'out'},{'sha256':'err'},'pre');assert result['passed']is True
# Entry guard must work even when environment says0 but CLI forces optimization.
cp=subprocess.run([sys.executable,'-O',str(D/'stage_receipt.py'),'--help'],env={**os.environ,'PYTHONOPTIMIZE':'0'},capture_output=True,text=True)
assert cp.returncode!=0 and 'Unoptimized Python is required'in cp.stderr
# Verify guard itself must reject optimized code independently of entry guard.
tree=ast.parse((D/'stage_receipt.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='verify');ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'verify-only','exec',optimize=1),ns)
try:ns['verify']({})
except RuntimeError as e:assert 'Unoptimized'in str(e)
else:raise AssertionError('optimized verify bypass')
for f in D.rglob('*.py'):ast.parse(f.read_text())
checks=dict(passed=True,**ident,plan_steps=sum(len(x['steps'])for x in p['profiles']),reverse_plan=True,reverse_files=len(pr['files']),pre_rejection_mocks=negative,failed_exit_retention_mocks=5,zero_exit_mock=True,optimizer_entry_rejected=True,optimizer_verify_rejected=True,compiled_atlas_calls=0,builds=0,source_mutations=0)
(D/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');(D/'optimizer-mock.json').write_text(json.dumps(dict(argv=['python','-O','stage_receipt.py','--help'],environment={'PYTHONOPTIMIZE':'0'},exit_status=cp.returncode,stdout=cp.stdout,stderr=cp.stderr),indent=2)+'\n');print(json.dumps(checks))
