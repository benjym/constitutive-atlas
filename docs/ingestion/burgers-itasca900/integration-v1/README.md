# Burgers physical-time integration v1

Task: IMPL-burgers-timed-v1. Coordinating parent, 1 November2026. **Integrated locally as a draft**, through a dedicated catalogue and the unchanged common physical-time engine. No scientific admission or experimental validation is claimed.

## Installed result

- `models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json`: exact bytes of the source packet's v0.3 continuous-law draft; twelve persistent scalar slots (Mandel stress and Kelvin strain), dry total stress, infinitesimal fixed-frame zero-spin scope.
- `CMakeLists.txt`: additive, opt-in `atlas_burgers_solver` target with dedicated generation. Native executable: `atlas_burgers_solver`; Wasm: `burgers.mjs` and `burgers.wasm`. No constitutive kernel, schema, compiler or generic solver change.
- [Timed-use guide](../../../BURGERS_TIMED.md), four [explicit examples](../../../../examples/burgers/) and [regression tests](../../../../tests/test_burgers.py).

The model remains outside the twelve-model strain-path/browser catalogue. Its physical-time contract cannot be routed through a duration-free laboratory update. The current browser has no timed-history UI; direct timed native/C/Wasm APIs and the existing Python schedule CLI are the supported route. Integration does not mean that this model is deployed or scientifically reviewed.

The original [source packet](../README.md), pinned draft and historical failed source checks are unchanged. Its statement that no root model was installed describes the earlier ingestion checkpoint; this separately identified task installs the dedicated research model.

## Prospective scope and references

[Freeze](freeze.json) pins the exact model, requests, acceptance policy, analytical reference program, collector/assessor and proposed target **before any compiled observations**. [Frozen source archive](frozen-source.tar.gz) retains 440 exact source files, with the complete [hash inventory](source-files.json). Native and Wasm compiled the same source closure. No private vendor HTML, PDFs, author binaries or compiled artifacts are bundled.

[References](references.json) use closed-form component solutions derived directly from the source Kelvin/Maxwell series partitions. The prescribed-strain solution shifts a two-exponential linear system by its stationary flowing state. The stress-controlled solution integrates a first-order Kelvin convolution and the Maxwell dashpot exactly. Hydrostatic response is purely elastic. Mixed controls prescribe normal strain and shear stress; those components have no hydrostatic/shear coupling. Inputs are interpreted as exact stored binary64 values. Independent 90/160-digit Decimal evaluations agree within `1e-65 * max(1,abs(reference))` before compilation. No Atlas evaluator or numerical time integrator generates the references.

The eight histories comprise six fine paths—strain relaxation, multisegment load/reverse/hold, stress-controlled creep, mixed control, stress ramp/hold, and hydrostatic load/hold—and two deliberately coarser refinement companions. There are 88 saved analytical schedule points per backend, including segment transitions. All stress, Kelvin-history and accumulated-strain channels are checked at every point.

[Acceptance](acceptance.json) fixes fine schedule budgets of20Pa stress and2e-6 Kelvin/accumulated strain; coarser diagnostic budgets are2000Pa/2e-4. Direct midpoint ODE advances use0.01Pa/1e-9 budgets. Fine relaxation endpoint stress/history error and creep endpoint strain error must improve over their coarse companions. Different adaptive partitions are not required to yield identical restart bits; each restart must satisfy the original analytical budgets. Native/Wasm parity budgets are0.01Pa and1e-9 for strain/rate quantities. None was changed after compiled observations.

## Execution and retained results

One native Release target built serially with `--parallel 1`; its gates passed before the Wasm build. The first Wasm Debug link failed because the installation cache was read-only (`libstubs-debug.a`). [Failure receipt](wasm-build-failure-v1.json) and the original log are retained. Copying the installed cache to writable private temporary storage allowed the same target to link on the second attempt; no law, solver setting, reference or acceptance gate changed. See [receipt](receipt.json) for commands, toolchain versions, artifact hashes and cache location.

