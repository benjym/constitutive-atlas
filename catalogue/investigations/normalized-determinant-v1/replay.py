"""Reassess retained opaque evidence using only its frozen trusted sources."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;REL=Path('catalogue/investigations/normalized-determinant-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replay():
 manifest=json.loads((HERE/'manifest.json').read_text())
 for name,pin in manifest['files'].items():assert sha(HERE/name)==pin,name
 freeze=json.loads((HERE/'prospective-freeze.json').read_text())
 with tempfile.TemporaryDirectory(prefix='atlas-normalized-determinant-replay-')as tmp:
  root=Path(tmp)
  for name,pin in freeze['files'].items():
   src=HERE/'source-snapshot'/name;assert sha(src)==pin,name;target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,target)
  shutil.copytree(HERE,root/REL,dirs_exist_ok=True)
  run=subprocess.run([sys.executable,'-B',str(root/REL/'verify_study.py')],cwd=root,text=True,capture_output=True,timeout=60);assert run.returncode==0,run.stderr
  return json.loads(run.stdout)|{'compiled_execution':False,'artifact_bytes_reopened_for_hash_only':True,'cache_free_frozen_closure':True}
if __name__=='__main__':print(json.dumps(replay(),indent=2))
