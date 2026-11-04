"""Coordinator-only versioned v2 semantic/HTTP verifier + qualified v3/gzip archive callback."""
from pathlib import Path
import sys,importlib.util,json,hashlib
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
import compressed

def main():
 for pin in json.loads((HERE/'POLICY.json').read_text())['inputs']:
  data=Path(pin['path']).read_bytes();assert len(data)==pin['bytes']and hashlib.sha256(data).hexdigest()==pin['sha256'],pin['path']
 spec=importlib.util.spec_from_file_location('semantic_v4',HERE/'verify-base-v4.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.verify_archive=compressed.verify_archive
 output=Path(sys.argv[sys.argv.index('--output')+1]);existed=output.exists()
 try:m.main()
 finally:
  if not existed and output.is_dir()and hasattr(compressed.verify_archive,'last_proof'):
   with(output/'compressed-transform.json').open('x')as stream:stream.write(json.dumps(compressed.verify_archive.last_proof,indent=2)+'\n')
if __name__=='__main__':main()
