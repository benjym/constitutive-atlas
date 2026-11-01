"""Saved-only verification of completed covariance/conditioning checkpoint."""
import gzip
import json
from pathlib import Path
from covariance import HERE,ROOT,load,sha,prepare,assess
from conditioning import audit


def verify():
 for name,expected in load(HERE/'manifest.json')['files'].items():
  assert sha(HERE/name)==expected,name
 for receipt in ['prospective-freeze.json','covariance-freeze.json','saved-audit-pins.json']:
  for name,expected in load(HERE/receipt)['files'].items():assert sha(ROOT/name)==expected,name
 freeze=load(HERE/'covariance-freeze.json')
 pins=ROOT/freeze['source_pins_path'];assert sha(pins)==freeze['source_pins_sha256']
 for name,expected in load(pins)['files'].items():assert sha(ROOT/name)==expected,name
 requests=load(HERE/'covariance-requests.json.gz');assert prepare()==requests
 text=gzip.decompress((HERE/'native-output.jsonl.gz').read_bytes()).decode()
 responses=[json.loads(line) for line in text.splitlines()]
 assessment=assess(requests,responses);assert assessment==load(HERE/'covariance-assessment.json')
 assert audit(requests,responses)==load(HERE/'native-conditioning.json')
 run=load(HERE/'native-run.json');assert run['returncode']==0
 import hashlib
 assert hashlib.sha256(text.encode()).hexdigest()==run['stdout_sha256']
 wire=str(len(requests['requests']))+'\n'+'\n'.join(' '.join(repr(x) for x in row['wire']) for row in requests['requests'])+'\n'
 assert hashlib.sha256(wire.encode()).hexdigest()==run['stdin_sha256']
 assert load(HERE/'native-build.json')['argv'][-4:]==['--target','atlas_transverse_probe','--parallel','1']
 for name in ['native-configure.json','native-build.json','native-assess-process.json','all-tests-process.json']:
  assert load(HERE/name)['returncode']==0,name
 assert 'Ran 12 tests' in load(HERE/'all-tests-process.json')['stderr']
 return {'completed_checkpoint_valid':True,'proper_rotation_covariance_pass':True,'states':39,'compiled_requests':4524,
         'candidate_integrations':0,'independent_finite_path_study':'pending; revalidate existing live handle',
         'original_native_qualification':False,'scientific_signature':None}


if __name__=='__main__':print(json.dumps(verify(),indent=2))
