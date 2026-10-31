"""Collect only new refinement calls from exact parent binaries; preserve originals."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys,os
s=Path(__file__).resolve().parent;base=s.parent/'terracotta-preparation-hold-v1';role=sys.argv[1];assert role in ('native','wasm')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 for n,h in json.loads((s/'manifest.json').read_text()).items():assert sha(s/n)==h,n
 for n,h in json.loads((s/'parent-bindings.json').read_text())['files'].items():assert sha(base/n)==h,n
verify();freeze=json.loads((s/'prospective-freeze.json').read_text());assert freeze['new_compiled_observations']==0 and freeze['manifest_sha256']==sha(s/'manifest.json')
out=s/role;assert not out.exists();out.mkdir()
parent=json.loads((base/role/'receipt.json').read_text());assert parent['completed']
for item in parent['artifacts'].values():assert sha(Path(item['path']))==item['sha256']
receipt={'backend':role,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent_receipt_sha256':sha(base/role/'receipt.json'),'artifacts':parent['artifacts'],'commands':[],'completed':False,'rebuild':False}
def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def run(label,cmd):
 p=subprocess.run(cmd,capture_output=True,timeout=240,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
 (out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 receipt['commands'].append({'label':label,'argv':cmd,'returncode':p.returncode});save();print(role,label,p.returncode,flush=True)
 assert p.returncode in (0,1);return p
save()
if role=='native':
 sys.path.insert(0,str(base/'frozen'));from atlas.schedule import schedule_command
 rows=[];binary=parent['artifacts']['atlas_terracotta_study']['path']
 for i,row in enumerate(json.loads((s/'requests.json').read_text())['records']):
  p=run('request-'+str(i),schedule_command(row['request'],binary));rows.append({**row,'raw':p.stdout.decode(),'returncode':p.returncode});(out/'journal.json').write_text(json.dumps(rows,indent=2)+'\n')
else:
 build=Path(parent['artifacts']['terracotta-study.js']['path']).parent
 p=run('observe',['node',str(s/'observe.mjs'),str(s),str(build),str(out)]);assert p.returncode==0
verify();receipt.update(completed=True,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),journal_sha256=sha(out/'journal.json'));save()
