import hashlib,json,subprocess,sys,time
from pathlib import Path
base=Path('/private/tmp/atlas-maxwell-current-v1')
plan=Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/maxwell-itasca900/atlas-build-v1/prospective-commands.json')
spec=json.loads(plan.read_text()); key=sys.argv[1]; cmd=spec['commands'][key]
logs=base/'execution';logs.mkdir(exist_ok=True)
assert not (logs/(key+'.json')).exists(), 'Do not overwrite an execution'
start=time.time()
with (logs/(key+'.log')).open('wb') as out:
 result=subprocess.run(cmd,cwd=spec['cwd'],stdout=out,stderr=subprocess.STDOUT)
record={'step':key,'command':cmd,'cwd':spec['cwd'],'plan_sha256':hashlib.sha256(plan.read_bytes()).hexdigest(),'started_unix':start,'elapsed_seconds':time.time()-start,'exit_code':result.returncode,'log_sha256':hashlib.sha256((logs/(key+'.log')).read_bytes()).hexdigest()}
(logs/(key+'.json')).write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record));print((logs/(key+'.log')).read_text()[-9000:]);sys.exit(result.returncode)
