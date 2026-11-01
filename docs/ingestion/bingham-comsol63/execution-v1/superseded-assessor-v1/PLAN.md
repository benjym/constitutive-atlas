# Bingham prospective numerical qualification v1

Frozen before any Bingham compiled observation. The exact candidate, source receipts,
reference inputs, mathematical oracle, collector, assessor, common runtime/compiler,
schema and dedicated CMake target are pinned in freeze-v1.json. The original source
packet and its accuracy proposal remain unchanged; this execution policy deliberately
uses an absolute plus relative physical-component budget, frozen before observations.

The136requests include108source-derived closed-form radial paths over all six
Mandel direction seeds, initial zero/below/exact/above yield, both signs, holds,
outward loading and reversal through both yield boundaries. Additional cases cover
hydrostatic load, zero hold, three fixed-basis tensor rotations, actual public
relaxation/creep/rate presets, noncoaxial load/hold/direction/reverse, refinement,
restart from actual complete committed state and clock, invalid viscosity/yield,
missing state, negative accumulated strain, plastic volume and invalid durations.
Every rejected request is followed by valid recovery in the same Wasm instance.
Each request repeats twice. A deliberately exhausted budget must return all13parent
state entries and physical clock after internally accepted substeps.

Closed-form references derive from the source scalar stress equation and compliance;
the additional oracle independently integrates stress plus accumulated strain using
RK4 and reconstructs plastic strain. Its4096/8192grids must converge within1e-9strain
and0.02Pa before compilation. Public-rate and noncoaxial references use this separate
stress-space method, not the DSL or production strain-space integration. This is
numerical verification of equations, not experimental validation.

Native direct physical-time integration uses the existing second-order explicit
midpoint/full-versus-two-half-step common engine, relative1e-9, absolute scale
fraction1e-12. Mixed schedules use the existing backward-Euler step-doubling host
and the same tolerances, nonlinear1e-10/40iterations. Both use1e-12minimum step,
1e6maximum step,1,000,000accepted-substep budget and existing40depth. No runtime
or material-specific kernel changes. These are project choices, not vendor solver
reproduction. The coarse refinement diagnostic uses1e-4/1e-7 only; the fine errors
must improve by at least factor5in both complete state and stress.

Accuracy for every successful physical component: absolute error <=
max(3e-7,2e-5*abs(reference)) for every strain/history scalar and
max(3Pa,2e-5*abs(reference)) for every stress. Coarse diagnostic alone has fixed
0.001strain/1000Pa bounds and is never counted as the fine accuracy result. Zero
state, controls, times, topology, required components and declared domain are
additionally checked. Nonsmooth yield derivatives and a physical-time tangent API
are not claimed; threshold behavior and constant-basis covariance are exercised.
There is no FE/global tangent or finite-rotation claim.

Backend parity is additional to independent accuracy: same status, structure,
messages and complete physical outputs; scaled physical differences <=2e-10with
stress floor1000Pa and dimensionless floor1. Internal iteration/substep/error
diagnostics may differ and are retained, never used to waive physical accuracy.

Build ownership is the coordinating parent. Read the shared board immediately
before claiming each native/Wasm slot; one explicit atlas_bingham_solver target,
--parallel1. Native first, understand all observations before Wasm. Failed checks
and raw attempts are retained. Changes following a failure require a separately
identified policy/reference/candidate study, never an observed-failure gate change.

Preparation history: first request-generation attempt failed because the schedule
schema correctly rejects maximum_depth as a caller field. Corrected before freeze
by retaining the engine default40in the result policy while omitting that field
from the schema-v0.2 request. No compiled call occurred during preparation.
