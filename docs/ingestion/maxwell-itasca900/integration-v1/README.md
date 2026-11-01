# Maxwell continuous law — runnable timed research model

Task: IMPL-maxwell-timed-v1. Integration owner: coordinating parent, 2026-11-01.

The [exact v0.3 Maxwell draft](../../../../models/research/maxwell/maxwell-itasca900-zero-spin-ode.json) now runs through the ordinary Atlas compiler, native timed solver and Wasm APIs. [Four ready-to-run examples and commands](../../../../examples/maxwell/README.md) cover relaxation, stress-controlled creep, constrained oedometer creep and full-tensor load/hold/reverse. The dedicated [CMake target](../../../../cmake/maxwell/CMakeLists.txt) keeps it separate from the existing public and research catalogues. No handwritten Maxwell kernel or shared solver/schema change was necessary. The copied model is byte-identical to the original ingestion candidate, including draft status.

## What is qualified

Dry, total-stress, fixed-frame, infinitesimal-strain continuous Maxwell response; elastic volumetric behavior and viscous deviatoric behavior, tau=eta/G. Source interpretations and caveats are retained in the [original source packet](../README.md). Scientific status remains an unreviewed draft. This is a common-engine integration of the continuous law, with project timesteppers; it does not claim vendor central-difference equivalence, finite-rotation objectivity, saturation, experimental calibration or an existing browser timed-control UI.

## Prospective policy and execution

[PLAN.md](PLAN.md), [reference-cases.json](reference-cases.json) and the [92-file input freeze](execution-freeze.json) precede compiled Maxwell observations. [Source closure](source-closure.tar.gz) preserves all original compiler/schema/header/build/model/reference inputs for future reproduction; its contents use original repository-relative paths. No copyrighted manual pages are inside this archive. Source HTML remains private under the paths in the ingestion receipt. The original ingestion manifest and all execution-freeze inputs were rechecked unchanged after qualification.

Native then Wasm builds used one explicit `atlas_maxwell_solver` target and `--parallel 1`, with no overlapping builds in this task. Native is AppleClang21; Wasm is Emscripten6.0.8. Commands and status are in the native/wasm build receipts and logs. The first Wasm link failed because the installed Emscripten cache was not writable; that failure is retained. A second link using a private copied `EM_CACHE` succeeded, with the same model/engine/source objects. System permissions and endpoint protection were not changed.

## Results

- **24 frozen cases, twice per backend**: 11 direct constant-rate/hold paths; seven schedule paths including coarse/fine refinement; six invalid-input/budget failures. All source accuracy, control, complete-state rollback and exact same-backend replay checks pass. Direct full-tensor paths span tau=0.2,2,20s and duration/tau=0.01,0.5,4. The hydrostatic and relaxation direct paths add separate volume/hold checks.
- **Six rejection/recovery pairs and two actual endpoint restarts per backend**, twice each: 28 supplementary calls per backend. Wasm recovery pairs share one module. Direct budget failure restores all incoming stress/time after nonzero internal work; scheduled failure retains its last committed point. Complete saved stress/strain/rate/time is used for creep and relaxation restart. Native JSON CLI creep replay is exactly equal, and untimed integration correctly rejects the model.
- **Accuracy:** maximum fine direct stress error 0.0238843Pa against 0.05Pa; maximum fine scheduled stress error 1.37521Pa against 15Pa. Strain gates are 2e-7. The fixed coarse/fine relaxation errors decrease from 138.381Pa to 1.36072Pa. All requested output times, boundary states, stresses and strain fields are checked against independent analytical references. No source accuracy limit was widened.
- **Parity:** the corrected physical-field assessor passes 5,962 numeric comparisons, including input/output physical restart fields. Maximum stress difference is 4.65662e-10Pa against 1e-6Pa; maximum strain/rate difference is 1.08421e-18 against 1e-11. Identities, time, null slots and control metadata agree; diagnostics satisfy their original independent bounds.
- **Usability/regression:** all four examples pass through `python3 -m atlas.cli run`. Nine focused Python contract/reference/assessor tests pass. Five above-budget corruption fixtures reject and three within-budget fixtures accept under the corrected field classification.

[Native raw responses](native-raw.json), [Wasm raw responses](wasm-raw.json), assessment logs, endpoint-derived transaction requests/raw responses/reports, [CLI creep result](cli-creep-result.json), [example results](example-results.json), [Python log](python-tests.log) and [parity result v2](parity-results-v2.json) are retained. Main and transaction collectors each make two calls per case, totaling **76 calls per backend** before separate CLI usability runs. Backend agreement is additional to independent analytical checks.

## Retained failures and limits

The [preparation failure](preparation-failures.json) was a self-test parameter fixture mismatch corrected before execution freeze. Native compilation reports one unused generated argument warning; it does not prevent execution. The first Wasm cache permission failure remains in `wasm-build.log`/receipt; successful follow-up is separately identified as attempt2.

The [original parity assessor failure](parity-v1-failure.json) is retained, along with its exact source and freeze. It classified endpoint-derived `initial_strain_rate` as exact metadata and rejected a difference of roughly 5e-20/s. [Assessor v2](compare_backends_v2.py) assigns physical initial stress/strain/rate fields their **original** 1e-6Pa/1e-11 physical limits; no model, backend result, reference or tolerance was changed. Classification corruption checks are separately recorded. The failed v1 assessment has not been relabeled as a pass.

This finite suite qualifies its explicit example parameters/loading envelope. The broad model parameter bounds are not fully qualified. There is no new experimental validation or independent scientific signature. Source index-typo interpretation, original Jaeger and vendor host reconciliation remain open. Temporary binaries and tool caches may be removed by the OS; rebuilding from the checked-in target or saved source closure is the durable route.

## Reproduction

See the [run guide](../../../../examples/maxwell/README.md) for ordinary builds/examples. The already qualified binaries are at `/private/tmp/atlas-maxwell-execution-v1/native/atlas_maxwell_solver` and `/private/tmp/atlas-maxwell-execution-v1/wasm/maxwell.js` plus `.wasm`; artifact hashes are in [manifest.json](manifest.json).

```sh
python3 tests/test_maxwell.py --solver /private/tmp/atlas-maxwell-execution-v1/native/atlas_maxwell_solver --output /private/tmp/maxwell-check.json
python3 -m unittest tests.test_maxwell tests.test_time.TemporalLanguageTests tests.test_schedule.ScheduleContractTests -v
node tools/test_maxwell_wasm.mjs /private/tmp/atlas-maxwell-execution-v1/wasm/maxwell.js docs/ingestion/maxwell-itasca900/integration-v1/reference-cases.json /private/tmp/maxwell-wasm-check.json
python3 tests/test_maxwell.py --assess /private/tmp/maxwell-wasm-check.json
```

The transaction scripts record outputs beside themselves; copy the evidence directory before rerunning them if preserving its exact receipt identity is required. Do not run `--freeze` over an existing reference file. Original hashes, failures and reports remain historical evidence. Nothing was committed, pushed, deployed or promoted into the public browser catalogue by this task.
