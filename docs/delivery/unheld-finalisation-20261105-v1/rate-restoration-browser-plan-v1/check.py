from pathlib import Path
import json,hashlib,tempfile,subprocess,importlib.util,copy
O=Path(__file__).resolve().parent;R=O.parents[3];P=O.parent/'current17-browser-plan-v1';W=O.parent/'retained-original702-browser-inputs-v1/source';old=R/'output/playwright/baseline-five-e7-20261105-v1/live';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):
 if not v:raise AssertionError(n)
 checks.append(n)
plan=json.loads((O/'plan.json').read_text());policy=json.loads((O/'POLICY.json').read_text());prior=json.loads((P/'plan.json').read_text());priorpolicy=json.loads((P/'POLICY.json').read_text())
receipt=O.parent/'retained-original702-browser-inputs-v1/receipt.json';routes=json.loads(receipt.read_text())['browser_pins'];mapping={x['path']:x['retained_path']for x in routes}
ok(len(routes)==10,'exact10 relocation routes')
for row in routes:ok(sha(Path(row['retained_path']))==row['sha256'],'retained reference '+Path(row['retained_path']).name)
for pin in policy['pins']:ok(sha(Path(pin['path']))==pin['sha256'],'all policy authority '+pin['path'])
expected=copy.deepcopy(priorpolicy);expected['identity']=policy['identity'];expected['revision']=policy['revision'];expected['reference_index']=mapping[expected['reference_index']]
for row in expected['pins']:row['path']=mapping.get(row['path'],row['path'])
ok(expected==policy,'entire policy unchanged except identity/pending revision/10 exact relocations')
ok((P/'validate.mjs').read_bytes()==(O/'validate.mjs').read_bytes(),'validator wholebyte unchanged')
for row in plan['scripts']:
 f=Path(row['path']);ok(sha(f)==row['sha256'],'script pin '+f.name)
 if 'source'in row:
  src=Path(row['source']);ok(sha(src)==row['original_sha256'],'original callback pin '+src.name)
  ok(f.read_text().replace(plan['output_directory'],prior['output_directory'])==src.read_text(),'exactcallback output substitution only '+f.name)
for f in plan['input_fixtures']:ok(sha(Path(f['source']))==f['sha256']=='e1a3814c7a153a1c86f5bb16498ddd76aff66abb11d8ac300787a0f3ef555872','exact old702 wrongcatalogue fixture')
order=plan['execution_order'];ok(order[-1]=='cycles-current17.js'and order[-3:-1]==['measurement-precondition.js','compression-live-v1.js'],'precondition compression cycles ordering')
ok(not plan['ready_for_actual']and'PENDING'in plan['source_revision']and'PENDING'in plan['runtime_regression_binding'],'no actual-ready inference')
node="const fs=require('fs');const A=Object.getPrototypeOf(async function(){}).constructor;for(const p of process.argv.slice(1))new A(fs.readFileSync(p,'utf8'));"
p=subprocess.run(['node','-e',node]+[r['path']for r in plan['scripts']],capture_output=True,text=True);ok(p.returncode==0,'all10callbacks parse without invoking '+p.stderr)
spec=importlib.util.spec_from_file_location('installer',O/'install.py');installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
root,payload=installer.validate(plan);ok(len(payload)==11,'installation includes10scripts plus1inputfixture; validation only')
for label,mutate in [('bad hash',lambda x:x['input_fixtures'][0].update(sha256='0'*64)),('escape',lambda x:x['scripts'][0].update(install_path=str(root.parent/'escaped.js'))),('duplicate',lambda x:x['input_fixtures'][0].update(install_path=x['scripts'][0]['install_path'])),('missing fixture',lambda x:x['input_fixtures'][0].update(source=str(O/'absent.json'))),('missing order',lambda x:x['execution_order'].pop())]:
 bad=copy.deepcopy(plan);mutate(bad)
 try:installer.validate(bad)
 except ValueError:ok(True,'installer rejects '+label)
 else:raise AssertionError('installer accepted '+label)
# Exact predecessor manufactured validation section; no changes to mathematical fixtures/gates.
code=(P/'check.py').read_text();code=code[code.index('# Manufactured metadata-transition'):]
exec(compile(code,str(P/'check.py'),'exec'),globals())
