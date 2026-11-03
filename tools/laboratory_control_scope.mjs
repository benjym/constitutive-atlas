// Public support is a pre-existing scope declaration, never an observed-failure waiver.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {validateSupport,unsupportedReason} from '../web/laboratory-support.mjs';
export {unsupportedReason};
export function validateControlScope(policy,catalogue,definitionHash){
 validateSupport(policy,catalogue);
 for(const row of policy.models)assert.equal(row.definition_sha256,definitionHash(row.model),'Stale control-support definition: '+row.model);
 return policy;
}
export function loadControlScope(catalogue){
 const read=path=>readFileSync(new URL('../'+path,import.meta.url));
 return validateControlScope(JSON.parse(read('catalogue/laboratory-control-support.json')),catalogue,id=>createHash('sha256').update(read('models/'+id+'.json')).digest('hex'));
}
