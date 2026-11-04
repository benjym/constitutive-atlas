"""Pure source/receipt fixtures only. No generator, analyzer replay or engine calls."""
from pathlib import Path
import ast,hashlib,json,tempfile,types,sys,unittest.mock as mock
O=Path(__file__).resolve().parent;P=O/'proposed';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ok(v,label):
 if not v:raise AssertionError(label)
 checks.append(label)
def put(r,n,b):
 p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b if isinstance(b,bytes)else b.encode());return p
def fails(f,label):
 try:f()
 except (ValueError,AssertionError,FileNotFoundError,KeyError):checks.append(label);return
 raise AssertionError('accepted negative '+label)
# Execute only unchanged receipt functions extracted verbatim from source AST.
tree=ast.parse((W/'atlas/evidence.py').read_text());functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in ('_sha','checked_receipt')]
ns={'Path':Path,'hashlib':hashlib,'json':json};exec(compile(ast.Module(body=functions,type_ignores=[]),'original-receipt-functions','exec'),ns);checked=ns['checked_receipt']
d=json.loads((O/'source-delta.json').read_text());delta=d['changes']+d['retained_inputs']
for row in delta:
 p=P/row['path'];ok(sha(p.read_bytes())==row['sha256'],'payload '+row['path'])
 if row['preimage_sha256']:ok(sha((W/row['path']).read_bytes())==row['preimage_sha256'],'preimage '+row['path'])
 if p.suffix=='.py':ast.parse(p.read_text());checks.append('syntax '+row['path'])
for original in (O/'original').rglob('*.py'):
 name=original.relative_to(O/'original');before=ast.parse(original.read_text());after=ast.parse((P/name).read_text())
 if name.name.startswith('test_'):
  def gates(t):
   return [ast.dump(n,include_attributes=False)for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr.startswith('assert')]
  a=gates(before);b=gates(after)
  # Precisely declared routing-only substitutions; every other original assertion exact AST.
  replacements={"current-sixteen-sclay1-v1":"current-sixteen-baseline-v03-v1","set(paths)":"historical_names"}
  text=original.read_text().replace('current-sixteen-sclay1-v1','current-sixteen-baseline-v03-v1').replace('self.assertTrue(set(paths) < current_paths)','self.assertTrue(historical_names < current_paths)').replace('preserved_model(ROOT,Path(name).name)','preserved_model(ROOT,Path(name).name,pin)').replace('preserved_model(ROOT,p.name)','preserved_model(ROOT,p.name,hashlib.sha256(p.read_bytes()).hexdigest())')
  ok(gates(ast.parse(text))==b,'all original assertion ASTs retained '+str(name))
# Validate every active sidecar route on a tiny independent tree using exact original checker.
routes=json.loads((O/'routing-audit.json').read_text())
with tempfile.TemporaryDirectory(prefix='historical-route-check-',dir=O)as td:
 r=Path(td)
 for row in routes:
  doc=row['document'];m=str(Path(doc).parent/'source-archive-map.json')
  put(r,doc,(W/doc).read_bytes());put(r,m,(P/m).read_bytes())
  archive=f"catalogue/source-snapshots/{row['sha256']}/{row['path']}"
  source=P/archive if(P/archive).is_file()else W/archive
  put(r,archive,source.read_bytes());put(r,row['path'],b'intentionally changed current bytes')
  selected=checked(r,doc,row['path'],row['sha256'])
  ok(sha(selected.read_bytes())==row['sha256'],'original receipt archive route '+doc+' '+row['path'])
  b=selected.read_bytes();selected.write_bytes(b'corrupt')
  fails(lambda:checked(r,doc,row['path'],row['sha256']),'corrupt archive rejects '+row['path'])
  selected.unlink();fails(lambda:checked(r,doc,row['path'],row['sha256']),'missing archive rejects '+row['path']);selected.write_bytes(b)
 # Explicit document corruption cannot be rescued by an otherwise valid archive.
 row=routes[-1];doc=r/row['document'];b=doc.read_bytes();doc.write_bytes(b+b' ')
 fails(lambda:checked(r,row['document'],row['path'],row['sha256']),'changed original document rejects');doc.write_bytes(b)
 fails(lambda:checked(r,row['document'],'../escape',row['sha256']),'unbound escape rejects')
