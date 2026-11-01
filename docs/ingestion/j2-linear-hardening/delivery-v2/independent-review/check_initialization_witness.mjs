// Pure lifecycle witness: extracted frozen descriptor/ensureEngine logic, inert candidate only.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const source=readFileSync(new URL('./source-v1/web/j2-laboratory.mjs',import.meta.url),'utf8');
const descriptor=source.slice(source.indexOf(' const descriptor=JSON.parse(engine.ccall'),source.indexOf('\nfunction ensureEngine()'));
const ensure=source.slice(source.indexOf('function ensureEngine()'),source.indexOf('\n\n function select(id)'));
assert.ok(source.includes('engine=await create('));
const run=Function(`return (async()=>{let engine,initialization,active=false,calls=0;const identity={catalogue_hash:'expected'},MODEL='j2';async function loadEngine(){engine={ccall(){calls++;return JSON.stringify({sha256:'wrong',models:[{id:'j2'}]});}};${descriptor}${ensure};let rejected=false;try{await ensureEngine();}catch(e){rejected=true;}await ensureEngine();return {rejected,secondAttemptResolved:!!engine,descriptorCalls:calls};})();`);
const result=await run();assert.deepEqual(result,{rejected:true,secondAttemptResolved:true,descriptorCalls:1});
console.log(JSON.stringify({witnessReproduced:true,...result,engineCalls:0,compiledCalls:0,scope:'Inert candidate replaces module creation; exact frozen descriptor and ensureEngine continuations execute.'},null,2));
