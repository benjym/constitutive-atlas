import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,lstatSync,realpathSync,mkdirSync,mkdtempSync,rmSync,renameSync,symlinkSync,unlinkSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {strictJSON} from '/private/tmp/atlas-baseline-delivery-20261105/source/web/controlled-time-engine.mjs';
const O=dirname(fileURLToPath(import.meta.url)),N=resolve(O,'../..'),A=join(N,'supported-package-source-binding-v1'),W='/private/tmp/atlas-baseline-delivery-20261105/source';
const hash=b=>createHash('sha256').update(b).digest('hex'),checks=[];const ok=(v,n)=>{assert.ok(v,n);checks.push(n);};
ok(hash(readFileSync(join(A,'manifest.json')))==='af2f176b9e943be9a0840e91cc5f28de51d9a1a62fceb665af112ce4be87a04f','exact author manifest');
for(const r of JSON.parse(readFileSync(join(A,'manifest.json'))).files)ok(hash(readFileSync(join(A,r.path)))===r.sha256&&lstatSync(join(A,r.path)).size===r.bytes,'frozen '+r.path);
const source=readFileSync(join(A,'proposed/tools/test_web_package.mjs'),'utf8'),helper=readFileSync(join(A,'helper-source.txt'),'utf8');ok(source.includes(helper),'actual complete helper source exact');
const extracted=join(O,'extracted-helper.mjs');writeFileSync(extracted,"import assert from 'node:assert/strict';import{readFileSync,lstatSync,realpathSync}from'node:fs';import{join,resolve}from'node:path';import{createHash}from'node:crypto';import{strictJSON}from'/private/tmp/atlas-baseline-delivery-20261105/source/web/controlled-time-engine.mjs';const hash=b=>createHash('sha256').update(b).digest('hex');\n"+helper);
const {controlledTimePackagerSources:f}=await import(extracted);
const packet='docs/delivery/unheld-finalisation-20261105-v1/',proofPath=packet+'interface-receipt-source-closure-v1/proof.json',reviewPath=packet+'shared-current17-review-v1/interface-receipt-source-closure-v1/source-view-decision.json';const proof=JSON.parse(readFileSync(join(W,proofPath))),expected='02b1dd6e36c2c23ca91a78d321c4af5060dd7b68dbf8385e142061f4149a4758';
const data={};for(const name of [proofPath,reviewPath,...Object.keys(proof.implementation),...Object.keys(proof.ancestors),...Object.keys(proof.aliases),...Object.values(proof.aliases).map(r=>r.archive)])data[name]=readFileSync(join(W,name));
const root=mkdtempSync(join(O,'fixture-'));
try{
 for(const [name,body]of Object.entries(data)){mkdirSync(dirname(join(root,name)),{recursive:true});writeFileSync(join(root,name),body);}
 const tools=join(root,'tools'),moved=join(root,'tools-real');renameSync(tools,moved);symlinkSync(moved,tools);assert.throws(()=>f(root,expected));checks.push('parent symlink source ancestry rejects');unlinkSync(tools);renameSync(moved,tools);
 const first=f(root,expected);ok(Object.keys(first).length===Object.keys(data).length,'all current source/authority members bound');ok(first['tools/build_controlled_time_web.py']===proof.implementation['tools/build_controlled_time_web.py'],'current packager remains current SHA');
 for(const name of Object.keys(data)){
  writeFileSync(join(root,name),Buffer.concat([data[name],Buffer.from('corrupt')]));assert.throws(()=>f(root,expected));checks.push('reject member corruption '+name);writeFileSync(join(root,name),data[name]);
 }
 assert.throws(()=>f(root,'0'.repeat(64)));checks.push('unknown historical expected rejects');
 const current=join(root,'tools/build_controlled_time_web.py'),old=data[proof.aliases['tools/build_controlled_time_web.py'].archive];writeFileSync(current,old);const direct=f(root,expected);ok(Object.keys(direct).length===1&&direct['tools/build_controlled_time_web.py']===expected,'original historical raw-source route preserved');writeFileSync(current,data['tools/build_controlled_time_web.py']);
 const before=f(root,expected);writeFileSync(current,Buffer.concat([data['tools/build_controlled_time_web.py'],Buffer.from('drift')]));assert.throws(()=>f(root,expected));checks.push('post-observation current drift rejects');writeFileSync(current,data['tools/build_controlled_time_web.py']);ok(JSON.stringify(f(root,expected))===JSON.stringify(before),'restored fixture exact stable snapshot');
}finally{rmSync(root,{recursive:true,force:true});}
const original=readFileSync(join(A,'original.mjs'),'utf8');let inverse=source.replace('readdirSync,lstatSync,realpathSync','readdirSync').replace(helper,'').replace(' let packagerSnapshot=null,packagerExpected=null;\n','').replace('  packagerExpected=decision.source_sha256;packagerSnapshot=controlledTimePackagerSources(repository,packagerExpected);',"  assert.equal(hash(readFileSync(join(repository,'tools/build_controlled_time_web.py'))),decision.source_sha256,'Changed accepted controlled-time packager');").replace(" if(packagerSnapshot!==null)assert.deepEqual(controlledTimePackagerSources(repository,packagerExpected),packagerSnapshot,'Packager source view changed during membership validation');\n",'');ok(inverse===original,'entire original test restored by exact intended inverse');
for(const p of ['tools/test_supported_package.mjs','tools/test_scoped_parity.mjs']){const row=JSON.parse(readFileSync(join(O,'preliminary-audit.json'))).sources.find(r=>r.path===p);ok(hash(readFileSync(join(W,p)))===row.sha256,'original consumer unchanged '+p);}
writeFileSync(join(O,'checks.json'),JSON.stringify({passed:true,count:checks.length,checks,actual_artifact_compiler_material_browser_network:false,fixtures_removed:true},null,2)+'\n');console.log(JSON.stringify({passed:true,count:checks.length}));
