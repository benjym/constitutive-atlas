# Independent review of VIBE mechanical references v2

Reviewer `/root/vibe_numerical_review`, task `REVIEW-vibe2026-mechanical-references-v2`, 3 November 2026. Ownership is only this new directory. I authored neither the reference nor the candidate. The board claim preceded dispatch. All prior source/reference/review bytes are preserved. This review extends the v1 source/transcription assessment with three named mechanical histories; it is not E5 approval, backend qualification or scientific admission.

**Decision: accept the exact independent reference-v2 packet and its bounded mechanical-history evidence.** The saved parent-produced Python comparisons also pass their unchanged gates. No unresolved blocker remains for this scoped review. No compiled, native, Wasm, browser, vendor or build execution occurred; no shared code, candidate or source packet was edited.

## Exact identity and construction

The reference-v2 manifest is `bf526d6149fd3e1082ba477c01d455caa8873c850fbbb83594c1b4010c988139`; its prospective plan is `6dd5a3b20eabcac10ffe82e0385d72cd37364009133a92c596898d0b322e814d`. The plan was frozen before the author's reported observations. It depends on the unchanged reference-v1 manifest `04dd3a8831e83cada428a38479f72908f8f1ed03ea640df4b4c9826dabf0d079`, including the source-authored Cartesian Decimal oracle and direct pivoted6x6 B solve. Neither reference imports production expressions. Source-v2 and the exact published explicit Appendix A identity, tensor-identity completions and disclosed Eq27 opposing-contribution discrepancy remain as assessed in review-numerical-v1. Its entire manifest and every bound file verify unchanged.

The same complete eight-component state is evolved: compression-positive Mandel net stress6, total void ratio and scan. Current positive suction and temperature are stage controls. The initial isotropic pressure is independently bisected to OA=1.005 at source BCV values, e=.725, scan=.35, suction10MPa and temperature294K. This is an illustrative constructed preparation, not a measurement or reconstructed experiment.

The three100s histories are exactly those in the frozen plan:

| History | Mechanical rate | Other controls |
| --- | --- | --- |
| mixed_mechanical_100 | [2,-1,3,-2,1,-3]×1e-8/s throughout | Fixed suction and temperature |
| mechanical_reversal_100 | Same vector for50s, its exact negative for50s | Fixed suction and temperature |
| coupled_mechanical_THM_100 | Same vector throughout | Suction+2000Pa/s; temperature+.02K/s |

All six mechanical components participate. This is mixed **constant-direction loading and sign reversal**. It does not change the deviatoric loading direction to establish nonproportional rotation coverage. Total strain is only a few parts per million, and the trajectories remain close to hydrostatic stress; no large-shear or general yield-region claim follows.

I audited the complete RK4 construction. All eight state components advance together; suction/temperature are evaluated at each RK stage. Every frozen partition count is even, so50s is exactly a step boundary. A reversal interval uses its own side's mechanical derivative for all four stages, including its shared endpoint, and does not average across the jump. Endpoint rates use the final side. No state clipping, projection, hidden threshold or altered source branch is introduced.

## Independent reproduction and checks

I reran all12 reference trajectories:64/128/256 partitions at70digits, plus256 at50digits for each history. Each of the three resulting JSON files matches the original **byte for byte**. I verified all eight reference-v2 manifest entries and all reference-v1 entries. Prior review-v1 manifest `a9dbb295044607d9c928d3a52b1611f7eadbc82f798b11224c91cec64fcfe535` and its14 entries remain intact.

At80-digit precision I independently recomputed every component's64-to128,128-to256 and50-to70digit convergence against the original gates: stress.01Pa+1e-7relative; e/scan1e-9+1e-7relative; em/eM/S_M/Sr/OA/re1e-8+1e-7relative. Every gate passes, including the additional coarse comparison. The worst128-to256 ratios are approximately1.66e-8 for mechanical-reversal stress and1.50e-7 for coupled-path scalar memory, far below one. Precision discrepancies are negligible relative to these gates. The full-state result and endpoint-rate vectors have eight components; all six stresses change.

I separately checked the exact solution of A15 at all four resolutions of every history. Since trace(strain_rate)=4e-8/s, the two constant-rate paths satisfy `e(t)=(1+e0)*exp(-4e-8*t)-1`; the symmetric reversal returns e0 analytically. The finest70-digit errors are about3.43e-39 for constant rate and4.47e-47 for reversal. Mechanical paths preserve scan exactly; the coupled path changes it positively. All endpoint physical controls and mechanical-rate signs agree with the frozen plan.

