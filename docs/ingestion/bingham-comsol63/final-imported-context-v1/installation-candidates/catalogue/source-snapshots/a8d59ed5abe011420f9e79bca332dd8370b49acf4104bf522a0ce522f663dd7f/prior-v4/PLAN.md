# Bingham qualification v4 — same requests, generic predictor runtime

This prospective study follows retained v1 direct-midpoint failures, v2 BE crossing failures and v3 capped-BE pure-shear nonlinear rejections. It does not relabel any old result as passing or pre-observation evidence. The sole new executable hypothesis is the separately reviewed generic admissible forward-Euler Newton initial guess in controlled BE. The continuous model, domains, parameter values, incoming states, loading histories, clock, numerical settings, references, gates, repeats and API remain unchanged. No v4 compiled/material call has been made by this source worker.

The exact generic prerequisite is `docs/investigations/schedule-predictor-v1/FREEZE-v3.json`, SHA256 `23df49f9226d15637e83f47a4df1b3c828b0b2b0fffd389542ead0ca80fcc5af`. It supersedes the parent generic v2 freeze only to add unchanged regression dependencies (including `models/linear-elastic.json`) and tool bindings; no CPP, fixture, test or setting changed. The earlier source-only preparation check against generic v2 is retained as `preparation-check-draft-generic-v2.json`. Final preparation/checks and this study freeze bind generic v3. Actual future review, tool execution, build, binary and result receipts must be separate; their hashes are not invented, predicted or repinned here.

## Exact lineage and runtime scope

`cases.json` is a **byte-for-byte copy** of old `/private/tmp/atlas-bingham-delivery-v1/docs/ingestion/bingham-comsol63/execution-v3/cases.json`, including its internal historical v3 identity label. All136complete records and IDs/order are unchanged. `study.py`, `collect_wasm.mjs`, `parity.py`, `oracle.py`, `synthetic_checks.py`, `expected-catalogue.json` and `reference-convergence.json` are also byte-for-byte copies. Their historical labels remain intentional; the new PLAN/freeze/source bindings identify v4. No numerical helper or assessor logic is changed.

Local imports in native collection/assessment/synthetic tests use this packet's copied oracle and the current root package. The collectors' execution paths need no external v1/v2/v3 directory. The copied `study.py prepare` action still reads execution-v1 and regenerates uncapped v2-style cases: **do not run it**. `PLAN.py` is the only v4 preparer/checker. It refuses overwrite when preparing/freezing, asserts exact case/helper bytes, verifies every generic-freeze pin and validates the old source closure against the current tree with explicit permitted deltas.

The old model/source packet was restored by the coordinator; this packet verifies its content hashes rather than inferring an unverified historical commit. `prior-v3-source-bindings.json`, `prior-v3-freeze-v1.json` and `prior-v3-PLAN.md` are exact archival input copies retaining the original provenance. The current and old108source-file closures are both recorded. The only changed existing source/build files relative to the old study are `cpp/include/atlas/schedule.hpp` and root `CMakeLists.txt`. The separate generic task additionally installs `tests/test_schedule_predictor.cpp`, three v0.3 test fixtures and its prospective documentation/source-plan records. Every added input and old/new hash is listed; unchanged old source files must match exactly. The complete closure is the union of the old Bingham source pins and final generic freeze pins, not merely the two changed files.

The generic predictor changes only the initial Newton guess, retaining the old guess if RHS/predictor/endpoint validation fails. It does not alter generated equations, model domains, Newton residual, derivative or acceptance, line search, adaptive estimator, transactions or schedule settings. Generic synthetic root/fallback tests do not establish Bingham continuous-history accuracy or guarantee convergence. In particular the discrete-root boundary fixture does not solve the known step-estimator blindspot; the unchanged Bingham cap and physical gates remain mandatory.

## Unchanged numerical protocol

The complete previous protocol is copied as `prior-v3-PLAN.md`. All108analytical radial cases, hydrostatic/zero histories, three covariance cases, public relaxation/creep/rate histories, noncoaxial history, coarse/fine refinement, actual-parent full13state restart and clock, late-budget last-committed-sample retention, seven invalids, every recovery and two exact repeats remain. All6stress and13state channels, topology/context/domain/finite/trace/monotonicα/rate assertions remain.

Every request retains maximum_step `min(its previous pre-v3 cap,0.0004069010416666667s)`, including coarse/fine, public cases, late-budget and invalid/recovery requests. Fine settings remain relative tolerance1e−9, absolute scale fraction1e−12, minimum step1e−12s, budget1,000,000accepted halfsteps, nonlinear tolerance1e−10,40iterations and depth40. Original coarse diagnostic settings remain unchanged. The source-derived event bound motivates this cap only; it is not a global accuracy guarantee, unrestricted public-parameter policy or noncoaxial/control theorem.

For each fine state/history component, error≤max(3e−7,2e−5|reference|); for each stress component error≤max(3Pa,2e−5|reference|). Coarse-only floors remain0.001state/1000Pa. Fine maximum state **and** stress errors must each be strictly smaller than coarse error/5. No solver-rejection output may be mistaken for a successful final-state error, and no failure permits gate relaxation or reference changes. Physical native/Wasm parity remains the original2e−10scaled comparison and original diagnostic exclusions.

Actual-state restart is re-encoded from the actual successful parent's13state, total strain, rate and time, and compared to the original independent analytical continuation from that parent. Late-budget retains the1e−6s committed first segment, budget2 and final recovery. Failure returns retained committed samples under the existing schedule contract; the assessor does not fabricate an additional constitutive trial after the budget is zero. Native requests run twice; the Wasm collector runs all272calls, including failures and recoveries, in one persistent engine.

## Source-only checks and later coordinator execution

`preparation-check.json` and `lineage-check.json` assert all136case bytes and helper bytes are identical and record the permitted runtime deltas. The unchanged synthetic suite accepts136manufactured ideal records and rejects25negative mutations. Those synthetic passes test the assessor only, not the material. Source/model/generic dependency hashes are verified before freeze; future artifacts must be attached in distinct coordinator receipts.

Recheck without any compiled call:

```sh
python3 -B docs/ingestion/bingham-comsol63/execution-v4/PLAN.py check
```

The coordinator must obtain separate exact prospective review of this study and the generic prerequisite, complete the generic frozen regressions, and bind the actual serial build/artifacts before new Bingham calls. Then run the unchanged collectors/assessor:

```sh
python3 -B docs/ingestion/bingham-comsol63/execution-v4/study.py native --solver /ABS/atlas_bingham_solver --raw docs/ingestion/bingham-comsol63/execution-v4/native-attempt1.json
node docs/ingestion/bingham-comsol63/execution-v4/collect_wasm.mjs /ABS/bingham.js docs/ingestion/bingham-comsol63/execution-v4/cases.json docs/ingestion/bingham-comsol63/execution-v4/wasm-attempt1.json
python3 -B docs/ingestion/bingham-comsol63/execution-v4/study.py assess --raw docs/ingestion/bingham-comsol63/execution-v4/wasm-attempt1.json
python3 -B docs/ingestion/bingham-comsol63/execution-v4/parity.py docs/ingestion/bingham-comsol63/execution-v4/native-attempt1.json docs/ingestion/bingham-comsol63/execution-v4/wasm-attempt1.json
```

Native/Wasm builds remain coordinator-owned, serial one explicit target with `--parallel 1`. Retain partial output, timeouts, failures, raw repeats and all old v1/v2/v3 evidence unchanged. A pass would support this exact bounded runtime study; it would not constitute experiments, broad-range numerical qualification, browser qualification, approval or live delivery.
