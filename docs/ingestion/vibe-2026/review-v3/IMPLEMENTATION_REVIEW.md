# Independent controlled-time implementation review

REVIEW-vibe2026-controlled-time-implementation-v3, reviewer `/root/vibe_gap_review`, 2026-11-03. This is a source and pure-Python review of the separately owned Stage A worktree `/private/tmp/atlas-vibe2026-controlled-time-v1`. Final byte-bound decision and verification are recorded separately. This document alone grants no execution or model approval.

## Reviewed behavior

The dedicated `physical_time` / `controlled_ode` profile preserves physical seconds, symmetric accumulated infinitesimal mechanical strain and explicit scalar control values/rates. Semantic validation enforces derivative dimensions, quantity/binding consistency, unique bindings, persistent-state roles and bounded component counts. Positive-duration holds remain genuine physical evolution. The explicit midpoint step-doubling estimator compares the full state with Richardson factor three, accepts the two-half-step state, and evaluates controls and time at matching stages. Local error tolerance is not a promised global error bound.

The Python and C++ algorithms retain the parent until a full advance succeeds. Initial preparation checks are distinct from evolving-domain restart checks. Context contains state, physical time, all control values and incoming rates, parameters and exact model/profile identity. Left/right observations at rate changes preserve state and time. Whole-schedule results remain local until success. The new route is not a stress-control, coupled transport, finite-rotation or generalized tangent capability.

The dedicated generator emits model-agnostic equations and a separate catalogue/API; no handwritten scientific kernel is introduced. C ABI checks model indices, exact counts, flags, settings, null/range arithmetic and forbidden overlaps before copies. Inputs cannot overlap outputs; outputs cannot overlap each other; read-only inputs can overlap. All output writes occur after successful evaluation/advance. Valid allocation ownership remains a native caller responsibility. The adapter checks exact context identity, endpoint/control equality, inputs and failure sentinels.

Old interpreter/environment/initialization/path/compiler routes reject the new profile. Shared stress binding permits net scope only for the new physical controlled profile. Existing ordinary generated catalogue bytes are compared to the retained preimplementation baseline. The narrowly authorized historical formulation test dispatch change preserves ordinary rejection and independently compares dedicated generation; its original discovery failure is retained.

## Findings and corrections

1. Initial same-shape stale-module identity checking was insufficient. The author added embedded model, canonical catalogue and exact catalogue-file SHA queries; NativeEngine verifies these before material calls, and the Wasm runner verifies exact catalogue bytes and embedded model identity before interpreting offsets. The exact-file binding closes catalogue layout tampering even if a stale hash field remains unchanged. Pure fake-module rejection is useful source-level coverage, not compiled evidence.
2. Initial native analytical coverage was narrower than the frozen written design. Both backend runners now consume the same prospective independent Decimal closed-form corpus, covering mechanical components, field forcing, opposing contributions, holds, explicit clock dependence, partitions, nonlinear state evolution, branches and maximum capacity. Actual pass status remains pending coordinator execution.
3. Initial capacity tests covered only state and control maxima. The capacity fixture now uses 256 parameters, 32 control components, 65 equation-input components, 32 state components and 24/144 observable fields/components. Highest parameter/control offsets drive the last state and observable. Over-capacity mutations reject. Since 65 is the mathematical maximum under unique order-0/1 bindings, a hypothetical additional input also necessarily violates binding uniqueness.
4. Detached old-profile stress utility previously admitted net stress even though the schema refused it. The utility now restricts net scope to the new controlled physical-time profile and has direct utility plus schema tests.
5. Raw execution records must preserve exact inputs/settings, all state and observable outputs/diagnostics, source/reference/catalogue/artifact identity and failures. Any remaining pending evidence requirements are stated in the final decision; source inspection does not establish successful native/Wasm behavior.

## Retained failure and limits

The original default-rtol C3 global bound failed. `SETTINGS_REVIEW.md` and `settings-decision.json` accept only the distinct stricter execution study, with unchanged references/bounds and disclosed chronology. Neither original default gate nor compiled qualification is passed by that decision. This review is not E5 approval of VIBE, experimental validation, atlas/browser qualification or E8 delivery. No compiled, vendor or browser program was executed by this reviewer.

## Cleanup

No preview process, worktree, download or compiled resource was created by this reviewer. Pure-test temporary directories are automatically removed. The implementation worktree and all retained source/failure evidence belong to the coordinator/author and are not removed by this reviewer. Only new review-v3 files are written here; frozen v1/v2 bytes remain unchanged.

## Final prospective gate closure

Source freeze v1 had remaining C4 test-source omissions; these were not observed runtime failures. A distinct v2 source addendum adds a late-domain fixture, native/Wasm rollback and recovery, and Wasm trial/depth exhaustion plus invalid duration/time/control tests. A distinct v3 adds meaningful assertions for the highest Wasm observable offset and explicitly uses the stricter recovery setting. Runtime, independent oracle and acceptance bounds remain unchanged. Every v1 and v2 bound file is recoverable at exact hashes in current files or named preimages; the reviewer verified all 116 historical entries. The final v3 source manifest binds 67 files. No further blocking source finding remains for coordinator-owned serial build and actual qualification. The same prospective gates must now be run against the exact compiled artifacts; source acceptance does not replace those observations.
