import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {MODEL,validateDescriptor,validateInterfaceRequest,validateInterfaceReplay} from '../../../../web/interface2016-laboratory.mjs';
const descriptor={id:MODEL,state:['sigma_normal','sigma_plane','tau_x','tau_z','e'].map((name,offset)=>({name,size:1,offset})),controls:['gamma_x','gamma_z','normal_strain'],parameters:['p_ref']};
const request={context:{coordinate:3,state:{sigma_normal:1e5,sigma_plane:8e4,tau_x:0,tau_z:0,e:.67},controls:{gamma_x:0,gamma_z:0,normal_strain:0},parameters:{p_ref:1e5}},progress:1,samples:10,controls_end:{gamma_x:.001,gamma_z:0,normal_strain:.0001},settings:[1e-8,1e-7,1e-9,.05,20,10000]};
let checks=0;assert.equal(validateDescriptor(descriptor),descriptor);checks++;assert.deepEqual(validateInterfaceRequest(request,descriptor),request);checks++;
for(const mutate of [r=>r.controls_end.slip_x=1,r=>delete r.controls_end.gamma_z,r=>r.context.state.sigma_plane=Infinity,r=>delete r.context.state.tau_z,r=>r.context.parameters.p_ref=NaN,r=>r.samples=201,r=>r.progress=-1,r=>r.progress=0,r=>r.extra=1,r=>r.context.extra=1,r=>r.settings[3]=0]){const r=structuredClone(request);mutate(r);assert.throws(()=>validateInterfaceRequest(r,descriptor));checks++;}
for(const mutate of [d=>d.state[0].size=4,d=>d.id='other',d=>d.controls[0]='slip_x',d=>d.state[1].name='sigma_normal']){const d=structuredClone(descriptor);mutate(d);assert.throws(()=>validateDescriptor(d));checks++;}
const loaded={identity:{model:MODEL,definition_sha256:'a'.repeat(64)},descriptor,request},document={kind:'atlas-interface2016-path-run-v1',model:MODEL,identity:loaded.identity,request,result:{request:structuredClone(request)}};
assert.deepEqual(validateInterfaceReplay(document,loaded),request);checks++;
for(const mutate of [d=>d.identity.definition_sha256='b'.repeat(64),d=>d.model='other',d=>d.kind='other',d=>d.result.request.progress=2,d=>d.request.settings[0]=1e-5]){const d=structuredClone(document);mutate(d);assert.throws(()=>validateInterfaceReplay(d,loaded));checks++;}
const clone=validateInterfaceRequest(request,descriptor);clone.context.state.e=123;assert.equal(request.context.state.e,.67);checks++;
const source=name=>JSON.parse(readFileSync(new URL('../implementation-v1/'+name,import.meta.url),'utf8'));
const actualDescriptor=source('generated/path_catalogue.json').models.find(d=>d.id===MODEL),example=source('example.json'),settingNames=['absolute','relative','min_step','max_step','max_depth','max_trials'];
const actualRequest={context:example.context,progress:example.advance.progress,controls_end:example.advance.controls_end,samples:40,settings:settingNames.map(n=>example.execution[n])};
assert.doesNotThrow(()=>validateInterfaceRequest(actualRequest,actualDescriptor));checks++;
const cases=source('package-cases.json');assert.equal(cases.definition_sha256,example.definition_sha256);checks++;
for(const c of cases.cases){const r=structuredClone(c.request);if(!Array.isArray(r.settings))r.settings=settingNames.map(n=>r.settings[n]);assert.doesNotThrow(()=>validateInterfaceRequest(r,actualDescriptor),c.id);assert.equal(c.expected.length,r.samples+1);assert.equal(c.expected.at(-1).observables.stress.length,6);checks++;}
console.log(JSON.stringify({passed:true,checks,compiledCalls:0,browserCalls:0,scope:'Pure fixed-local interface descriptor, complete source-angle request, strict replay identity and immutable request checks.'},null,2));
