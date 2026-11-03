import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,mkdirSync,writeFileSync,rmSync,readFileSync,readdirSync,unlinkSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {validatePackage,validateControlledTimeMembership} from '../tools/test_web_package.mjs';

function fixture(fn){
 const dir=mkdtempSync(join(tmpdir(),'atlas-package-test-'));
 const raw={};
 const put=(file,value)=>{raw[file]=typeof value==='string'?value:JSON.stringify(value);writeFileSync(join(dir,file),raw[file]);};
 const refreshDatabase=()=>{
  const database='SQLite format 3\0synthetic fixture';
  put('atlas.sqlite',database);
  const sha=value=>createHash('sha256').update(value).digest('hex');
  put('atlas-database.json',{kind:'constitutive-atlas-database-package',schema_version:'0.1',database:{path:'atlas.sqlite',media_type:'application/vnd.sqlite3',bytes:Buffer.byteLength(database),sha256:sha(database)},package_inputs:{'models.json':sha(raw['models.json']),'catalogue.json':sha(raw['catalogue.json'])},ordinary_engine_model_ids:['example'],measurements_included:false,source_documents_included:false,compiled_engines_included:false});
 };
 mkdirSync(join(dir,'models'));mkdirSync(join(dir,'schemas'));
 const model={id:'example',schema_version:'0.3',sources:[{url:'https://doi.org/10.1002/nag.416'}]};
 const meta={sha256:'test',models:[model]},catalogue={models:[{id:'example',executable:true}]};
 put('models.json',meta);put('catalogue.json',catalogue);put('models/example.json',model);put('schemas/model-v0.3.schema.json','{}');
 for(const name of ['atlas.js','atlas.wasm','worker.js','numerics.mjs','loading.mjs','recorded.mjs','state-contract.mjs','.nojekyll'])put(name,'');
 put('index.html','<script src="./atlas.js"></script><a href="./models/example.json">JSON</a><a href="https://doi.org/10.1002/nag.416">Source</a>');
 refreshDatabase();
 try{fn({dir,put,model,meta,catalogue,refreshDatabase});}finally{rmSync(dir,{recursive:true,force:true});}
}
test('complete local package resolves beneath project prefix',()=>fixture(({dir})=>assert.equal(validatePackage(dir).models.length,1)));
test('stale downloaded model definition is rejected',()=>fixture(({dir,put,model})=>{put('models/example.json',{...model,name:'stale'});assert.throws(()=>validatePackage(dir),/Stale packaged definition/);}));
test('executable and runtime lists must agree',()=>fixture(({dir,put,catalogue})=>{catalogue.models.push({id:'missing',executable:true});put('catalogue.json',catalogue);assert.throws(()=>validatePackage(dir),/Executable catalogue differs/);}));
test('duplicate model IDs are rejected',()=>fixture(({dir,put,meta})=>{meta.models.push(meta.models[0]);put('models.json',meta);assert.throws(()=>validatePackage(dir),/Duplicate runtime/);}));
test('unsafe source schemes cannot appear in release definitions',()=>fixture(({dir,put,meta,model})=>{model.sources[0].url='javascript:alert(1)';put('models.json',meta);put('models/example.json',model);assert.throws(()=>validatePackage(dir),/Unsafe source/);}));
test('missing local asset is rejected',()=>fixture(({dir,put})=>{put('index.html','<script src="./missing.js"></script>');assert.throws(()=>validatePackage(dir),/Missing linked asset/);}));
test('root-relative link breaks Pages project prefix and is rejected',()=>fixture(({dir,put})=>{put('index.html','<script src="/atlas.js"></script>');assert.throws(()=>validatePackage(dir),/escapes project prefix/);}));

test('legacy v0.1 model resolves its original schema filename',()=>fixture(({dir,put,meta,model,refreshDatabase})=>{model.schema_version='0.1';put('models.json',meta);put('models/example.json',model);put('schemas/model.schema.json','{}');refreshDatabase();assert.equal(validatePackage(dir).models.length,1);}));

test('declared public timed page and route module are required',()=>fixture(({dir,put,catalogue,refreshDatabase})=>{
 catalogue.models.push({id:'timed-example',executable:false,public_timed_laboratory:true,timed_laboratory:'timed-example.html'});put('catalogue.json',catalogue);
 assert.throws(()=>validatePackage(dir),/Missing public timed laboratory/);put('timed-example.html','');
 assert.throws(()=>validatePackage(dir),/Missing timed route module/);put('timed-route.mjs','');refreshDatabase();assert.equal(validatePackage(dir).models.length,1);
}));
test('unsafe public timed routes fail closed',()=>fixture(({dir,put,catalogue})=>{
 const entry={id:'timed-example',executable:false,public_timed_laboratory:true};catalogue.models.push(entry);
 for(const route of ['../escape.html','/escape.html','https://example.org/page.html','index.html?x=1','page.html#x','page%2ehtml','']){entry.timed_laboratory=route;put('catalogue.json',catalogue);assert.throws(()=>validatePackage(dir),/Unsafe public timed route/);}
}));

test('standard package gate requires the database artifacts before engine execution',()=>fixture(({dir,put})=>{
 put('atlas-database.json','{}');assert.throws(()=>validatePackage(dir),/Unknown database package/);
}));

