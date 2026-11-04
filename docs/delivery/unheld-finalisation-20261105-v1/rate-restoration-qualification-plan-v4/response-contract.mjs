// Exact existing scoped laboratory contract for both declared loading forms.
import assert from 'node:assert/strict';
export function verifySupplementInputs(result,specification){
 if(specification.loading){
  assert.deepEqual(result.loading.controls_bits,specification.loading.controls_bits);
 }else{
  assert.equal(result.loading,undefined);
  assert.equal(result.target,specification.target);
  assert.equal(result.cycles,specification.cycles);
 }
 assert.deepEqual(result.integration_settings,specification.integration_settings);
}
