// DOM stub exercises the actual inline UI lifecycle, with no Wasm/runtime calls.
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import * as contract from '../../../../../web/power-creep-contract.mjs';
const html=readFileSync(new URL('../../../../../web/power-creep.html',import.meta.url),'utf8');
let script=html.match(/<script type="module">([\s\S]*)<\/script>/)[1];
script=script.replace(/  import .*?;\n/,'');
// Exclude only engine startup; the tested event handlers are unchanged.
script=script.slice(0,script.lastIndexOf('  try{'));
const elements=new Map();
const element=id=>{if(!elements.has(id))elements.set(id,{id,value:contract.defaults[id]??'',disabled:false,textContent:'',listeners:{},addEventListener(name,fn){this.listeners[name]=fn;},replaceChildren(){},click(){}});return elements.get(id);};
const context=vm.createContext({...contract,document:{getElementById:element},setTimeout(){throw Error('Unexpected solver scheduling');},console});
vm.runInContext(script,context);
let rejectRead;
element('run-file').files=[{size:100,text:()=>new Promise((_,reject)=>rejectRead=reject)}];
const pending=element('run-file').listeners.change();
element('controls').listeners.input({target:element('duration')});
const latest=element('status').textContent;
rejectRead(Error('simulated delayed file I/O failure'));
await pending;
const observed=element('status').textContent;
assert.match(observed,/Import rejected: simulated delayed/);
assert.notEqual(observed,latest);
console.log(JSON.stringify({reproduced:true,compiled_calls:0,newer_status:latest,overwritten_status:observed,severity:'low: stale status only; current response/export remains invalidated'},null,2));
