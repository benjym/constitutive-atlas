# Scoped laboratory execution adapter

`web/laboratory-scope.mjs` provides a dedicated consumer boundary for the
existing scoped native/Wasm laboratory exports. The live laboratory view and
worker remain on their legacy effective contract; this module is not packaged
or selected automatically yet. Production total-profile validation remains
unchanged, and no model or scientific status is added.

## Contract

`validateScopedLaboratory(specification, catalogue)` requires explicit
`response_contract: "stress-scope-0.1"`, `stress_scope: "effective" | "total"`,
model, parameter vector, full initial state, protocol, target, steps and cycles.
Only the existing optional `integration_settings` and `loading` fields are allowed.
The caller supplies the trusted matching compiled catalogue. Legacy model0.1 has
its documented effective Cauchy stress; model0.3 must explicitly declare
strain-path/Mandel/compression-positive first persistent Cauchy sigma6 in Pa.
Timed/observable/unknown bindings cannot acquire a guessed stress scope.
Metadata checks do not replace full model validation or scientific review.

`runScopedLaboratory` clones its inputs, validates vectors/bounds/loading,
compares `atlas_describe` with the full catalogue and exact parameter-key order,
then selects only `atlas_run_scope_with_settings` or
`atlas_run_controls_scope_with_settings`. Missing exports throw; there is no
legacy fallback. Existing target/steps/cycles loading retains its backend waveform
semantics. Explicit loading uses the existing exact binary64 producer/echo checker.
The model catalogue, settings, mechanical controls and constitutive code do not
change. The initial vectors are mandatory rather than guessed by this boundary.

`verifyScopedLaboratory` checks API/schema/model/catalogue/stress identity,
resolved vectors and settings, protocol/range/loading identity, complete success
or finite committed failure prefix, initial state/zero strain, diagnostics and
pore availability. It does not recompute constitutive equations or all control
residuals. Returned failure metadata must use the matching scoped contract;
unversioned preflight errors are rejected as errors, never accepted as a result.

`laboratoryStress` resolves the supported state-stress descriptor.
`laboratoryPoreSeries` projects a verified result to axial-strain-percent versus
pore-pressure-change-kPa. Effective protocols2/3 require the exact reconstructed
change descriptor and finite numeric u (initial0). Effective0/1/4 and every total
protocol require the exact unavailability reason and u:null, returning an empty
series plus that reason. Null, booleans, strings and nonfinite values cannot become
a reconstructed curve, and numeric0 cannot stand in for unavailable pressure.
This is the existing external boundary assumption, not a constitutive pore law.

## Qualification

[freeze.json](freeze.json) predates observations. It selects ten exact existing
native cases (effective and synthetic total elasticity across all five protocols)
and one independent effective elastic exact-waveform reversal. The existing
pinned10-record Wasm artifact from `recorded-scope-view-v1` is reused after
checking engine hashes and every compiled source/header pin. No build or new
native execution occurs. Eleven material requests and their metadata calls were
made serially; there was no rerun or fit.

All ten scoped Wasm responses agree with saved native results under the frozen
relative1e-9 gate, with exact structures/settings/status/counters and elapsed time
excluded. The17-point exact cyclic reversal passes the original independent
stress0.002Pa and strain2e-10 limits: maximum stress error
3.92901711165905e-10Pa and strain error8.185726402265558e-18. Parameter/initial,
exact loading bits, unavailable pressure and full history are captured.
The fixture verifies generic transport; it is not Tresca verification or admission.

[The original exercise process failed](process.json) after all11 responses were
saved. An extra assertion, absent from the frozen acceptance policy, incorrectly
assumed history beyond sigma stayed constant during elastic loading. The actual
linear-elastic record declares
`e - (1 + e_n) * exp(-trace(de)) + 1`, so void ratio evolves with volumetric strain.
The original script, stderr and outputs remain intact. The separate saved-only
assessor applies the original frozen stress/strain policy to those captured
outputs without rerunning a material call. This does not turn the failed original
process into a passing process or invent a new numerical tolerance.

Six focused Python tests pass, including the JS contract harness on ten retained
responses,226 rejection assertions, exact/default endpoint routing, no fallback,
pore policy and finite failure prefixes. Four saved-evidence corruptions
(scope, pore nullability, stress and truncated prefix) reject. The exact-routing
unit case adds synthetic loading metadata to an unchanged saved monotonic
response solely to check dispatch/echo; the actual17-point Wasm call separately
checks the real explicit endpoint. This is not an actual browser-page gate.

```sh
python3 -B -m unittest tests.test_laboratory_scope_execution tests.test_laboratory_scope_contract tests.test_laboratory_scope_adapter_evidence -q
python3 -B docs/reviews/laboratory-scope-adapter-v1/verify.py
```

## Stopping point

Next connect laboratory view/worker routing, complete examples, scope-specific
protocol/axis/accessible labels, pore availability messages and versioned JSON/CSV
imports/exports together. Qualify those actual consumers with the existing scoped
engine before production total-profile activation and the existing Tresca
source/reference/backend gates. The current browser still has nine public models;
no deployment, schema/model migration or scientific admission occurs here.
