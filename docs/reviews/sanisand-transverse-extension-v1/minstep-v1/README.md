# Single-configuration minimum-step localization

Completed 1 November2026 under DIAG-sanisand-transverse-extension-v1. This is
an additive follow-up to the [terminal study](../RESULTS.md). It localizes the
minimum-step failure in one original configuration, **not a repair or a pass**.
Original continuous/native failures, model and numerical gates remain unchanged.

## Observed cause

The unchanged80digit/tolerance1e-10 variational configuration for extension,
e=0.907,p0=20kPa reproduces `diagnostic minimum step`. Python `sys.settrace`
observes the original frozen `advance` and `variational` functions; no integration
arithmetic, trial selection or budget is replaced. The three pre-run observer
tests verify unchanged accepted arithmetic, rejection behavior and trace restoration.
The original source hashes and observer bytes were frozen before this replay.

At parameter approximately0.0051007797825, the fabric variation is still zero,
while the stress/backstress variations have magnitudes approximately1.41e49 and
9.17e48. Dilatancy changes from positive to negative within the rejected RK trial,
activating fabric evolution. The componentwise relative-error norm uses
`max(1,abs(high_component))` for each variation separately. Its denominator for
the newly activated fabric component is therefore1, while other components are
already enormous. This demands vanishingly small steps at activation.

[The exact rejected-trial replay](replay.json) reproduces all high/low state values
and the original maximum error4.84744e-8 against tolerance1e-10. The worst component
is29, the fabric yy-minus-zz variation. The rejected trial h is about2.49463e-30;
its next h is6.51847e-31, below the original1e-30 minimum. Recent accepted trials
have zero estimated error for that component before activation; the captured
rejection sequence shows the subsequent step collapse.

[The domain replay](domain.json) observes positive pressure, positive fixed-memory
distance and positive loading denominator at all stages of this saved trial;
the smallest denominator is about1.43849e7. The evidence localizes a numerical
error-scaling problem in the **independent variational diagnostic**. It does not
establish a physical singularity or remove the separate transverse sensitivity
of the selected law. The earlier single unsupported stage rejection is retained
in the trace; it is not the immediate reason for the terminal step collapse.

For explanation only, dividing the rejected variation difference by a common
variation amplitude gives about3.44e-57. That comparison was not used to accept
any step, alter a gate or declare the original study passing. Changing an error
norm after observing failure would require a distinct prospective study.

## Evidence and verification

`saved/` contains the failure state, prior24attempts, partial completed samples,
error estimates, domain-exception counts and progress. `run-process.json` retains
exit2. Both exact rejected-trial and domain replays complete without accepting or
committing another state. Five observer/replay-corruption tests pass. No builds,
compiled calls, candidate updates, author code or experimental fits occur here.

```sh
python3 docs/reviews/sanisand-transverse-extension-v1/minstep-v1/verify.py
```

The verifier is saved-only, checks all pins and replays the last rejected trial.
It does not repeat the independent trajectory. The original26-run study is not
restarted; this single instrumented configuration is terminal too.

## Bounded conclusion and next action

The current diagnosis cycle is delivered: local continuous transverse growth,
proper-rotation residual/Jet covariance, independent discrete Jacobian agreement,
large symmetric-branch amplification and the diagnostic minimum-step cause are
separately evidenced. This does not provide a multiple-root/Newton-iterate
certificate or scientific admission, and leaves the original81-path qualification
failed. Source identity remains the project fixed-memory variant of
[Dafalias & Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29).

Next freeze a distinctly named homogeneous-variation study for **only the missing
case's three configurations**. Represent the linear homogeneous perturbation by
a commonly rescaled vector plus accumulated amplitude; prove exact reconstruction
and preserve all27base variables and the source law. Keep original output
precision/refinement gates and test the rescaling algebra before execution.
Report its new coordinate/error-control contract explicitly; never relabel v1 as
a pass. Reuse the five completed original case groups by exact identity rather
than rerunning them or the eight nonlinear perturbation runs. No material solver
change, forced symmetry, reduced constitutive model or website installation.
