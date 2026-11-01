// Replay only syntax/import/algebra/pin checks, intercepting the frozen report write.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../../../../../../');
const base=path.join(root,'docs/ingestion/lade-duncan-1975/atlas-integration-v1/public-ci-v1');
const frozen=fs.readFileSync(path.join(base,'pure-results.json'),'utf8');
const original=fs.writeFileSync;
let writes=0;
fs.writeFileSync=(name,bytes,...rest)=>{
 assert.equal(path.resolve(name),path.join(base,'pure-results.json'));
 assert.equal(bytes,frozen,'Pure replay report differs from retained evidence');
 original(path.join(here,'public-pure-replay-results.json'),bytes,...rest);writes++;
};
try{await import(pathToFileURL(path.join(base,'check_pure.mjs')));assert.equal(writes,1);}
finally{fs.writeFileSync=original;}
