# Original clay 2005: Appendix C / Eq40 seven-rate study v1

Task: SRC-clay2005-appC-rate. Owner: review_vw96. Date: 2026-10-31.

This is a **research-only, zero-spin draft**, separate from the immutable [source-ingestion packet](../README.md). Nothing is added to the public catalogue or shared compiler. It follows the accepted manuscript Appendix C Eqs73-85 and p10 Eq40/41. Printed p10 Eq38 has the conflicting minus unloading bracket documented in the parent packet. No final-publisher equivalence, full source review or scientific admission is claimed.

## Files and identity

- `model.json`: standard Atlas 0.1 rate model, original five material parameters, seven state components, scalar/tensor actions only.
- `reference.py`: independently written stdlib Cartesian stress/stretching action oracle. No Atlas imports, DSL evaluation or source implementation calls; explicit 81-component fourth-order contraction.
- `reference.json`: deterministic 41-case corpus with all seven rates, original binary64 inputs, source identity and frozen comparison policy.
- `test_rate.py`: ten Python groups, including source/interpreter agreement, spherical analytical identities, rotations, signs, all shears, domain and arithmetic-floor witnesses.
- `check_study.py` / `checks.json`: portable fresh-reference replay, common-interpreter comparisons and retained results with source/model/oracle/runtime pins.
- `invalid-cases.json`: finite explicit negative witnesses and expected support rejection, not fitted numerical failures.
- `manifest.json`: exact local file whitelist/hashes; private copyrighted sources, author archive, bytecode and shared files excluded.

