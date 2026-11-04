from pathlib import Path
import json,hashlib,io,gzip,tarfile,zipfile,tempfile,copy,importlib.util,sys
import compressed as C
P=Path(__file__).resolve().parent;N=P.parent;checks=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def ck(n,b=True):assert b,n;checks.append(n)
def reject(n,fn):
 try:fn()
 except (AssertionError,ValueError,OSError,EOFError):ck(n)
 else:raise AssertionError('Accepted '+n)
policy=json.loads((P/'POLICY.json').read_text())
for pin in policy['inputs']:
 raw=Path(pin['path']).read_bytes();ck('input '+pin['path'],len(raw)==pin['bytes']and sha(raw)==pin['sha256'])
oldcontract=json.loads((N/'live-release-artifact-plan-v1/contract.json').read_text());newcontract=json.loads((P/'contract-v4.json').read_text());old=json.loads((P/'original-index.json').read_text());ck('994 original entries',len(old['experiments'])==994)
ck('v2 semantic/API/HTTP code exact except contract file',(P/'verify-base-v4.py').read_text()==(N/'live-release-artifact-plan-v1/verify-v2.py').read_text().replace("H/'contract.json'","H/'contract-v4.json'"))
paths={'experiments/'+e['path']:'experiments/'+e['path']+'.gz'for e in old['experiments']}
ck('exact994 namespace replacements',newcontract['member_paths']==[paths.get(p,p)for p in oldcontract['member_paths']]and len(paths)==994)
ck('all original model/review/examples/roles/counts exact',all(newcontract[k]==oldcontract[k]for k in ['catalogue_hash','models','example_ids','roles','accepted_inventory_sha256']))
ck('all original exact pins unchanged',{k:v for k,v in newcontract['exact_pins'].items()if k!='experiments.mjs'}==oldcontract['exact_pins'])
ck('loader exact pin',newcontract['exact_pins']['experiments.mjs']=='d3615cb2041be9ef969de636a7cc6f1b0ba8b0c3b9d8b91b6efb4d682b207dbf')
ck('old HTTP gates remain prefix',newcontract['http_paths'][:len(oldcontract['http_paths'])]==oldcontract['http_paths'])
ck('index semantic added only',newcontract['semantic_json']==oldcontract['semantic_json']+['experiments/index.json'])
# Actual old index metadata only: no original experiment payload read or generated.
new=copy.deepcopy(old)
for e in new['experiments']:e.update(content_encoding='gzip',transport={'path':e['path']+'.gz','sha256':'a'*64,'size_bytes':100})
ck('exact old full metadata/order recovery',len(C.validate_index(json.dumps(new).encode(),old))==994)
for label,change in [('order',lambda x:x['experiments'].reverse()),('metadata',lambda x:x.update(attribution='changed')),('entrymetadata',lambda x:x['experiments'][0].update(rows=99999)),('encoding',lambda x:x['experiments'][0].update(content_encoding='br')),('missingtransport',lambda x:x['experiments'][0].pop('transport')),('extrapath',lambda x:x['experiments'][0]['transport'].update(extra=True)),('traversal',lambda x:x['experiments'][0]['transport'].update(path='../escape.json.gz')),('plainpath',lambda x:x['experiments'][0]['transport'].update(path=x['experiments'][0]['path'])),('badhash',lambda x:x['experiments'][0]['transport'].update(sha256='A'*64)),('toolarge',lambda x:x['experiments'][0]['transport'].update(size_bytes=33554433)),('boolean',lambda x:x['experiments'][0]['transport'].update(size_bytes=True)),('zero',lambda x:x['experiments'][0]['transport'].update(size_bytes=0))]:
 bad=copy.deepcopy(new);change(bad);reject('index rejects '+label,lambda bad=bad:C.validate_index(json.dumps(bad).encode(),old))
