import {readFile,writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {join,resolve} from 'node:path';
import assert from 'node:assert/strict';

const [launcher,fixtures,lifecycle,out,match] = process.argv.slice(2);
const cases = JSON.parse(await readFile(fixtures, 'utf8'));
const negative = JSON.parse(await readFile(lifecycle, 'utf8'));
const create = (await import(pathToFileURL(resolve(launcher)))).default;
const atlas = await create();
const call = (instance, name, args) => JSON.parse(instance.ccall(name, 'string', Array(args.length).fill('string'), args));
const bits = xs => xs.map(x => {const b=Buffer.alloc(8);b.writeDoubleBE(x);return b.toString('hex');});
const csv = xs => xs.map(x => Object.is(x,-0) ? '-0' : String(x)).join(',');
for (const row of cases.filter(row => row.negative && (!match || row.id.includes(match)))) {
  const [id,p,z,,,,settings]=row.args;
  const probe=negative[row.id];
  const state=csv(probe.fixed_state), de=csv([0,0,probe.axial,0,0,0]);
  const fixed=call(atlas,'atlas_evaluate',[id,p,state,state,de]);
  const parent=call(atlas,'atlas_evaluate',[id,p,z,z,de]);
  const refused=call(atlas,'atlas_replay_recorded_scope',row.args);
  const usable=Array.isArray(refused.state);
  const after=usable?csv(refused.state):z;
  const hold=call(atlas,'atlas_integrate_with_settings',[id,p,after,'0,0,0,0,0,0',settings]);
  const recovery=call(atlas,'atlas_integrate_with_settings',[id,p,after,csv(probe.recovery),settings]);
  const fresh=call(await create(),'atlas_integrate_with_settings',[id,p,z,csv(probe.recovery),settings]);
  const checks={fixed:fixed.ok, parent:parent.ok, refused:usable&&!refused.ok&&refused.points.length===0&&
    refused.message==='simultaneous stress constraints did not converge; entire path rolled back'&&
    JSON.stringify(bits(refused.state))===JSON.stringify(row.parent),
    hold:hold.ok&&JSON.stringify(bits(hold.state))===JSON.stringify(row.parent),
    recovery:recovery.ok&&fresh.ok&&JSON.stringify(bits(recovery.state))===JSON.stringify(bits(fresh.state))};
  const report={checks,fixed,parent,refused,hold,recovery,fresh};
  await writeFile(join(out,row.id+'.lifecycle.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
  console.log(row.id, checks);
}