A distinct diagnostic monitored the unchanged guarded algebra at every rate evaluation of each256-partition70-digit path:1025 calls per history,3075 total. All calls pass source guards. OA ranges from1.005 to at most1.007632; eM remains above.161989; scan stays within[.35,.504393]; Iv remains positive, between.004 and.0040004. Fm remains between zero and approximately1.211e-8. The retained extrema include temperature, suction, micro/macro pressure and voids, slopes, viscosity and B denominator. This checks every sampled stage, including provisional RK states, rather than only accepted endpoints. It does not prove admissibility between samples or across arbitrary paths.

## Parent candidate comparisons and retained failures

The parent compared unchanged candidate revision3 SHA256 `29d104bf55ec3225030e8710ee342f96b6518bd8a4434e784e455da300d08778` against these references using the dedicated Python adaptive-midpoint host. The corrected mechanical-study-v2 plan SHA256 is `07133b703addf5bc569db87ff8cdb82eb1343503e2dea9dd6182a2c86948ecd1`. It retains all three cases, original state/observable bounds and the earlier execution settings: absolute scale fraction1e-12, relative tolerance1e-11, maximum step10s, depth40,100000trials and physical origin11s. Reversal remains an exact50s/50s split.

I inspected the actual scripts, plan and three saved reports, checked each plan/reference/script/model hash, and independently recomputed candidate full-state errors against the full Decimal reference values. All pass. The saved reports' largest state/observable tolerance ratios are approximately2.94e-5 for mixed mechanics,2.96e-5 for reversal and.01566 for coupled mechanics/THM. Context time is111s, endpoint external controls and rate signs match, state and context copies agree, and diagnostics remain within the declared local error bound. These candidate integrations were **not independently rerun** by this reviewer. Raw endpoint observable values are absent from these reports, so their observable ratios are inspected parent-produced evidence rather than separately recomputed values; future backend evidence should retain raw observables.

The first parent mechanical-study-v1 script mistakenly addressed reference-v1 for new reference-v2 files. It fails with FileNotFoundError before initialization/rate evaluation. Its script, plan and failure receipt remain retained. The separately named v2 changes the reference directory and output/plan identities; cases, settings and acceptance bounds remain unchanged. This is a corrected binding, not a numerical gate relaxation.

One reviewer diagnostic also failed and is preserved: `audit.py` asserted exact decimal endpoint-strain equality for binary64 multiplication100×3e-8. The saved endpoint is2.9999999999999997e-6, differing from exact decimal3e-6 by3e-22; reversal returns exact zero. That reviewer assertion was not an original source/reference/candidate acceptance requirement. The original failed script and `reviewer-diagnostic-v1-failure.json` remain unchanged. A distinctly named `audit_v2.py` reports these representation errors diagnostically and retains every originally frozen numerical gate. No exact decimal input-transport claim is made. Earlier successful reference-only `audit-results.json` also remains intact; the final combined evidence is `audit-v2-results.json`.

## Reproduction and bounded handoff

From repository root:

```sh
python3 -B docs/ingestion/vibe-2026/reference-v2/run_histories.py --output docs/ingestion/vibe-2026/review-numerical-v2/reproduced-reference
python3 -B docs/ingestion/vibe-2026/reference-v2/verify_results.py
python3 -B docs/ingestion/vibe-2026/review-numerical-v2/audit_v2.py
```

The final audit reads exact saved candidate reports in the coordinator's isolated worktree but executes only pure Decimal source-reference analysis. It writes only this owned review directory. `input-bindings.json`, `decision.json` and the final manifest bind the evidence; no admission-registry record is supplied.

The smallest next action is coordinator-owned serial backend qualification followed by the final all-nine-item independent E5 review. These three paths extend the former hydrostatic-only trajectory evidence to the named small-amplitude mixed mechanical/reversal/coupled histories. Arbitrary nonproportional directions, broad parameter/state envelopes, singular/saturated boundaries, FE-host tangents, experimental validation and browser/live delivery remain separate.

Cleanup: no download, dependency environment, worktree, build or preview/background process was created. Reproduced JSON, diagnostics and failed checks are retained as required evidence. No path was removed and no temporary or uncertain resource remains. Only `docs/ingestion/vibe-2026/review-numerical-v2/` was written.
