# Independent prospective review: capped BE schedule study v3

Decision: **prospective accepted** for the exact frozen study below. No actual v3 result or E5 approval is asserted. Reviewer: `/root/bingham_review`; output ownership is only `execution-v3-review-v1/`. No build, material call, compiled execution, author change or canonical installation was performed.

## Exact identity and independent checks

Accepted freeze: `execution-v3/freeze-v1.json`, SHA-256 **b3f72df24459d66a15b45ef9912f6baf78d65fd869d533cb67c52290c807f0e1**. All 15 frozen files, 108 copied source pins, four analysis pins, and the separate complete original 138-input build closure match current bytes in the original delivery tree. The retained native executable is byte-identical at SHA-256 `8adc81893b6f59219aa6722f2090b4b8f46a72efe061aac397b8cf9a6248ed0d`. These checks do not execute the binary. Before actual collection the coordinator must recheck exact pins and claim the serial slot; this review is not a new build receipt or proof that an arbitrary other binary has these inputs.

For every one of 136 cases, an independent complete-record comparison against v2 permits exactly three representations of the same setting change: `specification.solver.maximum_step`, `args[11]`, and the value after `--max-time-step`. Every remaining field is equal, including IDs/order, references, physical loading, incoming context, control segments, timing, all other solver settings, invalidity and restart lineage. The exact new value is `min(previous maximum_step,0.0004069010416666667 s)`. All existing caps exceed this number, including the prior 0.1 s late-budget cap; all 136 cases receive the declared cap.

Seven helpers are byte-identical to v2: assessor/native collector, Wasm collector, parity, oracle, synthetic checks, expected catalogue and convergence evidence. The copied historical `SOLVER` constant and `prepare` command can generate uncapped requests, but the frozen execution commands consume existing cases; the plan explicitly forbids `study.py prepare` and names the separate immutable v3 preparer. Actual restart preserves the case solver settings while replacing only the actual incoming material state, total strain/rate and time. Neither collector substitutes the historical default maximum step into frozen requests.

Independent assessor-only execution produces all 136 manufactured positives and rejects all 25 original mutations. Two additional independent mutations reject an uncapped request argument and an uncapped returned solver setting. These are synthetic controls, not numerical observations. Their output is written only in this review directory; frozen helpers and evidence remain unchanged.

## Gates and scientific limits

The plan explicitly retains state error `max(3e-7,2e-5|reference|)`, stress error `max(3 Pa,2e-5|reference|)`, native/Wasm scaled parity `2e-10`, exact replay and all context, topology, domain, transaction and failure/recovery checks. The coarse diagnostic retains its historical tolerances and floors. Both coarse and fine receive the cap; both strict fine-error less than coarse-error/5 gates remain in the unchanged assessor. If a common cap defeats that comparison, it remains a genuine failure.

The first 1e-6 s segment of the late-budget history is still shorter than the cap. It must commit exactly two accepted halfsteps, nonidentity material state and positive Newton work before the later zero-budget failure; the same four-point retained-prefix contract remains. No additional budget, tolerance, timeout or relaxed scientific gate is introduced.

The accepted source analysis motivates the cap through a bound on one omitted radial active-exit flow contribution and its continuation. It gives no total finite-Newton or binary64 error certificate. The plan states this correctly and also excludes a scalar proof for noncoaxial/mixed-control cases. A passing complete study would establish bounded evidence for the actual settings and declared histories. It would not establish generic estimator robustness, arbitrary parameter/rate/control values, experimental validation, or the excluded direct midpoint API. No unseen pass is assumed.

## Prior failures and snapshot honesty

Post-observation selection of this cap is disclosed. Original v1 midpoint and v2 BE failures retain their identities. The frozen v3 source-binding file deliberately includes an earlier snapshot hash of then-growing v2 output. On final review only its context raw/log files have changed; the study/source pins have not. This historical context is not silently repinned.

The now-complete v2 raw file separately has 136 rows and two calls per row, SHA-256 **2e12f0c7fe47bca586d72bd563d1f002b1884a8c286f4376c2c2e1dcda01a449**. The retained native status records assessor exit 1. Its final raw, log and status are bound in this review as retained failure evidence, rather than inserted into the immutable v3 freeze. The coordinator's supplementary component diagnosis is not substituted for the original failing assessor.

## Public preparation cross-binding

Read-only review of the release tree's `interface-v3-preparation-v1/candidates/` finds the proposed contract changes exactly its fixed maximum step to the study value, plus a bounded-scope source comment. The package checker changes its policy path and adds exact policy/contract/request/response cap assertions, packaged-contract/checker hashes and cap-tampering rejection. The original physical/reference checks remain. The candidate policy states its prospective status, unchanged physical gates and excluded wider claims. The three exact candidate hashes are in `BINDINGS.json`.

These files are uninstalled preparations. The current canonical release contract still has the old maximum step 1e6 s. **Before any public qualification calls, the coordinator must install and bind the reviewed capped contract/policy/checker, enforce the cap in request and response validation, and preserve the exact source/build/accepted-evidence identity.** Final E5 must bind actual native/Wasm outcomes, the eventual actual build receipt and the effective public policy. This prospective acceptance does not authorize claiming the old uncapped public contract as qualified or imply approval of every custom value accepted by the UI.

## Reproduction and next action

Run `python3 -B docs/ingestion/bingham-comsol63/execution-v3-review-v1/check.py` from the original isolated tree. It checks hashes, complete-case deltas, helper identities and manufactured assessor mutations; it imports no model interpreter or material backend. `RESULTS.json`, `synthetic-results.json` and `check.log` retain output. `BINDINGS.json` binds the exact inspected inputs and review artifacts.

No prospective blocker remains for coordinator collection of this exact study after fresh pins and serial-slot claim. Preserve every raw attempt, timeout and failing assessment. Actual E4/E5 and public browser qualification remain pending.
