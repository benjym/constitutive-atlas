// Actual packaged engine qualification; coordinator serial execution handoff required.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(process.argv[2]??''),base=resolve(root,'engine-controlled-time'),read=name=>readFileSync(resolve(base,name)),hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const identity=JSON.parse(read('identity.json')),manifest=JSON.parse(read('package-manifest.json'));
assert.equal(manifest.kind,'controlled-time-mainatlas-package-v1');
for(const [name,expected] of Object.entries(manifest.files)){assert.ok(!name.startsWith('/')&&!name.split('/').includes('..'));assert.equal(hash(readFileSync(resolve(root,name))),expected,name);}
for(const [name,expected]of Object.entries(identity.files))assert.equal(hash(read(name)),expected,name);
for(const [name,expected]of Object.entries(identity.components))assert.equal(hash(readFileSync(resolve(root,name))),expected,name);
const {ControlledTimeEngine,canonical,strictJSON,validateRequest}=await import(pathToFileURL(resolve(root,'controlled-time-engine.mjs')));
const definition=strictJSON(read('model.json').toString()),catalogue=strictJSON(read('catalogue.json').toString()),examples=strictJSON(read('examples.json').toString()),expected=strictJSON(read('expected-results.json').toString());
const {default:create}=await import(pathToFileURL(resolve(base,'engine.mjs'))),module=await create({wasmBinary:read('engine.wasm'),print:()=>{},printErr:()=>{}}),engine=new ControlledTimeEngine(module,catalogue,definition);
assert.equal(identity.model,definition.id);assert.equal(identity.model_sha256,engine.descriptor.model_sha256);assert.equal(identity.catalogue_sha256,catalogue.catalogue_sha256);
let successes=0,failures=0;
for(const example of examples){const r=expected.cases.find(c=>c.id===example.id);assert.ok(r,'Missing frozen actual public result');assert.equal(canonical(r.request),canonical(example.request));const before=canonical(example.request),actual=engine.run(example.request);assert.equal(canonical(example.request),before,'Run changed request');assert.equal(canonical(actual),canonical(r.result),'Packaged replay differs: '+example.id);successes++;}
assert.ok(successes>=1);
assert.ok(Array.isArray(expected.failures)&&expected.failures.length>=1,'Actual qualified refusal/recovery corpus required');
for(const f of expected.failures){const before=canonical(f.request);assert.throws(()=>engine.run(f.request),undefined,'Qualified domain refusal: '+f.id);assert.equal(canonical(f.request),before);const valid=engine.run(examples[0].request);assert.equal(canonical(valid),canonical(expected.cases.find(c=>c.id===examples[0].id).result));failures++;}
const spec=examples[0].request,d=engine.descriptor;
for(const mutate of [r=>r.segments[0].duration=0,r=>r.context.model_sha256='0'.repeat(64),r=>r.context.profile='path-ode-v1',r=>r.segments.push(structuredClone(r.segments[0])),r=>r.context.controls.extra=0,r=>r.context.control_rates.strain.pop(),r=>r.settings.maximum_trials=1.5]){const r=structuredClone(spec);mutate(r);assert.throws(()=>validateRequest(r,d,definition));}
assert.throws(()=>strictJSON('{"a":1,"a":2}'));assert.throws(()=>strictJSON('{"a":1e999}'));
console.log(JSON.stringify({status:'pass',public_histories:successes,qualified_failures_and_recoveries:failures,model:identity.model,model_sha256:identity.model_sha256,catalogue_sha256:identity.catalogue_sha256}));
