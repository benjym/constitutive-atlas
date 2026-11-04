from pathlib import Path
import json,hashlib,ast,re
Q=Path(__file__).resolve().parent;N=Q.parents[1];A=N/'python-historical-contexts-actual-v2';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();labels=[]
def ok(v,s):assert v,s;labels.append(s)
p=A/'plan.json';ok(H(p)=='ffccf91e55ebd97912c6aefa45a5eaefa780925c6bf982f4c7773c07b02b7270','exact prospective actual plan')
plan=json.loads(p.read_text());ok(H(Path(plan['observer']))==plan['observer_sha256']=='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e','original observer source unchanged')
ok(plan['timeout']==1800,'original1800 timeout')
ok(H(N/'python-fixtures-review-v1/first-decision.json')==plan['A_review_sha256']=='25ecb38ccca651069a26a1473be90604cebdc53132d87a406506ab0eefba9639','accepted A decision')
ok(H(N/'python-fixtures-review-v1/second-source-v2/decision.json')==plan['B_review_sha256']=='f3eb83e420ec5f94780785407922d92de76dd415745439b1b6ff3e850c837baa','accepted B2 decision')
ok(H(Path(plan['env']['ATLAS_SOLVER']))==plan['runtime_sha256']=='606852e570c5d9082cec8b7281096ca352397de7b9c029e0630b5dca26c90747','unchanged qualified native runtime')
installation=json.loads((A/'installation.json').read_text());d=json.loads((N/'python-historical-contexts-fix-v2/source-delta.json').read_text());ok(installation['delta']==d and installation['review_sha256']==plan['B_review_sha256'],'actual installation exactly source-approved delta')
for row in d['changes']+d['retained_inputs']:
 ok(H(W/row['path'])==row['sha256'],'current exact B2 payload '+row['path'])
 if row in d['changes']and row['preimage_sha256']:ok(H(A/'preimages'/row['path'])==row['preimage_sha256'],'actual retained preimage '+row['path'])
r=json.loads((A/'observer/receipt.json').read_text());ok(r['argv']==plan['argv']and r['cwd']==plan['cwd'],'receipt original exact launch argv/cwd')
ok(r['returncode']==r['reaped_returncode']==0 and r['mandatory_reap']and r['status']=='passed'and r['cleanup_errors']==[] and r['signals_during_finalization']==[],'genuine observed pass mandatory reap and clean close')
for key in ('executable','stdout','stderr'):
 x=r[key];ok(H(Path(x['path']))==x['sha256'] and Path(x['path']).stat().st_size==x['bytes'],'actual '+key+' bytes/pin')
output=(A/'observer/stderr.raw').read_text();ok(bool(re.search(r'Ran 128 tests in 28\.806s\n\nOK\n',output)),'actual128 tests OK 28.806s')
actual=re.findall(r'^test_\w+ \(([^)]+)\) \.\.\. ok$',output,re.M);expected=[];mods=plan['argv'][4:-1];ok(len(mods)==18,'all18 modules')
for mod in mods:
 for c in ast.parse((W/(mod.replace('.','/')+'.py')).read_text()).body:
  if isinstance(c,ast.ClassDef):
   for f in c.body:
    if isinstance(f,ast.FunctionDef)and f.name.startswith('test_'):expected.append(mod+'.'+c.name+'.'+f.name)
ok(len(actual)==len(expected)==128 and sorted(actual)==sorted(expected),'all128 exact original test AST names once and pass; no skips')
freeze=N/'current16-qualification-plan-v1/source-freeze-v1.json';ok(H(freeze)=='eaf7ee22f2605dd2d4e366fa1c6a97ee33f46f16a8884c02a540903dba1af8d3','original source freeze unchanged')
f=json.loads(freeze.read_text());changed=[]
for row in f['inputs']:
 p=Path(row['path']);digest=H(p)
 if digest!=row['sha256']:changed.append({'path':str(p.relative_to(W)),'old_sha256':row['sha256'],'new_sha256':digest})
e=json.loads((N/'final-source-equivalence-python-fixtures-v2.json').read_text());ok(len(f['inputs'])==799 and len(changed)==5 and changed==e['changed_inputs'],'independently rehashed original799 exactly794 unchanged5 declared tool deltas')
# These five are all previously reviewed, never scientific/model/compiler/runtime sources.
allowed={'tools/build_experiments.py':'ac4a43fb38f9282db5972084cd911b1bef6125bb9b37ac0a070f944b26bb61b4','tools/check_native_fixture_contracts.py':'9aba8b8e63b345161b2eb1b9eb578ff2b889221cf199f581f241564924d48f81','tools/test_experiments.mjs':'31f380d1668fdbd04a4e9ba9542b463d58bf30322e688a5f5ae34f70226b6906','tools/test_numerics.mjs':'8381f20d6523b28698bb0f951bbbf211161e1cf292091c1b96fb0841d057b146','tools/test_recorded.mjs':'64ce5390fedda14aaff03a44ee6794ced587be4359e7ae6b4fb92457eec0a459'}
ok({x['path']:x['new_sha256']for x in changed}==allowed,'exact independently accepted five tool successors only')
# Pure source discovery: unchanged actual250 closure and namespace membership.
t=ast.parse((W/'tools/qualify_controlled_path_refresh.py').read_text());env={'ROOT':W,'Path':Path,'hashlib':hashlib};nodes=[]
for n in t.body:
 if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id in('MODEL_PATHS','NORSAND','INTERFACE')for x in n.targets):nodes.append(n)
 if isinstance(n,ast.FunctionDef)and n.name in('sha','relative','closure'):nodes.append(n)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'source-only-discovery','exec'),env)
c=env['closure']();ok(len(c)==250 and c==json.loads((N/'controlled-path-refresh-v1/plan-v1.json').read_text())['source_closure'],'fresh installed discovered closure exactly original250')
(Q/'checks.json').write_text(json.dumps({'status':'PASS','checks':len(labels),'labels':labels,'tests':actual,'changed_original_inputs':changed,'controlled_count':250},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(labels),'tests':len(actual)}))
