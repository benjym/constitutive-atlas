import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {normalizeWichtmann,validateExperiment,measuredSeries,decodeExperiment,fetchExperiment,comparisonMetadata,compatibleExperiment,comparisonSeries} from '../web/experiments.mjs';

const tmd='eps1 epsv eps3 epsq Void ratio q p eta = q/p\n[%] [%] [%] [%] [%] [kPa] [kPa] [-]\n\n0 0 0 0 .8 0 100 0\n1 .2 -.4 .8 .796 30 110 .27\n';
const tmu="eps1 u sigma3 sigma3' sigma1 sigma1' p q\n[%] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa]\n\n0 200 300 100 300 100 100 0\n1 220 300 80 330 110 90 30\n";
const drained=normalizeWichtmann(tmd,'TMD1.dat'),undrained=normalizeWichtmann(tmu,'TMU1.dat');
assert.equal(drained.rows[1].axial_strain,.01);assert.equal(drained.rows[1].volumetric_strain,.002);assert.equal(drained.rows[1].q,30000);assert.equal(drained.initial.void_ratio,.8);
assert.equal(undrained.rows[1].pore_pressure,20000);assert.equal(undrained.rows[1].pore_pressure_absolute,220000);assert.equal(undrained.initial.void_ratio,undefined);assert.equal(undrained.rows[1].volumetric_strain,undefined);
assert.deepEqual(measuredSeries(drained,true,'axial_strain','q'),[[0,0],[.01,30000]]);assert.deepEqual(measuredSeries(drained,false,'axial_strain','q'),[]);assert.deepEqual(measuredSeries(undrained,true,'axial_strain','volumetric_strain'),[]);
assert.equal(drained.rows.length,2); // Hiding does not destroy loaded measurements.
assert.throws(()=>normalizeWichtmann(tmd,'TCUI1.dat'));
assert.throws(()=>normalizeWichtmann(tmd.replace('[kPa]','[Pa]'),'TMD1.dat'));
assert.throws(()=>normalizeWichtmann(tmd+'bad row\n','TMD1.dat'));
assert.throws(()=>normalizeWichtmann(tmd.replace('30 110','NaN 110'),'TMD1.dat'));
assert.throws(()=>validateExperiment({...drained,id:null}));
assert.throws(()=>validateExperiment({...drained,conventions:{}}));
assert.throws(()=>validateExperiment({...drained,rows:[{axial_strain:0,q:0,p:NaN}]}));
const cyclic={...drained,rows:[{axial_strain:0,q:0},{axial_strain:.01,q:100},{axial_strain:0,q:-10}]};
assert.deepEqual(measuredSeries(cyclic,true,'axial_strain','q'),[[0,0],[.01,100],[0,-10]]);
console.log('Browser experiment import, units, missing channels, ordering and visibility checks passed.');
// Optional comparison against local original files; no measured data are committed.
if(process.argv[2]&&process.argv[2]!=='--built-assets'){
  let count=0;
  for(const name of (await readdir(process.argv[2])).filter(n=>/^(TMD|TMU)\d+\.dat$/i.test(n))){
    const actual=normalizeWichtmann(await readFile(process.argv[2]+'/'+name,'utf8'),name);
    const reference=JSON.parse(await readFile(new URL('../data/normalized/'+actual.id+'.json',import.meta.url),'utf8'));
    assert.deepEqual(actual.rows,reference.rows,name+' rows');assert.deepEqual(actual.initial,reference.initial,name+' initial state');count++;
  }
  assert.ok(count>0);console.log(`Original-file browser/Python mapping parity passed for ${count} tests.`);
}

// Native source channels never acquire normalized model-overlay semantics.
const native={schema_version:'0.1',kind:'measurement-series',id:'NATIVE-1',
  conventions:{stress:'source-defined',strain:'source-defined',stress_unit:'per-channel',strain_unit:'per-channel'},
  columns:[{key:'c2',name:'stress',unit:'kPa'},{key:'c3',name:'void ratio',unit:'1'}],
  source_plot:{x:'c2',y:'c3'},rows:[{c2:10,c3:1.2},{c3:1.1}]};
const nativePacked={format:'atlas-source-columns-v1',metadata:{...native,rows:undefined},columns:['c2','c3'],values:[[10,1.2],[null,1.1]]};
assert.deepEqual(decodeExperiment(nativePacked).rows,native.rows);
assert.deepEqual(measuredSeries(native,true,'c2','c3'),[[10,1.2]]);
assert.throws(()=>decodeExperiment({...nativePacked,format:'atlas-experiment-columns-v1'}));
assert.throws(()=>decodeExperiment({...nativePacked,columns:['c2','c4']}));
assert.throws(()=>decodeExperiment({...nativePacked,values:[[null,null]]}));
assert.throws(()=>validateExperiment({...native,source_plot:{x:'c9',y:'c3'}}));
assert.throws(()=>validateExperiment({...native,rows:[{c2:10,c4:1}]}));
assert.throws(()=>validateExperiment({...native,columns:[native.columns[0],native.columns[0]]}));

