# Independent diagnosis — midpoint misses Bingham activation

Task DIAG-bingham-time-crossing-v1; reviewer `/root/bingham_review`, 2 November2026. Owned only this new directory. Read source equations/reference derivation and generic time/schedule code; audited saved native-attempt1 outputs. No compiled call, build, production/source/evidence modification or network action was performed.

**Diagnosis: original integrate-time qualification fails because the explicit midpoint step-doubling estimator can have a zero defect while missing real viscoplastic evolution. The source/candidate law is not disproved. A separately identified, prospectively frozen study of the existing generic backward-Euler schedule interface is legitimate, with unchanged independent physical-accuracy gates and explicit interface limitations. This is neither acceptance of unseen BE results nor E5 approval.**

## Independent evidence

The saved original136rows contain272identical repeated calls; the original qualification command exited1. Independently comparing successful nonrestart direct outputs against the same frozen reference budgets finds42radial requests exceeding state and/or stress limits. The original raw outputs, failed status, source freeze and diagnosis must remain immutable. Diagnostic ratios are not replacements for the failed assessor.

For the first failing normal-direction case, scalar radial stress z starts0, prescribed d=.003/s, G=10MPa, Y=100kPa, eta=20MPa s, duration2s. Source reduction is

z'=60000-(1.5) sign(z) positive_part(abs(z)-100000) Pa/s.

Elastic prediction reaches yield at1.6666666667s. The exact endpoint q is115738.77361149466Pa and alpha=.00014204087961684466. Native returned elastic q=120000Pa, alpha=0 and vp strain=0, with2accepted substeps, no rejected step and temporal_error_norm=0.

The code explains this exactly. A full explicit-midpoint step evaluates its correcting derivative at1s, q=60000Pa. The two half steps evaluate correcting derivatives at.5s and1.5s, q=30000Pa and90000Pa. Every correcting derivative therefore has zero flow. Full and two-half states agree exactly on the elastic endpoint; the error estimate divided by its Richardson factor is zero. Endpoint time_domain checks admissibility, not quadrature accuracy or event crossing. Overstress is correctly admissible in this viscous model, so that check cannot reject the endpoint on physical grounds.

A second independent scalar calculation with z0=-200000Pa and the same positive rate shows a more general cancellation: full and two-half midpoint states again agree at z=-80000Pa despite active initial flow. All correcting midpoint stages lie in the inactive interval. Thus a proposed generic fix that merely checks whether the final endpoint is active would not cover the observed class. Many other crossings fail despite thousands of accepted substeps, so a successful adaptive error estimate is not itself independent equation verification. This report proposes no model-specific kernel or unreviewed generic numerical fix.

Saved six BE schedule histories have physical-component errors inside their original budgets (worst ratio approximately.2203; coarse diagnostic uses its separately predeclared bounds). This is limited already-observed evidence, not qualification of the unexecuted108radial BE requests, all lifecycle checks, Wasm delivery or the full interface. The new study must disclose these prior observations rather than claim no Bingham compiled observations have occurred.

## Legitimate bounded next study

Backward Euler is an existing generic implementation of the same continuous physical-time law: schedule.hpp solves z_next-z_parent=h*f(z_next,rate,t_next), endpoint mixed controls, then compares full versus two half BE steps with its first-order factor. This changes the numerical method/interface, not the source equations, yield function or constitutive parameter/state meaning. Public UI already requests that schedule method. Endpoint implicit sampling is a reasonable mechanism to investigate this activation failure, but does not prove that BE error estimation cannot fail or that the new histories will pass.

The smallest next action is a **new separately identified study**, preserving all original failure evidence, candidate/source/reference hashes, parameter/state inventories, exact original108six-component histories including signs and crossings, their physical start times/durations and independent endpoint references. Keep original physical budgets, strict domain checks, refinement requirement and backend physical parity; add intermediate reference points only from independent existing mathematics, not fitted to compiled results. Freeze exact BE requests, controls, solver settings/budgets, assessor and admitted interface before new compiled requests. Do not quietly overwrite execution-v1 or relabel its failed136case study as passed. The new plan should explicitly identify which previously saved six BE observations informed method selection.

All interfaces in any eventual approval must be stated. The failed integrate-time midpoint interface remains excluded/unqualified for this candidate until an independently reviewed generic capability repair and separate qualification exist. The current continuous ODE formulation can remain unchanged if the approved transport is restricted to the qualified schedule interface; public records/UI/docs must expose that restriction. A source-correct model plus passing BE results cannot imply every generated physical-time API is qualified.

**Transaction semantics need an explicit new contract.** integrate_time_history initializes result.state/time to the whole incoming parent and changes them only on complete success. run_schedule instead retains the last committed sample on a later schedule failure. Its internal advance_controlled rejects the attempted sample transaction, while prior accepted samples remain in returned history. Accordingly, the original whole-call rollback assertion cannot simply be copied to the schedule API or waived without disclosure. Freeze assertions for exact last-committed-sample preservation, no failed-stage state exposure, repeated trials, actual complete-state/clock restart, invalid control/domain rejection and same-instance recovery at the documented schedule boundary. Retain partial histories as such. If whole-history rollback is required by a consumer, that consumer must implement and qualify it separately.

This diagnosis finds no need to alter source equations or loosen independent scientific-accuracy gates. It does not authorize a revised numerical policy after seeing its new failure; any later failure stays retained under its exact study identity. Generic midpoint branch-crossing remediation is a separate capability task.

## Reproduction and files

`python3 -B docs/ingestion/bingham-comsol63/time-crossing-review-v1/diagnose.py`

This script performs scalar arithmetic and reads saved outputs only. It writes DIAGNOSTICS.json and INPUT-BINDING.json here. DIAGNOSTICS includes42failed direct budget comparisons, all six saved schedule physical diagnostics, exact first-case values and explicit midpoint alias stages for zero/negative initial stress. INPUT-BINDING hashes the actual raw/status/diagnostic files, source references/receipts, original study/oracle/cases, frozen source archive index, build-input manifest and inspected time/schedule headers. No compiled artifact executes.

No prospective BE-study approval has yet been issued: the exact new request/assessor/freeze is not available in this assignment. No final E5 decision is made. Parent should present that concrete revised study for prospective review before new compiled observations.
