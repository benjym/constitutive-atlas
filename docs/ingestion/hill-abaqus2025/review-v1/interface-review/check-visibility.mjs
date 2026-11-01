// Pure mocked-DOM selection test; no browser/Wasm/compiled calls or network.
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
class Element{
 constructor(tag='div'){this.tag=tag;this.hidden=false;this.value='';this.textContent='';this.children=[];this.disabled=false;}
 setAttribute(){} addEventListener(){} after(){} replaceChildren(...children){this.children=children;}append(...children){this.children.push(...children);}attachShadow(){return shadow;}
}
const ids=new Map(),node=id=>{if(!ids.has(id))ids.set(id,new Element());return ids.get(id);};
const ordinary=new Element(),links=new Element(),shadow={getElementById:node,set innerHTML(value){this.html=value;}};
globalThis.document={querySelector:selector=>selector==='#laboratory > .lab-layout'?ordinary:links,getElementById:id=>id==='hill-material-laboratory'?null:node(id),createElement:tag=>new Element(tag),createTextNode:text=>({textContent:text})};
globalThis.Option=class extends Element{constructor(text,value){super('option');this.textContent=text;this.value=value;}};
// A pending promise prevents initialization from creating any runtime or accessing a network.
globalThis.fetch=()=>new Promise(()=>{});
const {setupHillLaboratory}=await import(pathToFileURL(resolve('web/hill-laboratory.mjs')));
let cancelled=0;const view=setupHillLaboratory({cancelOrdinary:()=>cancelled++});
assert.equal(view.select(view.modelId),true);assert.equal(view.active,true);assert.equal(ordinary.hidden,true);assert.equal(links.hidden,true);assert.equal(node('import-run').hidden,true);
assert.match(node('model-description').textContent,/Hill anisotropic/);assert.equal(node('model-family').textContent,'Anisotropic plasticity');assert.equal(node('model-status').textContent,'Approved bounded scope');assert.equal(node('model-sources').children.filter(c=>c.tag==='a').length,3);assert.equal(typeof view.run,'function');assert.equal(cancelled,1);
assert.equal(view.select(null),false);assert.equal(view.active,false);assert.equal(ordinary.hidden,false);assert.equal(links.hidden,false);assert.equal(node('import-run').hidden,false);
// Router clears all interfaces first; an already inactive Hill must not reveal a newly selected peer.
ordinary.hidden=true;links.hidden=true;node('import-run').hidden=true;view.select(null);assert.equal(ordinary.hidden,true);assert.equal(links.hidden,true);assert.equal(node('import-run').hidden,true);
view.select(view.modelId);assert.equal(ordinary.hidden,true);assert.equal(links.hidden,true);assert.equal(node('import-run').hidden,true);
console.log(JSON.stringify({passed:true,assertions:22,compiledCalls:0,networkCalls:0,scope:'Mocked DOM selection/deactivation/header/source contract only; actual browser remains separate.'},null,2));
