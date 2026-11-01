from pathlib import Path
import subprocess,os,sys,json
r=Path('/Users/bmar5496/code/constitutive-atlas');p=r/'docs/reviews/declared-loading-browser-v1';out=p/'observations';out.mkdir(exist_ok=True)
args=sys.argv[1:]
if args[0]=='--script':args=['run-code',Path(args[1]).read_text()]
n=len(list(out.glob('*.command.json')))+1;stem=f'{n:03d}-{args[0]}'
cmd=['/Users/bmar5496/.codex/skills/playwright/scripts/playwright_cli.sh','--session','atlas-loading-rollout',*args]
result=subprocess.run(cmd,cwd=r,env=dict(os.environ,npm_config_offline='true'),capture_output=True,text=True)
(out/(stem+'.command.json')).write_text(json.dumps({'argv':cmd,'exit_code':result.returncode},indent=2)+'\n');(out/(stem+'.stdout')).write_text(result.stdout);(out/(stem+'.stderr')).write_text(result.stderr)
print(result.stdout[-4500:]);print(result.stderr[-1000:]);sys.exit(result.returncode)