// Hosted assets preserve observation order and reject stale/corrupted responses.
const columns=['axial_strain','q','p'];
const packed={format:'atlas-experiment-columns-v1',metadata:{...drained,rows:undefined},columns,values:drained.rows.map(r=>columns.map(c=>r[c]))};
const decoded=decodeExperiment(packed);
assert.deepEqual(decoded.rows,drained.rows.map(r=>({axial_strain:r.axial_strain,q:r.q,p:r.p})));
assert.throws(()=>decodeExperiment({...packed,columns:['axial_strain','q','q']}));
assert.throws(()=>decodeExperiment({...packed,values:[[0,1]]}));
assert.throws(()=>decodeExperiment({...packed,values:[[0,Infinity,1]]}));
// Optional channels can be missing without discarding the other observations.
const partial=decodeExperiment({...packed,values:[[0,0,null],[.01,30000,110000]]});
assert.equal(partial.rows[0].p,undefined);
assert.deepEqual(measuredSeries(partial,true,'axial_strain','p'),[[.01,110000]]);
assert.throws(()=>decodeExperiment({...packed,values:[[0,null,100000]]}));
const bytes=new TextEncoder().encode(JSON.stringify(packed));
const sha256=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
const entry={id:drained.id,path:drained.id+'.json',rows:2,size_bytes:bytes.byteLength,sha256};
let fetched;
assert.deepEqual(await fetchExperiment(entry,async path=>{fetched=path;return new Response(bytes);}),decoded);
assert.equal(fetched,'./experiments/KFS-TMD1.json');
await assert.rejects(fetchExperiment({...entry,path:'../private.json'},async()=>new Response(bytes)),/catalogue entry/);
let oversizedRequested=false;
await assert.rejects(fetchExperiment({...entry,size_bytes:33*1024*1024},async()=>{oversizedRequested=true;return new Response(bytes);}),/catalogue entry/);
assert.equal(oversizedRequested,false);
await assert.rejects(fetchExperiment(entry,async()=>new Response('not found',{status:404})),/could not be loaded/);
await assert.rejects(fetchExperiment({...entry,sha256:'0'.repeat(64)},async()=>new Response(bytes)),/checksum/);
await assert.rejects(fetchExperiment({...entry,rows:3},async()=>new Response(bytes)),/selected test/);
console.log('Hosted experiment decoding, integrity, channel semantics and request validation passed.');

if(process.argv[2]==='--built-assets'){
  const directory=process.argv[3];
  assert.ok(directory,'Provide the built experiments directory.');
  const manifest=JSON.parse(await readFile(directory+'/index.json','utf8'));
  const registry=JSON.parse(await readFile(new URL('../data/public_sources.json',import.meta.url),'utf8'));
  const approvedSources=new Map(registry.sources.filter(source=>source.public_hosting===true).map(source=>[source.id,source]));
  for(const entry of manifest.experiments){
    const content=await readFile(directory+'/'+entry.path);
    const actual=await fetchExperiment(entry,async()=>new Response(content));
    assert.equal(actual.rows.length,entry.rows);
    assert.deepEqual(entry.comparison,comparisonMetadata(actual));
    for(const column of actual.columns||[]){
      assert.ok(['standardized','unresolved'].includes(column.unit_status));
      assert.equal(typeof column.source_unit,'string');
      if(column.unit_status==='standardized')assert.ok(Number.isFinite(column.unit_conversion.scale)&&Number.isFinite(column.unit_conversion.offset));
    }
    const source=approvedSources.get(actual.provenance.source_id);
    assert.ok(source,`Unapproved built experiment source: ${actual.provenance.source_id}`);
    assert.ok(source.license_evidence,`Missing recorded license evidence for ${source.id}`);
    assert.equal(actual.provenance.license,source.license);
    assert.equal(actual.provenance.license_url,source.license_url);
  }
  console.log(`All ${manifest.experiments.length} built experiments passed browser decoding and checksum checks.`);
}

assert.equal(compatibleExperiment(drained,1,0),true);
assert.equal(compatibleExperiment(drained,2,0),false);
assert.equal(compatibleExperiment(drained,1,3),false);
assert.equal(compatibleExperiment(undrained,3,0),true);
assert.equal(compatibleExperiment(drained,0,0),false);
assert.equal(compatibleExperiment(native,1,0),false);
assert.equal(compatibleExperiment({...native,kind:'test-summary'},1,0),false);
assert.deepEqual(comparisonSeries(drained,true,'stress',1),[[0,0],[1,30]]);
assert.deepEqual(comparisonSeries(drained,true,'path',1),[[100,0],[110,30]]);
assert.deepEqual(comparisonSeries(drained,true,'volume',1),[[0,0],[1,.2]]);
assert.deepEqual(comparisonSeries(undrained,true,'pore',2),[[0,0],[1,20]]);
assert.deepEqual(comparisonSeries(undrained,true,'volume',2),[]);
assert.deepEqual(comparisonSeries(drained,true,'stress',2),[]);
assert.deepEqual(comparisonSeries(drained,false,'stress',1),[]);
assert.equal(comparisonMetadata(cyclic).loading,'reversing');
assert.equal(compatibleExperiment(cyclic,1,3),true);
assert.equal(compatibleExperiment({...entry,kind:'experiment',protocol:drained.protocol,comparison:comparisonMetadata(drained)},1),true);
const noisy={...drained,rows:[{axial_strain:0,q:0},{axial_strain:.01,q:100},{axial_strain:.00999,q:99}]};
assert.equal(comparisonMetadata(noisy).loading,'monotonic');
console.log('Comparison axes, display-unit conversions, drainage/loading filters and missing pairs passed.');
