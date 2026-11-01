# J2 mathematical backward-Euler qualification v1

Frozen before compiled observation, 2026-11-01. This study qualifies the exact
packet candidate through the existing generic DSL compiler and solver. It does
not execute OpenSees or claim vendor numerical replication. The source-specific
gamma shrink is deliberately absent. Constant isotropic linear elasticity,
associated J2 flow, nonnegative linear isotropic hardening, dry total stress,
infinitesimal strain and fixed spatial zero spin define the scope.

The independent oracle in tools/study_j2.py uses Cartesian tensors, analytical
elastic trial projection and the closed scalar consistency solution. Reference
cases and budgets are generated and hashed before compilation. Cases span three
hardening moduli (including perfect plasticity), three signed pressures, four
tensor loading directions, elastic/plastic amplitudes, hydrostatic/origin and
yield-surface holds, explicit nonzero-history restart, unloading/reversal and
nonproportional paths. Each finite increment is the named mathematical BE map;
it is not exact integration of an arbitrary continuous curved path. The frozen
solver forbids internal subdivision, permitting comparison with that map.

All six stresses must be within 0.002 Pa, both history layout values within
2e-10, endpoint yield excess below 0.003 Pa, and hardening must not decrease
beyond 2e-10. Two full 8x6 update tangents on strict elastic/plastic branches
compare with independent analytic derivatives: stress entries within 0.2 Pa and
history entries within 2e-8. These are bounded software checks, not empirical
validation or full declared-parameter-range qualification.

Two identical calls per request must replay exactly in each backend. Forced
iteration exhaustion must restore every input slot, including a nonzero incoming
temporary multiplier. Invalid hardening, overstress, missing/short state and
invalid modulus are rejected. Valid recovery calls follow malformed calls in
the same Wasm module. Native and Wasm each independently satisfy the analytical
gates; parity budgets are 1e-5 Pa stress, 1e-11 history, 0.01 Pa stress tangent
and 1e-11 history tangent. Diagnostics need not be bitwise portable. Failure
messages and limits remain retained; no budget changes after observations.

All Python/compiler/schema/header/C++ model/build/reference/assessor inputs are
hash-frozen and copied unchanged to private isolated source closure before the
first build. Build only atlas_j2_solver serially with --parallel 1: native first,
then Wasm. Retain toolchain/configuration/build logs and raw stdout. Do not modify
the shared engine, public catalogue, existing definitions or historical evidence.
Scientific technical review follows numerical assessment in a fresh agent.
Human signoff, finite rotations, pore-pressure coupling, experimental validation,
stress-controlled protocols and public browser packaging remain separate.
