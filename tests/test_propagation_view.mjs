import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {validatePropagation,propagationView} from '../web/propagation.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
const data=JSON.parse(execFileSync('python3',['-B','-c','import json; from tools.build_development import summary; print(json.dumps(summary()["propagation"]))'],{cwd:root,encoding:'utf8'}));
const ids=['file_initial','original_table_disputed_e0'];
const copy=()=>structuredClone(data);
test('all four selections use frozen scores and calibration-only selected alpha',()=>{
  const expected=[0.12934436297532312,0.1367717339283584,0.12470117631676818,0.13229439741406743];
  let i=0;for(const c of ids)for(const e of ids){const row=propagationView(data,c,e);assert.equal(row.score,expected[i++]);assert.equal(row.seed,0);assert.equal(row.alpha,c===ids[0]?0.12906250000000002:0.14);}
  assert.equal(propagationView(data,ids[0],ids[0]).relativeChange,0);
});
test('original failure and separate nested pass coexist',()=>{
  validatePropagation(data);assert.equal(data.original_refinement.passed,false);assert.equal(data.original_refinement.nonincrease_failures,4);
  assert.equal(data.nested.passed,true);assert.equal(data.nested.caller_points,9984);
});
test('missing duplicated or nonfinite factorial scores cannot render',()=>{
  for(const mutate of [d=>d.panels.pop(),d=>d.panels[1]=d.panels[0],d=>d.panels[0].root_scaled_mse=Infinity]){
    const d=copy();mutate(d);assert.throws(()=>validatePropagation(d),/factorial/);
  }
  assert.throws(()=>propagationView(data,'preferred-source',ids[0]),/Unknown/);
});
test('changing original failure flag cannot inherit nested acceptance',()=>{
  const d=copy();d.original_refinement.passed=true;assert.throws(()=>validatePropagation(d),/Conflated/);
});
test('nested pass requires both numerical and rejection-free gates',()=>{
  const d=copy();d.nested.rejection_free=false;assert.throws(()=>validatePropagation(d),/Conflated/);
});
test('missing nested rows cannot hide a failed channel',()=>{
  const d=copy();d.nested.rows[1]=d.nested.rows[0];assert.throws(()=>validatePropagation(d),/coverage/);
});
test('missing limits or changed selection budgets cannot render',()=>{
  const d=copy();d.limitations=[];assert.throws(()=>validatePropagation(d),/limits/);
  const b=copy();b.calibration.selection='evaluation_error';assert.throws(()=>validatePropagation(b),/selection/);
});
test('unsafe source URL and scientific promotion are rejected',()=>{
  const d=copy();d.sources[0].url='javascript:alert(1)';assert.throws(()=>validatePropagation(d),/Unsafe/);
  const p=copy();p.scientific_admission=true;assert.throws(()=>validatePropagation(p),/Unsupported/);
});
