import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {validatePackage} from '../tools/test_web_package.mjs';

function fixture(fn){
 const dir=mkdtempSync(join(tmpdir(),'atlas-package-test-'));
 const put=(file,value)=>writeFileSync(join(dir,file),typeof value==='string'?value:JSON.stringify(value));
 mkdirSync(join(dir,'models'));mkdirSync(join(dir,'schemas'));
 const model={id:'example',schema_version:'0.3',sources:[{url:'https://doi.org/10.1002/nag.416'}]};
 const meta={sha256:'test',models:[model]},catalogue={models:[{id:'example',executable:true}]};
 put('models.json',meta);put('catalogue.json',catalogue);put('models/example.json',model);put('schemas/model-v0.3.schema.json','{}');
 for(const name of ['atlas.js','atlas.wasm','worker.js','numerics.mjs','loading.mjs','recorded.mjs','state-contract.mjs','.nojekyll'])put(name,'');
 put('index.html','<script src="./atlas.js"></script><a href="./models/example.json">JSON</a><a href="https://doi.org/10.1002/nag.416">Source</a>');
 put('publications.html','<a href="./index.html#catalogue/example">Model</a>');
 try{fn({dir,put,model,meta,catalogue});}finally{rmSync(dir,{recursive:true,force:true});}
}
test('complete local package resolves beneath project prefix',()=>fixture(({dir})=>assert.equal(validatePackage(dir).models.length,1)));
test('stale downloaded model definition is rejected',()=>fixture(({dir,put,model})=>{put('models/example.json',{...model,name:'stale'});assert.throws(()=>validatePackage(dir),/Stale packaged definition/);}));
test('executable and runtime lists must agree',()=>fixture(({dir,put,catalogue})=>{catalogue.models.push({id:'missing',executable:true});put('catalogue.json',catalogue);assert.throws(()=>validatePackage(dir),/Executable catalogue differs/);}));
test('duplicate model IDs are rejected',()=>fixture(({dir,put,meta})=>{meta.models.push(meta.models[0]);put('models.json',meta);assert.throws(()=>validatePackage(dir),/Duplicate runtime/);}));
test('unsafe source schemes cannot appear in release definitions',()=>fixture(({dir,put,meta,model})=>{model.sources[0].url='javascript:alert(1)';put('models.json',meta);put('models/example.json',model);assert.throws(()=>validatePackage(dir),/Unsafe source/);}));
test('missing local asset is rejected',()=>fixture(({dir,put})=>{put('index.html','<script src="./missing.js"></script>');assert.throws(()=>validatePackage(dir),/Missing linked asset/);}));
test('root-relative link breaks Pages project prefix and is rejected',()=>fixture(({dir,put})=>{put('index.html','<script src="/atlas.js"></script>');assert.throws(()=>validatePackage(dir),/escapes project prefix/);}));

test('legacy v0.1 model resolves its original schema filename',()=>fixture(({dir,put,meta,model})=>{model.schema_version='0.1';put('models.json',meta);put('models/example.json',model);put('schemas/model.schema.json','{}');assert.equal(validatePackage(dir).models.length,1);}));
