"""Serial opaque collection using exact frozen-parent artifacts; no build."""
from pathlib import Path
import sys,json,hashlib,subprocess,datetime
s=Path(__file__).resolve().parent;b=sys.argv[1];assert b in('native','wasm');out=s/b;assert not out.exists();out.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check():
 for n,h in json.loads((s/'manifest.json').read_text()).items():assert sha(s/n)==h,n
check();reuse=json.loads((s/'artifact-reuse.json').read_text())['backend'][b];parent=reuse['receipt']
for artifact in parent['artifacts'].values():assert sha(artifact['path'])==artifact['sha256']
receipt={'backend':b,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':sha(s/'manifest.json'),'reused_build_receipt_sha256':reuse['receipt_sha256'],'artifacts':parent['artifacts'],'completed':False,'commands':[],'builds':0}
def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def run(label,args):
 try:p=subprocess.run(args,capture_output=True,timeout=180)
 except Exception as exc:receipt['exception']=repr(exc);save();raise
 (out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 receipt['commands'].append({'label':label,'argv':args,'exit_code':p.returncode});save();print(b,label,p.returncode,flush=True);return p
save()
if b=='native':
 exe=parent['artifacts']['atlas_laboratory_preview']['path'];p=run('describe',[exe,'--describe']);assert p.returncode==0;rows=[{'id':'describe','raw':p.stdout.decode()}]
 (out/'journal.json').write_text(json.dumps(rows,indent=2)+'\n')
 for i,req in enumerate(json.loads((s/'requests.json').read_text())):
  args=[exe,'--mode',req['mode'],'--model',req['model'],'--parameters',req['parameters'],'--initial',req['initial'],'--integration-settings',req['integration_settings']]
  for k in(['protocol','target','steps','cycles']if req['mode']=='run'else['strain']):args+=['--'+k,str(req[k])]
  p=run('request-'+str(i),args);rows.append({'id':req['id'],'request':req,'raw':p.stdout.decode()});(out/'journal.json').write_text(json.dumps(rows,indent=2)+'\n');assert p.returncode in(0,1)
else:
 build=Path(parent['artifacts']['atlas-preview.js']['path']).parent;p=run('observe',['node',str(s/'observe.mjs'),str(s),str(build),str(out)]);assert p.returncode==0
check()
for artifact in parent['artifacts'].values():assert sha(artifact['path'])==artifact['sha256']
receipt.update(completed=True,journal_sha256=sha(out/'journal.json'),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
