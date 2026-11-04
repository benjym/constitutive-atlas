"""Coordinator-only saved Pages metadata + streaming ZIP/tar + production HTTP checks.
Does not extract files, execute artifacts, invoke gh, or infer CI/deploy success.
"""
import argparse,hashlib,json,tarfile,zipfile,urllib.request
from pathlib import Path,PurePosixPath

def digest(stream):
 h=hashlib.sha256();size=0
 while chunk:=stream.read(1024*1024):h.update(chunk);size+=len(chunk)
 return h.hexdigest(),size

def verify_archive(archive,expected_names,capture_names):
 observed={};captured={}
 with zipfile.ZipFile(archive)as z:
  files=[i for i in z.infolist()if not i.is_dir()]
  assert len(files)==1 and files[0].filename=='artifact.tar','Expected sole artifact.tar'
  with z.open(files[0])as raw,tarfile.open(fileobj=raw,mode='r|*')as tar:
   for member in tar:
    rawname=member.name
    while rawname.startswith('./'):rawname=rawname[2:]
    if member.isdir():continue
    p=PurePosixPath(rawname)
    assert member.isfile()and not p.is_absolute()and '..'not in p.parts and str(p)==rawname and rawname not in observed,'Unsafe/duplicate tar member: '+member.name
    stream=tar.extractfile(member);assert stream is not None
    if rawname in capture_names:
     assert member.size<=16*1024*1024,'Semantic JSON too large'
     data=stream.read();h=hashlib.sha256(data).hexdigest();size=len(data);captured[rawname]=data
    else:h,size=digest(stream)
    assert size==member.size
    observed[rawname]={'sha256':h,'bytes':size,'mode':oct(member.mode)}
 assert set(observed)==set(expected_names),'Archive member namespace differs from reviewed package inventory'
 assert set(capture_names)<=set(captured),'Required semantic JSON absent'
 return observed,captured

def main():
 a=argparse.ArgumentParser();a.add_argument('--revision',required=True);a.add_argument('--pages-run',type=Path,required=True);a.add_argument('--artifact-metadata',type=Path,required=True);a.add_argument('--deployment',type=Path,required=True);a.add_argument('--deployment-status',type=Path,required=True);a.add_argument('--zip',type=Path,required=True);a.add_argument('--base-url',required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
 assert len(args.revision)==40 and all(c in'0123456789abcdef'for c in args.revision)
 H=Path(__file__).resolve().parent;contract=json.loads((H/'contract.json').read_text());read=lambda p:json.loads(p.read_text())
 run=read(args.pages_run);artifact=read(args.artifact_metadata);deployment=read(args.deployment);status=read(args.deployment_status)
 assert run['head_sha']==args.revision and run['conclusion']=='success'and run['status']=='completed'and run['name']=='Publish Pages'
 assert artifact['name']=='github-pages'and artifact['expired']is False and artifact['workflow_run']['id']==run['id']and artifact['workflow_run']['head_sha']==args.revision
 assert deployment['sha']==args.revision and deployment['environment']=='github-pages'and status['state']=='success'and status['deployment_url'].rstrip('/').endswith('/'+str(deployment['id']))
 assert args.base_url.startswith('https://')and status['environment_url'].rstrip('/')==args.base_url.rstrip('/')
 with args.zip.open('rb')as stream:zipsha,zipsize=digest(stream)
 # The API digest describes artifact content, not necessarily the download ZIP transport.
 # Preserve it; bind actual transport separately rather than assuming equivalence.
 assert artifact.get('digest','').startswith('sha256:')and len(artifact['digest'])==71
 capture=set(contract['semantic_json'])
 members,raw=verify_archive(args.zip,contract['member_paths'],capture)
 for name,expected in contract['exact_pins'].items():assert members[name]['sha256']==expected,name
 catalogue=json.loads(raw['models.json']);assert catalogue['sha256']==contract['catalogue_hash']and catalogue['models']==contract['models']
 registry=json.loads(raw['evidence-records/catalogue/approved-models.json']);assert len(registry['models'])==30
 examples=json.loads(raw['laboratory-examples.json']);assert examples['catalogue_hash']==contract['catalogue_hash']and len(examples['examples'])==9
 assert [e['id']for e in examples['examples']]==contract['example_ids']
 for e in examples['examples']:
  name=e['document_url'].removeprefix('./');assert members[name]['sha256']==e['document_sha256']
 for role in contract['roles']:assert any(p.startswith(role+'/')and p.endswith('.wasm')for p in members),role
 stamps={}
 for name in capture:
  obj=json.loads(raw[name]);value=obj.get('release_revision')
  if value is not None:assert value==args.revision,(name,value);stamps[name]=value
 assert stamps,'No actual production revision stamp found'
 assert not args.output.exists();args.output.mkdir(parents=True)
 # Compare selected real production bytes to this exact tested artifact, streaming only.
 http=[]
 for name in sorted(set(contract['http_paths'])|set(stamps)):
  url=args.base_url.rstrip('/')+'/'+name
  request=urllib.request.Request(url,headers={'Cache-Control':'no-cache','Accept-Encoding':'identity','User-Agent':'Constitutive-Atlas-release-audit'})
  with urllib.request.urlopen(request,timeout=120)as response:
   h,size=digest(response);row={'path':name,'url':response.url,'status':response.status,'sha256':h,'bytes':size,'headers':dict(response.headers.items())}
  assert row['status']==200 and h==members[name]['sha256']and size==members[name]['bytes'],name
  http.append(row)
 report={'status':'passed-artifact-and-selected-production-http','revision':args.revision,'pages_run_id':run['id'],'artifact_id':artifact['id'],'api_artifact_digest':artifact['digest'],'download_zip_sha256':zipsha,'download_zip_bytes':zipsize,'deployment_id':deployment['id'],'members':len(members),'tar_bytes':sum(x['bytes']for x in members.values()),'revision_stamps':stamps,'http':http,'scope':'No browser or compiled execution; all source/CI evidence review remains separate.'}
 (args.output/'members.json').write_text(json.dumps(members,indent=2)+'\n');(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
