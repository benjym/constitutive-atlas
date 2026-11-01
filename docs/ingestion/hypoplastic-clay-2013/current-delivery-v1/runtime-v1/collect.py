from pathlib import Path
import json,sys,subprocess,datetime
from identity import digest,require,verify_inputs
s=Path(__file__).resolve().parent;b=sys.argv[1];require(b in ('native','wasm'),'backend')
verify_inputs(s);plan=json.loads((s/'PLAN.json').read_text());out=s/b;out.mkdir(exist_ok=False)
if b=='wasm':
 require((s/'native/receipt.json').is_file(),'native must run first')
 require(json.loads((s/'native/receipt.json').read_text())['completed'],'native must complete first')
 require((s/'NATIVE_PRECHECK.json').is_file() and json.loads((s/'NATIVE_PRECHECK.json').read_text())['pass'],'native gates must pass before Wasm')
receipt={'backend':b,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'freeze_sha256':digest(s/'INPUT_FREEZE.json'),'artifacts':plan['artifacts'][b],'completed':False,'commands':[],'builds':0}
def save():(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def run(label,args):
 save()
 try:p=subprocess.run(args,capture_output=True,timeout=180)
 except Exception as exc:receipt['exception']=repr(exc);save();raise
 (out/(label+'.stdout.txt')).write_bytes(p.stdout);(out/(label+'.stderr.txt')).write_bytes(p.stderr)
 receipt['commands'].append({'label':label,'argv':args,'exit_code':p.returncode});save();print(b,label,p.returncode,flush=True);return p
save()
if b=='native':
 exe=plan['native'];p=run('describe',[exe,'--describe']);require(p.returncode==0,'descriptor')
 rows=[{'id':'describe','raw':p.stdout.decode()}]
 def journal():(out/'journal.json').write_text(json.dumps(rows,indent=2)+'\n')
 journal()
 for i,req in enumerate(json.loads((s/'requests.json').read_text())):
  args=[exe,'--mode',req['mode'],'--model',req['model'],'--parameters',req['parameters'],'--initial',req['initial'],'--integration-settings',req['integration_settings']]
  for k in (['protocol','target','steps','cycles'] if req['mode']=='run' else ['strain']):args+=['--'+k,str(req[k])]
  p=run('request-'+str(i),args);rows.append({'id':req['id'],'request':req,'raw':p.stdout.decode()});journal();require(p.returncode in (0,1),'unexpected native code')
else:
 p=run('observe',['node',str(s/'observe.mjs'),str(s),plan['wasm'],str(out)]);require(p.returncode==0,'Wasm collector')
verify_inputs(s);receipt.update(completed=True,journal_sha256=digest(out/'journal.json'),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
