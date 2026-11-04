from pathlib import Path
import hashlib,json,tempfile,subprocess
Q=Path(__file__).resolve().parent;O=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/current17-browser-plan-v1');R=O.parents[3];W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');old=R/'output/playwright/baseline-five-e7-20261105-v1/live';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):
 if not v:raise AssertionError(n)
 checks.append(n)
plan=json.loads((O/'plan.json').read_text());policy=json.loads((O/'POLICY.json').read_text());cat=json.loads((O/'catalogue17.json').read_text())
for row in plan['scripts']:
 p=Path(row['path']);ok(sha(p)==row['sha256'],'scriptpin '+p.name)
 if'source'in row:
  original=Path(row['source']);ok(sha(original)==row['original_sha256'],'originalpin '+original.name)
  text=p.read_text().replace(plan['output_directory'],str(old));expected=original.read_text()
  if p.name=='named.js':
   guard=text[text.index('await page.goto(root);const currentIndex='):text.index('for(const ex of examples){')];text=text.replace(guard,'')
   ok('currentIndex.examples.map(e=>e.id).sort()'in guard and cat['sha256']in guard,'named explicit membership/catalogue gate')
  ok(text==expected,'original script bytes except exact declared changes '+p.name)
for pin in policy['pins']:ok(sha(Path(pin['path']))==pin['sha256'],'authority '+pin['path'])
ok(len(cat['models'])==17 and cat['sha256']==plan['catalogue_hash'],'exact17 catalogue')
oldcat=json.loads(Path(json.loads((O.parent/'live-release-artifact-plan-v1/browser-validator-v2.POLICY.json').read_text())['catalogue']).read_text());newmodels={m['id']:m for m in cat['models']}
for m in oldcat['models']:ok(m==newmodels[m['id']],'original16 model object unchanged '+m['id'])
for row in json.loads((O.parent/'current17-source-witness-v1/source/tests/contexts/current-seventeen-md1997-baseline-v1.json').read_text())['models']:
 m=next(m for m in cat['models']if m['id']==Path(row['path']).stem)
 # JSON file byte hashes are checked by parent source witness; stable structure binds all17 here.
 ok(m['id']==Path(row['path']).stem,'current17 member '+m['id'])
# Check actual scripts parse as async browser callbacks without running any callback.
node="const fs=require('fs');const A=Object.getPrototypeOf(async function(){}).constructor;for(const p of process.argv.slice(1))new A(fs.readFileSync(p,'utf8'));"
p=subprocess.run(['node','-e',node]+[r['path']for r in plan['scripts']],capture_output=True,text=True);ok(p.returncode==0,'all9scripts syntax only '+p.stderr)
# Manufactured metadata-transition copies of saved702 downloads. No browser/engine execution.
with tempfile.TemporaryDirectory(prefix='atlas-current17-browser-fixture-',dir=Q)as td:
 t=Path(td);D=t/'downloads';D.mkdir()
 for p in old.glob('*.json'):
  if p.name=='wrong-catalogue.json':continue
  d=json.loads(p.read_text())
  if 'catalogue_hash'in d:d['catalogue_hash']=policy['catalogue_hash']
  if isinstance(d.get('result'),dict)and'catalogue_hash'in d['result']:d['result']['catalogue_hash']=policy['catalogue_hash']
  (D/p.name).write_text(json.dumps(d))
 for p in old.glob('*.csv'):(D/p.name).write_bytes(p.read_bytes())
 counter=0
 def run(expected,label):
  global counter
  counter+=1;out=t/f'report{counter}.json'
  r=subprocess.run(['node',str(O/'validate.mjs'),str(D),str(W),str(out)],capture_output=True,text=True)
  (Q/f'check-{counter}.stdout').write_text(r.stdout);(Q/f'check-{counter}.stderr').write_text(r.stderr)
  ok((r.returncode==0)==expected,label)
  return json.loads(out.read_text())if out.exists()else None
 report=run(True,'metadata-only transition fixture passes original579 gates');ok(report['checks']==579,'original579 count')
 named=D/('named-'+policy['expected_ids'][0]+'.json');saved=named.read_bytes();d=json.loads(saved);d['result']['points'][1]['p']+=1000;named.write_text(json.dumps(d));run(False,'original physical1e-10 gate rejects drift');named.write_bytes(saved)
 d=json.loads(saved);d['result']['catalogue_hash']=policy['old_catalogue_hash'];named.write_text(json.dumps(d));run(False,'actual oldcatalogue rejected');named.write_bytes(saved)
 d=json.loads(saved);d['specification']['cycles']+=1;named.write_text(json.dumps(d));run(False,'original named request changed rejects');named.write_bytes(saved)
 csv=D/'linear-elastic-default.csv';b=csv.read_text();lines=b.splitlines();cols=lines[1].split(',');cols[0]='Infinity';lines[1]=','.join(cols);csv.write_text('\n'.join(lines)+'\n');run(False,'nonfinite CSV axialstrain rejected');csv.write_text(b)
 mobile=D/'linear-elastic-mobile.json';b=mobile.read_bytes();d=json.loads(b);d['result']['points'][1]['p']+=1;mobile.write_text(json.dumps(d));run(False,'sameinstance mobile drift rejected');mobile.write_bytes(b)
 d=json.loads(saved);d['result']['model']='other';named.write_text(json.dumps(d));run(False,'exact otherresultfield drift rejected');named.write_bytes(saved)
(Q/'manufactured-checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'manufactured_only':True,'actual_browser_or_engines':0},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
