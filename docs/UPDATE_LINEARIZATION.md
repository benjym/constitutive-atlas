# Experimental accepted-update linearization

This C++ API advances NUM-01/02. It differentiates the complete converged discrete material update on its accepted partition, including parent memory preparation. It is distinct from the AD residual Jacobian already used inside Newton. It does not close the numerical API milestone or independently validate a constitutive model. The subsequent [native C ABI/CLI endpoint](UPDATE_LINEARIZATION_API.md) exposes this result; Wasm runtime verification remains open.

## Interface

Include [atlas/linearize.hpp](../cpp/include/atlas/linearize.hpp), with a current generated `models.hpp`, then call:

```cpp
auto result = atlas::linearize_update(model, parent, delta_epsilon, parameters);
if (result.advance.ok) {
    // result.advance.state is the accepted state; caller chooses whether to commit.
}
if (result.tangent_ok) {
    // result.state_tangent[i][j] = d accepted_state[i] / d delta_epsilon[j].
}
```

`parent`, `delta_epsilon` and `parameters` have the existing incremental API meanings. The parent and parameters are fixed during differentiation. Rows follow generated state-field/component order; columns are the six total Mandel strain-increment components. For legacy definitions, the first six rows form the stress tangent, with pressure units because strain is dimensionless. Other rows have their state's units per strain, including the returned last-substep transient multiplier. The matrix need not be symmetric, particularly for nonassociated plasticity. No symmetrization is performed.

`result.advance` contains the ordinary `Advance`, including update status, accepted state, integration diagnostics and failure message. The function first calls the unchanged `integrate` API. An unsuccessful update returns its original rollback state with `tangent_ok=false` and no tangent. The API never mutates the supplied parent or commits global state.

Derivative failure is separate: an accepted update can have `advance.ok=true` but `tangent_ok=false`, an empty matrix and a derivative explanation in `result.message`. Examples include a singular residual linearization, failed replay, nonfinite derivative or inconsistent replay endpoint. Do not discard a successful material result merely because its tangent is unavailable, or infer a tangent from the residual Jacobian in that case.

The exact-zero flag `reset_guard_at_zero` reports whether any parent reset guard evaluated to zero. It does not prove or disprove differentiability: an identically zero guard can be harmless, while other DSL switches can be nonsmooth without this flag. The returned tangent always has the fixed-branch semantics below. Physical-time definitions use their separate API and are rejected by this incremental entry point.

## Discrete derivative

1. Execute the ordinary update and retain its accepted `increment_fractions`. Keep that numerical partition fixed for linearization. Do not differentiate adaptation thresholds, failed trial iterations or the choice of Newton path.
2. Seed the six total strain components and differentiate the existing parent preparation map. Generated preparation is now templated over `double` and `Jet`; its five-argument double calls keep the previous semantics. A selected assignment depending on the complete increment contributes its derivative once, before subdivision. Guards select branches by value; no derivative through their Boolean decision is implied.
3. Replay each accepted substep. For a residual step, solve its endpoint again from the replayed previous state, then evaluate AD partials of the unmodified model residual. If `R(z_k,z_previous,f_k*Delta_epsilon)=0`, propagate

   ```text
   R_z * dz_k/dDelta_epsilon
     = -(R_previous * dz_previous/dDelta_epsilon + f_k*R_increment).
   ```

   Apply the same positive state/residual scales as the shared Newton solve. Solve all six control columns; do not differentiate the stopped Newton iterations. A nonsingular local residual Jacobian is required. The derivative is evaluated at the numerically converged root, so root stopping error can affect its accuracy.
4. For rate definitions, propagate AD through the exact accepted explicit midpoint recurrence, carrying previous-state sensitivities through every accepted substep. This differentiates the implemented discrete path, not the exact continuous ODE.
5. Require finite derivatives, partition coverage within `1e-12`, and replayed endpoint agreement within `1e-9` of each state scale before publishing the matrix. These are project verification tolerances; they do not change the integrator's existing stopping rules.

State and control derivative slots remain separate: endpoint unknowns use state slots `0..n-1`; six control derivatives use `max_state..max_state+5`. Current evidence exercises up to 26 state components; it does not add a new 32-state linearization verification claim. The preparation map remains frozen across internal cutbacks, while its derivative with respect to the caller's total increment propagates through the resulting integration. Existing schema and canonical model hashes are unchanged. Rebuild generated headers to use the new template; old binaries remain historical artifacts.

This is a local derivative of the selected discrete map. Where partition and expression/reset branches are locally stable and the implicit Jacobian is nonsingular, it supplies an algorithmic material tangent. At yield switches, norm-zero points, reset crossings, different root choices or adaptive partition thresholds, a unique full-map derivative is not guaranteed. No generic detection of all such boundaries is implemented. A fixed-branch matrix may still be returned there and must not be presented as a unique derivative. It is not a finite-rotation tangent, mixed-control solution derivative, parameter derivative or physical-time tangent. See [decision 0002](decisions/0002-fixed-partition-linearization.md).

