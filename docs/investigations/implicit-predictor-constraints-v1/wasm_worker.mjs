// Persistent common-engine worker; only coordinator executes this after build handoff.
import {createInterface} from 'node:readline';
import {pathToFileURL} from 'node:url';
const factory=(await import(pathToFileURL(process.argv[2]))).default;
const engine=await factory({print:x=>process.stderr.write(String(x)+'\n'),printErr:x=>process.stderr.write(String(x)+'\n')});
for await(const line of createInterface({input:process.stdin,crlfDelay:Infinity})){
 try{const c=JSON.parse(line),csv=x=>x.join(',');const raw=engine.ccall('atlas_integrate_with_settings','string',['string','string','string','string','string'],[c.model,csv(c.parameters),csv(c.initial),csv(c.strain),csv(c.integration_settings)]);process.stdout.write(JSON.stringify({raw})+'\n');}
 catch(error){process.stdout.write(JSON.stringify({error:String(error)})+'\n');}
}
