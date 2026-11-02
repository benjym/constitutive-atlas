# VIBE Appendix A independent numerical reference v1

Task REF-vibe2026-appendix-numerical-v1, owner `/root/vibe_source`, 3 November 2026. This packet owns only `docs/ingestion/vibe-2026/reference-v1/`. It implements a research reference oracle directly from the final original and the separately frozen source-v2 transcription. No production declarative candidate was read, imported or copied; no author, native, Wasm or browser material model was executed. This is reference evidence for coordinator comparison and separate review, not model approval.

The selected identity remains **Mašín 2026 VIBE, published explicit Appendix A formulation**, including all A1–A35 hydraulic, thermal, mechanical and viscous terms. The body Eq27 combined absolute value differs under opposing mixed internal THM contributions; the reference deliberately uses the explicit Appendix's separate A6/A8 contributions. The A7 identity and A9 tensor-rank completions have the source-v2 derivations and review. Positive suction is mandatory; no saturated-start memory extension is invented.

## Prospective freeze and method

[plan.json](plan.json) was written and its SHA256 sent to the coordinator **before any oracle rate or trajectory observations**: `facc17e21d786328f4b28e8c20d9d3e5b1909becb3e3d971195ca5d7c9435a63`. It freezes source identity, inputs and generation algorithms, all cases, physical units, precision, RK4 partitions, source domain and acceptance gates. No compiled candidate observations were available. Those cases and gates remain unchanged after observing success.

The source-v2 manifest is `90603c5756a0a1a8f2edd8cbdcb6d21ad639f51796d2dba78ceaca04047f442c`; the final PDF SHA256 is `90b1c3bc56bacf1294e3e8ea60a217ffa1651981c86c63b0c0d9354534764912`. See the source-v2 receipt for retained original, rendered pages and precise formula locations.

[oracle.py](oracle.py) uses only Python standard-library Decimal arithmetic, Cartesian 3×3 tensors, explicit contractions, tensor products and determinants. It forms the fourth-order B action from the composition in body Eq42, evaluates that action on each Mandel basis tensor to assemble a complete 6×6 matrix, and solves the system with pivoted Gaussian elimination. It does **not** use the production rank-one inverse. The source-sign computation receives negatives of compression-positive Atlas tensors and returns the negative source stress rate. Internal memories are exactly e and a_scan. Current suction, temperature and all derived variables are reconstructed at each stage.

The source Fm expression is evaluated directly from Cartesian stress invariants at high precision, independently of the coordinator's proposed stable deviatoric expression. Exact hydrostatic inputs take the uniquely continuous A12 product extension: Fm=0, shat=0 and the Lode-product contribution vanishes. No anisotropic regularization is imposed. Zero suction rate uses a finite fscan representative; every r-dependent contribution is multiplied by zero, so no additional branch memory is introduced. The Heaviside value at zero is one and sign at zero is zero, as stated by the source.

The environment had no `mpmath`; Decimal supplies arbitrary precision ln/exp/sqrt. Trigonometric functions use convergent Taylor sums at the current context precision with an explicit 110-digit pi. Equations contain no binary floating-point arithmetic. Runtime measurement is metadata only.

[run_reference.py](run_reference.py) defines the frozen point cases and classical fixed-step RK4 trajectories. The full eight-component state advances together; controls are sampled at all four RK stages. The hydraulic reversal is split exactly at 50 seconds, with each side's derivative used for its own interval endpoint. Prescribed strain rates are compression positive Mandel values. Inputs/outputs use Pa, K and seconds.

## Reference contexts and cases

The source Table1/Table2 BCV parameter set is retained, including explicit reference pressure 1000 Pa and viscous fraction .1. The source dry example uses e=.725, scan=0, suction100 MPa and isotropic net compression1000 Pa. It is far inside the ASBS and has an extremely small viscous stress rate (about −3.04×10^-259 Pa/s), so its stress change is below the finite 50/70-digit state resolution. It supplies a useful small-response check, not a meaningful relaxation demonstration.

The near-SBS example uses e=.725, scan=.35, suction10 MPa and temperature294 K; isotropic net pressure is determined by independent Decimal bisection so OA=1.005. This is an explicitly constructed illustrative state, not a measured or reconstructed preparation. Each parameter/scan context receives its own source-algebra pressure solution. The anisotropic context adds the frozen trace-free Mandel offsets `[2000,-1000,-1000,3000,-2000,1000]` Pa.

