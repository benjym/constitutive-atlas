// Generic ABI collector only. No constitutive equations or expected outputs.
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {pathToFileURL} from 'node:url';
const [modulePath,casesPath,output]=process.argv.slice(2),moduleFile=resolve(modulePath);
const create=(await import(pathToFileURL(moduleFile))).default;
const wasmBinary=readFileSync(join(dirname(moduleFile),'bingham.wasm'));
const engine=await create({instantiateWasm(imports,receive){WebAssembly.instantiate(wasmBinary,imports).then(({instance})=>receive(instance));return {};}});
const cases=JSON.parse(readFileSync(casesPath,'utf8')).cases,rows=[];
for(const source of cases){
 const c=structuredClone(source);
 if(c.restart_from){const prior=JSON.parse(rows.find(r=>r.id===c.restart_from).calls[0].stdout);c.args[2]=prior.points.at(-1).state.join(',');}
 const row={id:c.id,calls:[]};
 for(let repeat=0;repeat<2;repeat++){const stdout=engine.ccall(c.call,'string',c.types,c.args);row.calls.push({returncode:JSON.parse(stdout).ok?0:1,stdout,stderr:''});}
 const data=JSON.parse(row.calls[0].stdout);
 if(c.ok&&c.kind==='direct'&&data.ok)row.observation=engine.ccall('atlas_observe_time','string',['string','string','string','string','number'],[c.args[0],c.args[1],data.state.join(','),c.args[3],c.time]);
 rows.push(row);writeFileSync(output,JSON.stringify(rows,null,2)+'\n');
}
console.log(`Retained ${rows.length*2} calls in one persistent common-engine Wasm instance.`);
