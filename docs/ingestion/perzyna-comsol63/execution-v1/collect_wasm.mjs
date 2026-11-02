// Raw collector only: invokes the existing generic schedule ABI; no constitutive oracle.
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {pathToFileURL} from 'node:url';
const [modulePath,casesPath,output]=process.argv.slice(2),moduleFile=resolve(modulePath);
const create=(await import(pathToFileURL(moduleFile))).default;
const wasmBinary=readFileSync(join(dirname(moduleFile),'perzyna.wasm'));
const engine=await create({instantiateWasm(imports,receive){WebAssembly.instantiate(wasmBinary,imports).then(({instance})=>receive(instance));return {};}});
const cases=JSON.parse(readFileSync(casesPath,'utf8')).cases,rows=[];
for(const source of cases){
 const c=structuredClone(source);
 if(c.restart_from){
  const parent=JSON.parse(rows.find(r=>r.id===c.restart_from).calls[0].stdout).points.at(-1);
  if(parent.time!==c.args[7])throw Error('Restart clock does not match planned context');
  c.args[2]=parent.state.join(',');c.args[3]=parent.strain.join(',');c.args[4]=parent.strain_rate.join(',');c.args[7]=parent.time;
  for(const [flag,value]of [['--initial',c.args[2]],['--initial-strain',c.args[3]],['--initial-strain-rate',c.args[4]],['--start-time',String(parent.time)]])c.argv[c.argv.indexOf(flag)+1]=value;
 }
 const row={id:c.id,request:Object.fromEntries(['call','types','args','argv'].map(k=>[k,c[k]])),calls:[]};
 for(let repeat=0;repeat<2;repeat++){const stdout=engine.ccall(c.call,'string',c.types,c.args);row.calls.push({returncode:JSON.parse(stdout).ok?0:1,stdout,stderr:''});}
 rows.push(row);writeFileSync(output,JSON.stringify(rows,null,2)+'\n');
}
console.log(`Retained ${rows.length*2} BE-schedule calls in one persistent common-engine Wasm instance.`);
