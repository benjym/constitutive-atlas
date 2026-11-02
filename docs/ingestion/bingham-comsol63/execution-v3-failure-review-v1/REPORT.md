# Independent diagnosis: capped BE v3 pure-shear rejection

Decision: **changes requested; no actual numerical or E5 acceptance.** Reviewer `/root/bingham_review`. This source/saved-output diagnosis performs no compiled execution, material call, build, model/reference/gate modification or setting search. The running full collector is untouched.

## Observed response, not a final-state accuracy error

`native-partial-snapshot.json` retains the exact 110-row partial output observed here, SHA-256 `92311cd085d49e0e6e6e1314a15ce53b689232a8a519eea074bbfbb100e4009a`. It is not a final 136-case classification. The selected requests are `radial-channel-3-z100000-d-0.012`, channel 4 and channel 5 equivalents. Each returns `ok:false`, message `schedule solve failed in segment constant-rate; last committed sample retained`, with only the initial point and segment-entry right point. Their complete states are identical, including alpha zero. The two saved stdout repeats agree.

No final sample exists. Comparing the retained incoming state with the final reference would misclassify this rejection as a completed-endpoint physical error. The original frozen assessor will correctly fail the unsuccessful response. The bounded cap's resolution of earlier examples does not qualify these rejected cases.

## Source mechanism

The generated model computes `q=sqrt(1.5)*norm(sdev)` and `lambda=max(q-Y,0)/eta`. `amax` selects the active operand when it is strictly greater; Jet comparisons use values, and the active operand carries its active derivative. All quantities here are finite and q is far from zero. The model explicitly checks alpha >= 0 for every evaluation, including Newton line-search trials. That domain restriction is scientifically appropriate.

`controlled_backward_euler` initializes unknown material state to the incoming state, before applying the endpoint strain increment. It evaluates the residual/Jacobian there. It then tries positive Newton-direction fractions 1, 1/2, ..., 1/2048, rejecting any trial whose generated evaluation fails. After all fail, `advance_controlled` subdivides and retries from the same unchanged incoming state.

For a single positive Mandel shear let `e=eps_shear`, `p=eps_vp_shear`, `k=sqrt(1.5)`. Then `q=k*2G*(e-p)`, `p_prime=k*lambda`, `alpha_prime=lambda`, and prescribed `e_prime=D`. For the saved incoming e=`0.004082482904638631`, p=alpha=0, generated-style binary64 evaluation gives:

- shear stress `81649.65809277262 Pa`;
- q=`100000.00000000001 Pa`, slightly above Y;
- lambda=`7.275957614183426e-19 /s`;
- unloading D=`-0.009797958971132713 /s`.

Thus the initial Jacobian uses the active branch. In this one-shear subspace the exact local Newton linearization gives `delta_e=hD`, `delta_p=k delta_alpha`, and

`delta_alpha = [h lambda0 + h² k 2G D/eta] / [1 + (3G/eta)h]`.

This direction is negative whenever `h > 6.063298011819521e-17 s`, substantially below the allowed minimum step. At the first eligible dyadic full trial h=`0.000244140625 s`, delta_alpha=`-7.149938987185533e-10`; even its smallest line-search fraction gives negative alpha `-3.491181146086686e-13`. At h=`3.637978807091713e-12 s`, delta_alpha is still negative `-1.5881603063135449e-25`. All twelve positive line-search fractions remain outside the model domain.

The independent script checks this sign for every eligible initial dyadic step from the cap-limited first trial down to the minimum-step/depth limit. Further subdivision does not change the incoming state, branch derivative or alpha boundary. Eventually recursion cannot proceed. This source-derived mechanism explains all three saved pure-shear rejections. It is not an instrumented observation of each native Newton iterate, and no such internal trace is claimed.

The distinction matters: the active derivative at q>Y is locally correct, and the alpha-domain rejection is correct. Their interaction with the previous-state initial guess and simple Newton backtracking lacks a domain-valid path to the endpoint's inactive branch. This is a generic constrained/nonsmooth solve-globalization gap, distinct from the prior zero-defect step-estimator gap. Reducing maximum step alone cannot resolve this sign obstruction at permitted steps.

## Reference and representation checks

The frozen continuous reference starts at nominal signed z=Y and unloads elastically to the opposite yield boundary before flowing on that branch. Independent elementary integration gives final z=`-232196.16904792876 Pa` and alpha=`0.004926794365069039`, matching each frozen final reference within `1e-8 Pa` in the stress conversion and `1e-15` in alpha. It is a regular admissible continuous solution.

Strictly, the saved binary64 initial strain interpreted as an exact real number has q=`100000.00000000001125948... Pa`, not exactly Y. Its initial overstress is about `1.126e-11 Pa`; the source exit-flow bound delta²/(2v eta) is below `1.321e-35`. This minute representational difference cannot explain or justify a solver failure and is far below the original physical error floors. No reference, source-law or domain change is indicated. The failure is not evidence that the prescribed unloading history is physically inadmissible.

## Smallest separate generic capability task

Prepare a distinct controlled-BE domain-boundary globalization task. A minimal candidate could supply a validated endpoint/time predictor or another domain-aware nonsmooth Newton strategy that can move from the incoming active branch to a valid inactive endpoint without committing negative accumulated state. It must work through generic model evaluation and preserve the generated domain checks, coupled state equations and mixed-control residual. This diagnosis does not approve an unseen algorithm or establish that any particular predictor fixes every case. A Bingham-specific kernel, changing q/Y, clipping accepted alpha, weakening domain checks or changing scientific gates is not justified.

Freeze generic analytic boundary fixtures before new compiled observations: exact/representably adjacent yield states with alpha zero, inward and outward rates, all pure-shear components and rotated directions, and a constrained accumulated-history component. Challenge the interaction of initialization, active derivatives, domain checks and backtracking; include ordinary nonlinear/mixed-control regressions and original crossing counterexamples. Preserve all existing failure outputs and retain the complete original 136-case physical/reference/refinement/parity/transaction suite. Require exact source binding, independent prospective review and actual native/Wasm evidence for a subsequent generic fix/study.

The collector may finish unchanged to retain its full outcome. No Wasm qualification or public scientific approval follows from this partial diagnosis. Final assessor results and complete v3 failure evidence remain to be bound separately.

## Reproduction and binding

Run `python3 -B docs/ingestion/bingham-comsol63/execution-v3-failure-review-v1/diagnose.py` from the original isolated tree. It reads only the retained snapshot and frozen cases and performs local algebra/reference calculations. It never rereads the growing raw file into the saved fixture and runs no material trajectory or backend. `DIAGNOSTICS.json` records exact values and sign checks; `BINDINGS.json` binds the snapshot, script, report, case/freeze, relevant generic headers, generated source and candidate definition.
