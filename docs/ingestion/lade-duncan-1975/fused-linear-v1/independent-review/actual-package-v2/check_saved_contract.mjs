import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL,fileURLToPath} from 'node:url';
const root=process.cwd(),here=path.dirname(fileURLToPath(import.meta.url));
const c=await import(pathToFileURL(path.join(root,'web/implicit-path-contract.mjs')));
const base=path.join(root,'docs/ingestion/lade-duncan-1975/atlas-integration-v1/actual-package-v2');
const read=p=>c.parseRunJSON(fs.readFileSync(p,'utf8'));
const report=read(path.join(base,'public-presets.json')),identity=report.binding.identity;
const records=read(path.join(base,'public-presets.json.raw/material/manifest.json')).records;
let calls=0;
for(const row of report.rows){
 assert(c.equal(row.controls,c.preset(row.name)));let imported;
 for(const phase of row.phases){
  const record=records[calls++],actual=read(record.stdout.path);
  assert(c.equal(actual,phase.result));assert(c.equal(phase.args,c.request(row.controls,identity)));
  c.verifyResult(actual,identity,row.controls);
  if(phase.phase==='first'){
   const saved=fs.readFileSync(row.export_path,'utf8');imported=c.importRun(saved,identity);
   assert(c.equal(imported.controls,row.controls));assert(c.equal(imported.result,actual));
  }else c.verifyReplay(actual,imported.result);
 }
}
assert.equal(calls,4);
const metadata=read(path.join(base,'public-presets.json.raw/metadata/manifest.json')).records;
assert.equal(metadata.length,1);assert(c.equal(read(metadata[0].stdout.path),read(path.join(report.binding.build,'models.json'))));
fs.writeFileSync(path.join(here,'saved-contract-results.json'),JSON.stringify({status:'passed',material_responses:4,complete_replays:2,metadata_catalogues:1,scope:'Pure saved result/export/metadata parsing and complete contract checks; no engine import or API call'},null,2)+'\n');
console.log('PASS four saved complete responses, two full replay/export contracts and embedded catalogue');
