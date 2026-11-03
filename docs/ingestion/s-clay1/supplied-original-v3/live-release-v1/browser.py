"""Retain exact commands and results for the task-owned live browser."""
from pathlib import Path
import subprocess,sys,json,datetime
out=Path(__file__).resolve().parent/'browser';out.mkdir(exist_ok=True)
n=len(list(out.glob('*.json')))+1
args=['/Users/bmar5496/.npm/_npx/31e32ef8478fbf80/node_modules/.bin/playwright-cli','-s=sclay1-live-v1',*sys.argv[1:]]
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
r=subprocess.run(args,capture_output=True,text=True)
(out/f'{n:03}.stdout.log').write_text(r.stdout);(out/f'{n:03}.stderr.log').write_text(r.stderr)
(out/f'{n:03}.json').write_text(json.dumps({'command':args,'started':start,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'returncode':r.returncode},indent=2)+'\n')
print(r.stdout);print(r.stderr,file=sys.stderr);sys.exit(r.returncode)