# Helper uses caller's expected original identity; no implicit current model revision.
source=(P/'tests/historical_sources.py').read_text();t=ast.parse(source)
helper={'Path':Path,'hashlib':hashlib};exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helper-fixture','exec'),helper)
with tempfile.TemporaryDirectory(prefix='model-route-check-',dir=O)as td:
 r=Path(td);b=b'original0.1';h=sha(b);put(r,'models/example.json',b'new0.3');a=put(r,f'catalogue/source-snapshots/{h}/models/example.json',b)
 ok(helper['preserved_model'](r,'example.json',h)==b,'preview retains original0.1 bytes')
 a.write_bytes(b'corrupt');fails(lambda:helper['preserved_model'](r,'example.json',h),'preview corruption rejects')
 a.unlink();fails(lambda:helper['preserved_model'](r,'example.json',h),'preview missing archive rejects')
 fails(lambda:helper['preserved_model'](r,'../example.json',h),'preview path escape rejects')
# Historical membership retains canonical names, separate from archive selection.
s=(P/'tests/test_historical_generation.py').read_text()
ok("paths = [verified(item) for item in data['current_models']]"in s and 'len(paths), 12'in s,'all historical twelve still verified')
ok("historical_names = {ROOT / item['path'] for item in data['current_models']}"in s and 'self.assertTrue(historical_names < current_paths)'in s,'original canonical twelve strict subset retained')
fixture=json.loads((P/'tests/fixtures/current-sixteen-baseline-v03-v1.json').read_text());ok(len(fixture['models'])==16,'exact16 models')
for row in fixture['models']:ok(sha((W/row['path']).read_bytes())==row['sha256'],'qualified live model '+row['path'])
# Wrapper AST requires all previously installed assertions, original delegated numerical verify remains untouched.
s=(P/'tests/historical_burgers.py').read_text()
for text in ('original.verify(installed=False)',"manifest['installed_files'].items()","freeze['prior_models'].items()","checked_receipt(ROOT,(R/'manifest.json').relative_to(ROOT),name,digest)","checked_receipt(ROOT,(R/'freeze.json').relative_to(ROOT),name,digest)","models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json","(R/'target.cmake').read_text() in (ROOT/'CMakeLists.txt').read_text()"):
 ok(text in s,'Burgers installed gate preserved '+text)
# Original MCC functions remain byteexact and both delegates call original function, no numerical replacement.
for name in ('analyze','analyze_followups'):
 ok(f'.{name}('in(P/'tests/historical_mcc_reference.py').read_text(),'MCC delegate '+name)
context=json.loads((P/'tests/fixtures/historical-routing-v1.json').read_text())
for name,h in context['pins'].items():ok(sha((W/name).read_bytes())==h,'unchanged analyzer/receipt '+name)
# Exercise actual wrapper functions with fake original modules and tiny receipt trees.
def wrapper_functions(name,root,module):
 tree=ast.parse((P/'tests'/name).read_text())
 loader=types.SimpleNamespace(exec_module=lambda m:None)
 util=types.SimpleNamespace(spec_from_file_location=lambda *a:types.SimpleNamespace(loader=loader),module_from_spec=lambda spec:module)
 env={'ROOT':root,'R':root/'docs/ingestion/burgers-itasca900/integration-v1','hashlib':hashlib,'json':json,'sys':types.SimpleNamespace(path=[]),'checked_receipt':checked,'importlib':types.SimpleNamespace(util=util)}
 exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),name,'exec'),env)
 return env
