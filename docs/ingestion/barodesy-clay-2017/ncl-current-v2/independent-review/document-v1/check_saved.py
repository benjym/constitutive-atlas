from pathlib import Path
import json,hashlib,subprocess,tempfile
R=Path('/Users/bmar5496/code/constitutive-atlas');P=R/'docs/ingestion/barodesy-clay-2017/ncl-current-v2';O=P/'independent-review/document-v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
if O.exists():
 for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
plan=read(P/'document-plan-v1.json')
for p,h in plan['files'].items():assert sha(R/p)==h,p
doc=read(P/'laboratory-document-v2.json');old=read(P.parent/'ncl-laboratory-v1/laboratory-document.json');rows=read(P/'results/wasm.json');req=read(P/'results/requests.json');cat=read(plan['catalogue'])
assert doc['specification']==old['specification']==req[0]['specification'] and doc['result']==rows[0]['result']and doc['catalogue_hash']==cat['sha256']
entry=read(P/'proposed-example-entry-v2.json');reg=read(P/'proposed-registry-v2.json');original=read(R/'catalogue/laboratory-examples.json');assert reg['examples'][:-1]==original['examples'] and reg['examples'][-1]==entry and len(reg['examples'])==4
assert entry['document_sha256']==sha(P/'laboratory-document-v2.json')and entry['definition_sha256']==sha(R/'models/barodesy-clay-2017.json')
source=Path('/private/tmp/atlas-barodesy-ncl-document-v2/source');package=Path('/private/tmp/atlas-barodesy-ncl-document-v2/package');assert read(source/'catalogue/laboratory-examples.json')==reg
for e in reg['examples']:
 assert sha(source/e['document_path'])==e['document_sha256'];assert sha(source/f"models/{e['model']}.json")==e['definition_sha256']
 assert (package/f"laboratory-examples/{e['id']}.json").read_bytes()==(source/e['document_path']).read_bytes()
consumer=read(P/'document-consumer-v1.json');assert consumer['passed']and consumer['index']==read(package/'laboratory-examples.json')
for n,h in consumer['outputs'].items():assert sha(P/n)==h
# Pure creator/parser and normal consumer, generated into fresh reviewer temp only.
js="""import{readFileSync}from'node:fs';import assert from'node:assert/strict';import{createLaboratoryDocument,parseLaboratoryDocument}from'./web/laboratory-document.mjs';import{bundle}from'./tools/build_laboratory_examples.mjs';const p='docs/ingestion/barodesy-clay-2017/ncl-current-v2',read=x=>JSON.parse(readFileSync(x));const plan=read(p+'/document-plan-v1.json'),cat=read(plan.catalogue),doc=read(p+'/laboratory-document-v2.json'),s=read(p+'/results/requests.json')[0].specification,r=read(p+'/results/wasm.json')[0].result;assert.deepEqual(createLaboratoryDocument(s,r,cat),doc);assert.equal(JSON.stringify(doc,null,2)+'\\n',readFileSync(p+'/laboratory-document-v2.json','utf8'));assert.deepEqual(parseLaboratoryDocument(JSON.stringify(doc),cat),s);const index=await bundle('/private/tmp/atlas-barodesy-ncl-document-v2/source',process.argv[1],cat);assert.deepEqual(index,read(p+'/document-consumer-v1.json').index);console.log('PASS: generic creator/parser exact bytes and normal four-example consumer; no compiled calls');"""
with tempfile.TemporaryDirectory(prefix='ncl-document-independent-')as tmp:
 z=subprocess.run(['node','--input-type=module','-e',js,tmp],cwd=R,text=True,capture_output=True);assert z.returncode==0,z.stderr
# Independently reconstruct every reported leaf difference, including added diagnostic fields.
diffs=[]
def delta(a,b,path=''):
 if isinstance(a,dict)and isinstance(b,dict):
  for k in sorted(set(a)|set(b)):
   p=path+'/'+k
   if k not in a or k not in b:diffs.append({'path':p,'presence_changed':True})
   else:delta(a[k],b[k],p)
 elif isinstance(a,list)and isinstance(b,list):
  assert len(a)==len(b)
  for i,(x,y)in enumerate(zip(a,b)):delta(x,y,path+'/'+str(i))
 elif a!=b:diffs.append({'path':path,'old':a,'new':b})
delta(old,doc);saved=read(P/'document-delta-v1.json');assert diffs==saved['differences']and len(diffs)==912
print(json.dumps({'passed':True,'plan_pins':len(plan['files']),'saved_result_exact':True,'original_specification_identical':True,'existing_entries_unchanged':3,'normal_consumer_entries':4,'document_leaf_differences':len(diffs),'public_creator_consumer_stdout':z.stdout.strip(),'reviewer_compiled_calls':0,'root_installation_reviewed':False,'browser_reviewed':False},indent=2))
