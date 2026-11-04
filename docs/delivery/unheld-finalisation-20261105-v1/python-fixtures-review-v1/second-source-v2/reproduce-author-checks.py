"""Pure complete receipt and original controlled-closure checks; no engines."""
from pathlib import Path
import ast,hashlib,json,tempfile
from unittest.mock import patch
Q=Path(__file__).resolve().parent;O=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/python-historical-contexts-fix-v2');P=O/'proposed';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');V=O.parent/'python-historical-contexts-fix-v1';D='docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2'
sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ok(v,label):
 if not v:raise AssertionError(label)
 checks.append(label)
def fails(f,label):
 try:f()
 except(ValueError,KeyError,FileNotFoundError,AssertionError):checks.append(label);return
 raise AssertionError('accepted '+label)
def effective(n):return(P/n).read_bytes()if(P/n).is_file()else(W/n).read_bytes()
d=json.loads((O/'source-delta.json').read_text())
for row in d['changes']+d['retained_inputs']:
 ok(sha((P/row['path']).read_bytes())==row['sha256'],'payload '+row['path'])
 if row['preimage_sha256']:ok(sha((W/row['path']).read_bytes())==row['preimage_sha256'],'preimage '+row['path'])
 if row['path'].endswith('.py'):ast.parse((P/row['path']).read_text());checks.append('syntax '+row['path'])
# Exact original closure, using unchanged source-only closure function, not its run command.
source=(W/'tools/qualify_controlled_path_refresh.py').read_text();tree=ast.parse(source)
ns={'ROOT':W,'Path':Path,'hashlib':hashlib}
for n in tree.body:
 if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id in('MODEL_PATHS','NORSAND','INTERFACE')for t in n.targets):exec(compile(ast.Module(body=[n],type_ignores=[]),'original-closure-constants','exec'),ns)
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in('sha','relative','closure')]
exec(compile(ast.Module(body=functions,type_ignores=[]),'original-closure-functions','exec'),ns)
actual=ns['closure']();plan=json.loads((O.parent/'controlled-path-refresh-v1/plan-v1.json').read_text())['source_closure']
ok(len(actual)==len(plan)==250,'original closure count exactly250')
ok(actual==plan,'original full250 path and hash set exact')
ok(not any(r['path']in plan for r in d['changes']),'candidate changes none of250 controlled pins')
ok(not any(r['path'].startswith('tests/fixtures/')for r in d['changes']),'candidate adds no fixture closure members')
# A changed hash or added namespace member must still fail the unchanged equality gate.
bad=dict(actual);bad['tests/fixtures/prospective-extra.json']='0'*64;ok(bad!=plan,'added closure file rejected')
bad=dict(actual);bad['tests/historical_generation.py']='0'*64;ok(bad!=plan,'changed original helper rejected')
(Q/'controlled-closure-comparison.json').write_text(json.dumps({'status':'PASS','original_plan_sha256':sha((O.parent/'controlled-path-refresh-v1/plan-v1.json').read_bytes()),'tool_sha256':sha(source.encode()),'count':250,'original_path_hash_set_equal':True,'candidate_controlled_changes':[],'closure':actual},indent=2)+'\n')
# Execute verbatim original checked_receipt against a byte-backed virtual tree.
e=ast.parse((W/'atlas/evidence.py').read_text());env={'Path':Path,'hashlib':hashlib,'json':json}
exec(compile(ast.Module(body=[n for n in e.body if isinstance(n,ast.FunctionDef)and n.name in('_sha','checked_receipt')],type_ignores=[]),'original-checker','exec'),env)
checked=env['checked_receipt'];root=(O/'virtual-proof-root').resolve();store={}
audit=json.loads((O/'tresca-full-receipt-audit.json').read_text())
for row in audit:
 for n in(row['document'],str(Path(row['document']).parent/'source-archive-map.json'),row['path'],row['selected']):
  if n not in store:store[n]=effective(n)
# Complete enumeration must match literal original verify receipt iteration, including unchanged pins.
expected=[];mixed='catalogue/investigations/tresca-mixed-catalogue-v1'
for name in('source-pins.json','dependency-pins.json','prospective-freeze.json','manifest.json'):
 doc=mixed+'/'+name;v=json.loads((W/doc).read_text());pins=v.get('files',v)
 expected += [(doc,n,h)for n,h in pins.items()if isinstance(h,str)and len(h)==64]
