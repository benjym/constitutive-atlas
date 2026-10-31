# Checked expm study verification review

Read-only review of tools/expm_study.py, tools/test_expm_wasm.mjs, tests/test_expm_study.py and retained native/Wasm transcripts. No native/Wasm execution, builds or authoritative edits. Python reassessment reads existing transcripts and recomputes the independent Decimal oracle.

## Outcome

No remaining blocker identified in the main assessment/CLI flow after the Boolean-alias fixes below. The final packet manifest is now present and its hashes pass the retained-packet test.

The actual native and Wasm transcripts both pass fresh Decimal160assessment for44cases, full6×6Jacobian,29named contexts and23invalid requests. Maximum norm-scaled primitive/schema value error is8.9933844869e−15; Jacobian error8.9931338913e−15; recomputed native/Wasm parity1.0137230732e−16. These are normwise metrics with declared absolute floors, not component-relative or positive-definiteness certificates. See fresh-assessment.json.

## Concrete findings fixed during review

On the initially installed verifier, four corruptions of the actual loaded Wasm transcript passed: recovery.ok=1, recovery.values[0]=True for control value1, parser rejection ok=0, and first request input False for0. Python dictionary/list equality equates booleans and numbers. Recovery had only equality comparison; parser rejection had only dictionary equality; request input was not independently vector checked.

The synthetic test's recoveries initially aliased the control response object; deepcopy preserved this internal alias. Mutating recovery could corrupt the validated control too, masking the recovery-check gap. Parent fixed synthetic recovery isolation and added actual-loaded-transcript regressions.

Current fixes inspected and reprobed:

- Request input vectors reject Boolean elements before equality.
- Parseable metadata requires actual bool.
- Parser failure requires exact keys, ok is False and expected error string.
- Recovery passes full validate_response before equality with control.

All five postfix corruption probes reject, including parseable=0; see probes.json for historical accepted mutations and postfix-probes.json for current rejections. These historical failures are not evidence that current transcripts are numerically invalid.

## Trust and coverage assessment

- Exact ordered case identity, input/CSV/mode, runtime operator version, catalogue hash and reference-file hash are checked. Fresh mode independently recomputes every oracle value/Jacobian at160digits rather than trusting stored assessment. All36Jacobian entries are included for primitive and schema paths.
- Context validation requires the exact29name set and actual True values, not a count alone. Missing, renamed and false contexts reject. Runtime flags attest the pinned probe's assertions; the JSON alone cannot independently reconstruct its execution semantics.
- All23invalid requests are bound to their expected text and parseability. Range-rejected parseable inputs must expose no values/Jacobian; malformed/nonfinite CSVs must match the parser rejection contract. Wasm recoveries are now typed/shape/version/catalogue/context/value validated and equal the initial zero-input control after each invalid call.
- The Node runner actually invokes one persistent module, runs each invalid call and then the control, and checks equality before writing. This supports temporal recovery ordering when combined with pinned executed runner/artifact provenance; an archive alone cannot prove execution order.
- The Node parity pass compares all values/Jacobians; Python independently recalculates parity after assessing both reports. Raw-byte native-report hash semantics are consistent between Node and Python.
- Existing corruption tests now cover missing cases, input/response binding, incomplete/Boolean/incorrect Jacobians, named contexts, nonfinite/incorrect values, identity/budget changes, invalid records and recovery, plus the actual-loaded Boolean cases.

## Nonblocking limitations

The initially observed standalone verify_parity() precondition has been removed: current helper calls assess(fresh=False) on both reports before parity traversal. Complete shapes, finite types and coverage are therefore enforced for standalone calls too; fresh mathematical replay remains the outer assess default.

Binary/loader hash fields identify supplied artifacts; mathematical reassessment does not authenticate a rebuild or execute those artifacts. Manifest/build receipt dependencies remain essential. No experimental, constitutive-model or public admission follows from operator conformance.

## Python execution

- All five direct actual-transcript corruption repros reject after fixes.
- Fresh assess(native), assess(wasm) and verify_parity pass with metrics above.
- Final `python3 -m unittest tests.test_expm_study -v`:all10groups pass, including final manifest hashes, actual44case fresh independent replay, standalone parity and all corruption groups.

reviewed-hashes.json pins this inspected verifier/test/runner/transcript snapshot. Final manifest was included in the inspected hashes; parent owns final publication/commit pinning.
