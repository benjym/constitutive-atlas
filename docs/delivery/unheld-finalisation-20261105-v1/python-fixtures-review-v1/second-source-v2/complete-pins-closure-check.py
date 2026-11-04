from pathlib import Path
import ast,hashlib,json
Q=Path(__file__).resolve().parent;N=Q.parents[1];O=N/'python-historical-contexts-fix-v2';P=O/'proposed';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
H=lambda b:hashlib.sha256(b).hexdigest();labels=[]
def ok(b,s):assert b,s;labels.append(s)
def eff(n):return(P/n).read_bytes()if(P/n).is_file()else(W/n).read_bytes()
# Enumerate exactly original mixed verify and source-review verify consumed receipt pairs.
expected=[];mixed='catalogue/investigations/tresca-mixed-catalogue-v1';review='docs/reviews/tresca-v5-source-integration-v1'
for n in ('source-pins.json','dependency-pins.json','prospective-freeze.json','manifest.json'):
 doc=mixed+'/'+n;d=json.loads((W/doc).read_text());expected.extend((doc,k,v)for k,v in d.get('files',d).items()if isinstance(v,str)and len(v)==64)
doc=review+'/source-pins.json';expected.extend((doc,k,v)for k,v in json.loads((W/doc).read_text()).items())
doc=review+'/manifest.json';expected.extend((doc,r['path'],r['sha256'])for r in json.loads((W/doc).read_text())['files'])
audit=json.loads((O/'tresca-full-receipt-audit.json').read_text());actual=[(r['document'],r['path'],r['sha256'])for r in audit]
ok(len(actual)==len(expected)==535 and sorted(actual)==sorted(expected),'full535 receipt observations exactly match both original consumers')
for row in audit:
 doc,n,pin=row['document'],row['path'],row['sha256'];mapping=json.loads(eff(str(Path(doc).parent/'source-archive-map.json')))
 ok(H((W/doc).read_bytes())==mapping['documents'][doc],'original receipt exact '+doc)
 matches=[r for r in mapping['entries']if r['original_path']==n and r['sha256']==pin]
 ok(len(matches)<=1,'unambiguous source pair '+n)
 selected=matches[0]['archived_path']if matches else n
 ok(row['selected']==selected and row['routed']==bool(matches),'independent route agrees '+n)
 if matches:ok(selected==f'catalogue/source-snapshots/{pin}/{n}','strict archive address '+n)
 ok(H(eff(selected))==pin,'complete selected original bytes '+n)
ok(sum(r['routed']for r in audit)==74,'all74 exact routed observations')
# Recompute closure with exact previously accepted tool: source constants/functions only.
tool=W/'tools/qualify_controlled_path_refresh.py';accepted=N/'controlled-path-refresh-plan-v1/proposed/tools/qualify_controlled_path_refresh.py'
ok(tool.read_bytes()==accepted.read_bytes(),'qualifier original accepted tool byteexact')
planpath=N/'controlled-path-refresh-v1/plan-v1.json';ok(H(planpath.read_bytes())=='ed7839d19ec5c5b3615f5bf54d2e6273b8ec19fbe811f12a0336938c42581361','original actual controlled plan byteexact')
t=ast.parse(tool.read_text());env={'ROOT':W,'Path':Path,'hashlib':hashlib};nodes=[]
for node in t.body:
 if isinstance(node,ast.Assign)and any(isinstance(x,ast.Name)and x.id in ('MODEL_PATHS','NORSAND','INTERFACE')for x in node.targets):nodes.append(node)
 if isinstance(node,ast.FunctionDef)and node.name in ('sha','relative','closure'):nodes.append(node)
exec(compile(ast.Module(body=nodes,type_ignores=[]),'only-original-source-discovery','exec'),env)
closure=env['closure']();plan=json.loads(planpath.read_text())['source_closure']
ok(len(closure)==250 and closure==plan,'actual entire discovered250 path/hash map equality')
delta=json.loads((O/'source-delta.json').read_text());changes=delta['changes'];ok(not any(r['path']in closure for r in changes),'none of39 changes alter closure members')
# Exact closure source selectors show candidate new paths are not discovered.
fun=next(x for x in nodes if isinstance(x,ast.FunctionDef)and x.name=='closure')
(Q/'original-closure-function.txt').write_text(ast.get_source_segment(tool.read_text(),fun)+'\n')
ok(not any(r['path'].startswith('tests/fixtures/')for r in changes),'no new namespace fixture member')
for n in ('tests/historical_generation.py','tests/fixtures/source-archive-map.json'):
 ok(H((W/n).read_bytes())==plan[n] and not(P/n).exists(),'original helper/map unchanged and not targeted '+n)
# Adapter keeps the exact immutable ledger, expected literal SHA and public original delegates.
D='docs/delivery/unheld-finalisation-20261105-v1/python-historical-routing-v2'
ledger=(P/D/'historical-test-contexts.json').read_bytes();ok(ledger==(W/'tests/fixtures/historical-test-contexts.json').read_bytes(),'adapter exact original ledger bytes')
s=(P/'tests/historical_generation_v03.py').read_text();a=ast.parse(s)
assignment=next(x for x in a.body if isinstance(x,ast.Assign)and any(isinstance(y,ast.Name)and y.id=='LEDGER_SHA'for y in x.targets));ok(ast.literal_eval(assignment.value)==H(ledger),'adapter fixed original ledger SHA literal')
imports=next(x for x in a.body if isinstance(x,ast.ImportFrom)and x.module=='tests.historical_generation');ok([x.name for x in imports.names]==['contexts','public_models','public_paths','catalogue','generate'],'all five original helper delegates exact')
# v1 numerical wrapper bodies and historical source helper unchanged except context locator.
for n in ('tests/historical_burgers.py','tests/historical_mcc_reference.py'):
 old=(N/'python-historical-contexts-fix-v1/proposed'/n).read_text().replace('tests/fixtures/historical-routing-v1.json',D+'/historical-routing-v1.json');ok(old==(P/n).read_text(),'accepted wrapper body unchanged '+n)
ok((N/'python-historical-contexts-fix-v1/proposed/tests/historical_sources.py').read_bytes()==(P/'tests/historical_sources.py').read_bytes(),'DP and preview helper byteexact to accepted v1')
report={'status':'PASS','checks':len(labels),'labels':labels,'controlled_closure':closure,'full_receipt_observations':535,'routed_observations':74,'scope':'read-only original sources, literal data and source-only closure discovery'}
(Q/'complete-pins-closure-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(labels)}))
