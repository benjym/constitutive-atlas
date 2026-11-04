import subprocess,os,sys
from pathlib import Path
env=os.environ.copy();env.update(NPM_CONFIG_CACHE="/private/tmp/atlas-baseline-delivery-20261105/npm-cache",NPM_CONFIG_OFFLINE="true")
p=Path(__file__).parent.resolve()
r=subprocess.run(["/Users/bmar5496/.codex/skills/playwright/scripts/playwright_cli.sh","--session","baseline-five-20261105","run-code","async (page) => {"+Path(sys.argv[1]).read_text()+"}"],cwd=p,env=env,capture_output=True,text=True)
print(r.stdout);print(r.stderr,file=sys.stderr)
Path(sys.argv[1]+".result.txt").write_text(r.stdout+r.stderr)
sys.exit(r.returncode)
