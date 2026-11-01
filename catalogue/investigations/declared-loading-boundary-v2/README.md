# v0.3 declared loading boundary repair

Task **FIX-declared-loading-boundary-v2**, coordinator, 1 November 2026.

The generated evaluator now checks all six **primal** loading values for finiteness on entry to every v0.3 case, before derived expressions, domain/initial checks, check-only returns and observable routing. This implements the existing [explicit-input requirement](../../../docs/FORMULATION_CONTRACT.md#explicit-input-declarations), including unused inputs. The [failed v1 study](../declared-loading-boundary-v1/README.md) remains unchanged with126unexpected acceptances; its saved assessment still reproduces exactly.

The four-line change is in `atlas/compiler.py`; no model expression, schema, solver algorithm or C++ primitive changed. The guard uses component values, avoiding a norm-based test that would reject finite extreme values through norm overflow. It applies only to v0.3. Legacy generated cases remain unchanged.

## Deliberate derivative and lazy scope

`atlas::value(component)` checks the physical loading value for both double and Jet instantiations. This does **not** introduce unconditional validation of unused Jet derivative columns. Existing executed-node checks still validate a Jet's value and all derivative columns whenever its AST node executes. An invalid unselected expression remains lazy; a nonfinite *required input value* cannot evade the interface contract by being unused. The qualification here observes double primal boundaries; it does not establish a new Jet-input derivative policy or a material tangent.

## Frozen qualification

Three synthetic fixtures are byte-identical to v1 and cover incremental residual, strain-path rate and physical-time ODE profiles. The same378literal acceptance/recovery rows remain frozen, augmented by28finite-input controls: negative zero, smallest positive subnormal and both extreme finite signs in every applicable direct route. Fixtures are conformance specifications, not scientific models. [Protocol](protocol.json), assessor, expected rows, generated files and exact runtime/generating sources were [frozen before building](pre-build-freeze.json).

| Check | Result |
| --- | --- |
| Native qualification |406/406pass |
| Wasm qualification |406/406pass |
| Native/Wasm ordered status and input-preservation rows |Exactly equal |
| Original126invalid-input acceptances |All reject under unchanged policy |
| Public-integrator rejection/recovery and clock controls |Pass |
| Finite component controls |28/28pass, including norm-overflowing finite tensors in direct unused-loading routes |
| Formulation/interpreter/prior-context regression tests |14pass |
| Assessor damaged-journal checks |Truncation, restored NaN acceptance and changed row identity all reject |
| Historical compiler/test receipt bindings |15edges resolve exact archived bytes |

One native target was built/accepted before one Wasm target; both used `--parallel 1`, strict floating flags and frozen runtime headers. No runtime stderr or endpoint-protection interruption occurred. Backend receipts pin commands, executable/loader/Wasm hashes and post-run input checks. No author code ran.

The [complete-catalogue source comparison](generation-compatibility.json) covers all eleven current definitions: six v0.3 entry guards are the sole generated-header changes, and canonical catalogue JSON bytes are identical. The synthetic three-case header has the same exact guard-only delta. This is generation compatibility, **not a fresh compiled eleven-model/default-run qualification**.

The initial14-test selection exposed twelve subcase failures in an old assertion that legacy and migrated generated code were identical. [That result](initial-compatibility-failure.txt) is retained. The comparison now explicitly excludes the required v0.3 boundary guard while continuing to require identical material code; the [same tests pass](focused-tests.txt). Earlier test/compiler identities are archived with document-bound sidecars. A temporary runner-preparation import-path failure occurred before the runner or native build existed; it was corrected without changing the frozen cases. A pre-build catalogue-count metadata correction is recorded in [preparation notes](preparation-notes.txt), with its original value retained. Neither altered acceptance policy.

## Saved-only replay

From the repository:

```sh
python3 -B catalogue/investigations/declared-loading-boundary-v2/assess.py --both
python3 -B -m unittest tests.test_formulation tests.test_expression_finiteness tests.test_expression_context_evidence
```

The assessor verifies frozen inputs and compares every ordered observation. It does not build or execute artifacts. Its expected rows remain distinct from the original failed study. The backend runner refuses to overwrite existing observations; do not rerun it into this evidence directory.

## Remaining rollout gate

The compiler repair is qualified for these generated evaluator routes. Existing website/native release artifacts are unchanged and do not acquire this fix automatically. Next freeze the current mixed catalogue, rebuild serial native/Wasm targets, and replay prior ten passing ordinary defaults plus the explicit small GIS example. Retain the ordinary GIS default failure separately and unchanged; do not tune settings to make the rollout pass. Verify full state/control/status compatibility and package the new engine only after those checks. Browser delivery and deployment remain separately authorized steps. Source/scientific admission, other expression/history boundaries and the overall roadmap remain open.
