import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {resolve} from 'node:path';
import {importRun,exportRun,verifyResult} from '../../../../web/maxwell-atlas-contract.mjs';
const [site,folder]=process.argv.slice(2);
const identity=JSON.parse(readFileSync(resolve(site,'engine-maxwell/identity.json'),'utf8'));
let checked=0;
for(const name of readdirSync(folder).filter(n=>n.endsWith('.json')&&!['browser-assets.json','raw-byte-verification.json'].includes(n))){
 const text=readFileSync(resolve(folder,name),'utf8'),saved=JSON.parse(text);
 const restored=importRun(text,identity);
 verifyResult(restored.result,identity,restored.controls);
 assert.deepEqual(exportRun(restored.controls,restored.result,identity),saved);
 checked++;
}
assert.equal(checked,6);console.log('PASS: six complete browser exports/imports, identity, requests and results; no engine invocation.');
