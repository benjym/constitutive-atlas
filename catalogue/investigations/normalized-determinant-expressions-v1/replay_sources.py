"""Regenerate the frozen protocol in isolation; no compiled execution or reassessment."""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('catalogue/investigations/normalized-determinant-expressions-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replay():
 freeze=json.loads((HERE/'prospective-freeze.json').read_text())
 names=json.loads((HERE/'generator-replay.json').read_text())['files_compared']
 with tempfile.TemporaryDirectory(prefix='atlas-ratio-context-source-replay-')as tmp:
  root=Path(tmp)/'root';output=Path(tmp)/'generated';root.mkdir()
  for name,pin in freeze['files'].items():
   source=HERE/'frozen'/name;assert sha(source)==pin,name
   target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  env={k:v for k,v in os.environ.items()if k not in ('PYTHONPATH','PYTHONHOME')}
  run=subprocess.run([sys.executable,'-I','-B',str(root/REL/'generate-study.py'),str(output)],cwd=root,env=env,text=True,capture_output=True,timeout=60)
  assert run.returncode==0,run.stderr
  actual=sorted(str(p.relative_to(output))for p in output.rglob('*')if p.is_file())
  assert actual==names,'complete generated file set'
  for name in names:assert (output/name).read_bytes()==(root/REL/name).read_bytes(),name
  assert not any(p.suffix in ('.pyc','.pyo')or '__pycache__'in p.parts for p in root.rglob('*'))
  return {'outcome':'passed','frozen_files':len(freeze['files']),'generated_files_compared':len(names),'all_exact':True,'isolated_interpreter':True,'ambient_repository_sources_used':False,'compiled_execution':False,'raw_numerical_reassessment':False,'artifact_hash_reopened':False,'freeze_sha256':sha(HERE/'prospective-freeze.json')}
if __name__=='__main__':print(json.dumps(replay(),indent=2))
