# Retained v3 failures and prospective midpoint alternative

Independent followup, `REVIEW-lade-domain-control-v1`. No material advance, compiled execution, source/code edits or E5 approval. The v3 native domain study remains FAIL2/94 checks with704 requests. The separate triaxial study remains FAIL4/6 active-plastic refinement trends, despite all24 requests succeeding and meeting their individual reference bounds. Lifecycle38 and disabled legacy57 checks pass. The stricter supplement remains FAIL1/3825 checks: coarse loose half-critical source error0.005812849416886468 exceeds0.005. These are distinct retained results; no later candidate or study rewrites them.

## Original rejection diagnosis

Raw request0360 is loose99-percent-critical hydrostatic unloading with path tolerance1e-7, maxdepth20, maxacceptedhalves200000 and reservedtrial cap600000. It returns the exact original parent,170958 accepted internal halves and512901 reserved trials. Thus neither aggregate budget was exhausted. The frozen recursive code has only the depth boundary left as the terminating recursive budget condition; a failed trial can trigger recursion but cannot directly return failure before depth exhaustion under these counts. The final raw message does not identify why the deepest macrostep was rejected, so distinguish the hard stopping condition from the last local trial cause.

Accepted fractions sum exactly65331/65536=0.9968719482421875 of the supplied99-percent-critical request. The smallest accepted half fraction is2^-21, corresponding to a depth20 macrostep. Independent exact scalar FE replay of this accepted partition gives the internal pressure about2.04294e-9Pa. At that scalar state the next depth20 full-versus-two-half metric is about1.00013255e-7, just above the frozen1e-7 tolerance; a depth21 macrostep would give about2.49966e-8 but is forbidden. This strongly supports estimator-driven depth exhaustion. It is not an exact compiled replay: raw output omits internal states and per-attempt rejection reasons, and nonlinear residual errors may affect the precise last threshold. No claim of an exclusive nonlinear cause is made.

Depth/work/tolerance relaxation is not justified by this diagnosis. The retained failure is legitimate under the frozen policy.

## Midpoint elasticity assessment

Proposed v4 model SHA256120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63 changes the v3 elasticity to

    smid=(s+sn)/2
    E=Kur*pa*lambda_min(smid)^n.

It adds the same safe lazy repeated-min branch for smid and positive midpoint-pressure domain. It keeps previous-pressure residual normalization, endpoint plastic flow/work, q/H representation, frame, tensor conventions and domain limits. This is minimum eigenvalue of the mean tensor, not mean of two scalar minimum eigenvalues. The exact model diff has no unrelated source-law change. The first-order general split/second-order elastic description is appropriate. Before a v4 freeze, copied policy names referring to pre-v3 observations or v3 identity must be corrected; this note does not approve an unfinished v4 study configuration.

For exact positive hydrostatic/proportional endpoints u>v>0, midpoint elasticity consumes unloading strain

    Lmid=(u-v)/(Kur*((u+v)/2)^n).

Since g(s)=s^-n has g''=n*(n+1)*s^(-n-2)>0, midpoint quadrature gives

    Lmid <= integral(v to u) ds/(Kur*s^n).

Summing over arbitrary accepted positive steps, including two-half acceptance, telescopes to a total strictly below source extinction for0<n<1. The proportional SPD reduction uses Kur*(.9)^n, so the same proof applies after consistent rotation. The midpoint residual is monotone in v on the positive scalar branch and has at most one positive endpoint. This retains the desired exact-arithmetic one-sided lifetime property while reducing elastic local truncation error. It does not prove changing-direction/plastic all3D event fidelity or exact event enforcement under finite solver tolerances.

`check_v3_failure_midpoint.py` independently verifies the raw/frozen-study binding, replays accepted scalar fractions, checks10 high-precision midpoint quadrature inequalities and eight rotated midpoint known-endpoint residuals over60000 to1e-24Pa. It never advances the candidate material or runs compiled artifacts.

## Prospective refinement design

A distinct v4 joint-refinement study with the same24 external cases, source references, reference bounds and decreasing-error criterion is scientifically legitimate and stricter than holding the path tolerance fixed. Choosing path tolerance1e-7*(100/N)^2 refines active-plastic local O(h^2) control with external resolution and avoids treating the fixed-tolerance adaptive plateau as a convergence study. Also refine inner residual tolerance, for example2e-10*(100/N)^2, to retain the original0.002 residual/path tolerance ratio; fixed2e-10 residual tolerance is too close to the proposed finest3.90625e-10 path tolerance to presume estimator precision.

Retain maxdepth, work and source-error bounds. Freeze the exact rule before compiled v4 observations and preserve a separate fixed1e-7 diagnostic. Passing a new joint-refinement study would not make the failed fixed-settings v3 gate pass. Strict monotonic reference error is still an empirical required gate, not a theorem under adaptive branch changes/error cancellation. General active-plastic accuracy remains first order; midpoint elasticity does not make the endpoint plastic update second order.

The midpoint model is a credible separately identified numerical realization for prospective testing. Exact staged v4 source, policy, checkers and freeze still require review before any approval-to-study or qualification verdict.
