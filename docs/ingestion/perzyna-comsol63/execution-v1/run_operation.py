"""Coordinator serial recorder; retain genuine exits and verify frozen inputs."""
import datetime,hashlib,json,os,pathlib,subprocess,sys
BASE=pathlib.Path(__file__).resolve().parent
ROOT=BASE.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 f=json.loads((BASE/'FREEZE.json').read_text())
 for p,h in f['files'].items():assert sha(ROOT/p)==h,p
 for p,h in f['external_files'].items():assert sha(pathlib.Path(p))==h,p
 return sha(BASE/'FREEZE.json')
def main():
 name=sys.argv[1];argv=sys.argv[2:];assert name and all(c.isalnum() or c in '-_' for c in name) and argv
 out=BASE/'actual-v1';out.mkdir(exist_ok=True);log=out/(name+'.log');receipt=out/(name+'.json')
 assert not log.exists() and not receipt.exists()
 data=dict(argv=argv,cwd=str(ROOT),freeze_sha256=verify(),preverified=True,start=datetime.datetime.now(datetime.timezone.utc).isoformat(),environment=dict(os.environ))
 # Environment is retained privately in process memory; publish only build-relevant fields.
 data['environment']={k:v for k,v in data['environment'].items() if k in ['PATH','CC','CXX','CFLAGS','CXXFLAGS','LDFLAGS','SDKROOT','MACOSX_DEPLOYMENT_TARGET','EM_CACHE','PYTHONPATH','PYTHONNOUSERSITE','CMAKE_GENERATOR']}
 code=125
 with log.open('w') as stream:
  try:code=subprocess.run(argv,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,timeout=7200).returncode
  except (subprocess.TimeoutExpired,OSError) as error:data['execution_error']=repr(error)
 data.update(returncode=code,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),log_sha256=sha(log))
 try:verify();data['postverified']=True
 except Exception as error:data.update(postverified=False,postverify_error=repr(error))
 receipt.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2));sys.exit(code if data['postverified'] else 2)
if __name__=='__main__':main()
