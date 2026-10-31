import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {validateSummary,scenarioView} from '../web/development.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
const data=JSON.parse(execFileSync('python3',['-B','-c','import json; from tools.build_development import summary; print(json.dumps(summary()))'],{cwd:root,encoding:'utf8'}));
const copy=()=>structuredClone(data);
test('both scenarios preserve the declared locked six-test scores and contrast',()=>{
  const file=scenarioView(data,'file_initial'),alternative=scenarioView(data,'original_table_disputed_e0');
  assert.equal(file.rows[0].score,0.1690426791149183);assert.equal(alternative.rows[1].score,0.1367717339283584);
  assert.equal(file.rows[0].relativeChange,0);assert.ok(alternative.rows.every(r=>r.relativeChange>0));
  assert.ok(file.contrast<0&&alternative.contrast<0);assert.equal(data.scientific_admission,false);
});
test('a missing or duplicate package is rejected rather than reusing another score',()=>{
  const broken=copy();broken.scores[1]=broken.scores[0];assert.throws(()=>validateSummary(broken),/package scores/);
});
test('nonfinite scores and unknown scenario cannot render',()=>{
  const broken=copy();broken.scores[0].root_scaled_mse=NaN;assert.throws(()=>validateSummary(broken),/package scores/);
  assert.throws(()=>scenarioView(data,'preferred-source'),/Unknown/);
});
test('unsafe source links and missing scientific limits are rejected',()=>{
  const broken=copy();broken.sources[0].url='javascript:alert(1)';assert.throws(()=>validateSummary(broken),/Unsafe/);
  const missing=copy();missing.limitations=[];assert.throws(()=>validateSummary(missing),/limitations/);
});
test('incomplete refinement cannot inherit a passing result',()=>{
  const broken=copy();broken.refinement.shifts[1]=broken.refinement.shifts[0];assert.throws(()=>validateSummary(broken),/coverage/);
});
test('scientific promotion or missing archived identity is rejected',()=>{
  const promoted=copy();promoted.scientific_admission=true;assert.throws(()=>validateSummary(promoted),/Unsupported/);
  const missing=copy();missing.definition_sha256='live-default';assert.throws(()=>validateSummary(missing),/identity/);
});
