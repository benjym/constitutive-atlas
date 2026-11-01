import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {validatePackage} from '../tools/test_web_package.mjs';

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
