"""Original frozen v2 main/HTTP gates with separately qualified streaming namespace transform."""
from pathlib import Path
import importlib.util,hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
import transform

def main():
 policy=json.loads((HERE/'POLICY.json').read_text())
 for pin in policy['inputs']:
  raw=Path(pin['path']).read_bytes();assert len(raw)==pin['bytes']and hashlib.sha256(raw).hexdigest()==pin['sha256'],pin['path']
 original=next(x['path']for x in policy['inputs']if x['path'].endswith('/verify-v2.py'))
 spec=importlib.util.spec_from_file_location('frozen_v2_verifier',original);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.verify_archive=transform.verify_archive
 output=Path(sys.argv[sys.argv.index('--output')+1]);existed=output.exists()
 try:m.main()
 finally:
  if not existed and output.is_dir()and hasattr(transform.verify_archive,'last_proof'):
   with (output/'namespace-transform.json').open('x')as stream:stream.write(json.dumps(transform.verify_archive.last_proof,indent=2)+'\n')
if __name__=='__main__':main()