## Verification

Two small standalone C++20 `-O0` compilations and separately bounded native runs completed normally. The second used the repository preparation command and exactly reproduced all eleven matrix records and both status assertions. The [harness](../tests/native/update_tangent.cpp) retains eleven result records plus native assertions for two status cases. The [record](../catalogue/investigations/update-tangent-v1/manifest.json) pins the compiler/engine, fixtures, models, generated header, executable and full results.

- All five public formulations have smooth-regime comparisons against central differences of complete `integrate` calls, as do loading and reversed-parent SANISAND research cases. All six Mandel increment columns and all returned state rows are checked, not only the residual's current-state Jacobian. Both perturbed updates must select the same accepted partition as the base update. This supports only the tested regimes.
- A scalar quadratic backward-Euler fixture forces two accepted implicit substeps. Its endpoint and derivative are independently computed through closed-form quadratic roots and their chain rule. A scalar exponential-rate fixture requires 128 midpoint substeps and has a closed-form discrete recurrence derivative. MCC uses two accepted substeps; VW96 uses eight; IGS uses 154. These cases test accumulation across partitions rather than a final-substep Jacobian alone.
- A strain-dependent reset fixture assigns `anchor=trace(Delta_epsilon)` before rate integration with `sigma_dot=p_ref*anchor*de`. Its stress tangent is `p_ref*(trace(de)*identity_6 + de outer trace_selector)` and anchor derivative is `(1,1,1,0,0,0)`. The analytical check detects omission of reset preparation derivatives or accidental resetting on each substep.
- Linear elasticity supplies the full independent isotropic `6x6` Mandel stiffness. Together the independent analytical checks cover 228 entries.
- Ten smooth records cover 720 full-update central-difference entries with step `1e-7`. Error is normalized by `max(state_scale[i],abs(FD[i][j]))`; the maximum is `4.1505e-6`, below the declared `1e-5` threshold. This is not an unqualified relative error at zero components. Exact analytical comparisons use absolute-plus-relative tolerance `1e-10`. The scalar implicit derivative instead uses `1e-8` because the common Newton root tolerance is amplified through the implicit solves; its observed absolute derivative discrepancy is about `3.03e-9`. No integrator tolerance changed.
- A zero-increment reset-boundary case returns the selected branch matrix and the exact-zero guard flag. It intentionally has no two-sided FD comparison: perturbing across the guard can change memory discontinuously.
- A converged zero-increment synthetic residual with a singular current-state Jacobian keeps its accepted update and reports no tangent. A separate invalid-model assertion checks ordinary update failure and rollback. These two status cases are native assertions in the pinned harness, not additional matrix records.

Four [Python test groups](../tests/test_update_tangent.py) independently verify retained matrices and reject incomplete, nonfinite, malformed or corrupted evidence. Twelve existing language/code-generation checks and four parent-reset language checks also pass (20 Python groups total for this change). Those Python tests do not compile or execute binaries. No full native suite or Wasm rebuild was performed for this step.

## Gradual reproduction and remaining gates

```sh
python3 tools/verify_update_tangent.py prepare /private/tmp/atlas-update-tangent-small
c++ -std=c++20 -O0 -Icpp/include -I/private/tmp/atlas-update-tangent-small/generated /private/tmp/atlas-update-tangent-small/probe.cpp -o /private/tmp/atlas-update-tangent-small/probe
/private/tmp/atlas-update-tangent-small/probe > /private/tmp/atlas-update-tangent-small/output.json
python3 tools/verify_update_tangent.py verify /private/tmp/atlas-update-tangent-small/output.json --output /private/tmp/atlas-update-tangent-small/verification.json
```

Preparation and verification do not invoke native code. The C++ header was the initial API surface; [native C ABI/CLI access](UPDATE_LINEARIZATION_API.md) is now separately verified. Website access, native/Wasm parity, physical-time updates, broader branch-boundary policy, rotated tangent tests, independent directional perturbations at multiple step sizes, ill-conditioning diagnostics, highest-capacity cases and full numerical regression gates remain open. NUM-01/02 are not complete.

A subsequent [directional-refinement and rotation investigation](TANGENT_GEOMETRY.md) covers one arbitrary direction at three step sizes and six same-partition rotations. It retains one coarse finite-difference discrepancy and a changed-partition IGS rotation explicitly; broader geometry/regression gates remain open.

[Incremental settings](INCREMENTAL_SETTINGS.md) can now be supplied as an optional final C++ argument. Implicit replay uses those same settings; accepted partition and branch semantics are unchanged.
