# Independent prospective numerical-plan review v2

**Decision: ACCEPT for the exact prospective numerical qualification plan v2.**

Task REVIEW-perzyna-numerical-plan-v2; independent reviewer run `/root/perzyna_source_review`, 2 November 2026. Ownership is this new numerical-plan-review-v2 directory only. The coordinator authored the execution packet. The reviewer authored neither execution-v1 nor execution-v2, and altered no frozen input. This acceptance is not an E5 scientific approval, evidence of successful native/Wasm execution, browser qualification or live delivery.

Accepted freeze SHA-256: `7dcc4a01a3408dba2cd49258e52e904f8cfa822c365eacce5dd4c1def753bd64`. The exact candidate remains `7bfc33578593fab8c806dd1cd6473f54b9e2cd5cbf07ecacaffd328118e103ac`. All 171 source pins and 1935 external tool/cache pins matched before and after the review's Python/mock checks. This review's manifest binds the entire accepted freeze closure, compared v1 inputs, review policy and outputs. Original v1 rejection and all of its frozen bytes remain unchanged.

## NP-PERZ-01 resolved prospectively

The source-backed constant-stress rate is `D = 1.5 lambda s/q`, with `lambda = A max(q/Y-1,0)^n`. Holding all stresses fixed holds elastic strain fixed, so this is both total and permanent strain rate. The new assessor calculates stress from the supplied initial total/permanent state and parameters, constructs its deviator/equivalent stress, and checks every solved stress-controlled component within `max(1e-10 s^-1, 2e-5 |reference rate|)`. Its `max(q,Y)` denominator is the exact inactive extension already reviewed in the source contract. Entry-side stress-controlled rates remain null by the declared interface.

The initial-stress reference is valid for every stress-controlled case in this frozen set, because each is a single, all-stress-hold segment. This acceptance does not authorize the same shortcut for future stress-rate/target controls or for a stress-hold segment following an unrelated earlier segment; those need references based on their own segment context. Current mixed controls are outside qualification.

I independently manufactured all 107 synthetic result rows with independently calculated constant-stress solved rates; the positive fixture passes. I then tested **396 corruptions across all 10 stress-hold cases**, at all solved sample points and every component: the extreme-rate counterexample from v1, zero rates where the reference is materially nonzero, and rates 5% outside the frozen error boundary. Every corruption is rejected. These tests include signed creep, different exponents and nonzero history. The author fixture now constructs correct solved creep rates, and its retained synthetic-only report includes the additional zero-creep-rate mutation for 26 total negatives. The original v1 finite-only gap is therefore resolved for the exact declared scope.

These are gate tests, not material-engine observations. Shared-backend agreement remains insufficient for independent accuracy.

## Unchanged physics, requests and existing gates

I compared v1 and v2 byte-for-byte for `cases.json`, `reference-convergence.json`, `oracle.py`, `prepare.py`, `expected-catalogue.json`, `collect_wasm.mjs`, `parity.py` and `run_operation.py`; all are identical. Every originally frozen non-execution-v1 source pin is unchanged and all external pins are identical. Inspection of the assessor diff confirms the only scientific gate addition is solved stress-hold rate accuracy. State/stress budgets, strict fivefold coarse/fine improvement, solver settings, maximum-step policy, request identity checks, clock/topology, dimensions, memory constraints, exact repeats, invalids, late retained-commit checks, actual-parent restart and parity have not been weakened.

The 107 requests provide the disclosed directional, selected exponent, relaxation/creep/rate, hydrostatic, noncoaxial reversal/hold, custom parameter, nonzero memory, passive rotation, refinement, restart/failure/recovery coverage. Qualification remains limited to these illustrative coefficient/protocol studies, not the Cartesian product of wide input guards. The material case set uses n=1,1.5,2,3; it does not establish compiled accuracy at n=8 merely because n<=8 is source-contract admissible. Passive covariance is not finite-rotation transport. No FE tangent, generic mixed controller, vendor binary conformance, experimental validation or material calibration is claimed.

## Reference reproduction

Closed-form relaxation and fixed-stress creep follow the separately reviewed source equations and prior independent 50-digit scalar checks. For loading/noncoaxial references, the independently formulated stress-plus-alpha RK4 oracle is unchanged and distinct from the production 13-state backward-Euler solver. I read its balance/compliance equations and used reviewer-controlled loops to reproduce **all 26** low8192/high16384 comparisons without running author prepare.py or changing saved references.

Each recomputed high-grid state agrees with its saved reference within `1e-14`, its stress within `1e-6 Pa`, and every recomputed low/high error equals the saved error exactly. Maximum low/high differences are `1.0753800194079899e-13` in state and `1.886561221908778e-6 Pa` in stress, below frozen gates `5e-11` and `0.005 Pa`. This is reproduction of the independently formulated oracle's convergence evidence, not an alternative material solver or a proof about every history. All rate fixtures used a separately written tensor computation in the reviewer script.

The frozen state/stress accuracy budgets and coarse/fine improvement are defensible prospective gates. Passing is not guaranteed by accepting this plan. Actual failures must remain failures under these exact gates and be retained under distinct diagnostic identities rather than used to relax them.

## Build closure and actual execution requirements

The unchanged generic CMake recipe selects the isolated Perzyna model directory, normal compiler generation and the existing physical-time-v2 schedule header before the common include root. It adds no handwritten Perzyna kernel. Actual serial builds still require the coordinator's fresh slot/process handoff, one explicit target and `--parallel 1`. This review authorizes no independent worker build.

`tools/record_cmake_profile_build_v2.py` is now explicitly included in the prospective freeze. The mechanism previously inspected in the v1 review is unchanged and defensible as pre/post source/tool/build-record integrity evidence, with actual compiler/generator/flags/link/object/archive/depfile and lexical/canonical dependency bindings. Its versioned schedule selection must pass, with legacy schedule exclusion. It is not binary attestation or a hermetic OS/SDK/toolchain promise.

Before material calls, capture actual build receipts using `cpp/main.cpp`, `models/research/perzyna`, `cmake/perzyna/CMakeLists.txt`, `--schedule required`, the exact explicit target and native/Wasm artifact identities. Require normally generated metadata to equal frozen expected-catalogue.json, and retain actual compiler paths/flags/object dependencies, linked scalar archive and collector/assessor consumer sources. Keep source/tool pre/post freeze checks as well as actual-build pre/post verification. Capture exact raw calls, logs and genuine exits; assess both backends independently before physical parity. The persistent Wasm instance's recovery evidence and native new-process limitation remain explicit.

Acceptance covers prospective policy only. A later separate nine-item E5 review must inspect exact actual model/source/reference/build/numerical outputs and retained failures. The full model umbrella remains open through atlas/profile/browser/live delivery.

## Reproduction, failures and cleanup

Run `python3 -B /private/tmp/atlas-perzyna-delivery-v1/docs/ingestion/perzyna-comsol63/numerical-plan-review-v2/reproduce.py`. It writes only this review's CHECKS.json, imports source-only assessor/oracle functions, and executes no author prepare/check script, compiler, native material, Wasm module or browser. All original v1 failures, source harness attempts and receipts are unchanged.

An ancillary process-inventory attempt was denied by the environment (`ps: operation not permitted`). The reviewer started no preview/server/build process; the Python review reached its final saved result after all assertions. No cleanup of another owner's resource was attempted. No download, worktree or disposable scratch was created. Retained outputs are REVIEW.md, reproduce.py, CHECKS.json and MANIFEST.json. The coordinator owns durable source/tool/evidence retention before temporary-worktree cleanup.
