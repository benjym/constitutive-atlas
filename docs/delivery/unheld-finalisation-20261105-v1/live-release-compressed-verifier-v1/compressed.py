"""Source-only import; streaming compressed transport qualified against original JSON bytes."""
from pathlib import Path
import hashlib,json,re,gzip,tarfile,zipfile,importlib.util
HERE=Path(__file__).resolve().parent
MAX_BYTES=32*1024*1024

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)

def load_v3():
 path=HERE.parent/'live-release-ci-upload-transform-v1/transform.py'
 spec=importlib.util.spec_from_file_location('qualified_v3_namespace',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def validate_index(raw,original):
 actual=json.loads(raw);assert isinstance(actual,dict)and set(actual)==set(original)
 assert isinstance(actual.get('experiments'),list)and len(actual['experiments'])==len(original['experiments'])
 stripped={**actual,'experiments':[]};transports={}
 for entry,old in zip(actual['experiments'],original['experiments']):
  assert isinstance(entry,dict)and set(entry)==set(old)|{'content_encoding','transport'}
  assert entry['content_encoding']=='gzip'
  logical={k:v for k,v in entry.items()if k not in {'content_encoding','transport'}};assert canonical(logical)==canonical(old)
  assert re.fullmatch(r'[A-Za-z0-9_-]+\.json',old['path'])and old['path']==old['id']+'.json'
  assert type(old['size_bytes'])is int and 0<old['size_bytes']<=MAX_BYTES
  transport=entry['transport'];assert isinstance(transport,dict)and set(transport)=={'path','sha256','size_bytes'}
  assert transport['path']==old['path']+'.gz'
  assert isinstance(transport['sha256'],str)and re.fullmatch(r'[0-9a-f]{64}',transport['sha256'])
  assert type(transport['size_bytes'])is int and 0<transport['size_bytes']<=MAX_BYTES
  name='experiments/'+transport['path'];assert name not in transports
  transports[name]={'transport':transport,'original':old};stripped['experiments'].append(logical)
 assert canonical(stripped)==canonical(original),'Original index metadata/order differs'
 return transports

def decoded_identity(stream,entry):
 old=entry['original'];limit=old['size_bytes'];h=hashlib.sha256();size=0
 with gzip.GzipFile(fileobj=stream,mode='rb')as decoded:
  while True:
   chunk=decoded.read(min(1024*1024,limit+1-size))
   if not chunk:break
   size+=len(chunk);assert size<=limit and size<=MAX_BYTES,'Decoded experiment exceeds original declared bound'
   h.update(chunk)
 assert size==limit and h.hexdigest()==old['sha256'],'Decoded experiment differs from exact original JSON bytes'
 return {'sha256':h.hexdigest(),'bytes':size}

def verify_decoded_archive(archive,transports,members):
 proof={}
 with zipfile.ZipFile(archive)as zipped:
  files=[i for i in zipped.infolist()if not i.is_dir()];assert len(files)==1 and files[0].filename=='artifact.tar'
  with zipped.open(files[0])as raw,tarfile.open(fileobj=raw,mode='r|*')as tar:
   for member in tar:
    name=member.name
    while name.startswith('./'):name=name[2:]
    if name not in transports:continue
    assert member.isfile()and name not in proof
    entry=transports[name];transport=entry['transport'];observed=members[name]
    assert member.size==observed['bytes']==transport['size_bytes']<=MAX_BYTES
    assert observed['sha256']==transport['sha256']
    source=tar.extractfile(member);assert source is not None
    class HashedStream:
     def __init__(self):self.hash=hashlib.sha256();self.size=0
     def read(self,n=-1):
      chunk=source.read(n);self.hash.update(chunk);self.size+=len(chunk);return chunk
    checked=HashedStream();identity=decoded_identity(checked,entry)
    while checked.read(1024*1024):pass
    assert checked.size==transport['size_bytes']and checked.hash.hexdigest()==transport['sha256'],'Compressed bytes changed between archive passes'
    proof[name]={'compressed_sha256':observed['sha256'],'compressed_bytes':member.size,'decoded':identity}
 assert set(proof)==set(transports),'Every original experiment must be decoded and compared'
 return proof

def verify_archive(archive,expected_names,capture_names):
 v3=load_v3();members,raw=v3.verify_archive(archive,expected_names,capture_names)
 original=json.loads((HERE/'original-index.json').read_text());assert len(original['experiments'])==994
 transports=validate_index(raw['experiments/index.json'],original);assert len(transports)==994
 decoded=verify_decoded_archive(archive,transports,members)
 verify_archive.last_proof={**v3.verify_archive.last_proof,'compression':{'original_index_sha256':hashlib.sha256((HERE/'original-index.json').read_bytes()).hexdigest(),'actual_index_sha256':hashlib.sha256(raw['experiments/index.json']).hexdigest(),'entries':len(decoded),'decoded_members':decoded,'scope':'Actual compressed bytes self-bind new index; original decoded JSON bytes mandatory; no cross-zlib compressed-byte equivalence assumed'}}
 return members,raw
