"""Verify the Pages deployment for the exact successful release revision."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
HEAD='43ea5c45f0e6112661fe996b685a3adcdac12ce6'
BASE='https://benjym.github.io/constitutive-atlas/'
def api(path):return json.loads(subprocess.check_output(['gh','api','repos/benjym/constitutive-atlas/'+path]))
deployments=api('deployments?sha='+HEAD+'&environment=github-pages&per_page=100')
(HERE/'PAGES-DEPLOYMENTS.json').write_text(json.dumps(deployments,indent=2)+'\n')
assert deployments
d=deployments[0];assert d['sha']==HEAD and d['environment']=='github-pages'
statuses=api(f"deployments/{d['id']}/statuses")
(HERE/'PAGES-STATUSES.json').write_text(json.dumps(statuses,indent=2)+'\n')
assert statuses and statuses[0]['state']=='success'
s=statuses[0];assert s['environment_url'].rstrip('/')==BASE.rstrip('/')
receipt={'source_revision':HEAD,'run_id':41388826742,'deployment_id':d['id'],'deployment_url':d['url'],'status_id':s['id'],'state':s['state'],'environment_url':s['environment_url'],'log_url':s['log_url'],'created_at':s['created_at'],'passed':True}
(HERE/'PAGES-DEPLOYMENT-CHECK.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
