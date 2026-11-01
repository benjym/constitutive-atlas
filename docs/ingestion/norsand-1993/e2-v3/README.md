# NorSand 1993 — controlled path capability and numerical handoff

Lead `/root`, 2026-11-01; child `CAP-norsand-mixed-control-contract-v1`. This continues the accepted [original source packet](../supplied-original-v2/README.md) without rewriting it. E2 remains open: the new generic profile is staged, not installed in the shared schema/compiler or atlas. Native and Wasm now pass the same58frozen requests; see the separately accepted [compiled review](independent-review/COMPILED_REVIEW_V7.md).

## Implemented scope

[Contract](CONTRACT.md): dimensionless, monotonic `path_ode` with arbitrary persistent scalar/Mandel state, declared linearly interpolated controls and derivative channels, explicit scoped stress observable, complete initialization, retained control context, coordinate-offset preservation, exact zero-progress identity and whole-parent rollback. NorSand is a declarative [candidate](proposed-v3/candidate.json), with original Eqs5–12 and current-image state; it receives no model-specific runtime kernel, fictitious physical clock, elasticity or unsupported strain input.

[Reviewed v3 proposal](proposed-v3/) contains the semantic/schema extension, generic interpreter, C++ expression generator, checked C ABI and adaptive explicit-midpoint transaction runtime. [Full backend source snapshot](backend-proposal-v6/) also retains common compiler/DSL/tensor dependencies, explicit control-order metadata, checked-helper include coverage and Wasm exception support. It generates candidate plus analytical scalar/tensor fixtures through the normal compiler entry point in a separate explicit catalogue partition. Existing public model generation is [byte-identical for all13models](legacy-generation-results.json).

## Evidence and limits

- [Generic interpreter](generic-interpreter-results-v3.json):29 analytical, input/domain, restart, rollback and recovery checks pass.
- [Original-equation references](references-v2.json):9Latin-square cases, each N=0,.2,.39 and initial state parameter−.16,0,+.075; constant cell, constant mean or changing controls. Decimal RK4 evolves image pressure directly and solves original Eq7 plus mixed control at each stage, independently of the candidate eta derivative. Shear progress .16,4096/8192steps,50/75digits. Maximum refinement1.93137e−11 < frozen2e−8; maximum precision difference1.84653e−48 <1e−35. These are endpoint numerical references, not experimental curves.
- [Interpreter qualification](interpreter-qualification-v1.json):all9cases pass. Largest normalized source error2.72694e−7 <2e−6; current-volume invariant error2.13502e−9 <2e−8; split/restart state difference0. Each case also passes5rejections, zero-progress identity, exact parent preservation and recovery. [Execution bindings](executed-stage-bindings-v3.json) identify actual staged bytes/Python platform; earlier immutable proposals and freezes remain retained.
- [Independent review](independent-review/README.md) and [compiled follow-up](independent-review/COMPILED_REVIEW_V7.md):source reduction, static runtime, independent references, interpreter and exact native/Wasm capability accepted in bounded scopes. No E5 approval.
- [Backend request freeze](backend-source-request-freeze-v6.json):119source/request/evidence bindings; [58requests](backend-requests-v2.json), including9half paths,9actual-backend-state chained restarts,9cold restarts, zero identity, rejection→recovery, scalar/tensor analytical fixtures and invalid/domain/budget cases. Native and Wasm use the same flat C ABI and requests; outputs commit only on success. [Artifact checker](check_backend_results_v3.py) enforces exact lengths, finite values, statuses, failed-call sentinels and unchanged gates. [8checker-only selftests](result-checker-tests-v3.json) pass; these synthetic artifacts are explicitly not backend evidence.

[Actual backend qualification](backend-qualification-v2.json):58requests per backend,40successes/18expected rejections each; full native/Wasm result rows exactly equal, material/interpreter error0 against frozen2e−11. Curved analytical fixture error3.27452e−8 <2e−7. Native preceded Wasm, each explicit target --parallel1. Retained exact [native artifact](native-v1/) and [Wasm module/binary](wasm-v2/) are hash-bound. The original installed-cache permission failure and missing HEAPF64 export failure remain retained; repair only uses an isolated writable cache and explicit Wasm export, with unchanged source equations/runtime/requests/gates. [Toolchain](toolchain-execution-freeze-v2.json) identifies AppleClang21, Emscripten6.0.8 and Node26.7.0.

The historical v1/v2/v3 proposals, short-path reference and exact reviewed bytes remain available. Identifier-shadowing findings were corrected prospectively; no numerical acceptance gate was relaxed. The generic profile remains unsupported in the shared catalogue, and official E2 shared-profile installation, full-model qualification/CI registration, E5 admission, main-atlas/browser integration and live delivery remain pending. No source PDF is redistributed.

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

`NUM-norsand-path-capability-v1` completed bounded native/Wasm qualification and its serial slot is released. The separate reviewer accepted exact artifacts and all58requests/backend; the coordinator verified580source/review/artifact hash bindings. Preserve all originals and both retained packaging failures.

`INT-controlled-path-profile-v1` is the next shared capability task. The current assignment whitelist covers staged sources; shared schema/compiler ownership must be handed off explicitly before installing this fourth profile. Integrate the reviewed generic changes additively into current shared bytes, archive every affected pinned source first, and preserve all other agents’ dirty edits. Do not replace shared compiler/model files with entire staged copies. The separate profile partitions legacy full-strain/time models from declared controlled-path catalogues; public model generation must remain identical. Include durable generic native/Wasm regressions and catalogue/runtime metadata.

Then install the exact NorSand research candidate, its source crosswalk and a qualified named example; obtain separate nine-item E5 approval; integrate into the main atlas with dimensionless progress, declared stress controls and all persistent state/export/failure recovery. Current sources do not implement this shared/browser route. Actual packaged browser and live delivery remain separate gates. No push/deployment/remote CI was performed or authorized.
