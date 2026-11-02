/** Source-only candidate injection; no installation, build, engine or browser call. */
import assert from 'node:assert/strict';
import {readFileSync,readdirSync,statSync} from 'node:fs';
import {resolve,dirname,join} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const own=dirname(fileURLToPath(import.meta.url)),root=resolve(own,'../../../..'),id='bingham-comsol63-mises-perfect-zero-spin-ode';
const text=p=>readFileSync(p,'utf8'),json=p=>JSON.parse(text(p)),hash=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const before=await import(pathToFileURL(join(own,'model-profile-data.before.mjs'))),after=await import(pathToFileURL(join(own,'model-profile-data.candidate.mjs')));
assert.equal(hash(join(root,'web/model-profile-data.mjs')),hash(join(own,'model-profile-data.before.mjs')),'Current module drifted');
assert.equal(Object.keys(after.modelProfiles).length,Object.keys(before.modelProfiles).length+1);
for(const [key,value] of Object.entries(before.modelProfiles))assert.deepEqual(after.modelProfiles[key],value,key+' changed');
const a=text(join(own,'model-profile-data.before.mjs')),b=text(join(own,'model-profile-data.candidate.mjs'));assert.ok(b.startsWith(a.slice(0,-4)+',\n'),'Original object bytes changed');
const original=json(join(own,'original-profile-v1/profile.json')),draft=json(join(own,'profile.json'));
assert.equal(hash(join(own,'original-profile-v1/profile.json')),'dd90addf54320c13d677d61664866464a639afb7dac987cb6d36db152c5fbf41');
for(const key of Object.keys(original))if(key!=='parameterNote')assert.deepEqual(draft[key],original[key],key+' changed from source draft');
assert.ok(draft.parameterNote.startsWith(original.parameterNote));assert.match(draft.parameterNote,/starting state.*elapsed time.*accuracy checks/);
const renderer=text(join(root,'web/model-profiles.mjs')).replace("'./model-profile-data.mjs'",JSON.stringify(pathToFileURL(join(own,'model-profile-data.candidate.mjs')).href));
const api=await import('data:text/javascript;base64,'+Buffer.from(renderer).toString('base64'));
const entries=json(join(root,'catalogue/manifest.json')).models;
function defs(p){return readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?defs(join(p,e.name)):e.name.endsWith('.json')?[json(join(p,e.name))]:[]).filter(x=>typeof x.id==='string'&&x.parameters&&Array.isArray(x.state));}
const definitions=defs(join(root,'models')),definition=json(join(root,'docs/ingestion/bingham-comsol63/source-v1/candidate.json'));
const all=[...entries.filter(e=>e.id!==id),{id}];api.validateModelProfiles(all,[...definitions.filter(x=>x.id!==id),definition]);
assert.deepEqual(draft.parameters.map(p=>p.name),Object.keys(definition.parameters));assert.deepEqual(Object.keys(draft.stateLabels),definition.state.map(s=>s.name));
assert.deepEqual(draft.parameters.map(p=>p.unit),['Pa','Pa','Pa','Pa·s']);assert.doesNotMatch(JSON.stringify(draft),/Wasm|E5|7771|136 cases|SHA-256|agent checklist/i);
class Element{constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.textContent='';this.open=false;}append(...nodes){this.children.push(...nodes);}}
const document={createElement:t=>new Element(t)},section=api.modelProfileSection(document,definition,{catalogue:all});
const flatten=n=>[n,...n.children.flatMap(flatten)],nodes=flatten(section),rendered=nodes.map(n=>n.textContent).join(' ');
for(const expected of ['Pa·s','Starting state','√2xy','13 state','numerical accuracy checks'])assert.ok(rendered.includes(expected),expected);
assert.ok(nodes.filter(n=>n.tagName==='DETAILS').every(n=>!n.open));assert.ok(!nodes.some(n=>n.tagName==='SCRIPT'));
const v2='/private/tmp/atlas-bingham-release-v2';
const pending=[];for(const source of draft.contentSources){const p=join(root,source);try{assert.ok(statSync(p).isFile());}catch(e){assert.ok(statSync(join(v2,source)).isFile());pending.push(source);}}
const ui=text(join(v2,'web/bingham-laboratory.mjs'));
for(const label of ['Reset Bingham preset','Physical-time experiment','Relaxation · hold all strains','Creep · hold all stresses','Loading · constant strain rate','Run physical-time history','Plot component · Mandel','Selected total stress against physical time'])assert.ok(ui.includes(label),label);
assert.throws(()=>api.validateModelProfiles([{id}], [{...definition,parameters:{}}]),/unknown parameter/);
assert.throws(()=>api.validateModelProfiles([{id}], [{...definition,state:[]}]),/unknown initial-state/);
console.log(JSON.stringify({source_only:true,existing_profiles_preserved:Object.keys(before.modelProfiles).length,catalogue_profiles_checked:all.length,parameter_and_state_names:true,units:true,closed_equation_disclosure:true,negative_checks:2,ui_labels_match:true,pending_integration_content_sources:pending,candidate_sha256:hash(join(own,'model-profile-data.candidate.mjs')),browser_or_material_execution:false},null,2));