// Pure source-backed sealing fixture: copy bytes only; never import engine assets.
const sourceRoot=new URL('../',import.meta.url);
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
function controlledFixture(f){
 const base=join(f.dir,'engine-controlled-time');mkdirSync(base);
 const local=n=>readFileSync(new URL(n,sourceRoot));
 const registry=JSON.parse(local('catalogue/approved-models.json'));
 const approval=registry.models.find(a=>a.model_id==='vibe-2026'&&a.status==='approved');
 const qualification=JSON.parse(local('web/engines/controlled-time/public-qualification.json'));
 const components=['controlled-time-engine.mjs','controlled-time-worker.mjs','controlled-time-laboratory.mjs'];
 const write=(name,value)=>writeFileSync(join(base,name),typeof value==='object'&&!Buffer.isBuffer(value)?JSON.stringify(value,null,2)+'\n':value);
 for(const [name,path] of Object.entries({'model.json':approval.definition.path,'review.json':approval.review.path,'qualification.json':'web/engines/controlled-time/public-qualification.json','examples.json':qualification.examples.path,'expected-results.json':qualification.public_results.path,'catalogue.json':'web/engines/controlled-time/generated/controlled_time_catalogue.json','engine.mjs':'web/engines/controlled-time/atlas_controlled_time_capability.mjs','engine.wasm':'web/engines/controlled-time/atlas_controlled_time_capability.wasm'}))write(name,local(path));
 write('approval.json',approval);for(const n of components)writeFileSync(join(f.dir,n),local('web/'+n));
 const catalogue=JSON.parse(readFileSync(join(base,'catalogue.json')));
 const reseal=()=>{
  const names=readdirSync(base).filter(n=>!['identity.json','package-manifest.json'].includes(n));
  const identity={profile:'controlled-time-ode-v1',model:'vibe-2026',model_sha256:catalogue.models[0].model_sha256,definition_file_sha256:approval.definition.sha256,catalogue_sha256:catalogue.catalogue_sha256,files:Object.fromEntries(names.map(n=>[n,digest(readFileSync(join(base,n)))])),components:Object.fromEntries(components.map(n=>[n,digest(readFileSync(join(f.dir,n)))]))};
  write('identity.json',identity);
  const files=[...components,...[...names,'identity.json'].map(n=>'engine-controlled-time/'+n)];
  write('package-manifest.json',{kind:'controlled-time-mainatlas-package-v1',files:Object.fromEntries(files.map(n=>[n,digest(readFileSync(join(f.dir,n)))]))});
 };
 reseal();f.catalogue.models.push({id:'vibe-2026',executable:true,controlled_time_laboratory:'index.html'});f.put('catalogue.json',f.catalogue);f.refreshDatabase();
 return {base,write,reseal,entry:f.catalogue.models.at(-1),components,parse:n=>JSON.parse(readFileSync(join(base,n)))};
}
test('exact separately sealed controlled-time interface joins ordinary membership',()=>fixture(f=>{controlledFixture(f);assert.equal(validatePackage(f.dir).models.length,1);}));
test('fake controlled-time flag cannot suppress ordinary exact-set gate',()=>fixture(f=>{f.catalogue.models.push({id:'fake',executable:true,controlled_time_laboratory:'index.html'});f.put('catalogue.json',f.catalogue);assert.throws(()=>validatePackage(f.dir));}));
for(const [label,mutate] of [
 ['ordinary overlap',(f,c)=>c.entry.id='example'],
 ['unknown ID',(f,c)=>c.entry.id='unknown'],
 ['missing flag',(f,c)=>delete c.entry.controlled_time_laboratory],
 ['unknown route',(f,c)=>c.entry.controlled_time_laboratory='other.html'],
 ['nonexecutable claim',(f,c)=>c.entry.executable=false],
 ['stale profile',(f,c)=>{const x=c.parse('identity.json');x.profile='path-ode-v1';c.write('identity.json',x);}],
 ['unsafe seal member',(f,c)=>{const x=c.parse('package-manifest.json');x.files['../escape']='0'.repeat(64);c.write('package-manifest.json',x);}],
 ['missing seal member',(f,c)=>{const x=c.parse('package-manifest.json');delete x.files['controlled-time-worker.mjs'];c.write('package-manifest.json',x);}],
 ['missing asset',(f,c)=>unlinkSync(join(c.base,'review.json'))],
 ['extra asset',(f,c)=>c.write('unknown.json','{}')],
 ['missing component',(f,c)=>unlinkSync(join(f.dir,c.components[0]))],
])test('controlled-time membership rejects '+label,()=>fixture(f=>{const c=controlledFixture(f);mutate(f,c);f.put('catalogue.json',f.catalogue);f.refreshDatabase();assert.throws(()=>validatePackage(f.dir));}));
for(const name of ['approval.json','review.json','model.json','qualification.json','catalogue.json','engine.mjs','engine.wasm','examples.json','expected-results.json']){
 test('controlled-time rejects tampered '+name+' even after resealing',()=>fixture(f=>{const c=controlledFixture(f);if(name.endsWith('.json')){const x=c.parse(name);if(Array.isArray(x))x.push({forged:true});else x.forged=true;c.write(name,x);}else c.write(name,'throw Error("untrusted engine must never execute");');c.reseal();assert.throws(()=>validatePackage(f.dir));}));
}
test('controlled-time components require accepted source hashes after resealing',()=>fixture(f=>{const c=controlledFixture(f);writeFileSync(join(f.dir,c.components[0]),'throw Error("never execute");');c.reseal();assert.throws(()=>validatePackage(f.dir));}));
test('controlled-time library validation performs no material imports',()=>fixture(f=>{controlledFixture(f);assert.deepEqual(validateControlledTimeMembership(f.dir,f.catalogue.models,['example']),['vibe-2026']);}));
