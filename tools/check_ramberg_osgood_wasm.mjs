import assert from 'node:assert/strict';
import{readFileSync,writeFileSync}from'node:fs';
import{resolve}from'node:path';
import{pathToFileURL}from'node:url';
import{createHash}from'node:crypto';
const [directory,output,nativeFile]=process.argv.slice(2),root=resolve(import.meta.dirname,'..'),id='ramberg-osgood-ansys242',base=root+'/docs/ingestion/'+id+'/execution-v1/';
assert.ok(directory&&output&&nativeFile);
const read=p=>JSON.parse(readFileSync(p,'utf8')),sha=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const requests=read(base+'requests.json');assert.equal(sha(root+'/models/'+id+'.json'),requests.model_sha256);
const create=(await import(pathToFileURL(resolve(directory,'atlas.js')))).default,engine=await create();
const metadata=JSON.parse(engine.ccall('atlas_describe','string',[],[]));assert.deepEqual(metadata,read(resolve(directory,'generated/models.json')));assert.deepEqual(metadata.models.find(m=>m.id===id),read(root+'/models/'+id+'.json'));
const cases=[];
for(const c of requests.cases){let state=c.initial;const responses=[];
 for(const d of c.increments){const args=[id,requests.parameter_order.map(k=>c.parameters[k]).join(','),state.join(','),c.strain_csv_override??d.join(','),c.settings.join(',')];
  const r=JSON.parse(engine.ccall(c.mode==='linearize'?'atlas_linearize_with_settings':'atlas_integrate_with_settings','string',Array(5).fill('string'),args));responses.push(r);if(r.ok)state=r.state;
 }cases.push({id:c.id,responses});
}
const result={identity:'ramberg-osgood-responses-v1',model_sha256:requests.model_sha256,cases};writeFileSync(output,JSON.stringify(result,null,2)+'\n');
const native=read(nativeFile);assert.equal(native.model_sha256,result.model_sha256);assert.equal(native.cases.length,cases.length);let compared=0,maxRelative=0;
for(let i=0;i<cases.length;i++){assert.equal(native.cases[i].id,cases[i].id);const a=native.cases[i].responses,b=cases[i].responses;assert.equal(a.length,b.length);
 for(let j=0;j<a.length;j++){assert.equal(a[j].ok,b[j].ok);assert.equal(a[j].message,b[j].message);for(const key of ['state','state_tangent']){
 const x=a[j][key],y=b[j][key];if(x===undefined){assert.equal(y,undefined);continue;}assert.equal(x.length,y.length);
 const xf=x.flat(),yf=y.flat();assert.equal(xf.length,yf.length);for(let k=0;k<xf.length;k++){const e=Math.abs(xf[k]-yf[k])/Math.max(1,Math.abs(xf[k]));assert.ok(e<=1e-10,`${cases[i].id}/${j}/${key}/${k}: ${e}`);maxRelative=Math.max(maxRelative,e);compared++;}
 }}
}
writeFileSync(output+'.parity.json',JSON.stringify({status:'passed',model_sha256:requests.model_sha256,catalogue_sha256:metadata.sha256,cases:cases.length,compared,maxRelative,tolerance:1e-10,engine:{module_sha256:sha(resolve(directory,'atlas.js')),wasm_sha256:sha(resolve(directory,'atlas.wasm'))}},null,2)+'\n');
console.log(JSON.stringify({status:'passed',cases:cases.length,compared,maxRelative}));
