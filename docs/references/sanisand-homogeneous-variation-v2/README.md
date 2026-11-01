# SANISAND homogeneous-variation diagnostic v2

This is a bounded replacement numerical coordinate study for three previously
failed **independent reference diagnostics**, not a replacement model or a new
native qualification. See `assessment.json` for the terminal outcome.

## Terminal result — 1 November 2026

All three new ODE configurations completed. Ten preflight tests pass. Exact
normalized-coordinate reconstruction passes. Reusing the original completed
records, the **original output gates pass** for all six case groups: maximum
arithmetic difference `8.0031e-72`, temporal difference `1.2011e-8`, and nonlinear
swap error `1.8649e-76`. The new case's endpoint linear stress-mode gain is
approximately `1.1202e263`; it describes infinitesimal linear sensitivity, not a
finite stress prediction.

**The full frozen v2 assessor fails** its additional base-reference coordinate
binding. It demanded `1e-70` coordinate agreement against a reference archive
that serializes fewer digits. The largest stored-coordinate difference is
`4.4904e-37`. This was an assessor design mistake: the archived representation
cannot support the requested comparison. The frozen assessor, criterion and
failure receipt remain unchanged. A post-observation saved-only `report.py`
separates the original passing output audit from this failed additional binding.
It does not replace the gate. The descriptive index-matched base difference is
`3.1806e-11`; it is not a passing base-binding claim.

Original v1 audit and native qualification remain failed. No numerical process
is left running. This packet closes the bounded execution/diagnosis task only.
No follow-up integration or revised coordinate gate is scheduled here.

## Question and method

The [retained minimum-step diagnosis](../../reviews/sanisand-transverse-extension-v1/minstep-v1/README.md)
located error-control collapse when a newly active fabric perturbation starts
near zero while stress/backstress perturbations have already grown enormously.
The original 18-run study failed and remains unchanged.

For the homogeneous linear system `phi' = M(base) phi`, represent
`phi = 10^e psi`. Between accepted steps, `e` is constant, so `psi' = M(base) psi`.
After an accepted step choose integer `s = adjusted(max(abs(psi)))`, replace
`psi` by `psi * 10^-s`, and add `s` to `e`. This changes coordinates without changing
the represented perturbation. Decimal power-of-ten scaling avoids arbitrary
normalization division. The base's 27 Cartesian components are untouched by
this coordinate transformation. Its equations, source constants and initial
state come from the frozen independent reference, not the Atlas model or solver.

This explicitly changes **local variation error control**: the old componentwise
norm is now applied to normalized `psi`. Base error scales and equations stay
unchanged; adaptive steps can differ. It is not claimed to be the original local
error norm. Reconstructed `phi`, never `psi`, is used for the original precision
and temporal output gates.

## Frozen scope

Only `extension-e0.907-p20000`, at `(80,1e-10)`, `(80,1e-12)` and `(100,1e-12)`.
Each has entry plus 16 plastic output samples. Each sample interval retains the
20,000-attempt budget and minimum step `1e-30`. The original output gates remain
`1e-40` arithmetic, `1e-4` temporal and `1e-20` nonlinear proper-rotation error.
An additional base-reference gate is `1e-8` scaled state error.

`freeze.json` pins implementation, saved-only assessor, prospective policy,
ten passing preflight tests and the historical inputs **before integration**.
Rescaling tests check exact reconstruction/base preservation and independent
linear RHS/RK agreement. Assessor tests reject missing samples, incorrect
exponents, nonfinite coordinates and lost transverse symmetry.

## Evidence reuse and interpretation

The separately named composite audit reuses exactly the 15 completed historical
variation records, eight nonlinear records and six derivative checks. Only the
three failed variation records are substituted, with explicit v2 method identity.
It invokes the original saved-only assessor with its unchanged policy. No old
file, failure or numerical gate is overwritten. `runs/` retains each new record,
the composite result container and sample progress; `execution.json` records the
terminal process result. `manifest.json` binds the final packet.

A passing diagnostic measures instability of the selected project law's
antisymmetric mode. It cannot establish canonical source fidelity, scientific
admission, experimental validity or success of the failed 81-path native study.
The nonlinear checks remain the earlier single precision/tolerance diagnostic.
There are no new candidate/material integrations, compiled builds or public
model installations in this packet.

## Reproduction

From this directory:

```sh
python3 -m unittest -v test_rescale.py test_assess.py
python3 verify.py
```

Both commands use saved data/algebra only. To deliberately repeat the bounded
ODE study, from the repository root use a **new, nonexistent** output directory:

```sh
python3 docs/references/sanisand-homogeneous-variation-v2/generate.py /private/tmp/atlas-homogeneous-v2-repeat
```

## Stop rule and next roadmap decision

Stop this numerical branch after the three configurations and saved audit,
regardless of pass/fail. Do not launch another refinement ladder, tune the law,
force transverse symmetry or relax native accuracy thresholds to make it pass.
The next SANISAND task is a bounded source/scope decision: reconcile the selected
3D flow branch with the pinned source, document whether a restricted research
variant is useful, and retain unsupported production paths as failures. The
missing reversal source and independent admission remain explicit gates. This
study does not justify expanding the engine or delaying the other roadmap
source/review work.
