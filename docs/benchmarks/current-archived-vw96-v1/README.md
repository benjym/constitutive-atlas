# Current versus archived VW96: bounded synthetic comparison

**All frozen compatibility checks pass** for the two exact Atlas executables
on the synthetic states and paths below. This is a narrow implementation
comparison, not experimental validation or general engine equivalence.

## Fixed inputs and prospective limits

The [policy](policy.json) and [code freeze](freeze.json) were written before any
comparison calls. [Study code](study.py) generates 22 serial commands: two
catalogue queries, six raw-law evaluations, two zero increments and twelve
laboratory runs. No build, fitting or experimental data access occurs.

Both engines receive the same nine ordered parameter values, taken without
retuning from the existing file-initial density3 seed0 fit. This is one fixed
vector, not a published source-matched parameter set. Both start at synthetic
isotropic effective compression 100 kPa and void ratio 0.82, with Mandel shear
components zero. Compression, extension and Mandel shear raw-law directions
are declared in the policy. The paths are 1% drained/undrained monotonic axial
compression and a 0.2% sinusoidal drained reversal, at 32 and 64 caller increments.
These are synthetic controls, not an acquired experimental trajectory.

Prospective maximum differences are 10 Pa for stress components and p/q/u,
1e-7 for void ratio and strain components; raw-law difference must be at most
1e-12 after scaling stress by 100 kPa and void ratio by 1. Zero increment must
preserve state exactly. These are narrow software compatibility criteria,
not material accuracy or local integration-error bounds. No gate was altered.
Caller endpoints, complete point counts, parameter/initial/control echoes,
axisymmetry, drained lateral stress and undrained volume constraints are checked.
Reported error/counters are diagnostics, not physical-error guarantees.

## Results

The three raw-law directional responses match exactly; both zero increments
preserve state. All six path comparisons pass. The table gives maxima over
all caller endpoints and tensor/state components. Substep/rejection totals are
identical in both engines; the final column applies to each engine.

| Path | Caller increments | Max stress difference [Pa] | Max void-ratio difference | Max strain difference | Substeps / rejections, each engine |
| --- | --- | --- | --- | --- | --- |
| drained | 32 | 5.82e-11 | 0 | 6.51e-19 | 260 / 98 |
| drained | 64 | 8.73e-11 | 1.11e-16 | 6.51e-19 | 256 / 64 |
| undrained | 32 | 1.46e-10 | 0 | 0 | 328 / 132 |
| undrained | 64 | 1.46e-11 | 0 | 0 | 328 / 100 |
| drained-reversal | 32 | 2.91e-11 | 0 | 8.67e-19 | 456 / 196 |
| drained-reversal | 64 | 5.82e-11 | 0 | 1.73e-18 | 458 / 165 |

The largest stress-component difference is 1.4552e-10 Pa; the largest p/q/u
difference is 1.0186e-10 Pa. Differences are at floating-point roundoff scale
for this suite; this is not a cross-platform bit-reproducibility claim.

The within-engine 32/64 caller-grid changes remain separate descriptive results:
about 5.404 Pa maximum stress change for drained compression and 3.526 Pa for
reversal, with at most 2.621e-7 void-ratio change. Near-zero undrained grid
changes do not establish exact integration. Two resolutions do not prove
convergence or order; no refinement sweep follows from this packet.

## Identity and reproducibility

- Current executable SHA `960d6f8ebcc0c3296555dd6e294a3650a5ec2318108d30850216ee5a69e4f574`,
  built from commit `6ff25a9fb01de0fa9360c1bd04149877490319ef` with the
  [current source/build receipt](../current-source-build-v1/README.md).
- Archived executable SHA `c075e4010ad3bbaa4e299647d1a86d804b98eb8692f15c5a01e0e65b5db42cd7`;
  its exact source/build identity remains unresolved. It is our archived Atlas
  executable, not supplied author code.
- Both compiled catalogues bind VW96 to the pinned model bytes, allowing only
  source metadata and parameter labels to differ. All mathematical fields,
  parameter order/defaults/bounds, state and integration declarations match.
  No existing model or schema was migrated.
- Both invocations use built-in integration defaults. The current source and
  recorded historical source declare matching default settings; the archived
  binary/source association is still unproven. Common nondefault settings
  were not tested.

[Full synthetic observations](observations/processes.json) retain all 22 actual
commands, integer-zero returncodes and exact stdout/stderr hashes.
[Scalar results](observations/results.json) include diagnostics and descriptive
caller-grid changes. Public pinned input copies permit a saved-only audit even
without the private historical paper tree or either executable:

```sh
python3 docs/benchmarks/current-archived-vw96-v1/check_saved.py
python3 -m unittest discover -s tests -p test_vw96_engine_comparison.py -v
```

The audit exactly reconstructs the scalar results without executing C++.
[Six checks](tests.log) pass: saved reconstruction; substituted command,
nonzero returncode, altered input echo and missing point are rejected even
with rebound receipt hashes; a consistent 11 Pa response perturbation yields
a retained **failed** compatibility gate rather than a false pass.
These are evidence/software checks, not independent scientific review.

To intentionally repeat native observations, the original exact executables
and repository input paths in the policy must exist:

```sh
python3 docs/benchmarks/current-archived-vw96-v1/study.py run /private/tmp/atlas-vw96-engine-replay
```

Use a new output directory and coordinate serial execution. Never substitute a
newly built historical-looking executable or overwrite the original observations.
Receipts and hashes detect accidental changes; they are not signed attestations.

## Boundary and next delivery

The endpoint-defect integration change is documented in the
[historical partition diagnosis](../kfs-partition-diagnostic-v1/README.md).
This suite shows it has no material effect on the chosen VW96 paths/vector.
It does not cover every state, parameter, protocol, adaptive branch, formulation
or acquired-order experiment. Original reports, failed nonnested refinement,
source-state ambiguity and independent review gates remain unchanged.
No website or paper was edited or deployed by this study.

Next freeze one complete existing development-test replay under the pinned
current executable, preserving its parameter vector, initialization and acquired
loading order. That would connect this current build to one actual development
comparison without rerunning fits or reopening the completed refinement branch.
Independent source/scientific review remains a separate admission gate.