# Synthetic data only: complete real v3 + v4 streaming callback through994 mock experiments.
with tempfile.TemporaryDirectory(prefix='owned-synthetic-',dir=P)as tmp:
 root=Path(tmp);synthetic={'schema_version':'0.1','release':'public','attribution':'owned manufactured fixture','experiments':[]};encoded={};entries={}
 for i in range(994):
  data=json.dumps({'id':f'FIXTURE-{i}','synthetic':True},separators=(',',':')).encode();path=f'FIXTURE-{i}.json';e={'id':f'FIXTURE-{i}','path':path,'sha256':sha(data),'size_bytes':len(data)};synthetic['experiments'].append(e);gz=gzip.compress(data,mtime=0);entries[path]=gz
 current=copy.deepcopy(synthetic)
 for e in current['experiments']:e.update(content_encoding='gzip',transport={'path':e['path']+'.gz','sha256':sha(entries[e['path']]),'size_bytes':len(entries[e['path']])})
 def makezip(name,files):
  data=io.BytesIO()
  with tarfile.open(fileobj=data,mode='w')as tar:
   for path,body in files.items():
    member=tarfile.TarInfo(path);member.size=len(body);tar.addfile(member,io.BytesIO(body))
  path=root/(name+'.zip')
  with zipfile.ZipFile(path,'w')as z:z.writestr('artifact.tar',data.getvalue())
  return path
 v3=C.load_v3();report=(N/'live-release-ci-upload-transform-v1/reference/original-implicit-path-report.json').read_bytes();reportpath='implicit-path-package-checks/build-synthetic/report.json';files={'experiments/index.json':json.dumps(current).encode(),reportpath:report};files.update({'experiments/'+e['path']+'.gz':entries[e['path']]for e in synthetic['experiments']});archive=makezip('complete',files);(root/'original-index.json').write_text(json.dumps(synthetic));savedhere=C.HERE;savedload=C.load_v3
 try:
  C.HERE=root;C.load_v3=lambda:v3;members,raw=C.verify_archive(archive,['.nojekyll',*files],{'experiments/index.json'});ck('complete994 streamed decode gate',C.verify_archive.last_proof['compression']['entries']==994);ck('all106 v3 report gates retained',C.verify_archive.last_proof['report']['checks']==106)
 finally:C.HERE=savedhere;C.load_v3=savedload
 first=synthetic['experiments'][0];data=json.dumps({'id':first['id'],'synthetic':True},separators=(',',':')).encode();gz=entries[first['path']];entry={'original':first,'transport':current['experiments'][0]['transport']}
 ck('decoded exact bytes',C.decoded_identity(io.BytesIO(gz),entry)=={'sha256':sha(data),'bytes':len(data)})
 bad=copy.deepcopy(entry);bad['original']['sha256']='0'*64;reject('wrong original SHA',lambda:C.decoded_identity(io.BytesIO(gz),bad))
 bad=copy.deepcopy(entry);bad['original']['size_bytes']=1;reject('inflation exceeds declared bound',lambda:C.decoded_identity(io.BytesIO(gz),bad))
 reject('truncated gzip',lambda:C.decoded_identity(io.BytesIO(gz[:-3]),entry));reject('corrupt gzip',lambda:C.decoded_identity(io.BytesIO(b'wrong'),entry))
 # Correct decoded JSON with wrong claimed compressed hash must fail in second pass.
 path='experiments/'+first['path']+'.gz';tiny=makezip('crosspass',{path:gz});bad=copy.deepcopy(entry);bad['transport']['sha256']='a'*64;reject('compressed cross-pass change',lambda:C.verify_decoded_archive(tiny,{path:bad},{path:{'sha256':'a'*64,'bytes':len(gz)}}))
 reject('compressed size mismatch',lambda:C.verify_decoded_archive(tiny,{path:entry},{path:{'sha256':sha(gz),'bytes':len(gz)+1}}))
 empty=makezip('empty',{});reject('missing decoded member',lambda:C.verify_decoded_archive(empty,{path:entry},{}))
ck('no fixture trees remain',not root.exists())
print(json.dumps({'status':'PASS_SOURCE_MANUFACTURED_ONLY','checks':checks,'count':len(checks),'manufactured_gzip_members':994,'new_actual_ZIP_corpus_network_browser_compiled_calls':0,'temporary_fixture_trees_remaining':0},indent=2))
