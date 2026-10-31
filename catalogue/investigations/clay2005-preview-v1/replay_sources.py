"""Reconstruct trusted frozen study/reference sources; reassess raw evidence, no builds."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replay():
 for name,pin in json.loads((HERE/'evidence-manifest.json').read_text()).items():assert sha(HERE/name)==pin,name
 with tempfile.TemporaryDirectory(prefix='atlas-clay2005-preview-source-replay-')as tmp:
  target=Path(tmp)/'study';shutil.copytree(HERE,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))
  reference=subprocess.run([sys.executable,'-I','-B',str(target/'reference/check.py'),'--root',str(target/'frozen')],cwd=target,text=True,capture_output=True,timeout=60);assert reference.returncode==0,reference.stderr
  launcher="import runpy,sys; sys.path.insert(0,sys.argv[1]); runpy.run_path(sys.argv[1]+'/verify_study.py',run_name='__main__')"
  run=subprocess.run([sys.executable,'-I','-B','-c',launcher,str(target)],cwd=target,text=True,capture_output=True,timeout=60);assert run.returncode==0,run.stderr
  result=json.loads(run.stdout);assert result==json.loads((HERE/'assessment.json').read_text())
  return {'pass':result['pass'],'raw_assessment_identical':True,'reference_reproduced':True,'ambient_repository_sources_used':False,'compiled_execution':False,'artifact_bytes_reopened_for_hash_only':True}
if __name__=='__main__':print(json.dumps(replay(),indent=2))
