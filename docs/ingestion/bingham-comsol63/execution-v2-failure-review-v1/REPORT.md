# Independent diagnosis of execution-v2 backward-Euler failures

Decision: **changes requested — current numerical qualification fails; no E5 approval.** This is a source and saved-output diagnosis, with no compiled execution, build, material call, or author-file change. Reviewer: `/root/bingham_review`.

## Bound evidence and scope

`native-partial-snapshot.json` retains the exact 46-row partial collector output observed during this diagnosis, SHA-256 `ba1643ccc6c662bb74fe329e6729a17a66e193469c57010f429b60c764a7c4c4`. Collection was still running; this report does not classify the eventual complete 136-case run. `BINDINGS.json` binds the plan, cases, assessor, prospective freeze, source headers, and source analytical references. The unchanged v2 freeze is `2aa8e5e4b3ed4dce7fc74fd290cbf5adf2fef96a6afc344fbf7e13da598b9f0a`. No acceptance gate was changed. `diagnose.py` is an independent scalar calculation using Python's standard library; `DIAGNOSTICS.json` retains its results.

## References independently agree with the source law

For channel 0, write deviatoric stress as `s = (3/2) N z`, with `N = (2/3,-1/3,-1/3,0,0,0)`. Then `q = |z|`, prescribed deviatoric strain rate is `N d`, and the source law reduces to

`z' = b - a sign(z) max(|z|-Y,0)`, `alpha' = max(|z|-Y,0)/eta`,

where `b = 2G d`, `a = 3G/eta = 1.5 /s`, `G = 1e7 Pa`, `Y = 1e5 Pa`, and `eta = 2e7 Pa s`. On an active branch with sign `S`, `z(t) = S Y + b/a + (z(0)-S Y-b/a) exp(-a t)`. The yield exit follows directly by solving `z(t)=S Y`; the middle inactive interval is linear. Integrated alpha follows from `alpha_increment = S [b dt - delta_z]/(3G)` on each active branch. This calculation does not import the author oracle or model interpreter.

| Case | Independent exact final z (Pa) | Saved native final z (Pa) | Exact alpha | Saved native alpha |
|---|---:|---:|---:|---:|
| z0=200000, d=-0.012 | -214818.77470288426 | -214530.96587502904 | 0.0036606241415657174 | 0.0036025958083705503 |
| z0=-200000, d=0.003 | -30110.51873981471 | -30451.852483392973 | 0.0016629827086728428 | 0.0016516049172244556 |

Both independently computed endpoints match the frozen references within `1e-8 Pa` in z and `1e-15` in alpha. The stress observable is `sigma_xx = (2/3)z` for these trace-free cases. The discrepancy exceeds the original physical budgets; there is no evidence here supporting a reference change.

## Generic BE estimator can miss active-to-inactive flow

`controlled_residual` in `cpp/include/atlas/schedule.hpp` evaluates the rate at the backward-Euler endpoint. `advance_controlled` compares one full step against two halfsteps and accepts when their weighted state/strain difference is at most one. It has no independent activation-transition safeguard. A nonlinear residual measures the endpoint discrete equation, not the continuous-path error.

The scalar BE solution is available without iteration: set `trial = z0+b h`; if `|trial| <= Y`, the endpoint is `trial`; otherwise it is `(trial+a h S Y)/(1+a h)`, with `S = sign(trial)`. Plastic signed amplitude increases by `(trial-z1)/(3G)`, and alpha by its absolute value.

For the negative-initial case, independently applying this formula with the production step-doubling weights reproduces the saved endpoint to roundoff and exactly reproduces **62,278 accepted halfsteps**. At elapsed time `0.75 s`, a `0.25 s` trial starts at `z=-105451.85248339339 Pa`, still on the active negative branch. Its first halfstep endpoint is `-97951.85248339339 Pa`, and both full and two-half endpoints are `-90451.85248339339 Pa`. All endpoint evaluations are inactive. Both numerical paths therefore retain identical plastic state and alpha and return estimated error **zero**, although the continuous solution accumulates positive flow before exiting yield. Later small steps cannot recover that lost history.

The positive-initial case supplies another exact-arithmetic counterexample: a one-second trial from `200000 Pa` at `d=-0.012/s` gives a first-half endpoint `80000 Pa` and full/two-half endpoints `-40000 Pa`, again with zero estimated flow and error. The independent scalar adaptive run takes this partition and differs from the saved native partition; it is a mathematical estimator counterexample, **not** an asserted reconstruction of that native trajectory. Production strain/state roundoff can select different partitions. The negative-initial reconstruction already establishes the defect against actual saved output.

This is the same class of nonsmooth branch-crossing blind spot as the retained original midpoint failure, with different sampling locations. Tight tolerances and large counts on smooth pieces do not prevent a zero-defect crossing step. Neither Newton convergence nor backend agreement can establish the missing physical accuracy.

## Smallest next action

Create a separately owned generic adaptive-time capability task covering both controlled BE and the existing midpoint path. It must detect or safely resolve state-dependent activation transitions that make full and subdivided endpoint/stage estimates coincide despite nonzero path evolution. The implementation may use a justified generic defect/variation guard or an explicit generic event contract; this review does not approve an untested particular algorithm or infer undocumented event metadata. It must preserve generic model evaluation, Newton, transaction, budget, and failure contracts; a Bingham-specific handwritten kernel is unnecessary.

Freeze independent piecewise reference fixtures and numerical policy before new compiled observations. Include active-to-inactive and inactive-to-active transitions, both signs, reversals spanning both branches, holds, and the two zero-defect examples above; retain all original Bingham cases and physical gates. Require demonstrated refinement and native/Wasm checks after independent prospective review of the exact fix. Output sampling or a smaller maximum step alone is not evidence that the generic estimator is corrected; changing a numerical study would need its own prospective identity and cannot erase these failures.

Retain the original midpoint failure, this unchanged BE study and its final collector output. No Wasm qualification, packaging scientific approval, or E5 acceptance follows from this diagnosis. The collector may finish unchanged to preserve the complete failure record.

## Reproduction and limitations

The retained scalar diagnostics were produced by `python3 -B docs/ingestion/bingham-comsol63/execution-v2-failure-review-v1/diagnose.py` from the isolated delivery tree. That script reads the growing author collector file and rewrites only this owned review directory; rerunning later produces a new snapshot, so preserve the bound present snapshot and results first. It runs no material engine. This review independently resolves two failures and the estimator mechanism; it is not a full-run assessor or a complete trace of every native internal substep.
