"""Local command-routing check: intercept material runner, replay saved streams."""
from pathlib import Path
from unittest.mock import patch
from argparse import Namespace
import hashlib,json,shutil,sys
r=Path('/Users/bmar5496/code/constitutive-atlas');sys.path.insert(0,str(r))
from tools import benchmark_tmd2 as b
base=r/'docs/benchmarks/kfs-tmd2-research-range-v1';stage=Path(__file__).parent
pins=json.loads((base/'inputs/source-pins.json').read_text());solver=Path(pins['artifact']['path'])
archive=r/'data/raw/KFS-TMD1-5.zip';results=[]
original_command=b.command
for code in [0,23]:
 out=stage/f'command-exit-{code}';calls=[]
 def command(args,directory,stem):
  calls.append(stem)
  if stem=='execute':
   observations=out/'observations';shutil.copytree(base/'observations',observations)
   for p in observations.glob('*/receipt.json'):
    record=json.loads(p.read_text());record['freeze_sha256']=b.sha(out/'inputs/freeze.json')
    if p.parent.name=='tmd2-400':record['returncode']=code
    p.write_text(json.dumps(record))
  elif stem=='assess':original_command(args,directory,stem)
  else:raise AssertionError('Unexpected build/process stage: '+stem)
 args=Namespace(output=out,archive=archive,solver=solver)
 error=None
 with patch.object(b,'command',command):
  try: status=b.run(args)
  except ValueError as exc: status=1;error=str(exc)
 result={'altered_exit':code,'command_stages':calls,'status':status,'error':error,'assessor_invoked': 'assess' in calls,'process_check_written':(out/'process-check.json').exists(),'no_backend_calls':True,'no_build':True}
 if code==0:
  result['summary_identical']= (out/'results/summary.json').read_bytes()==(base/'results/summary.json').read_bytes()
  assert result['summary_identical'] and status==0 and calls==['execute','assess']
 else:assert status==1 and calls==['execute'] and 'integer zero' in error
 results.append(result)
report={'method':'Intercept supported command material-runner stage; replay recorded streams with fresh freeze binding. Only original Python assessor executes for valid case. Nonzero exception is mapped to status1 as main does. No solver or build invocation.','cases':results}
(stage/'command-routing-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
