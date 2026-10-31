# Generic instantaneous-rate transport review v1

Task: AUDIT-generic-rate-transport. Reviewer: review_sanisand. Date: 2026-10-31.

The five reproduced Python failure modes below are closed in the final reviewed draft. This is a bounded transport/code review, not approval of a source model, numerical study or compiled execution. The Node collector, actual frozen source-study protocols and actual build receipts were unavailable during this review.

## Exact reviewed inputs

The input is `tools/research_rate_observations.py`, staged by the coordinator under `/private/tmp/atlas-generic-rate/`. The reviewer preserved private exact copies before testing. Those implementation copies are not part of this public review packet; the coordinator owns their integration/archive.

| Snapshot | SHA-256 | Result |
| --- | --- | --- |
| Preliminary | `783002f9a5ac2440b497cda4fb20bc3a95cb6064c25a7733bf25ece0b38050c1` | All five witnesses reproduce. |
| Intermediate follow-up | `de31d03ae570e2c8f300467d61c3af86af0046c57c112e1857d80670358add99` | Four close; truncated-vector parity still falsely passes. |
| Final reviewed draft | `691a4dc606d0fb7b7ee0c5bc2816004292676eb50c3a4cd2e09e71634d75312a` | All five `--require-fixed` witnesses pass. |

These hashes identify changing preliminary source, not a historical freeze overwritten by the reviewer. Original and intermediate failures are retained separately.

## Findings and closure

1. **Raw parsed bytes could differ from final reported hash.** Preliminary `audit`, lines123–182, hashes the companion, then parses it separately, then hashes it again on return without requiring the same held bytes. The witness replaces the raw document immediately after parse: audit passes against the earlier response while its returned hash identifies the changed response. Final `Snapshot` hashes and parses held bytes and checks every input unchanged at completion. The mutation witness is rejected.
2. **Truncated parity vectors silently skipped comparisons.** Preliminary `parity`, lines186–201, uses `zip` without checking response lengths. One native `values=[]` versus Wasm `values=[99]` returned `passed=true` and `both_independent_assessments_passed=true`. Final parity checks complete finite typed vectors, expected statuses and model/catalogue identity before iterating. The witness is rejected. Parity still expects caller-supplied assessments; a future assessment command must audit both original observation/raw pairs before calling it, rather than trusting arbitrary JSON labelled `passed`.
3. **Finite operands produced nonfinite assessment errors.** Preliminary audit/parity subtract finite `1e308` and `-1e308`, yielding infinity. The audit records `outcome=failed` but strict JSON serialization fails, losing the assessment artifact. Final error representation uses `null` with an overflow flag, preserving a JSON-safe failure. The already-known zero parity budget/nonzero error case also now uses an explicit unbounded flag and null fraction. This review's independent witness covers subtraction overflow; the coordinator separately reported its own zero-budget test.
4. **Numerical failure exited successfully.** Preliminary CLI lines207–209 writes and prints a failed numerical assessment but exits0. A pure Python `runpy` witness executes only assessment mode against synthetic JSON, confirms the failed file was written and observes exit0. Final CLI retains the file and exits1. No external executable is launched by this witness.
5. **Protocol provenance could omit its model pin.** Preliminary `checked_protocol`, lines43–70, accepts an empty pin dictionary and an absolute `model_file` when the loaded definition matches. Final code requires model-file membership in the relative pin dictionary; the explicit absolute/empty-pin witness is rejected. The actual source study must still declare and review complete compiler/DSL/driver/reference/budget pins; this generic check does not establish the completeness of an unavailable source protocol.

A separate source-only concern was raised for collection: independent preflight/final reads could rebind a policy changed between validation and collection. In the final draft, `collect_native` uses one lifetime `Snapshot` for protocol, build receipt, source/artifact bytes and collector, retains raw transport before assessment, then checks the same snapshot after process completion. This closure was read in source; the reviewer did not execute the native collector.

## Binding and failure-channel observations

The audited design retains literal native stdin or CABI argument strings, not merely reconstructed numeric requests. Native command/function bindings, ordered response count, descriptor identity, complete response key sets, finite numeric echoes and exact expected status are checked. Recursive numeric identity accepts harmless int/float JSON serialization differences while distinguishing Boolean values. A parser rejection has the explicit `{ok,message}` shape; a typed material rejection has the full echoed response shape with null values. This is appropriate only when each actual protocol labels the driver's error class correctly. No real protocol was available to validate that mapping against its CSV parser and model domains.

Native stdout/stderr/return status are retained before numerical acceptance; timeout output is preserved as an incomplete observation. Exact response strings are required for the Wasm journal audit branch, but that branch's producing Node collector was not available. Error/recovery controls compare literal arguments and complete responses to a prior control. Actual protocol ordering must demonstrate successful known-state control, intervening rejection, and recovery in one persistent backend; the generic equality check alone does not prove a study contains that sequence. Arbitrary OS launch exceptions, persistent module lifecycle, descriptor CABI ABI and raw-before-parse behavior in Node remain unobserved here.

Build receipts are structural/hash inputs, not scientific reruns. Portable audit does not reopen artifact bytes; collection does reopen them. Final source alone does not establish who produced a receipt, that every build command was correctly recorded, or that compiled bytes correspond to all required source/generator settings. Those checks require the coordinator's frozen build-receipt generator and actual study receipts. No author code or generated kernel was executed by the reviewer.

## Portable regression witnesses

Run from any location with explicit paths:

```sh
python3 /path/to/witnesses.py --source /path/to/research_rate_observations.py --repo /path/to/constitutive-atlas --require-fixed
```

The harness uses a synthetic single-scalar transport model, mocks model loading/validation and temporary `ROOT`, and never calls collection mode or an external executable. It tests transport contracts, not model schema admission. Omit `--require-fixed` to retain observations against an earlier draft. The JSON result is printed; callers choose a new result path. Do not overwrite the historical result files in this packet.

`witness-results.json`, `revised-witness-results.json` and `final-witness-results.json` retain the three exact-source outcomes. All five preliminary failures reproduce; final `--require-fixed` succeeds. The coordinator's reported ten additional synthetic tests are not counted as reviewer-run evidence.

## Remaining gates

No reproduced Python blocker remains among these five cases at the final reviewed hash. Before any source-study execution: review the frozen Node collector and actual source protocol; verify complete source/reference/policy pins, pre-execution native/Wasm build receipts, typed-invalid mapping and persistent rejection/recovery order; then independently audit both original raw companions and apply the unchanged frozen numerical/parity gates. The review does not authorize execution, relax budgets, add scientific evidence or change catalogue admission.
