# Terminal independent study and discrete-map results

Follow-up to checkpoint commit32a2ac5, 1 November 2026. The earlier README/live
checkpoint remains an exact historical record. **The process is now terminal**:
study exit2, original full-study audit exit1. Do not restart handle13608/PID24764.
No candidate, model, numerical gate, solver, reference corpus or earlier receipt
was changed. No new builds/material calls occurred in this follow-up.

## Independent continuous study

[All original output](continuous-v1/study.json.gz), [terminal receipt](continuous-v1/process.json)
and [failed original audit](continuous-v1/original-audit-process.json) are retained.
Fifteen of18variational runs complete; all three e=0.907/p=20kPa configurations
fail with `diagnostic minimum step`. All eight signed nonlinear runs complete.
The cause/location of the minimum-step failures is not captured by the original
receipt and must not be guessed. **The full prospective numerical audit fails.**

[The descriptive summary](continuous-v1/summary.json) includes failed coverage
explicitly. Among the five completed three-configuration groups, the maximum
arithmetic difference is about8.00e-72 and fine/medium difference about5.64e-9,
with the original scaling. These observations do not repair the missing sixth group.
All864analytic transverse derivative components agree with full Cartesian rate
central differences under the original1e-24 gate.

At e=0.735, p0=20kPa, the linearized endpoint stress-difference gain is about
2.43e51; the p0=100kPa and500kPa counterparts give about1.47e26 and5.81e9.
Compression p0=20kPa gives a gain about0.227 for the same initial stress mode.
These are infinitesimal gains, not predictions of unbounded physical stress.

The full nonlinear20kPa extension runs begin with signed stress-difference
perturbations of only1e-16 or1e-24 times initial pressure. Endpoint lateral stress
differences are about70.2kPa and63.5kPa respectively, with opposite signs when
the initial perturbation changes sign. The full100kPa runs also amplify those
perturbations substantially. The signed trajectories obey the expected proper
rotation closely; measured yield excess stays small. They use one precision and
tolerance only, so they are supporting diagnostic observations, not independently
refined finite-amplitude solution certificates.

This supports strong sensitivity in the selected continuous fixed-memory law.
It does not certify the canonical source model or prove every native error is
caused by the same mechanism. Source/reset/admission questions remain separate.

## Independent backward-Euler Jacobian and gain

[discrete-v1/audit.py](discrete-v1/audit.py) derives the current-state transverse
residual Jacobian directly, independently of the generated code. With N the
normal denominator, lambda the endpoint multiplier and gamma its rescaled value:

```
a = 2*G*lambda*f/N
h = (2/3)*gamma
j = h*ab/N
J_transverse = [[1+a/p, -a/p0], [-j*p0/p, 1+h+j]]
```

Fabric adds a one-way third row. The parent stress/backstress residual block is
minus identity, so the local incremental amplification is `inverse(J_transverse)`.
This is a linearization of the full3D residual; no reduced model is integrated.

The independent3x3formula matches **135saved real-Jet directional components**
at15actual symmetric saved states with maximum scaled difference2.66e-14
under the prospectively frozen1e-8 gate. This adds an independent partial derivative
correctness check to the previous full rotation-covariance check. It does not
qualify every derivative or a full-update tangent.

For all nine low-pressure extension histories, the map-product audit stops at the
**first exact binary64 symmetry loss**. It never projects an asymmetric history
back onto symmetry. Three native histories remain exactly symmetric to their
endpoints; their infinitesimal stress-mode gains are approximately:

| Actual native history | Local map-product gain |
| --- | ---: |
| e=0.735, N512 | 2.71e60 |
| e=0.833, N1024 | 1.09e148 |
| e=0.907, N1024 | 2.49e417 |

A successful nominal path can therefore remain on a very sensitive symmetric
branch. This does not make the asymmetric histories inaccurate merely by definition,
or make the exact-symmetry paths generally robust. It is not proof of multiple
roots at a particular unrecorded Newton iterate.

[The90/140digit replay](discrete-v1/precision-assessment.json) changes the largest
relative gain by only about4.58e-86, passing the separately frozen1e-60 arithmetic
gate. This verifies the arithmetic replay, not a rigorous perturbation bound for
the actual nonlinear integration. Four additional inverse/symmetry tests pass.
Original81-path accuracy/refinement failures remain false.

## Verification and remaining bounded work

```sh
python3 docs/reviews/sanisand-transverse-extension-v1/verify_results.py
```

This reads saved outputs only, replays the unchanged failed original audit, all
independent discrete checks, higher-precision arithmetic and descriptive summaries.
It also verifies the unchanged earlier checkpoint. The original process completed;
there is no live study remaining to wait for.

Next localize the minimum-step failure with a separately frozen, instrumented
**single** failed configuration, preserving the original run and budgets. Capture
parameter, trial step, error, domain/failure and partial state before rejecting;
do not rerun the full26-run campaign. Then record the supported scope and decide
whether further actual-parent Newton/root evidence is needed. No symmetry-forcing
workaround, source-law rewrite, reduced replacement model, gate widening or public
installation follows from these observations. The diagnosis board row stays WIP.
