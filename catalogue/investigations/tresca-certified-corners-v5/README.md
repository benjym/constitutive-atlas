# Private Tresca certified-corner qualification, v5

**All frozen numerical qualification gates pass on native C++ and Wasm.** The candidate remains a private draft with pending scientific/source review; it is not installed in the public atlas.

The only formulation change from v4 is the derived `branch` expression: its two rounded corner comparisons become `principal_centered_mid_gt(trial_dev,width)` and the same strict comparison on `-trial_dev`. Record identity/description change to distinguish this revision. Equations, full sigma6/ep6 persistent state, source hyperlinks, parameter ranges, initial and solution constraints, residual domain and solver/controller budgets are unchanged. Source continuum closure is BK2022v1 associated perfect Tresca; the finite backward-Euler projection remains a separately identified project algorithm.

Each backend passes:

- All 219 original requests: 194 acceptances, 25 intended rejections, 2,328 value comparisons and 27,816 derivative comparisons over all 61 cases and all 38 columns. No derivative coverage gaps. Maximum normalized value error is 1.17e-10 and derivative error 4.14e-14, within the original gates.
- All 12 continuous own-committed-state history steps, with independent exact source admissibility of actual parents and commits and 288 reference component checks. Original 200/280-digit references and budgets are retained.
- All 29 original laboratory requests across five protocols and two preparation states, with 1,746 full-state/strain comparisons, 97 exact committed-state admissibility checks and 29 same-instance recoveries. Maximum stress error is 1.99e-7 Pa and strain/plastic error 2.04e-10. The previously failing `isotropic-0` path now completes all nine points. The deliberately unattainable stress target correctly retains only its four-point prefix.
- The exact saved failed-parent reversal, independently replayed with original parameters/loading/budgets. It accepts in 30 of the original 45 allowed iterations with one unsplit update. Raw double and Jet evaluation succeed, state remains source-admissible and full state meets the original 2e-9 value budget. No iteration-budget change was needed.
- The unchanged generic callback checks: physical inadmissibility versus raw residual extension, malformed layouts, 48 nonfinite primal cases, 1,368 nonfinite state seed cases, full rollback and recovery.

The corpus/history assessors, policies, requests and original laboratory assessor/references/input wire are exact copies. No accepted case was dropped or reclassified to obtain this pass. `prospective-freeze.json` binds the candidate, exact original gates, source pins, generated header and input wires before either build. One explicit serial target per backend, native first: `atlas_tresca_certified_corners --parallel 1`. Five modes run on each resulting binary. The driver uses the exact production API implementation for laboratory responses. The normal-generated header is retained separately; the execution header adds only the two original branch-observation lines.

All 45 related software regressions pass, including process-denied saved replay, exact candidate-change limits, normal generation, original failure preservation and corruption rejection in derivative column 37, laboratory history and reversal probes. Process logs, complete outputs and local binary hashes are retained. Laboratory, callback and reversal response values match across backends; corpus and history have small floating differences, detailed in `backend-comparison.json`. Both pass the independent original gates; bitwise identity across backends is not claimed.

Reopen the qualification without a build or material call:

```sh
python3 -B catalogue/investigations/tresca-certified-corners-v5/verify.py
python3 -B -m unittest tests.test_tresca_certified_corners -q
```

Earlier failed v1, continuous-history, domain-v3 and laboratory-v1 assessments remain unchanged and false. This is a distinct qualified numerical revision, not a rewrite of those verdicts. The existing nine public models, website package, experimental data, review statuses and paper are unchanged. No push or deployment occurred.

Stop numerical expansion here. [The review handoff](REVIEW_HANDOFF.md) binds the exact current candidate and remaining source/formulation/preparation questions before a separate public integration decision. This pass supplies no Wichtmann applicability or predictive-accuracy claim.
