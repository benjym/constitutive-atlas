# Prospective independent reference v1

Source specialist `/root/ramberg_source`, 2 November 2026. NUM-ramberg-osgood-reference-v1. No compiled artifact was built or executed by this specialist.

The frozen [requests.json](requests.json) contains 83 cases and 265 individual operations. Parameters are ordered `E,nu,sigma0,alpha,n`. Every case contains explicit full initial state, a list of increments and solver settings; accepted response state is the next operation's parent. Rejected responses do not advance the parent. Successful cases carry independently expected full states. Invalid cases require rejection; inconsistent-state and exhausted-budget cases additionally require exact whole-state rollback.

The reference in `tools/check_ramberg_osgood.py` inverts the primary scalar equivalent-strain relation by 160 bisections using its linear-elastic upper bracket, then reconstructs stress. It does not import atlas, parse the production DSL or reproduce the production tensor residual/Newton implementation. Source-compliance evaluation is used only for preparing explicitly consistent nonzero parents and source closed-form checks. State strain accumulation is independently prescribed and tested componentwise.

Coverage: seven parameter sets (default, n1.5, n2.5, n8, negativeν, near-incompressibleν and original vendor example); zero/origin, hydrostatic reversal, uniaxial loading/unloading/reversal, all three Mandel shear planes with both signs, fully mixed tensor load/hold/reversal, fixed-basis rotation, nonzero initial state, 16increment refinement and positive1000fold stiffness/stress-unit scaling. Separate origin and mixed-state tangent requests compare the returned complete state tangent to linear elasticity or central differences of the independent source inverse. No finite-rotation objectivity claim follows from a basis change.

Negative requests: α0, n1, ν0.5, negativeE, inconsistent preparation, omitted initial state, nonfinite loading and exhausted solve budget; then successful fresh recovery. The nonfinite request uses `strain_csv_override: "nan,0,0,0,0,0"`, keeping the frozen request JSON strict and portable. Native and Wasm callers must honor this override. It is a wire-level rejection test, not a zero-loading request.

The parent PLAN.md governs unchanged tolerances. The checker applies stress2e-5σ0, strain2e-8σ0/E and refinement4e-5σ0. Tangent component errors are normalized by `max(1,E,abs(reference_component))` to avoid dividing by exact zero tensor entries; thresholds are origin1e-8 and mixed2e-5. Origin reference is the exact linear tangent. All compiled failures must remain in original reports; do not change this packet to turn observations into passes.

Commands (coordinator only for compiled execution):

```sh
python3 -m unittest tests.test_ramberg_osgood -v
python3 tools/check_ramberg_osgood.py --solver /absolute/path/to/atlas_solver --save-responses /path/native-responses.json --output /path/native-results.json
python3 tools/check_ramberg_osgood.py --responses /path/wasm-responses.json --output /path/wasm-results.json
```

Saved-response schema is `{identity:"ramberg-osgood-responses-v1", model_sha256:<frozen hash>, cases:[{id:<request case id>, responses:[<parsed common-engine response per operation>]}]}`. Calls are `atlas_integrate_with_settings` or `atlas_linearize_with_settings` for `mode:"linearize"`. Use current full state12, the same parameter order, comma-separated increments and six integration settings. The native CLI uses corresponding `--mode integrate|linearize`, `--parameters`, `--initial`, `--strain`, and `--integration-settings` flags. Wasm response ordering/identity must match the requests; caller must not substitute source expected states into subsequent updates.

Python-only evidence: five tests pass for schema, valid/nonzero preparation and invalid initialization, independent scalar-inverse/closed-form consistency, basis/unit/reversal properties and byte-equivalent reproducible requests. These do not claim compiled qualification. Native/Wasm parity at relative1e-10 still requires the parent to compare independently saved operation state/tangent responses after both backend gates. Broad parameter-domain coverage and material experiments remain outside this bounded reference study.