Source: [Mašín 2005 DOI](https://doi.org/10.1002/nag.416), [accepted manuscript](https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf), SHA256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`. General density continuity is [Mašín/Herle 2005](https://doi.org/10.1016/j.compgeo.2005.09.001), manuscript p9 Eq25, SHA256 `549e337e39505ba2757da6f4ab95a00c702d08952fbd9e2c48c8022be2e4189a`. Sources remain private; parent receipt pins access and page maps.

## Exact source-to-draft mapping

`p`, `H`, `Hdev` represent mean positive effective compression, source hat(T) and its deviator. Let `j2=Hdev:Hdev`, `j3=trace(Hdev^3)`. Source p24 Eq79 gives, in exact arithmetic,

```
det(H) = 1/27 - j2/6 + j3/3
I1*I2/I3 + 9 = (-j2 + 3*j3)/det(H)
Y = Yi + (1-Yi)*(j2-3*j3)*cos(phi)^2/(8*det(H)*sin(phi)^2)
```

The DSL uses these scale-free identities and `dev(dev(sigma))/trace(sigma)` to suppress a false spherical residual. This is a numerical evaluation choice, algebraically identical for exact traceless Hdev. The independent oracle instead evaluates the source invariant ratio through a Cartesian cofactor determinant. It is intentionally not copied from the DSL rewrite. Agreement near isotropy cannot certify the lost digits in that determinant subtraction.

`a`, `alpha`, `Delta`, `c1`, `c2` are main Eqs77,84,85; `Delta=3+a^2-2^alpha*a*sqrt(3)`. The fourth-order action is Eq75, `L:X=3[c1*X+c2*a^2*H*(H:X)]`. `F`, `m`, `m_unit` are Eqs80-82, with **H/3**, and denominator **2+sqrt(2)*tan(psi)*cos(3theta)**. `pe`, `fd`, `fs` are Eq83 using source reference pressure 1000 Pa. With sigma=-T, E=-D and **source m retained**, the positive-compression rate is

```
sigma° = fs * [L:E + fd*Y*(L:m_unit)*norm(E)]
e_dot = -(1+e)*trace(E)
```

Thus the nonlinear term is a **plus multiplying the negative spherical source direction**. A second sign flip of m would be wrong. State/loading Mandel order is `[xx,yy,zz,sqrt(2)*xy,sqrt(2)*yz,sqrt(2)*xz]` and stress is Pa. Physical frequency/time, spin, total strain, pc, IGS, structure and anisotropy are absent. Parameter `r` is Ki/Gi, not nu. The model's p_ref and p_scale are reference-unit and solver-scale metadata; fixed lode_allowance/j2_floor are numerical support metadata.

At exact sphere, source-derived F=1, Y=Yi and m=-a/(3+a²)*I are used. The local NCL loading and unloading tangents are p*v/lambda and p*v/kappa, respectively. Only NCL compression has the finite exponential NCL trajectory; finite unloading is generally nonlinear.

## Explicit bounded numerical support

The metadata bounds are deliberately finite research support: phi 0.01..1.4 rad, lambda 1e-4..1, kappa 1e-5..1 with kappa<lambda, N -10..10, r 0.01..10; alpha must additionally be positive. They are not a universal calibrated-material range. Stresses must have strictly positive eigenvalues (positive trace, pair invariant and determinant), e>=0, L positive definite (c1>0 and c1+c2*a²*(H:H)>0), and required factors positive/finite. Negative c2 alone is allowed. Broad finite arithmetic caps are declared in `model.json`; all derived values must also be representable. No density/pressure/Lode clipping, return map, stress reset or hidden state initialization is applied. An optional SOM diagnostic and true SBS admissibility are separate from this rate evaluability domain.

For nonzero deviators require **j2>=1e-100**. This floor is an arithmetic support decision: it keeps the `j2**1.5` Lode denominator above binary64 underflow, without attempting a wider scaled invariant implementation. It is not a source material constant, discontinuity or small-deformation regularization. Smaller nonzero values reject. If squared norm underflows to zero, an independently computed exact spherical component residual must also vanish; a tiny nonzero shear cannot masquerade as a sphere. The raw Lode invariant is required within ±(1+64*ulp(1)); it is **not clamped**. An internal zero placeholder is used below the floor solely to keep unsupported expressions evaluable until the domain rejection; no rate is accepted there.

Tests distinguish an exact sphere, nonzero shear whose j2 underflows, j2 at roughly 0.5 and 2 times the support floor, and a supported-but-uncertified tiny shear. Such boundary witnesses test rejection/branch semantics only, not numerical accuracy. The first comparison corpus deliberately contains only exact spheres or nonisotropic j2>=1e-8. **Near-isotropic accuracy remains an unresolved gate**, requiring an independently high-precision source evaluation rather than a loose direct-determinant comparison. The current draft is therefore not a certification of every rate it can algebraically evaluate.

## Reproduction and retained checks

From this directory in an installed checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 check_study.py --output checks.json
```

For the staged packet, supply a checkout containing the generic interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 check_study.py --repo /path/to/constitutive-atlas --output checks.json
```

Optional `--source /private/path/to/accepted-manuscript.pdf` verifies its exact hash. The private PDF is never required for ordinary replay. Independently replay the frozen reference with `python3 reference.py --output /tmp/clay2005-reference.json`; no repository-specific module is imported by that oracle.

All **41 seven-rate comparisons and ten unittest groups pass**. Largest stress discrepancy divided by the fixed input scale is approximately 2.50e-13; largest void-rate discrepancy is zero. Comparison policy was declared in source before evaluation: per stress component error <= 1e-10 Pa + 2e-12*S, where S=max(1 Pa,norm(sigma0))*norm(E); void-rate error <= 1e-15+2e-13*max(1,(1+e0)*norm(E)). These are floating-point numerical budgets, not error bounds on the constitutive theory. Invalid finite states/parameters and expected arithmetic-floor rejections remain explicit in tests and `invalid-cases.json`. No author code, C++ compilation, compiled execution or integration was performed. Tests of immutable input handling do not establish common-engine finite-update rollback.

## Smallest compiled study proposal and remaining gates

After independent source/model review, freeze these exact bytes and run the generic instantaneous-rate transport against this isolated model, serial native then Wasm. Use all 41 cases with the same predeclared policy, every full7 output, exact request/descriptor/source/model/artifact hashes, raw preparse stdout/C-ABI responses and both raw companions for parity. Include finite invalid cases, malformed/nonfinite/bool API probes and same-process known-state recovery; do not count a thrown domain error as transactional finite-path verification. Never relax this gate after observation. No model-specific kernel is required.

A later independent noncoaxial finite-path study must address all-stage domain support, coupled density, caller-state chaining, reversals, objective frame handling, adaptive error scales, budget-after-progress rollback and finite-update tangent scope. Near-isotropic high-precision accuracy, final-publisher Eq38 reconciliation, physical initialization/admissibility and experimental validation remain unresolved. This draft does not change original model counts or scientific admission.
