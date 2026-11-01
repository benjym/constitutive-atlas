# SANISAND transverse-extension diagnosis — work in progress

DIAG-sanisand-transverse-extension-v1, checkpoint 1 November 2026. This packet
advances the diagnosis of the [failed native study](../sanisand-v03-monotonic-v1/README.md).
The original candidate, inputs, gates and failed result remain unchanged.
No scientific admission, public installation, Wasm build or deployment.

## Established at this checkpoint

The [analytical derivation](DERIVATION.md) identifies an antisymmetric lateral
stress/backstress mode in the selected fixed-memory continuous law. Its transverse
flow coefficient at symmetric extension is `(9c-7)/2`, which is **-0.296** for
c=0.712. After entry on the positive plastic branch, the stress/backstress
linearization has determinant `-A*H/p<0`: one instantaneous eigenvalue is positive.
This establishes a local saddle in this project law. It does not quantify finite-path
amplification or prove that all of the observed native error has the same cause.
The compression counterpart has positive flow coefficient. This is new analysis
of the already-pinned equations, not a new source reading or an independent source
review signature. The original publication is
[Dafalias & Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29).

A separately frozen **compiled residual/AD covariance audit passes** at 39 actual
saved incoming/end-state/increment triples. It tests all current26, parent26 and
loading6 directional seeds, each before and after a proper rotation exchanging
y/z and reversing x. The generic adapter calls the unchanged normal-generated
residual and real Jet implementation; it contains no constitutive equations and
performs no material integration. All 4,524 evaluations succeed, covering 117,624
paired value/derivative components. Maximum scaled differences are about
1.04e-17 for residual values and 3.81e-15 for directional derivatives, below the
frozen 1e-8 gate. See [assessment](covariance-assessment.json) and
[prospective inputs/source freeze](covariance-freeze.json).

A descriptive [conditioning audit](native-conditioning.json) reconstructs each
26x26 current-state Jacobian in the solver's declared scales. The largest observed
infinity-condition estimate is about **191,354**, at extension e=0.833, initial
pressure20kPa, N256, point28. The inverse is computed at70digits from stored
binary64 AD entries. This is endpoint residual conditioning, not an exact-source
certificate or conditioning of unrecorded Newton iterates. The raw Jacobians,
inversion checks and all smaller cases are retained. No new acceptance threshold
is inferred from these observations.

The combined evidence supports an intrinsically growing transverse mode and
excludes a large violation of the tested rotation covariance in those generated
residual/AD probes. Covariance is **not independent derivative correctness** and
does not rule out all transcription, integration or branch-selection errors.
Twelve covariance-corruption/rotation/conditioning self-tests pass. One explicit
native diagnostic target was built serially with `--parallel 1`. No material
candidate, author program or new fit was executed in this checkpoint.

## Running independent study

[policy.json](policy.json) and [prospective-freeze.json](prospective-freeze.json)
freeze six base cases, three precision/tolerance configurations (18 variational
runs) and eight signed nonlinear perturbation runs. `study.py` uses the existing
independent full Cartesian Decimal continuous law. It integrates all27 stress,
backstress and fabric Cartesian values, with three analytic variation components
alongside the symmetric base trajectory. Nonlinear runs perturb yy/zz stress
at exact entry; there is no projection, reduced axisymmetric update or forced
symmetry. Derivatives of the analytic variation matrix are independently checked
against central differences of the full rate law at all16plastic reference samples.
The original zero-history/fixed-memory scope remains explicit.

This study was **still running** in the same observed process when this checkpoint
was written. [The live checkpoint](live-study-checkpoint.json) records the existing
handle/PID and expected private output paths; revalidate the handle rather than
restarting it. No completed numerical study result or numerical audit pass is
claimed here. `assess_study.py` is saved for the eventual numerical audit under
the already-frozen criteria.

## Reproduction and evidence

Saved-only verification of the completed checkpoint:

```sh
python3 docs/reviews/sanisand-transverse-extension-v1/verify.py
python3 -m unittest discover -s docs/reviews/sanisand-transverse-extension-v1 -p 'test_*.py' -v
```

The verifier checks exact frozen sources and requests, reconstructs actual-state
probe selection, repeats covariance/conditioning assessments from saved raw output
and preserves the distinction between delivered evidence and the running study.
It does not compile or integrate. Native configure/build/run receipts preserve
actual commands, stdout/stderr, input/output hashes and executable hash. Normal
Atlas source pins and the generated header remain bound to the earlier research
freeze. `native-output.jsonl.gz` preserves every raw diagnostic response; literal
requests reconstruct the whitespace input file exactly.

To reproduce the native adapter, use the exact configure/build commands in
`native-configure.json` and `native-build.json`, with a new build directory and
a stage restored from the original source/generator pins. The explicit target is
`atlas_transverse_probe`; never use a broad build target. The independent ODE
command is in the live checkpoint and source; its output must be a new exclusive
file. Do not launch a second copy while the existing study remains live.

## Remaining bounded work

Collect and audit the existing independent study, retain every failure and compare
linear and nonlinear perturbation growth. Then identify what additional
actual-parent/discrete-root evidence is needed before any solver correction.
The original four fine-accuracy failures and all three native refinements remain
open. No forced symmetry, reduced model, history projection, gate widening or
website work is authorized by this diagnostic result. The board stays WIP.
