import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const [study,build,out]=process.argv.slice(2);
const create=(await import(pathToFileURL(build+'/atlas-barodesy-preview.js'))).default;
const m=await create({wasmBinary:fs.readFileSync(build+'/atlas-barodesy-preview.wasm')});
const requests=JSON.parse(fs.readFileSync(study+'/requests.json'));
const rows=[];const save=()=>fs.writeFileSync(out+'/journal.json',JSON.stringify(rows,null,2)+'\n');
rows.push({id:'describe',raw:m.ccall('atlas_describe','string',[],[])});save();
for(const r of requests){
 const row={id:r.id,request:r};rows.push(row);save();
 if(r.mode==='run')row.raw=m.ccall('atlas_run','string',['string','string','string','number','number','number','number'],[r.model,r.parameters,r.initial,r.protocol,r.target,r.steps,r.cycles]);
 else row.raw=m.ccall('atlas_integrate','string',['string','string','string','string'],[r.model,r.parameters,r.initial,r.strain]);
 save();
}
