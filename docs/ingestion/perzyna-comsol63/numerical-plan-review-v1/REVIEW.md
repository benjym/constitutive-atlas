# Independent prospective numerical-plan review v1

**Decision: CORRECTIONS REQUIRED. Do not execute Perzyna material calls against this v1 freeze as an accepted plan.**

Task REVIEW-perzyna-numerical-plan-v1; reviewer separate agent run `/root/perzyna_source_review`, 2 November 2026. This reviewer previously reviewed the source packet independently of its author, and did not author or modify execution-v1. The owned output is only this new numerical-plan-review-v1 directory. This is prospective numerical-policy review, not E5 model approval.

Reviewed freeze SHA-256: `48455810b86348658266e0f16459c9ddd96df8af1b763630b54c30bfef929817`. All 168 source-relative pins and 1935 external tool/cache pins match. The source candidate remains `7bfc33578593fab8c806dd1cd6473f54b9e2cd5cbf07ecacaffd328118e103ac`. This review's MANIFEST.json binds the exact freeze, all of its transitive file pins, the separately proposed actual-build inspector and the review outputs. No compiled observation occurred in this run.

## Blocking finding NP-PERZ-01: solved creep rate is unqualified

`study.assess` requires each solved stress-controlled `strain_rate` component to be finite but places no source-derived accuracy bound on its value. `synthetic_checks.manufacture` consequently uses zero for the solved creep rate at every non-entry point and still passes. A stress-hold entry's null rate is intentional and appropriate for the state-only stress binding; this finding concerns the later solved, numeric rates.

At constant total stress, isotropic elastic strain is constant. Thus total strain rate equals permanent strain rate, and the selected printed law gives

`D = 1.5 * A * max(q/Y - 1, 0)^n * s/q`, with zero at inactive/hydrostatic stress.

The public-creep fixture's first component should be approximately `0.008836853357244831 s^-1`, accompanied by the other source-derived tensor components in CHECKS.json. I independently manufactured all 107 fixture rows with correct creep solved rates, and the v1 assessor accepted them. I then replaced **all six solved rates at every public-creep sample** with alternating `+1e20` and `-1e20 s^-1`, leaving state, strain, stress, clock, topology, controls, requests and both repeated raw outputs unchanged. The assessor still returns `passed: true` for the complete 107-case fixture.

Both backends could report the same wrong rates and pass parity, since parity tests agreement rather than independent accuracy. Complete physical output is therefore not qualified by the current gate. This is a gate/reference omission, not evidence that the generic engine actually reports wrong rates. It must be repaired prospectively before observation, with a distinct immutable execution revision, source-derived stress-hold rate references and explicit bounds, correctly manufactured positive fixtures and negative mutations for the solved rate. Retain v1 unchanged, including this rejection.

Reproduction: `python3 -B /private/tmp/atlas-perzyna-delivery-v1/docs/ingestion/perzyna-comsol63/numerical-plan-review-v1/reproduce.py`. It imports only the assessor functions; it does not run author prepare/check scripts, a compiler, material executable, Wasm module or browser. It writes only this review's CHECKS.json. Its two calls to `assess` are synthetic result checks, not material calls.

## Other inspected policy elements

The 107 unique ordered cases cover the described six Mandel directions, radial holds, signed creep, three public modes, hydrostatic loading, selected noncoaxial reversals/holds, custom coefficients, nonzero memory, passive rotations, refinement, actual-parent restart, invalid inputs, late failure and recovery. They do not establish coverage of the full guarded parameter interval, arbitrary loading histories, general mixed controls, finite rotation, FE tangents or vendor binary conformance. In particular material execution at n=8 is not in this case set; the source's regular exponent guard is not a whole-interval numerical qualification claim.