ok({(r['document'],r['path'],r['sha256'])for r in audit if r['document'].startswith(mixed)}==set(expected),'ALL four original Tresca receipt pin sets exact')
original_read=Path.read_bytes;original_exists=Path.exists;original_isfile=Path.is_file
key=lambda p:str(p.relative_to(root))if p.is_relative_to(root)else None
def rb(p):
 n=key(p)
 if n is None:return original_read(p)
 if n not in store:raise FileNotFoundError(n)
 return store[n]
def ex(p):
 n=key(p);return n in store if n is not None else original_exists(p)
def text(p,*a,**k):return rb(p).decode()
# Adapter shares exact original ledger bytes; original helper delegates remain unchanged.
ledger=D+'/historical-test-contexts.json';store[ledger]=(P/ledger).read_bytes();store[D+'/source-archive-map.json']=(P/D/'source-archive-map.json').read_bytes()
ok(store[ledger]==(W/'tests/fixtures/historical-test-contexts.json').read_bytes(),'new ledger exact original byte copy')
ledgerdata=json.loads(store[ledger])
for item in ledgerdata['current_models']:
 n=item['path'];store[n]=(W/n).read_bytes();h=item['sha256'];a=f'catalogue/source-snapshots/{h}/{n}'
 if(P/a).is_file()or(W/a).is_file():store[a]=effective(a)
with patch.object(Path,'read_bytes',rb),patch.object(Path,'read_text',text),patch.object(Path,'exists',ex),patch.object(Path,'is_file',ex):
 for row in audit:
  selected=checked(root,row['document'],row['path'],row['sha256'])
  ok(sha(selected.read_bytes())==row['sha256'],'complete receipt '+row['document']+' '+row['path'])
  if row['routed']:
   n=row['selected'];b=store[n];store[n]=b'corrupt'
   fails(lambda:checked(root,row['document'],row['path'],row['sha256']),'corrupt routed archive '+n)
   del store[n];fails(lambda:checked(root,row['document'],row['path'],row['sha256']),'missing routed archive '+n);store[n]=b
 adapter=ast.parse((P/'tests/historical_generation_v03.py').read_text());aenv={'ROOT':root,'LEDGER':root/ledger,'LEDGER_SHA':sha(store[ledger]),'hashlib':hashlib,'json':json,'checked_receipt':checked}
 exec(compile(ast.Module(body=[n for n in adapter.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'adapter-fixture','exec'),aenv)
 for item in ledgerdata['current_models']:ok(sha(aenv['verified'](item).read_bytes())==item['sha256'],'adapter historical byte identity '+item['path'])
 b=store[ledger];store[ledger]=b+b' ';fails(lambda:aenv['verified'](ledgerdata['current_models'][0]),'adapter rejects ledger drift');store[ledger]=b
 bad=dict(ledgerdata['current_models'][0],sha256='0'*64);fails(lambda:aenv['verified'](bad),'adapter rejects unbound hash')
 bad=dict(ledgerdata['current_models'][0],path='../escape');fails(lambda:aenv['verified'](bad),'adapter rejects escape')
imports=[n for n in adapter.body if isinstance(n,ast.ImportFrom)and n.module=='tests.historical_generation']
ok(len(imports)==1 and {n.name for n in imports[0].names}=={'contexts','public_models','public_paths','catalogue','generate'},'adapter delegates all original public helpers')
for n in('tests/historical_generation.py','tests/fixtures/source-archive-map.json'):
 ok(sha((W/n).read_bytes())==plan[n],'original controlled helper/map restored '+n)
for n in('tests/test_historical_generation.py','tests/test_controlled_time.py','tests/historical_burgers.py','tests/historical_mcc_reference.py'):
 before=(V/'proposed'/n).read_text().replace('tests/fixtures/current-sixteen-baseline-v03-v1.json',D+'/current-sixteen-baseline-v03-v1.json').replace('tests/fixtures/historical-routing-v1.json',D+'/historical-routing-v1.json').replace('from tests.historical_generation import contexts, public_models, public_paths, verified','from tests.historical_generation_v03 import contexts, public_models, public_paths, verified')
 ok(before==(P/n).read_text(),'v1 source preserved except declared locator '+n)
report={'status':'PASS','checks':len(checks),'labels':checks,'full_tresca_pin_count':len(audit),'routed_count':sum(r['routed']for r in audit),'controlled_count':250,'execution':'source-only; no material/module/compiler/generate/browser/network/Git'}
(Q/'manufactured-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k]for k in('status','checks','full_tresca_pin_count','routed_count','controlled_count')}))