The 32 point references cover positive and negative rates in all six mechanical components; anisotropic mixed mechanical loading and a viscous hold; wetting and drying; heating and cooling; opposing simultaneous hydraulic/thermal rates; both scan endpoints; a sensitivity parameter set; and rate-independent versus IvT-zero holds. The sensitivity set changes ns=.02, ls=.005 and lT=.01 explicitly as a **project study, not a BCV calibration**. It produces negative DsP and DTP, activating opposite collapse branches to the default set. Both directions of each control are retained. Each result stores complete stress6/e/scan rates and initialization/control/parameter values, plus em,eM,S_M,Sr,OA,re,Fm and collapse-driving derivatives.

Seven invalid contexts explicitly refuse zero/negative suction, negative macrovoid, an invalid temperature context, scan outside [0,1] and nonpositive micro pressure. These are source/reference domain tests, not integration transaction or production error-message tests. A context can violate more than one bound; the retained reason identifies the first checked violation.

## Results and limits

[point-results.json](point-results.json) retains all 32 accepted cases at 100 digits and their 70/100-digit convergence checks; seven invalid cases are retained as explicit refusals. Every rate component passes the frozen point gate: stress `1e-8 Pa/s + 1e-7 relative`, scalar `1e-12/s + 1e-7 relative`.

All five trajectories ran at 64/128/256 partitions with 70 digits; the finest partition was repeated at 50 digits. Full-state stress, scalar memory and dimensionless observables pass both finest-partition and precision convergence gates. Stress tolerance is `.01 Pa + 1e-7 relative`; e/scan tolerance `1e-9 + 1e-7 relative`; dimensionless observable tolerance `1e-8 + 1e-7 relative`. Full original run results and discrepancies are retained, rather than only the successful summary.

| Trajectory | Isotropic net compression change | Hydraulic memory change |
| --- | ---: | ---: |
| Near-SBS hold, 1000 s | −3323.523949315 Pa | exactly zero |
| Near-SBS hold, 3600 s | −10486.664588186 Pa | exactly zero |
| Dry hold, 1000 s | below finite reference state resolution | exactly zero |
| Mixed ramp, 100 s, Δs=+.2 MPa and ΔT=+2 K | −8857.874967379 Pa | +.154392591834381 |
| Wet/dry reversal, 100 s, returning to original suction | −2454.541895243 Pa | +.0135296563137794 |

Void ratio is exactly constant for these zero-mechanical-rate paths, and shear components remain zero. The point probes separately exercise nonzero void-rate and all shear/normal stress responses. This v1 trajectory set is hydrostatic; it does **not** establish nonproportional trajectory convergence, all parameter sensitivity trajectories, every source-boundary limit, or experimental agreement. The mixed case applies full Appendix A thermal and hydraulic terms, without claiming Eq27 equivalence. The reference captures physical duration and current-temperature ordering, but host commit/rollback/restart, native/Wasm comparison, compiled integration budgets and browser qualification remain coordinator tasks.

The source domain is strictly positive suction, positive micro/macro pressures and active slopes, nonnegative Fm below one, inside/on the selected ASBS, valid scanning range and nonsingular denominators. Boundary rejection is explicit. No clipping, state projection, old-temperature lag, numerical suction-rate threshold or source-code stress floor is inherited.

## Reproduction and cleanup

Verify retained acceptance evidence:

```sh
python3 -B docs/ingestion/vibe-2026/reference-v1/verify_results.py
```

Reproduce numerical results into a **new** output directory to preserve frozen originals:

```sh
python3 -B docs/ingestion/vibe-2026/reference-v1/run_reference.py points --output /private/tmp/vibe-reference-reproduction
python3 -B docs/ingestion/vibe-2026/reference-v1/run_reference.py trajectories --output /private/tmp/vibe-reference-reproduction
```

Point JSON is deterministic. Trajectory numeric contents are deterministic; runtime metadata is intentionally variable. The Decimal implementation uses no dependency installation, network access or compiled process. No worktree, build, preview server or disposable downloaded source was created. Original reference scripts/results and source evidence remain required for independent review and production comparison. Any future revised cases/settings need a distinct plan identity rather than editing this frozen plan.

`manifest.json` binds the scripts, plan, retained results and this narrative. The coordinator should compare the exact candidate against these independent references, preserve failures, request separate scientific review and continue E0–E8. This source worker does not mark scientific admission or delivery complete.
