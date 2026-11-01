import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const read=p=>readFileSync(new URL(p,import.meta.url),'utf8'),proposed=read('./app-proposed.js'),clause=read('./catalogue-clause.txt').trimEnd(),needle='}else if(entry.implicit_path_laboratory&&timedView?.supports(entry.id)){',original=proposed.replace(clause,needle),modelId='kelvin-voigt-comsol63-deviatoric-zero-spin-ode';
function run(source,id=modelId,supports=true){
 const nodes=new Map(),fallback=[];class Node{constructor(tag,text){this.tag=tag;this.textContent=text||'';this.children=[];this.open=false;}append(...children){this.children.push(...children);}replaceChildren(){this.children=[];}showModal(){this.open=true;}}
 const $=id=>{if(!nodes.has(id))nodes.set(id,new Node());return nodes.get(id);};
 const context=vm.createContext({$,document:{createTextNode:t=>new Node('text',t)},element:(tag,text)=>new Node(tag,text),timedView:{supports:key=>supports&&key===modelId},j2View:null,timedLaboratoryRoute:()=>null,refreshCatalogueStatus:()=>{},recordedDescription:x=>x,formulationSection:(_d,spec)=>{fallback.push(spec);return new Node('p','No browser definition is packaged for this candidate.');},evidenceSection:()=>new Node(),applicabilitySection:()=>new Node(),evidenceIndex:null,evidenceState:null,applicabilityMatrix:null,applicabilityState:null,catalogueModelHash:id=>'#catalogue?model='+id});
 const start=source.indexOf('function showCatalogueModel('),end=source.indexOf('\nfunction download(',start);assert(start>=0&&end>start);vm.runInContext(source.slice(start,end),context);context.showCatalogueModel({id,name:'fixture model',family:'fixture',timed_laboratory:'index.html'},undefined);
 const walk=node=>[node,...node.children.flatMap(walk)];return {all:walk($('catalogue-detail-body')),nodes,fallback};
}
test('original missing definition is reproduced and proposed supported Kelvin details replace it with source-bound contract',()=>{
 const before=run(original);assert.equal(before.fallback.length,1);assert(before.all.some(n=>n.textContent.includes('No browser definition')));
 const after=run(proposed);assert.equal(after.fallback.length,0);const text=after.all.map(n=>n.textContent).join(' ');for(const phrase of ['Eq. 3-36','six persistent total infinitesimal strain','zero spin','Mandel','dry total Cauchy','immediately sheds viscous stress','No experimental validation'])assert(text.includes(phrase),phrase);
 const links=after.all.filter(n=>n.tag==='a');assert.equal(links.length,5);assert(links.some(n=>n.href==='./engine-kelvin-voigt/'+modelId+'.json'));for(const path of ['review.html','review.json','approval.json'])assert(links.some(n=>n.href==='./engine-kelvin-voigt/'+path));assert(links.some(n=>n.href.includes('#3441080')));assert.equal(after.nodes.get('catalogue-explore').hidden,false);assert.equal(after.nodes.get('catalogue-dialog').open,true);
});
test('guarded clause preserves unrelated and unsupported fallback behavior',()=>{
 for(const [id,supports]of [['unrelated-model',true],[modelId,false]]){const out=run(proposed,id,supports);assert.equal(out.fallback.length,1);assert(out.all.some(n=>n.textContent.includes('No browser definition')));assert(!out.all.some(n=>n.href?.includes('engine-kelvin-voigt')));}
 assert.equal(proposed.split(clause).length,2);assert.equal(original.replace(needle,clause),proposed,'Proposal consists solely of the guarded branch insertion');
});
