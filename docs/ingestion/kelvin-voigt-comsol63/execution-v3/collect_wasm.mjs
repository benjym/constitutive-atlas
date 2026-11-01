// Prospective raw collector: common ABI only, no material equations.
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';import {pathToFileURL} from 'node:url';
const [modulePath,casesPath,output]=process.argv.slice(2);
const create=(await import(pathToFileURL(resolve(modulePath)))).default;
const wasm=await create();const cases=JSON.parse(readFileSync(casesPath,'utf8')).cases,rows=[];
for(const source of cases){
 const c=structuredClone(source);
 if(c.restart_from){const previous=rows.find(r=>r.id===c.restart_from);c.args[2]=JSON.parse(previous.calls[0].stdout).state.join(',');}
 const calls=[];
 for(let repeat=0;repeat<2;repeat++){
  const stdout=wasm.ccall(c.call,'string',c.types,c.args);calls.push({returncode:JSON.parse(stdout).ok?0:1,stdout,stderr:''});
 }
 const row={id:c.id,calls};
 if(c.ok&&c.kind==='direct'){
  const data=JSON.parse(calls[0].stdout);
  if(data.ok)row.observation=wasm.ccall('atlas_observe_time','string',['string','string','string','string','number'],[c.args[0],c.args[1],data.state.join(','),c.args[3],c.time]);
 }
 rows.push(row);writeFileSync(output,JSON.stringify(rows,null,2)+'\n');
}
console.log(`Saved ${rows.length*2} raw calls in one persistent Wasm module.`);
