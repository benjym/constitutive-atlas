# Native recorded stress-scope contract

Completed 1 November 2026. This connects the [recorded0.2 request design](../../RECORDED_STRESS_SCOPE.md) to native C exports and CLI response selection. Python/JavaScript execution adapters and browser rendering/import/export remain legacy-only. Production total incremental validation stays disabled; no public model is added.

## Native interface

New exports, with all arguments encoded as strings like the existing recorded API:

```text
atlas_replay_recorded_scope(id, parameters, initial, initial_strain,
                           controls, knots, material_settings,
                           control_settings, stress_scope)
atlas_replay_recorded_scope_with_restarts(id, parameters, initial,
                           initial_strain, controls, knots,
                           material_settings, control_settings,
                           restart_settings, stress_scope)
```

Scope is required and must equal generated effective/total model metadata. A null scope pointer selects an invalid empty scope, never the legacy interface. Both old recorded exports now require effective scope. All scope/shape/physical-time checks happen before parameter/state parsing or constitutive evaluation. Early errors keep the existing plain failure envelope.

Native CLI `--mode recorded --recorded-stress-scope effective` or `total` selects response api_version `experimental-recorded-replay-0.2`. Omitting the scope option retains0.1. The option is confined to recorded mode. Unknown/empty/mismatched values reject. Version0.2 adds the same closed compression-positive Mandel state sigma/Cauchy stress descriptor as the laboratory interface. Recorded state/strain projections do not reconstruct pore pressure; no pore law or drainage meaning is added.

Wire coefficients, absolute targets, acquired order, history initialization, numerical settings, controller/restart arithmetic, diagnostics, failure prefixes and serialization precision are unchanged. The shared incremental stress guard now names its caller in errors; laboratory error text remains the same through its default context.

## Frozen verification

[freeze.json](freeze.json), the exact [gate](gate.py), [case plan](cases.json) and source/generated pins precede observations. One explicit `atlas_recorded_scope_gate` target was built serially with `--parallel 1`. It contains the current CLI, exact archived pre-change CLI and a direct C API driver. All use the same private ten-record catalogue: nine unchanged public definitions plus the restricted synthetic total-elastic transport fixture from the laboratory gate. Its test-only lowering does not enable a production profile or supply Tresca/scientific validation.

All46process calls pass:

- Nine current public-model zero-increment cases: old/new legacy responses are byte-identical, and scoped effective responses have exactly the same decoded mechanics/settings/diagnostics after removing only the stress descriptor and replacing the API version.
- Nonzero mixed-control elastic reversal: exact old/new effective legacy and scoped response equality.
- Four synthetic total-elastic histories: all-strain reversal with retained hold under absent/zero/one restart policies, plus mixed fixed-radial-stress reversal. Independent closed-form stress/strain gates pass; maximum stress error is0Pa under the frozen0.002Pa limit. This is a synthetic transport/reference check, not general equivalence or material admission.
- A one-material-trial budget produces the frozen third-knot failure with two committed points. Old/new legacy and scoped prefixes match exactly with zero and one allowed restart; full state/strain and counters are retained. These pure-strain cases do not exercise an accepted restart search; original restart research evidence remains separate.
- Legacy total, both mismatch directions, unknown and empty scope reject despite malformed parameters/state. The direct C driver exercises both old exports, both new exports, missing/wrong scope, and scoped success with/without explicit restarts.

[Raw process receipts](observations/summary.json), binary hashes and configure/build output are retained. The core solver/recorded/restart headers did not change. The exact previous main.cpp and previous request-status document are preserved through [previous-sources.json](previous-sources.json). No acceptance gate was relaxed and no author code or binary was executed.

## Saved-only checks

```sh
python3 -B docs/reviews/recorded-scope-native-v1/gate.py
python3 -B -m unittest tests.test_recorded_scope_native tests.test_recorded_scope tests.test_recorded_api.RecordedRunContractTests tests.test_laboratory_scope_contract -v
```

Fourteen focused tests pass. Saved replay runs with subprocess execution denied. Seven copied corruptions reject: changed scope, response version, wire, process exit, retained state, restart policy and missing receipt. Captured commands also match their declared scope and restart selection. These checks use no binary or new material process; the gate's `native_calls:0` describes saved replay, not the original46-call exercise.

To reproduce native observations, use prepare.py with a fresh private destination, configure its CMake project, build only `atlas_recorded_scope_gate --parallel 1`, then run exercise.py against that stage. Preparation freezes the complete case plan, source files and generated inputs before compilation. Existing evidence is never overwritten and all process calls use bounded timeouts.

## Stop and next dependency

Next connect dedicated scope-aware Python/JavaScript execution adapters to these endpoints. Require validated model/scope identity before execution and exact returned version/stress/catalogue/request/settings/restart identity afterward; prohibit fallback to legacy calls. Browser scope labels, CSV/JSON import/export and source/reference/backend gates remain separate before total-profile activation and installation of the existing Tresca transcription. No Wasm build, browser rollout, push, deployment or scientific promotion occurs here.
