"""Verify frozen inputs, raw assessment, configuration and artifact hashes; no execution."""
from pathlib import Path
import datetime,hashlib,json
from assess import assess
HERE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 freeze=read(HERE/'prospective-freeze.json');assert freeze['compiled_observations_at_freeze']==0 and freeze['manifest_sha256']==sha(HERE/'manifest.json')
 for name,pin in read(HERE/'manifest.json').items():assert sha(HERE/name)==pin,name
 for name,pin in read(HERE/'input-pins.json').items():assert sha(HERE/'frozen'/name)==pin,name
 receipts={}
 for role in ('native','wasm'):
  receipt=read(HERE/role/'receipt.json');receipts[role]=receipt
  assert receipt['environment']['EMCC_CORES']=='1'
  build=next(c for c in receipt['commands']if c['label']=='build')
  assert build['argv'][-4:]==['--target','atlas_laboratory_preview','--parallel','1']and build['exit_code']==0
  for artifact in receipt['artifacts'].values():assert sha(Path(artifact['path']))==artifact['sha256']
  config=read(HERE/role/'configuration.json');assert config['receipt_sha256']==sha(HERE/role/'receipt.json')
  for name,pin in config['files'].items():assert sha(HERE/role/name)==pin,name
 assert datetime.datetime.fromisoformat(receipts['native']['finished_utc'])<=datetime.datetime.fromisoformat(receipts['wasm']['started_utc'])
 result=assess();assert result==read(HERE/'assessment.json')
 return result
if __name__=='__main__':print(json.dumps(verify(),indent=2,allow_nan=False))
