import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {isDeepStrictEqual} from 'node:util';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
const Q=path.dirname(new URL(import.meta.url).pathname),P=path.join(Q,'../direct-interface-package-check-v1'),S='/private/tmp/atlas-md1997-current-main-integration-v1/source',D='/private/tmp/atlas-md1997-direct-app-v1/site-v3';
const hash=x=>createHash('sha256').update(x).digest('hex'),read=f=>JSON.parse(fs.readFileSync(f));let count=0;
const ck=(x,n)=>{assert.ok(x,n);count++;};
const m=read(path.join(P,'manifest.json'));ck(hash(fs.readFileSync(path.join(P,'manifest.json')))==='b72673d9f297b09d2ab4100c25f0f0323c2c0af7f4e116b63baf449b9b88207b','subject');
for(const[n,h]of Object.entries(m.files))ck(hash(fs.readFileSync(path.join(P,n)))===h,n);
for(const[n,h]of Object.entries(read(path.join(P,'source-hashes.json'))))ck(hash(fs.readFileSync(path.join(S,n)))===h,n);
const before=fs.readFileSync(path.join(P,'original-checker.mjs'),'utf8'),after=fs.readFileSync(path.join(P,'proposed-checker.mjs'),'utf8'),boundary='const {createPathEngine}=await import';
ck(before.slice(before.indexOf(boundary))===after.slice(after.indexOf(boundary)),'entire engine/numerical/reference body byteexact');
ck(fs.readFileSync(path.join(S,'tools/test_interface2016_package.mjs'),'utf8')===before,'original checker intact');
let oldBuilder=fs.readFileSync(path.join(P,'before-build_web.py'),'utf8'),newBuilder=fs.readFileSync(path.join(P,'proposed-build_web.py'),'utf8');
const oldLine="    subprocess.run(['node',str(ROOT/'tools/test_interface2016_package.mjs'),str(dest)],check=True)";
const newLines="    interface_checker = 'test_interface2016_compatible_package.mjs' if (dest/'material-point-interface2016/engine-path/source-compatibility.json').is_file() else 'test_interface2016_package.mjs'\n    subprocess.run(['node',str(ROOT/'tools'/interface_checker),str(dest)],check=True)";
ck(newBuilder.replace(newLines,oldLine)===oldBuilder,'only exact dispatch change');
const prefix=after.slice(0,after.indexOf(boundary)).replace(/^import .*;\n/gm,'').replaceAll('import.meta.url','checkerURL');
ck(!prefix.includes('await import')&&!prefix.includes('WebAssembly'),'no engine/runtime code in prefix');
let overrides=new Map(),extra=false;
const key=p=>p instanceof URL?p.pathname:path.resolve(p);
function run(){const sandbox={assert,isDeepStrictEqual,createHash,resolve:path.resolve,join:path.join,URL,checkerURL:pathToFileURL(path.join(S,'tools/test_interface2016_compatible_package.mjs')).href,process:{argv:['node','pure-prefix',D]},readFileSync(p,...a){const k=key(p);if(overrides.has(k)){const v=overrides.get(k);if(v===null)throw Error('manufactured missing evidence');return a[0]?v.toString():v;}return fs.readFileSync(p,...a);},readdirSync(p){const n=fs.readdirSync(p);return extra&&path.resolve(p)===path.join(D,'material-point-interface2016/engine-path')?[...n,'unexpected.json']:n;},lstatSync:fs.lstatSync,writeFileSync(){throw Error('No writes permitted');},console};vm.runInNewContext(prefix,sandbox,{timeout:5000});}
run();count++;
const base=path.join(D,'material-point-interface2016/engine-path');
for(const name of ['source-compatibility.json','source-compatibility-review.json'])for(const bad of [null,Buffer.from('{}')]){overrides=new Map([[path.join(base,name),bad]]);assert.throws(run);count++;}
overrides=new Map();extra=true;assert.throws(run);count++;extra=false;
for(const name of ['qualification.json','build-review.json','build-receipt.json','engine.wasm']){overrides=new Map([[path.join(base,name),Buffer.from('{}')]]);assert.throws(run);count++;}
overrides=new Map();
// Rehash the altered receipt in package metadata, so its current-source closure guard must reject.
const receipt=read(path.join(base,'build-receipt.json'));receipt.source_closure={};const rb=Buffer.from(JSON.stringify(receipt));
const identity=read(path.join(base,'identity.json'));identity.files['build-receipt.json']=hash(rb);const ib=Buffer.from(JSON.stringify(identity));
const manifest=read(path.join(base,'package-manifest.json'));manifest.files['material-point-interface2016/engine-path/build-receipt.json']=hash(rb);manifest.files['material-point-interface2016/engine-path/identity.json']=hash(ib);
overrides=new Map([[path.join(base,'build-receipt.json'),rb],[path.join(base,'identity.json'),ib],[path.join(base,'package-manifest.json'),Buffer.from(JSON.stringify(manifest))]]);assert.throws(run);count++;
console.log(JSON.stringify({passed:true,checks:count,purePrefixPositive:1,refusals:10,unchangedRuntimeBody:true,enginesOrWasmOrModelsExecuted:0},null,2));
