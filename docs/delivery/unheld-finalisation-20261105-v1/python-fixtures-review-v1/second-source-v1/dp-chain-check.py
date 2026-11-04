from pathlib import Path
import ast,hashlib,json,tempfile
Q=Path(__file__).resolve().parent;O=Q.parents[1]/'python-historical-contexts-fix-v1';P=O/'proposed';W=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
H=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ok(b,s):assert b,s;checks.append(s)
def fails(f,s):
 try:f()
 except (ValueError,OSError,AssertionError):checks.append(s);return
 raise AssertionError(s)
t=ast.parse((W/'atlas/evidence.py').read_text());env={'Path':Path,'hashlib':hashlib,'json':json};exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in ('_sha','checked_receipt')],type_ignores=[]),'receipt','exec'),env)
t=ast.parse((P/'tests/historical_sources.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helper','exec'),env)
bp='catalogue/investigations/dp-dilatancy-domain-v1';pre='d40db28d8de98b7eb8597c90787d16d1f76bac0d145cabb9a5853e86d811650d';post='b2ae340e97fca4209e671b1f610dac7b1520394eefe3070548f299bd603ee877'
with tempfile.TemporaryDirectory(prefix='dp-chain-',dir=Q)as td:
 r=Path(td)
 def put(n,b):p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);return p
 for n in ('manifest.json','previous-definition.json','candidate-definition.json'):put(bp+'/'+n,(W/bp/n).read_bytes())
 put('models/drucker-prager.json',(W/'models/drucker-prager.json').read_bytes())
 archive=put('catalogue/source-snapshots/'+post+'/models/drucker-prager.json',(W/bp/'candidate-definition.json').read_bytes())
 for pin,n in ((pre,'previous-definition.json'),(post,'candidate-definition.json')):
  ok(env['preserved_model'](r,'drucker-prager.json',pin)==(W/bp/n).read_bytes(),'real DP original '+n+' identity retained')
 for a,s in ((r/bp/'previous-definition.json','original previous receipt'),(r/bp/'candidate-definition.json','original candidate receipt'),(archive,'archived approved domain model')):
  old=a.read_bytes();a.write_bytes(b'corrupt');fails(lambda:env['preserved_model'](r,'drucker-prager.json',pre),'DP corruption rejects '+s);a.write_bytes(old)
 old=(r/bp/'manifest.json').read_bytes();(r/bp/'manifest.json').write_bytes(b'{}');fails(lambda:env['preserved_model'](r,'drucker-prager.json',pre),'DP missing original manifest binding rejects');(r/bp/'manifest.json').write_bytes(old)
 archive.unlink();fails(lambda:env['preserved_model'](r,'drucker-prager.json',pre),'DP missing approved candidate archive rejects')
 # No symlink escape is accepted by the unchanged receipt validator.
 a=r/'escape.json';a.symlink_to(W/bp/'previous-definition.json');fails(lambda:env['checked_receipt'](r,bp+'/manifest.json','escape.json',pre),'unbound symlink path rejects')
(Q/'dp-chain-checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
