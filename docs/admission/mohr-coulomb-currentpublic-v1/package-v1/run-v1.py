from pathlib import Path
import json,subprocess,time,hashlib
packet=Path('/Users/bmar5496/code/constitutive-atlas/docs/admission/mohr-coulomb-currentpublic-v1/package-v1')
plan=json.loads((packet/'execution-plan.json').read_text())
assert not (packet/'build-status.json').exists()
pre=subprocess.run(plan['commands']['preflight'],capture_output=True,text=True)
(packet/'execution-preflight.log').write_text(pre.stdout+pre.stderr)
assert pre.returncode==0,pre.stdout+pre.stderr
start=time.time();cmd=plan['commands']['standard_package']
with (packet/'build.log').open('wb') as log:
 process=subprocess.run(cmd,cwd='/private/tmp/atlas-mc-admission-public-v1',stdout=log,stderr=subprocess.STDOUT)
result={'command':cmd,'exit_code':process.returncode,'start_unix':start,'end_unix':time.time(),'source_commit':'000ab5e79619038e0b56483e0146cf2e9ce4bd18','freeze_sha256':plan['freeze_sha256'],'log_sha256':hashlib.sha256((packet/'build.log').read_bytes()).hexdigest(),'status':'passed' if process.returncode==0 else 'failed'}
(packet/'build-status.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));print((packet/'build.log').read_text()[-3500:])