Closed-form hold and constant-stress creep state references agree with the source derivations already independently accepted in source-contract-review-v1. I read the stress-space RK4 oracle and the prepare path: it integrates stress plus alpha and reconstructs permanent strain by elastic compliance, distinct from production 13-state BE integration. All 26 saved low8192/high16384 convergence entries meet the predeclared state `5e-11` and stress `0.005 Pa` gates; maxima are approximately `1.07538e-13` and `1.88656e-6 Pa`. I audited those saved entries and generation equations but did not recompute the grids in this rejected-plan review. A later acceptance review should finish reference reproduction against the new exact freeze.

The state/stress gates, maximum-step cap and strict fivefold coarse/fine improvement are frozen before observations and are meaningfully stronger than backend parity. They are not a promise that this plan will pass. The serialized requests, complete state/stress shapes, exact model/catalogue identity, clock/topology/segment sides, repeats, initialization, prescribed strain rates, monotone alpha, trace-free permanent memory and late-failure retained committed sample receive real checks. The 25 retained author mutations are useful assessor checks and correctly labeled synthetic only; they did not cover NP-PERZ-01. The dynamic restart takes the actual parent state, strain, rate and clock rather than substituting the analytical parent. That is a defensible transaction test, limited to the shown context/protocol.

`parity.py` compares physical output at its explicit scaled `2e-10` budget and excludes enumerated solver diagnostics. Agreement remains separate from accuracy. Native new-process collection versus one persistent Wasm instance is explicitly disclosed; recovery in the persistent instance has useful scope. No process-persistence equivalence beyond this is implied.

The `run_operation.py` pre/post checks genuinely hash the frozen source/tool sets and retain log hashes and return codes. The environment subset is deliberately limited to build-relevant fields. These checks are integrity evidence, not a hermetic OS/SDK image, proof of the binary's compilation, or success merely because an operation was logged. The stop/failure policy must continue to retain actual failed rows/logs and never reinterpret a material failure as a passing mutation fixture.

## Actual build-proof mechanism

At the coordinator's request I also inspected unchanged `tools/record_cmake_profile_build_v2.py`, separately bound here because it is not in execution-v1/FREEZE.json. Its proposed use is defensible as **pre/post integrity and build-record dependency evidence**, explicitly not binary attestation or numerical approval. It executes no compiler or material code. Its snapshot hashes actual CMake/cache/compiler/generator/flags/link records, ordered compile commands, scalar archive/object membership, object depfiles and resolved dependency identities, tool paths, generated model metadata and artifacts. It checks the generated catalogue against exact model inputs, the generated-header catalogue binding, actual versioned schedule header selection with exclusion of the legacy header, ordered include roots, the scalar rounding flag and archive bytes, and later verifies that the same closure is unchanged. It also retains build-local evidence copies.

Use the exact proposed `--entrypoint cpp/main.cpp`, `--models models/research/perzyna`, `--recipe cmake/perzyna/CMakeLists.txt`, `--schedule required` and explicit native/Wasm target/artifact identities. Capture before material calls and verify afterward, with exact collector/assessor consumers included. The actual normally generated metadata must additionally equal the frozen expected-catalogue.json before calls, and actual compiler paths/flags/object dependencies must be retained. The freeze source/tool checks and actual-build proof are complementary: neither should replace the other. Since no build was authorized for this reviewer, I did not generate or accept an actual build receipt.

## Required next action and cleanup

Create a distinct execution-v2, repair NP-PERZ-01 without loosening existing state/stress/refinement/parity gates, freeze the new references/helpers/mutation evidence before compiled observations, and request independent review of those exact new bytes. This v1 decision remains CORRECTIONS REQUIRED even after a later revision is accepted.

No author packet, frozen file, shared source, board or Git state was changed. No download, build, preview process, worktree or disposable scratch was created. Retained outputs are REVIEW.md, reproduce.py, CHECKS.json and MANIFEST.json. All input originals and historical failures remain in place. The coordinator owns durable retention of temporary-worktree sources/tools/evidence and subsequent cleanup.
