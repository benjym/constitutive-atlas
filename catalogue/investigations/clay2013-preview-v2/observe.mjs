import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
const [study,build,out]=process.argv.slice(2);
const create=(await import(pathToFileURL(build+'/atlas-preview.js'))).default;
const m=await create({wasmBinary:fs.readFileSync(build+'/atlas-preview.wasm')});
const requests=JSON.parse(fs.readFileSync(study+'/requests.json'));
const rows=[];const save=()=>fs.writeFileSync(out+'/journal.json',JSON.stringify(rows,null,2)+'\n');
const call=(id,request,name,types,args)=>{
 const row={id,...(request?{request}:{})};rows.push(row);save();
 try{row.raw=m.ccall(name,'string',types,args);}
 catch(error){row.raw=null;row.exception=String(error);save();throw error;}
 save();if(typeof row.raw!=='string')throw new Error('non-string response retained');
};
call('describe',null,'atlas_describe',[],[]);
for(const r of requests){
 if(r.mode==='run')call(r.id,r,'atlas_run_with_settings',['string','string','string','number','number','number','number','string'],[r.model,r.parameters,r.initial,r.protocol,r.target,r.steps,r.cycles,r.integration_settings]);
 else call(r.id,r,'atlas_integrate_with_settings',['string','string','string','string','string'],[r.model,r.parameters,r.initial,r.strain,r.integration_settings]);
}
