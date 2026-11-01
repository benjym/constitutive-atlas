"""Execute exact inspected Playwright CLI scripts and retain raw tool output."""
import sys,pathlib,subprocess,json,re
base=pathlib.Path(__file__).resolve().parent;name=sys.argv[1]
script=base/(name+'.js');log=base/(name+'.log');out=base/(name+'.json')
assert not log.exists(),log
p=subprocess.run(['node','/Users/bmar5496/.npm/_npx/31e32ef8478fbf80/node_modules/@playwright/cli/playwright-cli.js','-s=barodesy-sand-v3','run-code',script.read_text()],capture_output=True,text=True,timeout=180)
log.write_text(p.stdout+p.stderr);m=re.search(r'### Result\n(.*?)(?:\n###|\Z)',p.stdout,re.S)
if not m:print(p.stdout[-3000:]);raise SystemExit(1)
data=json.loads(m.group(1));out.write_text(json.dumps(data,indent=2)+'\n');print(name,'saved',len(out.read_bytes()),'bytes');assert p.returncode==0
