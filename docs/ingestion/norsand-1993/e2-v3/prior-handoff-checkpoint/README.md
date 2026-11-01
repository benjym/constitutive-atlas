# NorSand 1993 — controlled path capability and numerical handoff

Lead `/root`, 2026-11-01; child `CAP-norsand-mixed-control-contract-v1`. This continues the accepted [original source packet](../supplied-original-v2/README.md) without rewriting it. E2 remains open: the new generic profile is staged, not installed in the shared schema/compiler or atlas. No native/Wasm build or compiled material call occurred.

## Implemented scope

[Contract](CONTRACT.md): dimensionless, monotonic `path_ode` with arbitrary persistent scalar/Mandel state, declared linearly interpolated controls and derivative channels, explicit scoped stress observable, complete initialization, retained control context, coordinate-offset preservation, exact zero-progress identity and whole-parent rollback. NorSand is a declarative [candidate](proposed-v3/candidate.json), with original Eqs5–12 and current-image state; it receives no model-specific runtime kernel, fictitious physical clock, elasticity or unsupported strain input.

[Reviewed v3 proposal](proposed-v3/) contains the semantic/schema extension, generic interpreter, C++ expression generator, checked C ABI and adaptive explicit-midpoint transaction runtime. [Full backend source snapshot](backend-proposal-v5/) also retains common compiler/DSL/tensor dependencies, explicit control-order metadata, checked-helper include coverage and Wasm exception support. It generates candidate plus analytical scalar/tensor fixtures through the normal compiler entry point in a separate explicit catalogue partition. Existing public model generation is [byte-identical for all13models](legacy-generation-results.json).

## Evidence and limits

- [Generic interpreter](generic-interpreter-results-v3.json):29 analytical, input/domain, restart, rollback and recovery checks pass.
- [Original-equation references](references-v2.json):9Latin-square cases, each N=0,.2,.39 and initial state parameter−.16,0,+.075; constant cell, constant mean or changing controls. Decimal RK4 evolves image pressure directly and solves original Eq7 plus mixed control at each stage, independently of the candidate eta derivative. Shear progress .16,4096/8192steps,50/75digits. Maximum refinement1.93137e−11 < frozen2e−8; maximum precision difference1.84653e−48 <1e−35. These are endpoint numerical references, not experimental curves.
- [Interpreter qualification](interpreter-qualification-v1.json):all9cases pass. Largest normalized source error2.72694e−7 <2e−6; current-volume invariant error2.13502e−9 <2e−8; split/restart state difference0. Each case also passes5rejections, zero-progress identity, exact parent preservation and recovery. [Execution bindings](executed-stage-bindings-v3.json) identify actual staged bytes/Python platform; earlier immutable proposals and freezes remain retained.
- [Independent review](independent-review/README.md):source reduction, static runtime and independent reference adequacy reviewed separately; final scoped numerical/request review records exact hashes. No E5 approval.
- [Backend request freeze](backend-source-request-freeze-v6.json):119source/request/evidence bindings; [58requests](backend-requests-v2.json), including9half paths,9actual-backend-state chained restarts,9cold restarts, zero identity, rejection→recovery, scalar/tensor analytical fixtures and invalid/domain/budget cases. Native and Wasm use the same flat C ABI and requests; outputs commit only on success. [Artifact checker](check_backend_results_v3.py) enforces exact lengths, finite values, statuses, failed-call sentinels and unchanged gates. [8checker-only selftests](result-checker-tests-v3.json) pass; these synthetic artifacts are explicitly not backend evidence.

The historical v1/v2/v3 proposals, short-path reference and exact reviewed bytes remain available. Identifier-shadowing findings were corrected prospectively; no numerical acceptance gate was relaxed. The generic profile remains unsupported in the shared catalogue, and official E2/E3 closure, actual native/Wasm qualification, E5 admission, main-atlas/browser integration and live delivery remain pending. No source PDF is redistributed.

## Reproduction

Read-only evidence verification from repository root:

```sh
python3 -B docs/ingestion/norsand-1993/e2-v3/check_packet.py
python3 -B docs/ingestion/norsand-1993/e2-v3/test_result_checker_v3.py
```

Reproduce interpreter evidence in the explicitly owned temporary stage:

```sh
python3 -B docs/ingestion/norsand-1993/e2-v3/restore_stage.py
python3 -B docs/ingestion/norsand-1993/e2-v3/test_staged_profile_v3.py
python3 -B docs/ingestion/norsand-1993/e2-v3/qualify_interpreter.py
```

Reference replay uses `build_references_v2.py` (approximately3minutes on the recorded host). Replay into a distinct evidence destination if retaining different runtime timing; do not overwrite frozen reference bytes. The source PDF is unnecessary for these public algebra/numerical reproductions.

## Next handoff

`NUM-norsand-path-capability-v1` is queued behind the explicitly claimed `NUM-newton-endpoint-constraints-v1` serial build slot. Do not infer release from an idle compiler process. After its recorded release, record toolchain paths/versions/environment and the exact source/request freeze before configuration. Build only `atlas_path_capability`, native first and then Wasm, each `--parallel 1`, with isolated temporary build directories. Inspect and retain native results/failures before any Wasm build. Run `run_native_requests_v2.py` and `run_wasm_requests_v2.mjs` against the same frozen58requests, then `check_backend_results_v3.py` against each and both result artifacts. Preserve failures and exact binaries/toolchain receipts.

The new profile needs a distinct exact-byte-preserving shared-schema/compiler integration handoff from its current owner. A successful isolated capability study does not itself install or approve the model. Main-atlas controls and actual packaged/live browser qualification remain separate gates; remote push/deployment is not authorized in this assignment.
