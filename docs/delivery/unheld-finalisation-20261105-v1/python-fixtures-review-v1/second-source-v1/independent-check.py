from pathlib import Path
import ast,hashlib,json
Q=Path(__file__).resolve().parent
O=Q.parents[1]/'python-historical-contexts-fix-v1';P=O/'proposed';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
H=lambda b:hashlib.sha256(b).hexdigest()
checks=[]
def ok(value,label):
 assert value,label
 checks.append(label)
expected='8d6e3b2e8dea8fc251baad63aa27e1ba431c2db528c3672c2f8481478fe89c82'
ok(H((O/'manifest.json').read_bytes())==expected,'exact frozen proposal manifest')
m=json.loads((O/'manifest.json').read_text())
for row in m['files']:
 n=Path(row['path']);ok(not n.is_absolute() and '..' not in n.parts and not(O/n).is_symlink(),'safe literal member '+str(n))
 b=(O/n).read_bytes();ok(H(b)==row['sha256'] and len(b)==row['size_bytes'],'manifest member '+str(n))
ok(len(m['files'])==75,'all75 members')
ok(H((O/'source-delta.json').read_bytes())=='aedc5eb770aa18834f917bd58f669cedbd750a49a05d1690a6f464f8bb3670c3','exact delta')
d=json.loads((O/'source-delta.json').read_text());ok(len(d['changes'])==36 and len(d['retained_inputs'])==12,'36changes12retained')
paths=[r['path'] for r in d['changes']+d['retained_inputs']];ok(len(set(paths))==48,'unique48payloads')
for row in d['changes']+d['retained_inputs']:
 n=row['path'];b=(P/n).read_bytes();ok(H(b)==row['sha256'] and len(b)==row['size_bytes'],'delta successor '+n)
 if row['preimage_sha256']:
  old=(W/n).read_bytes();ok(H(old)==row['preimage_sha256'],'current exact preimage '+n)
  if row in d['changes']:
   archive=P/'catalogue/source-snapshots'/row['preimage_sha256']/n
   ok(archive.read_bytes()==old,'old bytes durable before replacement '+n)
 else:ok(not(W/n).exists(),'newpath absent '+n)
 if n.endswith('source-archive-map.json') and n.startswith(('tests/fixtures/','catalogue/agent-reviews/','catalogue/investigations/','docs/')):
  before=json.loads((W/n).read_text());after=json.loads(b)
  ok(all(after[k]==v for k,v in before.items() if k not in ('documents','entries')),'sidecar metadata preserved '+n)
  ok(all(after['documents'].get(k)==v for k,v in before['documents'].items()),'all old document pins preserved '+n)
  ok(all(e in after['entries'] for e in before['entries']),'all old routes preserved '+n)
  for doc,pin in after['documents'].items():ok(H((W/doc).read_bytes())==pin,'exact immutable document '+doc)
  pairs=[]
  for e in after['entries']:
   name=e['original_path'];pin=e['sha256'];a=f'catalogue/source-snapshots/{pin}/{name}'
   ok(e['archived_path']==a,'strict hash address '+name)
   b=(P/a).read_bytes() if(P/a).exists()else(W/a).read_bytes()
   ok(H(b)==pin,'every archive independently hashed '+a);pairs.append((name,pin))
  ok(len(pairs)==len(set(pairs)),'no ambiguous map routes '+n)
# New current16 context is a literal copy of full current definitions, with no generation.
f=json.loads((P/'tests/fixtures/current-sixteen-baseline-v03-v1.json').read_text());models=sorted((W/'models').glob('*.json'))
ok([r['path'] for r in f['models']]==[str(x.relative_to(W)) for x in models] and len(models)==16,'exact16 full canonical membership')
c=json.loads((P/f['catalogue']['path']).read_text());raw=[json.loads(x.read_text()) for x in models]
ok(c['models']==raw,'all16 catalogue literal source objects identical')
ok(c['sha256']==H(json.dumps(raw,sort_keys=True,separators=(',',':')).encode())=='beb2f2b422c77502cc41c91b1c68921fd9db89f1b7dbc2e4f0368526d627e575','unchanged canonical catalogue digest')
ok(H((P/f['catalogue']['path']).read_bytes())==f['catalogue']['sha256'],'catalogue byte pin')
ok(H((W/f['authority']['decision']).read_bytes())==f['authority']['sha256'],'independent actual qualification authority pin')
# Compare whole original test AST after the precisely declared locator substitutions.
for old in sorted((O/'original/tests').glob('test_*.py')):
 text=old.read_text().replace('current-sixteen-sclay1-v1','current-sixteen-baseline-v03-v1')
 text=text.replace('self.assertTrue(set(paths) < current_paths)','self.assertTrue(historical_names < current_paths)').replace("        for item in live['models']:","        for item in live['models']:")
 if old.name=='test_historical_generation.py':text=text.replace('        self.assertTrue(historical_names < current_paths)',"        historical_names = {ROOT / item['path'] for item in data['current_models']}\n        self.assertTrue(historical_names < current_paths)")
 text=text.replace('preserved_model(ROOT,Path(name).name)','preserved_model(ROOT,Path(name).name,pin)').replace('preserved_model(ROOT,p.name)','preserved_model(ROOT,p.name,hashlib.sha256(p.read_bytes()).hexdigest())').replace("str(R/'verify.py')","str(ROOT/'tests/historical_burgers.py')").replace('from tools.analyze_mcc_continuous import analyze,analyze_followups','from tests.historical_mcc_reference import analyze,analyze_followups')
 ok(ast.dump(ast.parse(text),include_attributes=False)==ast.dump(ast.parse((P/'tests'/old.name).read_text()),include_attributes=False),'WHOLE original test AST only exact locator changes '+old.name)
# Original implementation inputs are untouched and literal pinned; no replacement of numerical functions.
ctx=json.loads((P/'tests/fixtures/historical-routing-v1.json').read_text())
for n,pin in ctx['pins'].items():ok(H((W/n).read_bytes())==pin,'original delegate implementation unchanged '+n)
original=ast.parse((W/'docs/ingestion/burgers-itasca900/integration-v1/verify.py').read_text())
v=next(x for x in original.body if isinstance(x,ast.FunctionDef) and x.name=='verify')
installed=next(x for x in v.body if isinstance(x,ast.If) and isinstance(x.test,ast.Name) and x.test.id=='installed')
ok(len([x for x in ast.walk(installed) if isinstance(x,ast.Assert)])==4,'all four original installed assertion families identified and reviewed')
report={'status':'accepted','checks':len(checks),'labels':checks,'scope':'source, literal data, immutable receipts and AST only; no generated/runtime/numerical execution'}
(Q/'independent-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
