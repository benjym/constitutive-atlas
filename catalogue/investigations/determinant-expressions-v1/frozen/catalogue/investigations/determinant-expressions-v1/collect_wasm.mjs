import{readFileSync,writeFileSync,existsSync}from'node:fs';
import{pathToFileURL}from'node:url';
import assert from'node:assert/strict';
const[loader,input,output]=process.argv.slice(2);assert.ok(loader&&input&&output&&!existsSync(output));
const journal=[];const save=()=>writeFileSync(output,JSON.stringify(journal)+'\n');save();
const factory=(await import(pathToFileURL(loader))).default;const module=await factory({wasmBinary:readFileSync(loader.replace(/\.mjs$/,'.wasm'))});
for(const line of readFileSync(input,'utf8').trimEnd().split('\n')){
 const row={input:line};try{row.raw=module.ccall('determinant_context','string',['string'],[line]);}catch(error){row.exception=String(error);journal.push(row);save();throw error;}journal.push(row);save();
}