with tempfile.TemporaryDirectory(prefix='wrapper-check-',dir=O)as td:
 r=Path(td);bp='docs/ingestion/burgers-itasca900/integration-v1'; calls=[]
 installed={'tests/test_burgers.py':sha(b'old-test')};prior={'models/example.json':sha(b'old-model')}
 put(r,bp+'/verify.py',b'original analyzer sentinel')
 put(r,bp+'/manifest.json',json.dumps({'installed_files':installed}))
 put(r,bp+'/freeze.json',json.dumps({'prior_models':prior}))
 pins={bp+'/'+n:sha((r/bp/n).read_bytes())for n in ('verify.py','manifest.json','freeze.json')}
 put(r,'tests/fixtures/historical-routing-v1.json',json.dumps({'pins':pins}))
 mapping={'version':'immutable-source-archive-map-0.1','documents':{bp+'/'+n:sha((r/bp/n).read_bytes())for n in ('manifest.json','freeze.json')},'entries':[]}
 for name,b in [('tests/test_burgers.py',b'old-test'),('models/example.json',b'old-model')]:
  h=sha(b);a=f'catalogue/source-snapshots/{h}/{name}';put(r,a,b);put(r,name,b'new-current')
  mapping['entries'].append({'original_path':name,'sha256':h,'archived_path':a})
 put(r,bp+'/source-archive-map.json',json.dumps(mapping))
 put(r,bp+'/model.json',b'research-model');research=put(r,'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json',b'research-model')
 put(r,bp+'/target.cmake',b'original-target');cmake=put(r,'CMakeLists.txt',b'prefix original-target suffix')
 module=types.SimpleNamespace(verify=lambda installed:(calls.append(installed)or {'ok':True}))
 env=wrapper_functions('historical_burgers.py',r,module)
 ok(env['verify']()=={'ok':True}and calls==[False],'Burgers delegates saved checks before all installed checks')
 for e in mapping['entries']:
  a=r/e['archived_path'];b=a.read_bytes();a.write_bytes(b'corrupt')
  fails(env['verify'],'Burgers rejects corrupt '+e['original_path']);a.unlink()
  fails(env['verify'],'Burgers rejects missing '+e['original_path']);a.write_bytes(b)
 for a,label in [(research,'research model'),(cmake,'CMake target'),(r/bp/'verify.py','original analyzer')]:
  b=a.read_bytes();a.write_bytes(b'changed');fails(env['verify'],'Burgers rejects changed '+label);a.write_bytes(b)
with tempfile.TemporaryDirectory(prefix='mcc-wrapper-check-',dir=O)as td:
 r=Path(td);doc='catalogue/investigations/recorded-refinement-v1/manifest.json';name='models/modified-cam-clay.json';b=b'old MCC';h=sha(b)
 put(r,doc,json.dumps({name:h}));put(r,name,b'new MCC');a=f'catalogue/source-snapshots/{h}/{name}';put(r,a,b)
 put(r,str(Path(doc).parent/'source-archive-map.json'),json.dumps({'version':'immutable-source-archive-map-0.1','documents':{doc:sha((r/doc).read_bytes())},'entries':[{'original_path':name,'sha256':h,'archived_path':a}]}))
 tool=put(r,'tools/analyze_mcc_continuous.py',b'original MCC sentinel')
 put(r,'tests/fixtures/historical-routing-v1.json',json.dumps({'pins':{'tools/analyze_mcc_continuous.py':sha(tool.read_bytes())}}))
 module=types.SimpleNamespace();module.analyze=lambda report:module.ROOT;module.analyze_followups=lambda report,followup:(module.ROOT,followup)
 env=wrapper_functions('historical_mcc_reference.py',r,module);report={'cases':[{'id':'mcc-plastic-isotropic-strain','model_sha256':h}]}
 expected=(r/a).parents[1]
 ok(env['analyze'](report)==expected,'MCC original analyze gets exact archived model ROOT')
 ok(env['analyze_followups'](report,42)==(expected,42),'MCC original followups gets archive ROOT and unchanged arguments')
 (r/a).write_bytes(b'corrupt');fails(lambda:env['analyze'](report),'MCC wrapper rejects corrupt archive');(r/a).unlink()
 fails(lambda:env['analyze'](report),'MCC wrapper rejects missing archive');put(r,a,b)
 bad={'cases':[{'id':'mcc-plastic-isotropic-strain','model_sha256':'0'*64}]}
 fails(lambda:env['analyze'](bad),'MCC wrapper rejects hash not bound by original manifest')
 tool.write_bytes(b'changed');fails(lambda:env['analyze'](report),'MCC wrapper rejects analyzer drift')
# No actual compiler generation or engine/process invocation in this source checker.
report={'status':'PASS','checks':len(checks),'labels':checks,'execution':'source AST and tiny manufactured receipt/model trees only; no compiler/generate/reference replay/engine'}
(O/'check.stdout.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
