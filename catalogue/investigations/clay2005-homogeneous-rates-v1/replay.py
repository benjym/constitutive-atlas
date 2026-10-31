"""Re-audit the retained source closure in an isolated temporary tree.

Copies trusted Atlas Python sources and opaque evidence, never compiles or runs
material artifacts. The historical verifier reopens artifact bytes by hash.
The source closure excludes caches and bytecode.
"""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
REL=Path('catalogue/investigations/clay2005-homogeneous-rates-v1')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def replay():
 manifest=json.loads((HERE/'manifest.json').read_text())
 for name,pin in manifest['files'].items():assert sha(HERE/name)==pin,name
 protocol=json.loads((HERE/'protocol.json').read_text())
 with tempfile.TemporaryDirectory(prefix='atlas-claydet-replay-')as tmp:
  root=Path(tmp)
  for name,pin in protocol['files'].items():
   source=HERE/'frozen-sources'/name;assert sha(source)==pin,name
   target=root/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  # Exact retained model/protocol/evidence; no historical byte substitution.
  shutil.copytree(HERE,root/REL,dirs_exist_ok=True)
  run=subprocess.run([sys.executable,'-B',str(root/REL/'verify_study.py')],cwd=root,text=True,capture_output=True,timeout=60)
  assert run.returncode==0,run.stderr
  observed=json.loads(run.stdout);expected=json.loads((HERE/'verification.json').read_text());assert observed==expected
  return {'version':'clay2005-homogeneous-frozen-source-replay-v1','retained_verification_identical':True,'outcome':observed['outcome'],'calls_per_backend':observed['calls_per_backend'],'source_files':len(protocol['files']),'compiled_execution':False,'rebuild':False,'artifact_bytes_reopened_for_hash_only':True,'incidental_bytecode_snapshot_imported':False,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(replay(),indent=2))
