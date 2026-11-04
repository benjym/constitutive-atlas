from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[3];BASE=Path('/private/tmp/atlas-baseline-delivery-20261105/source');OLD=ROOT/'docs/delivery/unheld-finalisation-20261102-v1/baseline-five-nine-named-observations-v2';OVER=P.parent/'current-main-overlay-v1/final-active-v1/proposed'
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(x):return json.dumps(x,indent=2,ensure_ascii=False)+'\n'
(P/'policy.json').write_bytes((OLD/'policy.json').read_bytes())
index=json.loads((BASE/'catalogue/laboratory-examples.json').read_text());oldbase=ROOT/'docs/delivery/unheld-finalisation-20261102-v1/baseline-five-current-example-integration-v1/proposed';oldindex=json.loads((oldbase/'catalogue/laboratory-examples.json').read_text());entries=[(e,BASE) for e in index['examples']]+[(e,oldbase) for e in oldindex['examples'] if e['id'].startswith('baseline-v03-')];assert len(entries)==9
rows=[];pins={}
for e,source in entries:
 raw=(source/e['document_path']).read_bytes();assert sha(raw)==e['document_sha256'];d=json.loads(raw);model='models/'+e['model']+'.json';f=OVER/model if (OVER/model).is_file() else BASE/model;assert sha(f.read_bytes())==e['definition_sha256']
 path='references/'+e['id']+'.json';dest=P/path;dest.parent.mkdir(exist_ok=True);dest.write_bytes(raw)
 rows.append({'id':e['id'],'entry':e,'definition':{'path':model,'sha256':e['definition_sha256']},'specification':d['specification'],'old_document':{'path':str(dest.resolve()),'sha256':sha(raw),'original_path':str(source/e['document_path'])},'new_document_path':'protocols/'+e['id']+'-baseline-current16-20261105-v1.json'})
 pins[model]=e['definition_sha256']
(P/'requests.json').write_text(dump(rows));(P/'original-four-index.json').write_bytes((BASE/'catalogue/laboratory-examples.json').read_bytes())
# Exact current pure module closure used by old collector imports; source-only copy.
for f in (BASE/'web').glob('*.mjs'):
 dest=P/'context/web'/f.name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes());pins['web/'+f.name]=sha(f.read_bytes())
(P/'source-pins.json').write_text(dump(pins))
core=(OLD/'collector-core.mjs').read_text()
# Record every differing result field without assigning a historical numerical budget.
helper='''export function historicalDifferences(a,b,path='result',out=[]){
 if(path.endsWith('.elapsed_ms')||path.endsWith('.catalogue_hash'))return out;
 if(a&&b&&typeof a==='object'&&typeof b==='object'&&Array.isArray(a)===Array.isArray(b)){
  const keys=new Set([...Object.keys(a),...Object.keys(b)]);
  for(const key of keys)historicalDifferences(a[key],b[key],Array.isArray(b)?path+'['+key+']':path+'.'+key,out);
 }else if(!Object.is(a,b)&&!(a===0&&b===0))out.push({path,old:b===undefined?null:b,current:a===undefined?null:a,old_missing:b===undefined,current_missing:a===undefined,...(typeof a==='number'&&typeof b==='number'?{absolute_difference:Math.abs(a-b),relative_difference:Math.abs(a-b)/Math.max(1,Math.abs(a),Math.abs(b))}:{})});
 return out;
}
'''
core=core.replace('const clone=structuredClone;',helper+'const clone=structuredClone;')
core=core.replace("const old=readOld(row),observation=", "const old=readOld(row);assert.deepEqual(old.specification,s);entry.historical_result_differences=historicalDifferences(result,old.result);entry.historical_comparison_gate='diagnostic-only-no-budget';const observation=")
(P/'collector-core.mjs').write_text(core)
collect=(OLD/'collect.mjs').read_text();(P/'collect.original.mjs').write_text(collect)
# Gate all input identities before output creation and recheck in finally. Actual
# process lifecycle remains the approved coordinator observer, no new driver.
collect=collect.replace("const journal=", "const journal=")
start="assert.ok(!fs.existsSync(out),'Never overwrite observation');fs.mkdirSync(out);"
replace="""const protectedPaths=[freeze.repo,freeze.metadata.path,...Object.values(freeze.artifacts).map(x=>x.path),...rows.map(r=>r.old_document.path)].map(resolve);
assert.ok(!protectedPaths.some(p=>out===p||out.startsWith(p+'/')||p.startsWith(out+'/')),'Observation overlaps source/inputs');
const checkPins=()=>{
 for(const pin of [freeze.metadata,...Object.values(freeze.artifacts),freeze.fresh_qualification_receipt]){assert.ok(pin&&typeof pin.sha256==='string'&&/^[a-f0-9]{64}$/.test(pin.sha256));assert.equal(sha(pin.path),pin.sha256);}
 const catalogue=read(freeze.metadata.path);assert.equal(catalogue.sha256,'beb2f2b422c77502cc41c91b1c68921fd9db89f1b7dbc2e4f0368526d627e575');assert.equal(catalogue.models.length,16);
 for(const [name,expected]of Object.entries(read(join(HERE,'source-pins.json'))))assert.equal(sha(join(freeze.repo,name)),expected,name);
 for(const row of rows){assert.equal(sha(row.old_document.path),row.old_document.sha256);assert.deepEqual(catalogue.models.find(m=>m.id===row.specification.model),read(join(freeze.repo,row.definition.path)));assert.equal(sha(join(freeze.repo,row.definition.path)),row.definition.sha256);}
};checkPins();
assert.ok(!fs.existsSync(out),'Never overwrite observation');fs.mkdirSync(out);"""
assert start in collect;collect=collect.replace(start,replace)
collect=collect.replace("finally{emit({phase:'collector-final',status:failure?'failed':'passed'});}","finally{let post=null;try{checkPins();}catch(e){post={name:e.name,message:e.message,stack:e.stack};emit({phase:'post-input-failure',error:post});}emit({phase:'collector-final',status:failure||post?'failed':'passed'});if(post&&!failure)throw Error('Post-input guard failed: '+post.message);}")
(P/'collect.mjs').write_text(collect)
print('Prepared9 exact requests, original policy and current pure web closure')
