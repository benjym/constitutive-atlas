import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {normalizeWichtmann,validateExperiment,measuredSeries} from '../web/experiments.mjs';

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
if(process.argv[2]){
  let count=0;
  for(const name of (await readdir(process.argv[2])).filter(n=>/^(TMD|TMU)\d+\.dat$/i.test(n))){
    const actual=normalizeWichtmann(await readFile(process.argv[2]+'/'+name,'utf8'),name);
    const reference=JSON.parse(await readFile(new URL('../data/normalized/'+actual.id+'.json',import.meta.url),'utf8'));
    assert.deepEqual(actual.rows,reference.rows,name+' rows');assert.deepEqual(actual.initial,reference.initial,name+' initial state');count++;
  }
  assert.ok(count>0);console.log(`Original-file browser/Python mapping parity passed for ${count} tests.`);
}
