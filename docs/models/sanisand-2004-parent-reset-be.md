# SANISAND: parent-direction-reset backward-Euler research variant

Status: **executable project variant; independent review pending**. The [definition](../../models/research/sanisand-2004-parent-reset-be.json) retains the original continuous tensor equations and project finite discretization of the [fixed-memory research draft](sanisand-2004-fixed-memory-be.md). It adds one explicitly scoped parent reset through existing generic engine support. This is not a claim to implement the canonical original reversal rule, reproduce the complete OpenSees material, or admit another public model.

## Source distinction and policy

The original [Dafalias and Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29) paper, p. 631 after Eq. (24), calls for updating `alpha_in` when `(alpha-alpha_in):n` becomes negative, with reference to Dafalias (1986). The full 1986 loading-process rules remain unreviewed. No original-model event rule is inferred from their absence.

The pinned OpenSees [`integrate()`](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/ManzariDafalias.cpp#L858) instead selects memory before internal integration using `(alpha_n-alpha_in_n):(Ce*Delta_epsilon)`. For exactly deviatoric history and positive isotropic elastic shear modulus, this has the sign of `(alpha_n-alpha_in_n):dev(Delta_epsilon)`, since the hydrostatic contraction vanishes and `2G>0`. The numerical guard below explicitly uses the deviatoric contraction. It does not promise bitwise equivalence with contraction of a stored source matrix, especially near zero or with trace roundoff.

```json
{
  "increment_reset": {
    "scope": "parent_increment",
    "updates": [{
      "target": "alpha_in",
      "guard": "dot(alpha-alpha_in, dev(de))",
      "value": "alpha"
    }]
  }
}
```

Only a strictly negative finite guard resets memory. Zero, positive, and transverse guards preserve it. Values read the same immutable committed parent. The selected anchor is frozen through internal trials and recursive cutbacks. Successful updates commit that anchor; any failure restores the complete parent, including its original anchor and transient multiplier. Each independent outer trial starts again from that parent. These are the existing [parent-increment transaction semantics](../PARENT_INCREMENT_RESETS.md), not new engine code.

The policy is an algorithmic parent boundary, not a located physical reversal. Caller partitions can alter reset decisions on nonproportional paths. A hidden change in loading direction must be supplied as an explicit path boundary. No partition invariance or unique derivative at a guard crossing is asserted. The inner AD residual Jacobian holds the selected reset fixed; a complete update tangent through selection is not provided. This experimental choice is recorded in [decision 0001](../decisions/0001-sanisand-parent-reset-research.md).

The source cone-normal guard and this parent trial-direction guard can disagree even in simple unloading: at a compression peak `(alpha-alpha_in):n` can remain positive while its contraction with the reversed increment is negative. A dedicated test records this distinction. The local disagreement does not resolve the source's complete event rules.

## What remains the same

All parameters, 26 state components, continuous derived expressions, residual equations, state domains and initial checks are identical to the fixed-memory research definition. This variant keeps current-void-ratio elasticity, normalized off-cone directions, the `gamma=Delta_lambda*h` finite-product residuals, project exponential volume closure, and the common solver's backward-Euler/Newton/subdivision settings. It does not import OpenSees initial-density elasticity, pressure shifts/floors, low-pressure correction, finite hardening cap, constructor/stage transitions, source projection or reference tangent schemes. Original-paper and full OpenSees equivalence both remain unproven.

## Native evidence

One small standalone C++20 `-O0` compilation and a separate bounded native run completed normally. The [harness](../../tests/native/sanisand_parent_reset.cpp) runs two proportional constant-total-volume directions:

- Triaxial direction `(0.002,-0.001,-0.001,0,0,0)`.
- General Mandel direction `(0.001,-0.0003,-0.0007,0.001,-0.0004,0.0002)`.

Each uses four legs with direction factors `1,-2,2,-1` and 16, 32 or 64 increments per leg. All **896 cyclic increments** succeed, with three resets per path/partition, giving 18 cyclic resets. Each successful cyclic increment uses one accepted internal substep. The first monotonic legs reproduce all 224 corresponding retained fixed-memory states exactly as numeric values; the native harness independently asserts this parity against the fixed-memory definition.

Six extra zero trials preserve the parent anchor. Six intentionally invalid increments select a new nonzero anchor, accept three internal substeps, then fail after 15 rejected attempts. Every failure returns the full pre-reset parent. These are failure/isolation tests, not valid loading benchmarks or evidence of a physical failure location. Across all 908 records, the [Python verifier](../../tools/verify_sanisand_parent_reset.py) checks complete matrix order, path continuity, interpreted/native preparation equality, fixed selected memory, successful endpoint residuals and reset rollback. The largest scaled successful residual is `1.9811e-10`, below the existing `2e-10` solver threshold.

Successive cyclic endpoint changes under step halving have ratios about `0.456` and `0.506`, consistent with first-order convergence on these prescribed parent-partitioned paths. This does not establish event-policy independence, an absolute integration-error bound, nonproportional-path convergence or independent scientific validation.

The [manifest](../../catalogue/investigations/sanisand-parent-reset-v1/manifest.json) pins source definitions, compiler/engine/harness, generated header, executable and compressed full input/preparation/output trajectories. Five [Python test groups](../../tests/test_sanisand_parent_reset.py) cover definition identity, guard boundaries, immutable preparation, source-guard disagreement, the retained native matrix and corrupted-evidence rejection. All 26 SANISAND Python groups pass together.

## Reproduce gradually

```sh
python3 tools/verify_sanisand_parent_reset.py prepare /private/tmp/atlas-sanisand-parent-reset-small
c++ -std=c++20 -O0 -Icpp/include -I/private/tmp/atlas-sanisand-parent-reset-small/generated /private/tmp/atlas-sanisand-parent-reset-small/probe.cpp -o /private/tmp/atlas-sanisand-parent-reset-small/probe
/private/tmp/atlas-sanisand-parent-reset-small/probe > /private/tmp/atlas-sanisand-parent-reset-small/output.json
python3 tools/verify_sanisand_parent_reset.py verify /private/tmp/atlas-sanisand-parent-reset-small/output.json --output /private/tmp/atlas-sanisand-parent-reset-small/verification.json
```

Preparation/verification do not compile or execute native code. Full OpenSees builds remain deferred. Canonical reversal rules, located first-yield/reversal events, nonproportional paths, accepted-substep reset alternatives, mixed controls, complete-update tangents, matching independent reference histories, Wasm and website execution remain open under SAN-03/05/06. No public model count or review status changes.