Both backends pass **44 calls** each, covering:

- Eight reference histories, deterministic repeated requests and three direct constant-rate ODE advances.
- Complete-history restart from each backend's own stress/Kelvin/strain/rate/time checkpoint.
- Invalid duration/settings, missing state, invalid Kelvin trace, zero viscosity, and rejection by the untimed API.
- Exact ODE state/time rollback after a budget failure with accepted internal work; schedule interval rollback retains only the committed initial/entry transition.
- Recovery in the same Wasm instance after each rejected request; native recovery uses a fresh process, not a persistent-instance claim.
- Observable stress equality to the corresponding state and exact descriptor/model binding.

[Raw native calls](native-calls.json) and [raw Wasm calls](wasm-calls.json) preserve every wire argument and response. The portable verifier reconstructs the complete original request sequence, including response-dependent restart arguments, before reassessing. [Assessment](assessment.json) passes all frozen gates. Across6,168 physical parity comparisons, the maximum stress difference is `1.4551915228366852e-11 Pa`; maximum strain/rate difference is `8.673617379884035e-19`.

[Path metrics](path-metrics.json) retain every path's maximum independent error. The six fine schedules have maximum stress error4.32515Pa and maximum Kelvin/accumulated-strain error5.40541e-7. The maximum state budget fraction is0.270271. Fine relaxation and creep errors improve over the deliberately coarser companions. This is bounded numerical qualification for the named inputs, not a universal global-error guarantee, stiffness assessment over all allowed parameters or proof of full vendor-host equivalence.

[Execution logs](execution-logs.tar.gz) retain configure/build/test output, the failed first link and two CLI creep runs; [per-file hashes](execution-log-files.json) allow exact extraction checks. The documented CLI creep example runs successfully and its exported result replays with an exactly equal complete response. Its final `xx` accumulated strain is approximately0.0183903. Collector preparation errors occurred before references/builds and are retained in [their ledger](preparation-failures.json).

## Installation and reproducible checks

Before installation, the current CMake file was archived in `installation-baseline-CMakeLists.txt`; earlier baseline files are retained under `baseline/`. Existing unrelated CMake edits were preserved. The model and target were installed only after native, Wasm and parity gates passed. Current installed compiler, solver and schemas match the qualified source closure. The installed model generates exactly the qualified header and descriptor. Root CMake configures successfully. [Installation checks](installation-checks.json) also establish byte-identical before/after generation of the twelve-model public header/catalogue; no public definitions changed.

```sh
python3 -B docs/ingestion/burgers-itasca900/integration-v1/verify.py
python3 -B -m unittest tests.test_burgers tests.test_time.TemporalLanguageTests -v
python3 -B docs/ingestion/burgers-itasca900/verify.py
```

The eight regression tests pass, including rejection of a corrupted stress trajectory even when its repeat and observable are corrupted consistently. No compiled binary or private source is needed for these saved-evidence checks. The prior ingestion verifier still reproduces515 portable algebra cases and validates its original pinned dependencies.

To regenerate analytical references in a separate review copy, run `reference.py`; to rerun compiled qualification, extract the frozen source archive, configure/build only `atlas_burgers_solver` serially, then run `study.py native ENGINE --output DIR` followed by `study.py wasm MODULE --output DIR`. Preserve a new study identity and every failure; do not overwrite these original calls or loosen their gates. `wasm_host.mjs` is a persistent generic API transport with no material equations.

## Remaining boundaries

Source completeness remains the original bounded manual subsystem: no finite-rotation/history-transport or coupled pore-pressure convention is inferred. The integrated algorithms approximate the continuous ODE; exact reproduction of the vendor centered timed-discrete update remains BUR-CAP-01 and is not necessary to execute the explicitly named continuous-law draft. Calibrated data, parameter-domain stiffness studies, finite-step tangents, browser timed controls and independent scientific signoff remain separate work. There was no push, deployment, source migration or change to model admission status.
