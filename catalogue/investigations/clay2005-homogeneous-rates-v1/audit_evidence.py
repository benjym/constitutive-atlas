"""Check retained closure/configuration/serial-build receipts and numerical report."""
import hashlib,json
from pathlib import Path
from verify_study import verify
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 manifest=json.loads((HERE/'manifest.json').read_text())
 for name,pin in manifest['files'].items():assert sha(HERE/name)==pin,name
 for role in ('native','wasm'):
  build=json.loads((HERE/(role+'-build.json')).read_text())
  config=json.loads((HERE/(role+'-configuration.json')).read_text())
  assert config['build_receipt_sha256']==sha(HERE/(role+'-build.json'))
  for name,pin in config['files'].items():assert sha(HERE/name)==pin,name
  cmd=json.loads((ROOT/build['commands'][-1]['path']).read_text())
  assert cmd['argv'][-4:]==['--target','atlas_isolated','--parallel','1']
  assert cmd['environment']['EMCC_CORES']=='1'
 report=verify();assert report==json.loads((HERE/'verification.json').read_text())
 return {'outcome':report['outcome'],'calls_per_backend':120,'retained_file_pins':len(manifest['files']),'configuration_and_serial_build_receipts_verified':True,'compiled_execution':False}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
