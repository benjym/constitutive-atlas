"""Independent pure source/manufactured review; never invokes verifier main/HTTP."""
from pathlib import Path
import contextlib,copy,gzip,hashlib,importlib.util,io,json,runpy,sys,tarfile,tempfile,zipfile
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;A=R.parent/'live-release-compressed-verifier-v1';checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(name,value=True):
 assert value,name
 checks.append(name)
def reject(name,fn):
 try:fn()
 except (AssertionError,ValueError,OSError,EOFError):ck(name)
 else:raise AssertionError('Accepted forbidden fixture: '+name)
manifest=(A/'manifest.json').read_bytes();ck('exact author manifest',sha(manifest)=='515985a2dc1affb2aab32dd4ca6efef2f8c873b0793fc101357fb2ff6e805a44')
for pin in json.loads(manifest)['files']:
 b=(A/pin['path']).read_bytes();ck('member '+pin['path'],len(b)==pin['bytes'] and sha(b)==pin['sha256'])
ck('complete13 member namespace',{str(p.relative_to(A)) for p in A.rglob('*') if p.is_file()}=={'manifest.json',*[x['path'] for x in json.loads(manifest)['files']]})
for pin in json.loads((A/'POLICY.json').read_text())['inputs']:
 b=Path(pin['path']).read_bytes();ck('declared input '+pin['path'],len(b)==pin['bytes'] and sha(b)==pin['sha256'])
old=R.parent/'live-release-artifact-plan-v1';v3=R.parent/'live-release-ci-upload-transform-v1'
ck('original base exact one literal substitution',(A/'verify-base-v4.py').read_text()==(old/'verify-v2.py').read_text().replace("H/'contract.json'","H/'contract-v4.json'"))
c0=json.loads((old/'contract.json').read_text());c1=json.loads((A/'contract-v4.json').read_text());original=json.loads((A/'original-index.json').read_text())
ck('original index994',len(original['experiments'])==994)
inventory=json.loads((R.parent/'package-inventory-v1.json').read_text())
# Inventory schema inspected from saved JSON only.
rows=inventory.get('files',inventory.get('members',[]))
if isinstance(rows,dict): rows=[{'path':k,**v}for k,v in rows.items()]
pin=next(x for x in rows if x['path']=='experiments/index.json');ck('original index accepted inventory SHA',pin['sha256']==sha((A/'original-index.json').read_bytes()))
ck('original contract unaffected keys',all(c1[k]==v for k,v in c0.items()if k not in {'identity','member_paths','exact_pins','semantic_json','http_paths'}))
ck('exact versioned identity',c1['identity']=='baseline-five-compressed-Pages-streaming-contract-v4')
ck('all old exactpins retained',all(c1['exact_pins'][k]==v for k,v in c0['exact_pins'].items()))
ck('exact loader only added pin',set(c1['exact_pins'])-set(c0['exact_pins'])=={'experiments.mjs'})
ck('old semantic JSON retained prefix',c1['semantic_json']==c0['semantic_json']+['experiments/index.json'])
ck('old HTTP ordered prefix',c1['http_paths'][:len(c0['http_paths'])]==c0['http_paths'])
# Replay author's exact47 checks; redirect its disposable fixture under reviewer ownership.
real_temp=tempfile.TemporaryDirectory
@contextlib.contextmanager
def owned_temp(*args,**kwargs):
 kwargs['dir']=R
 with real_temp(*args,**kwargs)as path:yield path
sys.path.insert(0,str(A));out=io.StringIO()
with contextlib.redirect_stdout(out),contextlib.redirect_stderr(out):
 tempfile.TemporaryDirectory=owned_temp
 try:runpy.run_path(str(A/'check.py'),run_name='author_source_replay')
 finally:tempfile.TemporaryDirectory=real_temp
