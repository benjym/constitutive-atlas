from pathlib import Path
import json,hashlib,ast,importlib.util,io,tempfile,subprocess,urllib.error
H=Path(__file__).resolve().parent;N=H.parents[1];P=N/'live-release-artifact-plan-v1';ROOT=N.parents[2];D=ROOT/'output/playwright/baseline-five-e7-20261105-v1';S=Path('/private/tmp/atlas-baseline-delivery-20261105/source');checks=[]
def ok(name,test=True):assert test,name;checks.append(name)
def sha(b):return hashlib.sha256(b).hexdigest()
for filename,expected in [('manifest.json','342c878025ab331dfe7c62667efe4cb2eeace71c81b7d4d75c42025f8b986d0d'),('browser-validator-v1.manifest.json','bde302f9c8e341ca9adc47d40ec30e764ec7959f1b4fb750dddfab74b5d55f47'),('manifest-v2.json','62e7dea099f881bc6b0a32d0b781dc0319e590ef35828883cc2b6da209757f9e')]:
 b=(P/filename).read_bytes();ok(filename+' exact',sha(b)==expected)
 for row in json.loads(b)['files']:
  b=(P/row['path']).read_bytes();ok(filename+'/'+row['path'],sha(b)==row['sha256'] and len(b)==row['bytes'])
a=ast.parse((P/'verify.py').read_text());b=ast.parse((P/'verify-v2.py').read_text())
func=lambda t,n:next(x for x in t.body if isinstance(x,ast.FunctionDef)and x.name==n)
for name in ['digest','verify_archive']:ok(name+' entire AST unchanged',ast.dump(func(a,name))==ast.dump(func(b,name)))
oldmain=func(a,'main');newmain=func(b,'main');boundary=lambda f:next(i for i,x in enumerate(f.body)if isinstance(x,ast.Assert)and 'args.output.exists' in ast.unparse(x))
ok('All API/archive/identity/revision gates unchanged',ast.dump(ast.Module(body=oldmain.body[:boundary(oldmain)],type_ignores=[]))==ast.dump(ast.Module(body=newmain.body[:boundary(newmain)],type_ignores=[])))
old=(P/'browser-validator-v1.validate.mjs').read_text();new=(P/'browser-validator-v2.validate.mjs').read_text()
strip=lambda s:s.replace("import{laboratoryDocumentCSV}from'../nine-example-refresh-plan-v1/context/web/laboratory-document.mjs';\n",'').replace('browser-validator-v2.POLICY.json','browser-validator-v1.POLICY.json')
ok('Browser request/JSON/replay gates unchanged',strip(new[:new.index(' const csvText=')])==old[:old.index(' const csv=')])
ok('Named original parity/replay gates unchanged',new[new.index('assert.equal(examples.length,9);'):]==old[old.index('assert.equal(examples.length,9);'):])
policy=json.loads((P/'browser-validator-v2.POLICY.json').read_text())
for row in policy['pins']:ok('Pinned browser authority '+row['path'],sha(Path(row['path']).read_bytes())==row['sha256'])
ok('Original numeric policy unchanged',json.loads(Path(policy['parity_policy']).read_text())['parity_relative_tolerance']==1e-10)
spec=importlib.util.spec_from_file_location('review_v2',P/'verify-v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='http-',dir=H)as temp:
 t=Path(temp);good=b'owned-data';member={'a':{'sha256':sha(good),'bytes':len(good)}}
 class Response(io.BytesIO):
  status=200;url='https://example.invalid/a';headers={'X-Owned':'fixture'}
 class Partial(Response):
  seen=False
  def read(self,n=-1):
   if self.seen:raise IOError('owned partial failure')
   self.seen=True;return b'partial'
 interrupt=KeyboardInterrupt('owned interrupt')
 class Interrupted(Partial):
  def read(self,n=-1):
   if self.seen:raise interrupt
   self.seen=True;return b'partial'
 cases=[('success',lambda:Response(good),None),('mismatch',lambda:Response(b'bad'),AssertionError),('partial',lambda:Partial(b''),OSError),('interrupted',lambda:Interrupted(b''),KeyboardInterrupt)]
 for label,make,error in cases:
  out=t/label;out.mkdir();report={};m.urllib.request.urlopen=lambda *a,**k:make()
  try:m.verify_http('https://example.invalid',member,{'a'},out,report)
  except BaseException as e:
   ok(label+' original error preserved',isinstance(e,error));
   if label=='interrupted':ok('KeyboardInterrupt exact object',e is interrupt)
  else:ok(label+' only success',error is None)
  saved=json.loads((out/'report.json').read_text());row=saved['http'][0];ok(label+' durable headers',row['headers']=={'X-Owned':'fixture'});ok(label+' durable digest',row['sha256']==sha(good if label=='success' else b'bad' if label=='mismatch' else b'partial'));ok(label+' durable size',row['bytes']==len(good if label=='success' else b'bad' if label=='mismatch' else b'partial'));ok(label+' terminal saved',saved['status']==('passed-artifact-and-selected-production-http'if error is None else'failed-production-http'))
 out=t/'httperror';out.mkdir();failure=urllib.error.HTTPError('https://example.invalid/a',503,'owned failure',{'Retry-After':'1'},None)
 def fail(*a,**k):raise failure
 m.urllib.request.urlopen=fail
 try:m.verify_http('https://example.invalid',member,{'a'},out,{})
 except BaseException as e:ok('HTTPError original identity',e is failure)
 row=json.loads((out/'report.json').read_text())['http'][0];ok('HTTPError code/header retained',row['status']==503 and row['headers']=={'Retry-After':'1'})
# Every CSV nonfinite column and finite corruption must reject actual pure validator.
with tempfile.TemporaryDirectory(prefix='csv-',dir=H)as temp:
 t=Path(temp);dl=t/'downloads';dl.mkdir()
 for p in D.glob('*.json'):(dl/p.name).symlink_to(p)
 for p in D.glob('*.csv'):
  if p.name!='linear-elastic-default.csv':(dl/p.name).symlink_to(p)
 rows=[line.split(',')for line in(D/'linear-elastic-default.csv').read_text().splitlines()]
 def run(label,changed):
  (dl/'linear-elastic-default.csv').write_text('\n'.join(','.join(r)for r in changed)+'\n')
  return subprocess.run(['node',str(P/'browser-validator-v2.validate.mjs'),str(dl),str(S),str(t/(label+'.json'))],capture_output=True,text=True)
 for at in [0,1,2,3,4,8,9]:
  changed=[r[:]for r in rows];changed[1][at]='Infinity';p=run('infinite-'+str(at),changed);ok('CSV numeric column '+rows[0][at]+' rejects Infinity',p.returncode!=0)
 for at in [0,1,2,8,9]:
  changed=[r[:]for r in rows];changed[1][at]=str(float(changed[1][at])+1);p=run('finite-'+str(at),changed);ok('CSV '+rows[0][at]+' rejects finite corruption',p.returncode!=0)
 changed=[r[:]for r in rows];changed[1][5]='0';ok('Unavailable pore pressure remains blank',run('pore',changed).returncode!=0)
 p=run('valid',rows);ok('Actual saved local JSON+CSV passes',p.returncode==0);(H/'saved-local.stdout.json').write_text(p.stdout);(H/'saved-local.stderr.txt').write_text(p.stderr)
 report=json.loads(p.stdout);ok('579saved checks',report['checks']==579)
(H/'checks.json').write_text(json.dumps({'status':'PASS_SOURCE_AND_SAVED_ONLY','checks':checks,'count':len(checks),'actual_network_browser_module_compiled_calls':0,'temporary_resources_remaining':0},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
