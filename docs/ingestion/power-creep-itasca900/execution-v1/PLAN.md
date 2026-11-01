# Power-creep continuous execution v1 — prospective freeze

Frozen before the first compiled observation on 2026-11-01. This is the new
execution task; the original ingestion packet and its failures remain unchanged.

## Definition decisions

The runnable identity is `power-creep-itasca900-both-active-ode`. It implements
the primary manual's explicit **Both Components Active** formula, not the
thresholded whole family. Both mechanism rates add for all stresses. No finite
upper threshold, event location, smoothing or switching convention is hidden in
the implementation. The unresolved general threshold formulation is not claimed
as supported.

- PC-01: use the deviatoric strain rate in source Eq. (2), together with elastic
  volume Eqs. (4)/(6). Do not transcribe the inconsistent printed Eq. (7).
- PC-02/05: select the published both-active specialization; threshold equality
  and crossing remain outside this executable identity.
- PC-03: restrict the model to `n_i>=1`. At zero deviatoric stress use its
  continuous vector limit. In `dot(s)`, the linear mechanism has its finite
  decay coefficient and higher-power mechanisms have zero linearized decay.
  Lazy `select` avoids computing a negative power or `0**0` at the origin.
  Sublinear exponents are rejected, not clipped.
- PC-04: declare `b_i=A_i*p_ref**n_i` in 1/s and use dimensionless stress ratios.
  `p_ref` is explicit; changing it while holding `b_i` fixed changes the law.
- PC-06/07: use the existing common physical-time integrators and transactional
  semantics, with explicit seconds, small strain, fixed spatial frame and zero
  spin. The stress observable is effective only in a dry/uncoupled `u=0` host.
  No vendor algorithm equivalence, finite rotation or pore-pressure coupling.

All model parameter limits and illustrative values are project choices, not
vendor calibration or source-prescribed admissibility. A separate positive
`time_scale` sets the creep-rate observable's numerical scale only. It does not
enter the material equations. Persistent state is exactly six Mandel stresses;
all initialization state/time/loading is explicit.

## Fixed reference and acceptance policy

`study.json` specifies 27 requests, inputs, exact API bindings and scalar/array
oracles. `tools/power_creep_study.py` independently constructs Cartesian source
rates, exact scalar hold trajectories and exact stress-hold creep strains.
Constitutive evolution remains solely in the declarative model/common engine.

Reference holds use `qdot=-a*q-b*q^3`, including pure linear and pure cubic
limits. Constant imposed rate with a linear law uses an affine exponential
solution. Tests cover general tensor/shear loading and simultaneous sign reversal,
hydrostatic holds and elastic volume, the zero-stress Newton path, unsupported
exponents, missing state, zero/negative duration, accepted-partial-work rollback,
and recovery/replay. Schedule creep constrains all six stresses and checks the
resulting strain, not just material rate evaluation.

Frozen budgets: source rate `1e-7 Pa/s + 1e-11 relative`; direct midpoint state
`0.06 Pa`; implicit schedule state `15 Pa`; stress-hold creep strain `1e-10`;
native/Wasm physical parity `1e-8 absolute + 1e-10 relative`. The per-case
`study.json` values are authoritative. Success diagnostics must meet the solver's
recorded error and residual bounds. Late failure must retain the exact incoming
state and time after at least two accepted substeps. Every expected status and
process result must match. No gate is relaxed after observation.

## Execution order and preservation

1. Validate model, typed initialization and example schedules in Python. Generate
   deterministic C++ and catalogue. Snapshot the complete common source closure,
   definitions, reference requests, collector and assessor; hash in `freeze.json`.
2. Build **only** `atlas_power_creep_solver`, native Release, `--parallel 1`.
   Retain configure/build logs. Collect all 27 raw results and process statuses;
   assess against the frozen references. Retain a failure without overwriting it.
3. Only after native passes, build the same frozen source for Wasm with the same
   single target/job. Collect all requests in **one module instance**, including
   failure then recovery/replay. Reapply independent gates and physical parity.
4. Run the two user-facing JSON examples through `atlas.cli run`, preserving
   complete specifications/results. Verify replay and exact frozen source hashes.

Build products live under `/private/tmp/atlas-power-creep-execution-v1/`.
Raw small responses/reports/logs are retained in this packet. Root CMake receives
an opt-in research target; public `models/*.json`, shared schema/compiler/solver,
website packaging and historical evidence are unchanged. No push or deployment.
The separate frozen minimal CMake project permits exact-source reproduction.

This freeze supplies a bounded technical execution policy, not independent
scientific review, vendor validation or experimental admission.
