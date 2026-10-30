# Update-tangent directional refinement and rotations

This exploratory follow-up advances NUM-02 using the experimental [native JSON API](UPDATE_LINEARIZATION_API.md). It reuses the prior hash-verified native executable, with no new compilation. Forty-nine serial native requests completed normally; the initial all-step verifier rejected one coarse perturbation. All responses and the resulting refinement analysis are retained in the [manifest](../catalogue/investigations/tangent-geometry-v1/manifest.json).

## Directional perturbations

Seven previously verified parent/increment pairs cover the five public formulations and loading/reversed-parent SANISAND research cases. For each, central differences of complete ordinary updates use the unit Mandel direction `(2,-1,3,4,-2,1)/sqrt(35)` and steps `2e-7`, `1e-7`, `5e-8`. Compare each state derivative to the previously retained full-update matrix times this direction. Both perturbed updates must preserve the original accepted partition. These are independent perturbations from the previous coordinate-column comparisons, not independent model implementations.

Errors use `abs(tangent_direction - central_difference) / max(state_scale, abs(central_difference))`. Across 288 state comparisons in 21 directional cases, twenty cases lie below `1e-5`. The reversed SANISAND research case gives maxima `1.7739063e-5`, `4.4347693e-6`, `1.1087244e-6` as the step halves. That roughly fourfold reduction supports central-difference truncation error rather than a constant derivative discrepancy. The largest finest-step error over all seven cases is `1.1087244e-6`.

The retained verifier requires the finest step below `1e-5`, and any discrepancy above that threshold to decrease by at least a factor of two on halving. This refinement acceptance policy was adopted after inspecting the initial coarse-step failure; it is exploratory evidence, not a preregistered all-step pass. Small discrepancies need not decrease monotonically because stopped-root error and cancellation also contribute. The loading SANISAND discrepancy approaches `1.02e-6`; these results do not justify tighter solver or derivative accuracy claims.

## General tensor rotation

Use the proper Rodrigues rotation with axis `(1,2,3)/sqrt(14)` and angle `0.61` radians. Construct its orthogonal Mandel map `Q` directly from `R A R^T`. Rotate every symmetric parent-history field and the complete increment, leaving scalar state unchanged. If `B` is the block state rotation, compare the rotated tangent to `B T Q^T`, and its accepted state to `B z`. This checks state history rows as well as the stress block; it does not establish finite-rotation objectivity.

Six cases retain exactly the same accepted numerical partition. Their maximum normalized tangent discrepancy is `2.284e-13`, below the declared `1e-7` rotation tolerance. Their scaled state discrepancies are below `6e-16`.

**IGS selects a different adaptive partition after rotation.** Its scaled state discrepancy is `2.861e-7` and tangent discrepancy `7.906e-6`. These values are diagnostics, not a passing same-partition covariance check. The existing midpoint controller takes componentwise maxima of scaled errors/defects (`cpp/include/atlas/solver.hpp`), so its refinement decision is not generally invariant under rotation. An isotropic continuous law does not imply identical discrete outputs when that controller chooses different steps. Preserve this limitation until a fixed-partition replay comparison or independently refined rotation study resolves it. Do not change integration defaults from this single observation; configurable numerical settings and provenance remain NUM-03 work.

## Reproduction and remaining scope

With the hash-matched native solver prepared as in the API document:

```sh
python3 tools/verify_tangent_geometry.py capture --solver /private/tmp/atlas-linearization-api-reproduce/solver --output /private/tmp/tangent-geometry-responses.json
python3 tools/verify_tangent_geometry.py verify catalogue/investigations/tangent-geometry-v1/responses.json.gz --output /private/tmp/tangent-geometry-report.json
python3 -m unittest tests.test_tangent_geometry tests.test_linearization_api tests.test_update_tangent tests.test_atlas.LanguageTests tests.test_parent_reset.ParentResetLanguageTests -q
```

Capture executes native requests serially with 45-second individual bounds. Verify and the five new Python test groups operate offline; all 29 related groups pass. Corruption checks reject incomplete/nonfinite results, altered directional derivatives, incorrect rotated matrices and changed partitions in required cases. Mandel-map orthogonality, determinant, trace and contraction checks support the rotation convention.

Only one direction and rotation are tested at seven states. No Wasm/browser check, physical-time/control derivative, broad branch-boundary coverage, full numerical regression or independent scientific model admission follows. NUM-01/02 remain open.
