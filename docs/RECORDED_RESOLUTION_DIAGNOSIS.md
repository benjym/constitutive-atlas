# Recorded-path failure and continuous-limit diagnosis

The [original 60-run study](RECORDED_REFINEMENT.md) retains six coarse failures. This follow-up identifies their mechanisms and supplies a continuous reference for its isotropic Cam-Clay case. The [manifest](../catalogue/investigations/recorded-resolution-diagnosis-v1/manifest.json) pins evidence. These are numerical checks of the declared project equations; they do not establish source reproduction or experimental validity. The three parallel AI reviews informed the checks; independent scientific review remains open.

## IGS97: initial history and recursion depth

The first mixed-control trial prescribes axial strain with zero radial increments. Direct native material calls reproduce its failure, isolating it from the outer stress-control root. A Python reproduction follows the exact C++ midpoint stage order and its componentwise error calculation down the first leftmost recursive branch. At the configured terminal depths, all stages satisfy the domain; the full-versus-two-step `h_xx` estimate causes rejection.

| Axial increment | Rate tolerance | Original depth cap | Error at cap | First locally passing depth | Native substeps at increased cap |
|---:|---:|---:|---:|---:|---:|
| 0.003 | 1e-6 | 14 | 2.30157e-6 | 15 | 618 |
| 0.003 | 1e-8 | 18 | 3.11115e-8 | 20 | 2,788 |
| 0.0015 | 1e-8 | 18 | 1.08324e-8 | 19 | 2,512 |

For collinear loading from zero history with `beta_r=0.5`, the history law reduces to `dh/ds=1-sqrt(h/R)`. The initial expansion contains an `s^(3/2)` term, so the smooth-path cubic local-error estimate does not apply at this origin. Coarser stages can violate the history band; subdivision clears those violations before the terminal error rejection.

All three isolated material intervals complete at the predicted increased depths with unchanged tolerances and substep cap. This does not prove the entire coarse mixed-control history succeeds, establish global accuracy, or justify changing defaults. Preserve the initial failures as depth-budget evidence. A future diagnostics API should distinguish domain, local-error and depth-limit rejection instead of reporting a generic material failure.

## Drucker–Prager: singular initial control guess

All three plastic drained failures occur after a successful material update. The zero-radial-increment initial guess for unloading lies strictly inside the apex branch. Independent constant-elasticity scalar return algebra reconstructs `sigma=(-c/M) I=-8333.333 Pa I`. The radial control residual magnitude is `1.083333333333`, matching every retained failure. Stress is locally constant at this apex; the reduced two-by-two radial Jacobian is zero. Positive and negative small derivative probes stay on the same branch.

Independent scalar bracketing finds attainable radial increments for the failed endpoints: `0.0073253968254`, `0.0028566468254`, and `0.002234375` for factors 1, 2 and 4. The failures therefore demonstrate a local root-initialization limitation, rather than unattainable controls. A lateral elastic guess escapes the apex in the scalar analysis. These guesses and roots have not been run through a new native control solve.

The next implementation should add a bounded generic restart within the prescribed-strain nullspace, with explicit settings/provenance, immutable-parent trials, global trial accounting and failure-prefix regression. Tiny finite-difference fallback alone cannot escape a locally constant branch. Do not add model-specific Poisson-ratio logic to the common driver or silently insert caller knots.

## Cam-Clay: exact continuous isotropic reference

Let `v=1+e` and `epsilon_v` be compression-positive volumetric strain. The continuous limit of the declared project equations gives

- `v = v0 exp(-epsilon_v)`;
- elastically, `d(log p) = v d(epsilon_v) / kappa`, with constant `pc`;
- on isotropic plastic compression, `p=pc` and `d(log p) = v d(epsilon_v) / lambda_c`.

The plastic relation follows by eliminating plastic volumetric strain between elastic pressure evolution and `d(log pc)=v d(epsilon_v^p)/(lambda_c-kappa)`. Since `dv=-v d(epsilon_v)`, each segment integrates exactly in specific volume. Split compression when elastic pressure first reaches `pc`; unload elastically. This reference permits reversals and repeated observations and requires isotropic strain, `0<p<=pc`, positive void ratio, and `0<kappa<lambda_c`.

[The reference implementation](../atlas/isotropic_reference.py) uses these integrated expressions, independently of the finite-step residual. The analyzer verifies retained requests, controls, settings and observation mapping before comparison. The all-strain isotropic path is unchanged geometrically by collinear subdivision; the difference here comes from material discretization. The residual solver has no constitutive accuracy estimator: a converged nonlinear residual can still have substantial finite-step error.

| Factor | Maximum pressure/pc error against continuous reference (Pa) |
|---:|---:|
| 8 | 17,611.512 |
| 16 | 8,931.922 |
| 32 | 4,496.985 |
| 64, new native run | 2,258.461 |

At the second compression peak, the continuous value is `285627.752 Pa`. Observed orders at the last retained levels are approximately one. Factor 64 confirms another approximate halving. At the final unloading observation, factor 32 still differs by about 11% in pressure. These results support first-order approach for this particular path; they do not make factor 32 or 64 accurate enough for every use.

A second new native run at factor 32 tightens residual tolerance from `2e-10` to `1e-12` and returns identical states at the original observations. The error here is insensitive to that algebraic tolerance change. `rate_tolerance` does not control this residual model. Richardson estimates must remain diagnostics rather than replacing accepted states.

## Reproduction and next gates

All five new native calls reused the previously verified binary serially; no compilation occurred. To regenerate the diagnostics and analytical comparisons:

```sh
python3 tools/diagnose_igs_recorded_depth.py --output igs-depth.json.gz
python3 tools/diagnose_dp_recorded_apex.py --output dp-apex.json
python3 tools/run_recorded_resolution_probes.py --solver /path/to/atlas_solver --output-dir followup
python3 tools/analyze_mcc_continuous.py \
  catalogue/investigations/recorded-refinement-v1/plastic-report.json.gz \
  --followup followup/mcc-native-followup.json.gz --output mcc-continuous.json
python3 -m unittest tests.test_isotropic_reference tests.test_resolution_diagnosis -v
```

The next numerical work is bounded mixed-control restarts and an explicit accuracy policy for implicit materials, backed by references like this one. Full recorded experimental replay, source-matched nonlinear reference histories, independent scientific review and general convergence claims remain open under NUM-03/04.
