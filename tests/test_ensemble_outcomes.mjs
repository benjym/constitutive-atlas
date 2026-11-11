import test from 'node:test';
import assert from 'node:assert/strict';
import {describeEnsembleOutcome} from '../web/ensemble.mjs';

const record={initial:{effective_stress:[103720,103720,103720,0,0,0],void_ratio:.416},rows:[{axial_strain:.001}]};
const invalid='invalid recorded-path parameters or initial state';
const lineSearch='mixed-control line search failed or trial budget exhausted; last committed knot retained';

test('no accepted point is a start failure, with a specific reason only when supported',()=>{
 const job={status:'stopped',message:invalid,result:{points:[],failed_knot:-1}};
 const unknown=describeEnsembleOutcome(job,record);
 assert.equal(unknown.label,'Couldn’t start with this specimen');
 assert.equal(unknown.symbol,'×');
 assert.match(unknown.reason,/did not identify which check failed/);
 const sand={...job,model:'hypoplastic-sand-vw96',parameters:{hs:5.8e9,n:.28,ed0:.53,ei0:1}};
 assert.match(describeEnsembleOutcome(sand,record).reason,/0\.416 must be above 0\.4973/);
 assert.match(describeEnsembleOutcome(sand,{initial:{...record.initial,void_ratio:1.1}}).reason,/1\.1 must be below/);
});

test('stop strain uses the last committed point on the chart axis, including a first-step failure',()=>{
 const job={status:'stopped',message:'singular mixed-control system; last committed knot retained',result:{points:[{strain:[0]},{strain:[.00837]}],failed_knot:2}};
 const stopped=describeEnsembleOutcome(job,record);
 assert.equal(stopped.label,'Solver stopped at 0.937% axial strain');
 assert.equal(stopped.symbol,'!');
 assert.match(stopped.reason,/control system was singular/);
 job.result.points.pop();
 assert.equal(describeEnsembleOutcome(job).label,'Solver stopped at 0% axial strain');
});

test('line search tooltip distinguishes a known trial limit from a failed stress match',()=>{
 const job={status:'stopped',message:lineSearch,result:{points:[{strain:[.01]}],material_trials:762,control_settings:{max_material_trials:20000}}};
 assert.match(describeEnsembleOutcome(job).reason,/No trial step improved/);
 job.result.material_trials=20000;
 assert.match(describeEnsembleOutcome(job).reason,/Reached the limit/);
 delete job.result.material_trials;
 assert.equal(describeEnsembleOutcome(job).reason,'mixed-control line search failed or trial budget exhausted');
 assert.equal(describeEnsembleOutcome({status:'rejected',message:'M is outside declared bounds.'}).reason,'M is outside declared bounds.');
});
