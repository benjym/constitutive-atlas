from pathlib import Path
import subprocess,sys,json,hashlib,time
base=Path(__file__).resolve().parent
name=sys.argv[1];args=sys.argv[2:]
if args[0]=='run-file':args=['run-code',Path(args[1]).read_text()]
log=base/(name+'.log');receipt=base/(name+'.receipt.json')
assert not log.exists() and not receipt.exists(),'Use a new evidence identity'
start=time.time();r=subprocess.run(['node','/Users/bmar5496/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js','-s=vibe-live-v3',*args],capture_output=True,text=True)
b=(r.stdout+r.stderr).encode();log.write_bytes(b);bad=r.returncode!=0 or b'### Error' in b
receipt.write_text(json.dumps({'command':args,'returncode':r.returncode,'cli_error':bad,'started_unix':start,'elapsed_seconds':time.time()-start,'log_sha256':hashlib.sha256(b).hexdigest()},indent=2)+'\n');print(b.decode());raise SystemExit(1 if bad else 0)
