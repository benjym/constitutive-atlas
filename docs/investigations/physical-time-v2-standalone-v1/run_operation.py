"""Coordinator-only sequential operation recorder; no queued/background operations."""
import datetime,hashlib,json,os,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 f=json.loads((OUT/'FREEZE.json').read_text())
 assert all(sha(ROOT/p)==v for p,v in f['files'].items())
 t=json.loads((OUT/'TOOLS.json').read_text())
 assert all(sha(pathlib.Path(p))==v for p,v in t['binary_files'].items())
def main():
 name=sys.argv[1];argv=sys.argv[2:]
 assert name and all(c.isalnum() or c in '-_' for c in name) and argv
 dest=OUT/'actual-native-v1';dest.mkdir(exist_ok=True)
 log=dest/(name+'.log');receipt=dest/(name+'.json')
 assert not log.exists() and not receipt.exists()
 verify()
 data={'argv':argv,'cwd':str(ROOT),'source_freeze_sha256':sha(OUT/'FREEZE.json'),'tools_sha256':sha(OUT/'TOOLS.json'),'recorder_sha256':sha(pathlib.Path(__file__)),'start':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preverified':True,'environment':{k:os.environ[k] for k in ['PATH','CC','CXX','CFLAGS','CXXFLAGS','LDFLAGS','SDKROOT','MACOSX_DEPLOYMENT_TARGET','CMAKE_GENERATOR','PYTHONPATH','PYTHONNOUSERSITE','ATLAS_TIME_SOLVER'] if k in os.environ}}
 code=125
 with log.open('w') as f:
  try:code=subprocess.run(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,timeout=240).returncode
  except (subprocess.TimeoutExpired,OSError) as error:data['execution_error']=repr(error)
 data.update(returncode=code,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),log_sha256=sha(log))
 try:verify();data['postverified']=True
 except Exception as error:data['postverified']=False;data['postverify_error']=repr(error)
 receipt.write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps(data,indent=2));sys.exit(code if data['postverified'] else 2)
if __name__=='__main__':main()
