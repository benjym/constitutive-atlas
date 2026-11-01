import {pathToFileURL} from 'node:url';
import readline from 'node:readline';
const engine=await (await import(pathToFileURL(process.argv[2]))).default();
for await(const line of readline.createInterface({input:process.stdin,crlfDelay:Infinity})) {
 try {const r=JSON.parse(line);const before=JSON.stringify(r.args);const response=JSON.parse(engine.ccall(r.function,'string',r.types,r.args));console.log(JSON.stringify({response,inputs_unchanged:before===JSON.stringify(r.args)}));}
 catch(e){console.log(JSON.stringify({transport_error:String(e)}));}
}
