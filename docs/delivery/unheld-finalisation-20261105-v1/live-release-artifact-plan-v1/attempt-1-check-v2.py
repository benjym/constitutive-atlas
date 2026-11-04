from pathlib import Path
import json,hashlib,importlib.util,tempfile,subprocess,shutil,io
P=Path(__file__).resolve().parent;checks=[]
spec=importlib.util.spec_from_file_location('verifier_v2',P/'verify-v2.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(dir=P,prefix='owned-v2-fixture-')as tmp:
 root=Path(tmp)
 class Response:
  url='https://manufactured.invalid/one';status=200;headers={'x-witness':'retained'}
  def __init__(self,partial=False):self.calls=0;self.partial=partial
  def __enter__(self):return self
  def __exit__(self,*args):return False
  def read(self,size):
   self.calls+=1
   if self.calls==1:return b'wrong'
   if self.partial:raise OSError('manufactured mid-body failure')
   return b''
 original=m.urllib.request.urlopen
 for label,partial in [('mismatch',False),('partial',True)]:
  output=root/label;output.mkdir();m.urllib.request.urlopen=lambda *a,**kw:Response(partial)
  try:m.verify_http('https://manufactured.invalid',{'one':{'sha256':'0'*64,'bytes':5}},['one'],output,{'status':'pending'})
  except (AssertionError,OSError):pass
  else:raise AssertionError('must fail '+label)
  report=json.loads((output/'report.json').read_text());row=report['http'][0]
  assert report['status']=='failed-production-http'and row['headers']=={'x-witness':'retained'}and row['sha256']==hashlib.sha256(b'wrong').hexdigest()and row['bytes']==5 and row['status']==200 and row['observation_status']=='failed'and row['error'];checks.append('durable '+label+' response/hash/headers/failure')
 m.urllib.request.urlopen=original
 # Saved local E7 fixtures only; no native/module/material execution.
 D=root/'downloads';D.mkdir();old=P.parent/'browser-v1/artifacts'
 for f in old.iterdir():
  if f.suffix in ['.csv','.json']:shutil.copyfile(f,D/f.name)
 target=D/'linear-elastic-default.csv';originalcsv=target.read_text();lines=originalcsv.splitlines();values=lines[1].split(',')
 source='/private/tmp/atlas-baseline-delivery-20261105/source'
 def run(label):
  output=root/(label+'.json')
  result=subprocess.run(['node',str(P/'browser-validator-v2.validate.mjs'),str(D),source,str(output)],capture_output=True,text=True)
  return result,output
 result,output=run('good');assert result.returncode==0,result.stderr;checks.append('original saved574+5 CSVexport checks pass');(P/'saved-local-v2.stdout.json').write_text(result.stdout)
 for index in [0,1,2,3,4,8,9]:
  cells=values.copy();cells[index]='Infinity';target.write_text('\n'.join([lines[0],','.join(cells),*lines[2:]]))
  result,output=run('nonfinite-'+str(index));assert result.returncode!=0 and not output.exists();checks.append('nonfinite CSVcolumn '+str(index)+' rejected')
 for index in [0,1,2,8,9]:
  cells=values.copy();cells[index]='1';target.write_text('\n'.join([lines[0],','.join(cells),*lines[2:]]))
  result,output=run('finite-corrupt-'+str(index));assert result.returncode!=0 and not output.exists();checks.append('finite corrupted CSVcolumn '+str(index)+' rejected')
 target.write_text(originalcsv)
assert not any(x.name.startswith('owned-v2-fixture-')for x in P.iterdir())
print(json.dumps({'status':'PASS_SOURCE_SAVED_MOCK_ONLY','checks':checks,'count':len(checks),'real_http_browser_module_material_calls':0,'temporary_fixtures_remaining':0},indent=2))
