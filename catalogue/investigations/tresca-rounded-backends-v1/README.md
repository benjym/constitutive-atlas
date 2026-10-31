# Tresca rounded-input backend qualification — v1 failed

**The frozen numerical qualification fails on both native and Wasm. Tresca is not installed or scientifically admitted.** The complete evidence is retained to drive a source-supported correction, rather than changing the gates or omitting difficult cases. This is the first compiled observation of the unchanged BK2022v1/project-BE draft under the independent rounded-input corpus.

## Frozen study

`prospective-freeze.json` binds the exact candidate, generated original/instrumented headers, core C++ snapshots, literal request wire, policy and toolchain. `assessor-freeze.json` predates candidate execution. Generated numerical expressions are unchanged: the instrumented header only captures the existing branch value. Removing the two capture lines reproduces the complete original header byte-for-byte. Normal generation of the unchanged draft also reproduces it.

Each backend has 219 requests:183 corpus calls (61 cases × double residual/38 column Jet residual/unsplit solve),12 reference-parent history restarts,23 negative/poisoned-seed cases and one tentative-Newton rollback transaction. Every completed request runs a valid zero-increment baseline before and after in the same process. Builds were serial: one explicit `atlas_tresca_rounded` native target, then the same Wasm target, each `--parallel 1`. No numerical kernel, compiler, schema, public model or browser source changed.

The source is [Boulmezaoud–Khouider2022v1](https://arxiv.org/abs/2207.12719v1), with the separately project-derived BE projection recorded by the [source packet](../../../docs/ingestion/tresca/README.md). Raw source PDFs remain private. The [independent reference corpus](../../../docs/reviews/tresca-rounded-reference-v1/README.md) supplies actual stored-Mandel references, full sigma6/ep6 history and the prospective negative-input policy.

## Results and retained failures

Both backends have identical status/branch/iteration/rollback outcomes for all 219 requests.211 rows are exactly equal; the others differ by at most 1.37e-15 in normalized values and 3.46e-15 in derivatives. Backend agreement does not establish constitutive accuracy: both fail the same source-reference gates.

| Check | Native and Wasm result |
| --- | --- |
|219 requests completed | Yes;196 accepted/23 rejected each |
|2,328 value components checked | Three failures, all plastic-strain components of the near-isolation solve |
|26,904 derivative components checked | Pass; maximum normalized error 4.14e-14 against 2e-8 |
|Source-invalid rounded initial parent | Incorrectly accepted in history restart 7 and its duplicate negative case |
|Selected boundary derivatives | Two explicit coverage gaps: dense yield and large-offset near isolation choose adjacent elastic branches |
|Input preservation and same-instance baseline recovery | Pass for all requests |
|Tentative Newton rollback | Tentative state actually changes, budget-limited solve rejects, all 12 incoming state bits return unchanged, recovery matches |

The frozen assessment therefore has five failed assertions and two derivative coverage gaps per backend. Its status remains failed even though the saved-evidence tests pass.

### Large hydrostatic offset loses plastic history

The near-isolation case starts at 2^60 Pa hydrostatic stress, whose binary64 spacing is 256 Pa. Its exactly stored strain increment creates a small exact deviatoric elastic change `[4,4,-8]`Pa. Adding that change to the absolute stress rounds it away before return classification. The independent source reference selects an upper corner and changes plastic strain by `[0.5,0.5,-1]`; both backends select elastic and leave plastic strain unchanged. Absolute stress agreement at the large offset conceals this history error. `diagnosis.json` retains exact inputs, reference trial/history and the separately reproduced binary64 arithmetic.

Pressure/deviator separation is a source-supported candidate remedy because the selected Tresca yield cylinder and associated correction are pressure invariant. Any revised residual formulation needs an explicit equivalent-row derivation and corresponding independent residual/derivative reference transformation. It must not be substituted into this frozen failed study or justified by widening error tolerances.

### Strict initial membership is not certified by rounded roots

Reference history parent 7 exceeds the independently converged exact-input yield range by approximately 2.10e-17 Pa. Both backends nevertheless accept it. The current value-only principal-root comparison cannot certify strict source membership at that sub-ulp distance. No clipping, silent projection or initial-yield tolerance was added. An exact/certified generic membership or rejection contract, or a distinctly identified source-reviewed numerical initialization policy, is a separate unresolved requirement. The original source-ideal condition remains unchanged.

## Wasm transport failure and completion

The first Node process read piped stdin, emitted 64 complete responses and exited 2 with `invalid token`. That raw prefix and original process receipt remain intact. A prospective transport-resume note froze the identical remaining 155 wire records and unchanged binary hash. Only those uncompleted records were then read from a regular input file, producing 155 responses with exit 0. No completed material request was replayed and no rebuild occurred. The driver parses a complete request before any baseline or candidate call; the aborted partial request had not reached material execution. `wasm-output-assembly.json` binds the prefix/tail and assembled 219 record stream. Per-request same-instance recovery remains valid; this does not claim one process for all 219Wasm requests. The precise pipe/parser failure cause is not established by this transport correction.

Two source-only preparation mistakes (a Python keyword and expected generated whitespace) were corrected before the prospective build/execution freeze; their summaries are retained there. No numerical policy was changed after observation.

## Verification and stopping point

```sh
python3 -B catalogue/investigations/tresca-rounded-backends-v1/verify.py
python3 -B -m unittest tests.test_tresca_backend_evidence
```

`verify.py` replays only saved results and verifies source/driver identity, original failures and stream assembly. The four evidence tests also reject added value, derivative, rollback and recovery corruptions. With the independent-reference, activation and archive suites, 28 focused tests pass. Those are software/evidence checks, not a passing material qualification. Compiled binaries remain local and are identified in `artifacts.json`; build recipes, frozen sources and all outputs are committed. No source data was fitted or replaced.

Keep the numerical qualification task open. Next: a separately identified pressure/deviator candidate and equivalent residual/reference derivation, plus an explicit strict-initial-membership decision. Freeze any revised backend policy and driver before new observations. Preserve all61 cases, histories, negative inputs and current failures. Continuous accepted history and actual browser candidate exposure still need later gates; installation, scientific admission, deployment and push remain outside this failed study.
