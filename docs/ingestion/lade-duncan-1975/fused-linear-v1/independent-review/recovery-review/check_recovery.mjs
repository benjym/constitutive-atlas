// Pure normalized-byte reconstruction from original retained stdout.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';import {fileURLToPath} from 'node:url';
const out=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(out,'../../../../../..'),packet=path.join(root,'docs/ingestion/lade-duncan-1975/fused-linear-v1');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),pins={};
function bytes(name,pin){const p=path.resolve(root,name),b=fs.readFileSync(p),h=hash(b);if(pin)assert.equal(h,pin,p);pins[path.relative(root,p)]=h;return b;}
const recovery=JSON.parse(bytes(path.join(packet,'legacy-prerequisite-recovery-v1/RECOVERY.json'))),manifest=JSON.parse(bytes(recovery.worker_manifest.path,recovery.worker_manifest.sha256));
const early=JSON.parse(bytes(path.join(packet,'wasm-legacy-prerequisite-results.json'))),full=JSON.parse(bytes(path.join(packet,'wasm-results.json')));
assert.equal(recovery.records.length,57);assert.equal(manifest.records.length,57);assert.equal(recovery.changed,24);assert(early.passed&&full.passed);
let changed=0;const elapsedOnly=[];
for(const [index,row] of recovery.records.entries()){
 assert.equal(row.index,index);const worker=manifest.records[index];assert.equal(row.original_worker_stdout.path,worker.stdout.path);assert.equal(row.original_worker_stdout.sha256,worker.stdout.sha256);
 assert.equal(worker.state,'finished');assert.equal(worker.status,0);assert.equal(worker.signal,null);assert.equal(worker.error,null);assert(worker.elapsed_ms<120000);
 const stdout=bytes(worker.stdout.path,worker.stdout.sha256);bytes(worker.stderr.path,worker.stderr.sha256);
 const normalized=Buffer.from(JSON.stringify(JSON.parse(stdout.toString('utf8')))+'\n');assert.equal(hash(normalized),row.old_sha256);
 const old=early.records.find(x=>x.study==='native-legacy-results.json'&&x.index===index),now=full.records.find(x=>x.study==='native-legacy-results.json'&&x.index===index);
 assert(old&&now&&old.passed&&now.passed);assert.equal(old.raw_path,row.original_path);assert.equal(old.raw_sha256,row.old_sha256);assert.equal(now.raw_path,row.original_path);assert.equal(now.raw_sha256,row.current_full_sha256);
 const current=bytes(row.original_path,row.current_full_sha256);assert.equal(row.changed,row.old_sha256!==row.current_full_sha256);
 if(row.changed){changed++;assert.equal(row.archived_path,'catalogue/source-snapshots/'+row.old_sha256+'/'+row.original_path);assert.equal(Buffer.compare(bytes(row.archived_path,row.old_sha256),normalized),0);
  const a=JSON.parse(normalized),b=JSON.parse(current);delete a.elapsed_ms;delete b.elapsed_ms;assert.deepEqual(a,b);elapsedOnly.push(index);
 }else{assert.equal(row.archived_path,null);assert.equal(Buffer.compare(current,normalized),0);}
}
assert.equal(changed,24);
fs.writeFileSync(path.join(out,'recovery-check-results.json'),JSON.stringify({passed:true,records:57,changed_archived:24,unchanged:33,changed_only_elapsed_ms_indices:elapsedOnly,scope:'Saved worker stdout normalization/archive/current-full identity only; no material calls',pins},null,2)+'\n');console.log(JSON.stringify({passed:true,records:57,changed_archived:24,unchanged:33}));
