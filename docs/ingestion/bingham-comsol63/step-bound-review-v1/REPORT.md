# Independent review: source-only maximum-step analysis

Decision: **accepted for its stated analytical scope and as motivation for a prospective bounded empirical study.** This is not acceptance of an unseen study plan, a numerical guarantee for the compiled solver, or E5 approval. Reviewer: `/root/bingham_review`. Owned output: `step-bound-review-v1/`; no author files, compiled artifacts or material engines were changed or executed.

## Derivation

The finalized source analysis is `step-bound-analysis-v1/{README.md,analyze.py,results.json,handoff.json}`. Its README SHA-256 is `6c309e4975d8be0a4d212629968344e6f1c69e34e05daeb13be3b34ec064fd0c`. Its post-v1/v2-observation origin is explicit. Its arithmetic uses original source parameters and rate bounds rather than fitting saved errors.

The radial reduction is correct: `s=N z`, `N:N=2/3`, `q=|z|`, `z_prime=c-a sign(z)(|z|-Y)+`, with `c=2Gd`, `a=3G/eta`. For each original constant radial segment, f is nonincreasing and the scalar implicit resolvent is nonexpansive. The exact trajectory is monotone, its speed decreases, and `TV(z_prime) <= F0`. The sum of endpoint quadrature residuals therefore gives `Ez <= H F0`, where H bounds each committed BE step. Separating alpha trajectory error and right-endpoint quadrature error gives `Ealpha <= 2HTF0/eta`. The stress and plastic-strain component conversions are consistent with the Mandel norm and elastic law.

Thus the stated complete-segment exact-BE absolute-alpha-floor calculation, `H <= 3.846153846153846e-6 s`, is correct and deliberately conservative. The host cap would be twice this, because the generic schedule commits two halfsteps, not the discarded full-step trial. Its dyadic cost alone is 524288 accepted halfsteps over 2 s; additional adaptive restrictions and finite solver errors remain. This is not the proposed empirical-study cap and is not a finite-Newton certificate.

For an active exit omitted by an inactive BE endpoint, initial overstress delta satisfies `delta <= vH`. Exact integration gives `I=(delta-v tc)/(3G)`, with `tc=log(1+a delta/v)/a`. Monotonicity in delta and `x-log(1+x) <= x²/2` give `I <= vH²/(2eta)`. The inequality follows for all nonnegative x from its derivative, `x/(1+x) <= x`, and zero initial value. The immediate signed stress error has magnitude `3G I`; each plastic-strain component is bounded by `(3/2)|Ni|I`. Subsequent exact scalar evolution is contractive; Lipschitz alpha accumulation adds at most `a T I`. Therefore `(1+aT)I` is a valid bound for the isolated omission and its continuation. It does not bound all discretization errors along the actual numerical trajectory.

Independent 60-digit decimal arithmetic agrees with the finalized values:

| Quantity | Verified value |
|---|---:|
| Proposed host cap M | 0.0004069010416666667 s |
| Maximum committed BE halfstep H | 0.00020345052083333334 s |
| Omitted-exit alpha bound I | 2.483526865641276e-10 |
| Immediate scalar stress contribution | 0.007450580596923828 Pa |
| Maximum plastic-strain component contribution | 3.041686791657381e-10 |
| Isolated alpha contribution including continuation over 2 s | 9.934107462565104e-10 |

These quantities are below the original absolute error floors, but that comparison allocates no complete remaining error budget. The factor 1024 is a declared numerical resolution choice, not a vendor constant or a uniquely derived accuracy factor. The cap alone implies 16384 dyadic accepted halfsteps per 2 s request; it does not guarantee work-budget success.

## Finite Newton and scope

The conditional nonlinear-residual argument is consistent: with state scales one and h below one, an exact real residual bounded by tolerance implies state-balance forcing proportional to `tolerance*h`, rather than a fixed error per substep. The stated `4G sqrt(6) tolerance T` deviatoric-stress forcing bound and `6G tolerance T²/eta + tolerance T` alpha bound follow from contraction, six-component norm conversion and time integration for prescribed strain. They are conditional real-arithmetic estimates. A computed binary64 residual is not a certified bound on its real counterpart, and mixed controls introduce additional algebraic coupling. The source correctly leaves roundoff and finite-Newton qualification to actual evidence.

The event bound applies to constant radial strain-rate segments. It does not prove error control for noncoaxial loading, mixed/stress control, arbitrary parameter values or arbitrary histories. The vector extension is presented only as an analytical starting point. The scalar cap cannot be advertised as a proven universal public parameter envelope. The analysis itself retains these limits; no blocking source correction is requested.

## Review principle for a possible next study

A generic transition safeguard is needed for a claim of general estimator robustness. It is not a prerequisite for every explicitly bounded maximum-step numerical contract. A distinct, prospectively frozen empirical study using this cap can legitimately test the same complete law and exact named controls/histories. If all actual native/Wasm cases and original gates pass, the evidence may qualify that declared bounded contract. It does not establish untested neighborhoods of parameters, controls or histories.

Before execution, the coordinator must make a concrete new plan reviewable and freeze exact inputs. Required scope is:

- Retain all 136 cases, original physical histories, source law, parameters, references, actual-state restart, invalid/recovery and committed-prefix failure checks. Declare the maximum-step setting as the only numerical change, with an exact case-by-case delta and treatment of any originally tighter cap.
- Preserve every original state/stress, topology, determinism, parity and strict fivefold refinement gate. Declare how the cap applies to both coarse and fine diagnostics. Similar coarse/fine errors after a common cap would be a genuine refinement failure.
- Retain and disclose all v1 midpoint and v2 BE failures. Disclose this analysis and the new cap's post-observation origin. Do not relabel the new study as pre-observation parameter selection or as a corrected generic estimator.
- If adopted publicly, enforce the exact reviewed solver cap/settings and state the qualified named controls, nominal parameters and histories. A passing fixed-history suite alone does not qualify every value accepted by a broad input form. Keep direct midpoint and any other excluded interface outside the approval claim.
- Acquire actual full native/Wasm records under the unchanged gates, then perform separate final evidence review. No pass is assumed from the analytical bounds or prospective acceptance.

The smallest next action is a separately identified, exact frozen plan satisfying these requirements. An independent prospective review remains necessary before new material execution; final E5 remains dependent on actual results.

## Checks and correction of prior notation

`python3 -B docs/ingestion/bingham-comsol63/step-bound-review-v1/check.py` performs independent decimal arithmetic, seven logarithmic-inequality checks, five source pins and three finalized handoff pins. All pass. It imports no oracle, model interpreter or backend and makes zero material calls. `BINDINGS.json` binds the exact inspected analysis and supporting source inputs; `RESULTS.json` retains independent values.

`PRIOR-REPORT-ERRATUM.md` corrects a single stress-normalization prefactor typo in the retained `execution-v2-failure-review-v1/REPORT.md`. The correct convention is `s=N z`. Its script, scalar ODE, reference conversions, numerical results and diagnosis already use that convention. The original report and hashes remain unchanged.
