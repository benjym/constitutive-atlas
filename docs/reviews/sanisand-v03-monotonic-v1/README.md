# SANISAND v0.3 monotonic native qualification v1 — failed

NUM-sanisand-v03-monotonic-v1, executed 1 November 2026. The native study is
complete and **does not qualify the candidate**. The original frozen model,
parameters, paths, settings and acceptance gates are unchanged. Wasm was not built
or run: the policy stops qualification after native gate failure. No installation,
public catalogue change, source signature, experiment fit, push or deployment.

## Results

All 81 native recorded paths completed (48,546 saved full-state points,
48,465 material intervals). All 12 negative probes reject; all 12 following
recoveries succeed. Full incoming engine-state rollback, including a nonzero
temporary multiplier, passes where promised. The actual-parent trial, forced
failure, repeated trial, zero-load and binary64 full-state restart checks pass.
The normal C++ generator reproduces the earlier pinned hashes. One Release
`atlas_solver` target was built with `--parallel 1`.

The frozen assessor passes 77 of 81 trajectory checks; four N1024 paths exceed
the 0.01 scaled state-error gate:

| Path, all at initial pressure 20 kPa | Maximum scaled fine error | Largest error component |
| --- | ---: | --- |
| compression, e=0.735 | 0.02698797 | sigma_xx at endpoint |
| compression, e=0.833 | 0.01689095 | sigma_xx at endpoint |
| extension, e=0.735 | 2.32908324 | sigma_yy at endpoint |
| general shear, e=0.735 | 0.01110882 | sigma_xx at endpoint |

Stress error is divided by **initial pressure**, not current stress. Thus 2.329
means an approximately 46.6 kPa component error for the last extension case; it
must not be described as a 233% relative error in current stress. The four failed
checks reach their accuracy gate after passing the all-point layout/domain,
yield, trace, anchor, multiplier and control checks.

[The unchanged assessment](native-assessment.json) also reports two coarse-to-medium
refinement failures and unavailable refinement for the four failed fine paths.
[The separately identified saved-only audit](saved-diagnosis.json) retains
all 81 errors, all components and all refinement ratios, including failed paths:
extension e=0.735 has a fine/medium ratio about 103.55, extension e=0.833 has a
medium/coarse ratio about 1.0067, and extension e=0.907 about 31.39. No failed
path is discarded to obtain an accuracy or refinement pass.

## What the saved diagnosis establishes

Some low-pressure axisymmetric extension outputs lose yy/zz symmetry under
symmetric loading. At e=0.735, N1024 develops a maximum lateral stress difference
of about 69,048.91 Pa. The same case stays symmetric at N512 but loses symmetry
at N256. Other low-pressure densities show a similar partition-dependent effect.
This observation explains large component differences; it is **not a proof of
root cause**. Continuous-law transverse instability, residual transcription,
multiple discrete roots and numerical branch selection remain to be distinguished.
The smaller compression/general-shear fine errors are also retained separately.

## Prospective controls and checks

[execution-freeze.json](execution-freeze.json) binds the driver, independent
saved-output assessor, tests and input manifests before any build or integration.
The earlier [candidate/input/policy freeze](../sanisand-v03-research-freeze-v1/README.md)
and [independent continuous reference](../../references/sanisand-project-monotonic-v1/README.md)
remain authoritative. The source is
[Dafalias & Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29),
with unresolved canonical reversal and source choices recorded in those packets.
This study uses the explicitly named fixed-memory project variant, not canonical
cyclic SANISAND. Entry is externally partitioned at the reference yield coordinate.

The assessor imports no Atlas/DSL/author integrator. It checks every saved state,
all 18 full-state reference samples per request, input echoes and settings, reference
accuracy/refinement, yield/trace/control, negatives/recovery, actual-parent transactions
and eventual backend parity. Gamma is temporary and excluded from the 25-component
reference comparison, but included in promised full rollback and restart.

Twenty-four synthetic/mock self-tests pass, including deliberate corruption,
missing results, wrong settings/identity, temporary-state rollback, request/raw-output
binding, timeout retention and large-output transport. Synthetic sample-and-hold
fixtures exercise the assessor only and are never numerical evidence. An initial
self-test injected accuracy error at an unsampled knot; its failure and original
test bytes are preserved. The corrected test injects at a frozen reference sample.
No model or policy changed. The initial saved-only verifier also compared integer
object keys with their JSON string representation in the descriptive audit; its
failure and exact initial verifier/manifest are retained, and JSON normalization
corrects that comparison. The frozen numerical assessor is unchanged.
Real native assessment exit code **1 is expected**
and retained; the wrapper's successful execution does not convert that into a pass.

## Reproduction

From the repository root, saved-only verification:

```sh
python3 docs/reviews/sanisand-v03-monotonic-v1/verify.py
python3 -m unittest discover -s docs/reviews/sanisand-v03-monotonic-v1 -p 'test_*.py' -v
```

The verifier reads all 110 compressed raw process receipts, checks exact requests
against the freeze, recomputes the failed assessment and descriptive audit, and
verifies original build/process receipts. It does not build or run material code.
Compressed receipts retain complete raw stdout/stderr, parsed responses, actual
arguments, timings and return codes. Redundant temporary CSV/request files are
reconstructed from literal arguments instead of copied into the repository.

To repeat the native study in a **new** exclusive directory:

```sh
python3 docs/reviews/sanisand-v03-monotonic-v1/build.py native /private/tmp/atlas-sanisand-v03-new
python3 docs/reviews/sanisand-v03-monotonic-v1/run.py native /private/tmp/atlas-sanisand-v03-new/native/build-receipt.json /private/tmp/atlas-sanisand-v03-new/native-results
python3 docs/reviews/sanisand-v03-monotonic-v1/assess.py /private/tmp/atlas-sanisand-v03-new/native-results
```

The last command is expected to return 1 for this failed candidate. Do not launch
Wasm or widen gates to manufacture qualification. The Wasm prerequisite also
checks a passing saved native assessment before allowing its build.

## Next bounded action

Freeze a distinct low-pressure extension diagnosis using these actual native
parents and the independent law: audit lateral-swap residual/AD covariance,
identify onset and conditioning in the transverse mode, and compare the independent
continuous response under explicit small symmetry perturbations. Determine what
is source behavior and what is a discrete/implementation effect before proposing
a correction. Preserve the original three refinements and all failed evidence;
do not force symmetry, silently project histories, add a model-specific kernel,
or substitute a reduced axisymmetric formulation. No broad refinement campaign
or website work until this question has a defensible answer. Smaller truncation
errors require a separate prospective correction/refinement decision afterward.
