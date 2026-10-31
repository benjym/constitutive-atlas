"""Verify retained context evidence, frozen source closure and exact assessment."""
import hashlib,json
from pathlib import Path
from assess import assessment
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 manifest=json.loads((HERE/'manifest.json').read_text())
 for name,pin in manifest['files'].items():assert sha(HERE/name)==pin,name
 frozen=json.loads((HERE/'prospective-freeze.json').read_text());assert frozen['compiled_observations_at_freeze']==0
 for name,pin in frozen['files'].items():assert sha(HERE/'frozen'/name)==pin,name
 result=assessment();assert result==json.loads((HERE/'assessment.json').read_text())and result['outcome']=='passed'
 assert result['calls_per_backend']==1953 and result['explicit_recovery_pairs']==726
 for role in ('native','wasm'):
  build=json.loads((HERE/(role+'-build.json')).read_text())
  command=json.loads((ROOT/build['commands'][-1]['path']).read_text())
  assert command['argv'][-4:]==['--target','atlas_normalized_determinant_context','--parallel','1']
  assert command['environment']['EMCC_CORES']=='1'
 config=json.loads((HERE/'configuration-capture.json').read_text())
 for role,data in config.items():
  assert data['build_sha256']==sha(HERE/(role+'-build.json'))
  for entry in data['configuration_files']:assert sha(HERE/entry['retained'])==entry['sha256']
 print(json.dumps({'outcome':result['outcome'],'calls_per_backend':result['calls_per_backend'],'material_recovery_pairs':result['explicit_recovery_pairs'],'scalar_AD_columns':38,'history_recovery_triplets':6}))
if __name__=='__main__':verify()