(R/'author-replay.stdout.json').write_text(out.getvalue())
ck('author exact47 replay',json.loads(out.getvalue())['count']==47)
import compressed as C
new=copy.deepcopy(original)
for e in new['experiments']:e.update(content_encoding='gzip',transport={'path':e['path']+'.gz','sha256':'a'*64,'size_bytes':50})
def changed(mutator):
 result=copy.deepcopy(new);mutator(result);return json.dumps(result).encode()
for name,mutator in [
 ('last original SHA',lambda x:x['experiments'][-1].update(sha256='0'*64)),
 ('last original numeric type',lambda x:x['experiments'][-1].update(rows=float(x['experiments'][-1]['rows']))),
 ('last transport boolean size',lambda x:x['experiments'][-1]['transport'].update(size_bytes=True)),
 ('last transport omitted',lambda x:x['experiments'][-1].pop('transport')),
 ('last encoding omitted',lambda x:x['experiments'][-1].pop('content_encoding')),
 ('last original order',lambda x:x['experiments'].__setitem__(slice(-2,None),x['experiments'][-2:][::-1])),
 ('top-level metadata omission',lambda x:x.pop('attribution')),
 ('transport path URL query',lambda x:x['experiments'][-1]['transport'].update(path=x['experiments'][-1]['path']+'.gz?download')),
]:reject(name,lambda mutator=mutator:C.validate_index(changed(mutator),original))
with real_temp(prefix='independent-',dir=R)as tmp:
 root=Path(tmp);data=b'{"owned_fixture":true}';gz=gzip.compress(data,mtime=0);name='experiments/LAST.json.gz';entry={'original':{'size_bytes':len(data),'sha256':sha(data)},'transport':{'size_bytes':len(gz),'sha256':sha(gz)}}
 def archive(items):
  buf=io.BytesIO()
  with tarfile.open(fileobj=buf,mode='w')as tar:
   for path,body in items:
    info=tarfile.TarInfo(path);info.size=len(body);tar.addfile(info,io.BytesIO(body))
  path=root/'fixture.zip'
  with zipfile.ZipFile(path,'w')as zip:zip.writestr('artifact.tar',buf.getvalue())
  return path
 members={name:{'bytes':len(gz),'sha256':sha(gz)}}
 ck('independent valid second-pass identity',C.verify_decoded_archive(archive([(name,gz)]),{name:entry},members)[name]['decoded']['sha256']==sha(data))
 altered=bytearray(gz);altered[4]=1 # valid same decoded gzip, altered transfer metadata/header
 reject('same JSON changed compressed header',lambda:C.verify_decoded_archive(archive([(name,bytes(altered))]),{name:entry},members))
 reject('duplicate compressed member',lambda:C.verify_decoded_archive(archive([(name,gz),(name,gz)]),{name:entry},members))
 reject('missing final compressed member',lambda:C.verify_decoded_archive(archive([]),{name:entry},members))
 bad=copy.deepcopy(entry);bad['original']['size_bytes']=len(data)-1
 reject('decoded one byte above original declared limit',lambda:C.decoded_identity(io.BytesIO(gz),bad))
 v=C.load_v3();expected=['.nojekyll','implicit-path-package-checks/build-old/report.json',name];report=(v3/'reference/original-implicit-path-report.json').read_bytes();files=[('implicit-path-package-checks/build-new/report.json',report),(name,gz)]
 reject('unexpected nontransport member',lambda:v.verify_archive(archive([*files,('extra.json',b'{}')]),expected,set()))
 reject('hidden payload unexpectedly uploaded',lambda:v.verify_archive(archive([*files,('.nojekyll',b'')]),expected,set()))
ck('all fixture directories cleaned',not any(p.is_dir()and p.name.startswith(('independent-','owned-synthetic-'))for p in R.iterdir()))
print(json.dumps({'status':'PASS_SOURCE_MANUFACTURED_ONLY','count':len(checks),'checks':checks,'author_checks_replayed':47,'actual_artifact_corpus_network_browser_compiled_calls':0},indent=2))
