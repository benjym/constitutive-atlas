# PLAN-md1997-native-admissible-fixture-v1

This is an independent source-only prospective fixture plan. The actual native all16 explicit-v5 `atlas_numerical` failure remains unchanged evidence; five other native tests passed in that retained run. No executable was run, built or edited here. The proposed profile needs separate prospective review and implementation authorization.

`prove.py` imports no Atlas evaluator, production expressions, compiler or backend. It independently evaluates the original source's invariant scalar/tensor domain/branch algebra using only Python math and proves matrix rank using exact Fractions. It pins the exact model bytes and reproduces the parent diagnostic: scaled h=1e-6 changes each diagonal alpha by1e-6, violating `abs(trace(alpha))<=1e-10` by10000 times; only flat indices7/8/9 fail. The old rotation parent [105000,95000,160000,1000,0,0] also violates `yield_scaled<=1e-8`. Neither observation converts an actual failed native test into a pass.

## Derivative study choice and claims

| Study | Independent directions | Domain and interpretation | Numerical limitation |
| --- | ---: | --- | --- |
| Original Cartesian h=1e-6 |14|Three probes exceed the declared trace domain|Cannot test AD there|
| Bounded Cartesian, h<=half trace band for alpha diagonals |14|Inside the implementation's declared finite-width domain; retains every AD column|Tiny normal-direction steps can amplify cancellation; mandatory h/h2 checks may fail|
| Tracefree alpha basis plus stress/e/gamma |13|Exactly spans all physical source state directions|Does not test isotropic alpha trace-normal derivative|

The frozen recommendation requires both admissible studies; neither is a fallback for the other. Full14-column Cartesian checks retain3e-5 relative/floored AD error limits at h and h/2, and add a1.5e-5 FD-level agreement gate. The rank13 physical-tangent study uses the same limits and h/h2 gate. This keeps the implementation's full ambient Jacobian claim while stating the physical source tangent claim precisely. All prior15 models retain their original h, AD assertions, fixture values, settings and later regression assertions. No tiny-step AD error or derivative convergence result has been observed; only domain, branch, rank and algebraic margins are proved here. `POLICY.md` freezes every concrete number before compiled execution. Any subsequent failure remains a failure; do not tune steps/limits from compiled outcomes.

For alpha, B1=(1,-1,0,0,0,0)/sqrt2, B2=(1,1,-2,0,0,0)/sqrt6 and B3/B4/B5 are the Mandel shear coordinate vectors. B-transpose B=I5; trace annihilates each column. Their rational unnormalized representatives have rank5. Adding six independent stress coordinates, e and gamma gives rank13 in14 coordinates, exactly ker(trace_alpha). The one excluded normal is proportional to the three diagonal-alpha unit vectors' sum. IEEE constructions at the zero-alpha base cancel the first two normalized diagonal directions' traces exactly; the probe receipts verify this as well.

All56 Cartesian h/h2 plus/minus probes and20 alpha-basis h/h2 probes satisfy the unchanged domain and source branch vector (relative_norm>0, psi sign, bn sign, D_raw sign). The stress/e/gamma directions of the rank13 study are already covered by the same Cartesian probes. The AD base is a residual trial, not an admissible initial or converged material state; its previous state remains the original valid hydrostatic parent. This distinction matches the unchanged residual evaluator use and does not bypass integration initial checks.

## Rotation algebra

Use4*p_ref=640kPa hydrostatic pressure plus a small distinct-eigenvalue deviator [500,-500,0,100,0,0]Pa, with source e=.65, alpha=0, gamma=0. It passes source initial-yield/domain checks before and after the exact orthogonal quarter-turn. Preserve the original strain, settings and .01Pa stress covariance gate, and add alpha/e/gamma covariance checks.

For every proportional prefix, pressure lies in[640000,650000]Pa. The backward-Euler elastic pressure map has its endpoint upper bound648688.007Pa below650000, and its derivative is less than0.01, so the fixed point is unique in that interval. The invariant deviator norm is at most18928.031Pa, while the yield radius is at least26127.891Pa: a strict7199.860Pa elastic margin. Source void ratio remains positive and psi<0. With alpha=0 and g=1, bounding gb is in[kbe/kbc,1], so bn>0 and b_ref-|bn|>=sqrt(2/3)*alpha_bc>0 for every Lode direction. Initial deviator and strain deviator have positive dot product, excluding a zero-normal crossing along the prefix. Thus the fixture needs no yield projection or altered material parameter to be admissible. This elastic rotation fixture does not establish plastic-path covariance; original independent full-path references remain mandatory.

## Minimal future isolated implementation whitelist

Recommended required paths, only after parent authorization:

- `tests/test_solver.cpp`: accept an additional **numerical-only** selector `ATLAS_NUMERICAL_FIXTURES=md1997-source-admissible-v1` alongside exact inherited `ATLAS_NATIVE_FIXTURES=explicit-gis20-occ-restart-duncan-v5`. Require MD presence and expected14-field layout; reject unknown selector/incompatible pairing before test work. Add only the MD probe/rotation branches and stronger MD checks. Keep all prior15 fixture branches/assertions and the unset-selector behavior unchanged. Emit a distinct profile label for the new mode.
- NEW `tools/check_md1997_native_fixture_contract.py`: verify the exact generated normal16 catalogue/model identities, invoke legacy explicit-v5 with the new selector removed, require exit1/exact `FD test outside domain`/original16-model stdout, retain complete argv/environment identity/return/stdout/stderr, then test unknown/new-selector pairing rejection. Use fresh outputs and bounded process timeouts. No generic material kernel belongs in this helper. Existing `check_native_fixture_contracts.py` and all its strict-original checks stay intact; that older tool's catalogue compatibility is separately assessed rather than silently widened here.
- `.github/workflows/verify.yml`: add the new selector only to the separately identified native admissible numerical CI profile on both platforms, while retaining inherited v5 for other native executables, existing checks, build matrix, serial targets and archival gates. Run the explicit16 legacy failure contract as a required gate. The normal CTest invocation can inherit the additional numerical-only selector without changing other tests. Do not mask atlas_numerical's nonzero exit; new profile execution must itself return success.
- `tests/test_ci_profiles.py`: lock the distinct selector/profile, required legacy-failure contract, original inherited token, both platforms and existing archival gates. Preserve every old assertion.

No CMake change is necessary: the existing atlas_numerical_tests target and atlas_numerical CTest already invoke this file and inherit environment. No target/build-list, runtime/model/schema/compiler, recorded-test, catalogue-policy or reference edit is required by this plan. If a separate named CTest is preferred, authorize only a new same-executable alias in root CMakeLists with its two explicit environment values; do not change or relabel the legacy test. That optional route needs a separately specified CI dispatch contract so it cannot accidentally ignore the original failure.

The independent implementation review must compare exact source diff/protected15-model behavior, environment dispatch, all unchanged inequalities and retained legacy contract before any actual new numerical result. Coordinator owns serial builds and compiled calls. This plan authorizes none.

## Evidence

`inputs.json` binds source/model, prior diagnostic, actual failure and source receipt. `proof-results.json` contains every domain/branch probe, rank result and rotation envelope. `prove.py` is reproducible with `python3 -B .../native-admissible-fixture-plan-v1/prove.py`; it writes only this plan's proof report. `manifest.json` binds the final prospective packet. Scientific approval and new-profile execution status remain unasserted.
