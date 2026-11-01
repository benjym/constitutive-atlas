# Tresca actual-parent reversal diagnostic, v1

**Cause established on native and Wasm: inconsistent branch predicates reject a repeated spectrum before Newton can step.** The original laboratory qualification remains failed. No solver, model, tolerance or public catalogue changes are included.

The input is the exact 12-component committed parent at `isotropic-0` step 6 of the [laboratory v1 study](../tresca-laboratory-v1/README.md), followed by the original axial increment 1/128 with zero lateral strain. Original parameters and settings are retained, including 45 iterations, max_depth 0 and residual tolerance 2e-10. The independent exact solution and admissible nearest binary64 state are copied with their source hash.

An independent standard-library Fraction/float calculation, made before compilation, finds a rounded trial tensor with exact principal range `16 + 2^-49` Pa. The exact range predicate correctly classifies it as plastic. Both rounded corner-comparison operands equal -16 Pa, however, selecting the face expression rather than the repeated-minimum corner. That face expression requests the unique minimum-eigenvector projector at a repeated minimum. The pinned spectral implementation rejects unresolved selected eigenvalues; the generated expression guard propagates that rejection.

The compiled trace confirms branch 3 and the same trial tensor in the actual Jet evaluation. Both backends reject on the first Jacobian call: **zero Newton corrections and zero backtracking trials**. A raw double probe also rejects at the independently admissible physical solution. The default diagnostic error remains zero because evaluation fails before the residual norm is computed; it is not evidence of convergence. This rules out an iteration-budget or line-search stall as the cause of this rejection.

The binary contains separate original and instrumented copies in distinct namespaces. Hooks record already computed branch values, evaluation verdicts, iterates, corrections and trials without changing original arithmetic, guards, short-circuit ordering or budgets. Removing the hooks and namespace isolation recovers all 22 original source files exactly (`check_instrumentation.py`). Baseline and instrumented verdict, full state, diagnostic counters and error bits match. Full rollback, unchanged inputs and same-instance zero-increment recovery pass. Native and Wasm response documents are identical.

`prospective-freeze.json` predates the one explicit serial build target per backend, native first: `atlas_tresca_reversal_diagnostic --parallel 1`. Complete sources, input wires, independent branch reference and observational policy are retained with process logs and artifact hashes. The original reference's pre-build corner assumption failed; `preflight-reference-failure.json` preserves that observation. The corrected independent reference records the mismatch instead of inventing a return map. No compiled observation preceded that correction or the freeze.

Reopen the evidence without a build or material execution:

```sh
python3 -B catalogue/investigations/tresca-reversal-diagnostic-v1/verify.py
python3 -B -m unittest tests.test_tresca_reversal_diagnostic -q
```

Seventeen related software tests pass, including saved-only replay with process execution denied and trace-corruption checks. Software success does not change the failed material verdict.

The [correction proposal](CORRECTION_PROPOSAL.md) gives an exact-invariant route for the centered-middle spectral comparisons. Next is a bounded source-only proof/oracle/contract design, followed separately by generic capability implementation and complete original corpus qualification. No endpoint widening, iteration-budget change, special model kernel, source promotion, experimental validation, push or deployment is included.
