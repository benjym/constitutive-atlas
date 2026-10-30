# Independent Cartesian clay-2013 rate oracle

Research diagnostic only: no integration, constitutive admission, independent scientific-review completion or 2014/IGS claim. Standard-library Python only; the implementation imports neither Atlas nor any reduced/Mandel implementation.

Source: David Mašín, *Clay hypoplasticity with explicitly defined asymptotic states*, [DOI](https://doi.org/10.1007/s11440-012-0199-y), [author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf), SHA-256 `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`. Appendix equations 43–58 on author-PDF pages 13–14 were visually inspected again for this task. Objective/density conventions are p.3 Eqs.(1),(3),(7). Full publisher/manuscript equivalence remains unverified. No original PDF/text/render is included here.

Interface: `rate(stress, stretching, e, *, phi_c, lambda_star, kappa_star, N, nu)`. Both matrices are finite, exactly symmetric 3×3 Cartesian tensors with **compression positive**. Stress is in Pa, phi_c in radians, e and the other four parameters dimensionless; stretching is per caller coordinate. No physical time scale is inferred. Returns `stress_rate`, `e_rate` and intermediate diagnostics. Source conversion is `T=-stress`, `D=-stretching`; the returned rate is `-T_circle`. W is identically zero. No Jaumann finite-spin update is supplied.

The oracle forms all 81 components of the fourth-order L and A, including the symmetric fourth-order identity, then sums both contractions explicitly over k,l. It calculates determinant by Cartesian cofactors and cubic trace through two actual 3×3 matrix multiplications. Source invariants use I2=(T:T-tr(T)^2)/2, including its unusual sign. For Fm only, all three invariants are evaluated from T/p to avoid dimensional cubic overflow; Fm is unchanged by that common stress scale. Diagnostics identify this normalization. It never invokes the reduced isotropic contraction formulas or a Mandel conversion.

Exact isotropic branch: T=-p1 gives Fm=0 and That_star=0. For 0<phi_c<pi/2, Eq.(56) has the direction limit

`dA = -(2/3) [sin(phi_c)^xi/(1-sin(phi_c)^xi)] 1`, hence `d=-1/sqrt(3)`.

Only exact spherical Cartesian input triggers this branch. It is the algebraic limit; no arbitrary Lode angle is assigned (`cos3theta=None`). Near-isotropic non-spherical inputs use the printed expressions and may reject if cancellation takes Fm or cos3theta outside their domains. No clipping/perturbation is applied. Underresolved limits need further numerical analysis, not a claim of general stability.

An independent scalar derivation supplies `isotropic_pressure_rate`. Let v be compression-positive volumetric stretching, `r=(p/pe)^2`, `B=(3p/2)(1/lambda_star+1/kappa_star)` and `C=(3p/2)(1/lambda_star-1/kappa_star)`. Since L:1=(1+nu)/(1-2nu)1, `fs L:1=B1` and `A:d=C1/sqrt(3)`. Substituting D=-v1/3 and ||D||=|v|/sqrt(3) into Eq.(43), followed by stress-sign conversion, gives

`p_dot = (p/2)[(1/lambda_star+1/kappa_star)v + r(1/lambda_star-1/kappa_star)|v|]`.

At an isotropic NCL state pe=p: loading v>0 gives `p_dot=p*v/lambda_star`; unloading v<0 gives `p_dot=p*v/kappa_star`. These are instantaneous rates at that state, not claims of an exact finite unloading curve. At other densities, the general r formula applies. Density separately obeys `e_dot=-(1+e)v` from source Eq.(7). A zero stretching tensor yields zero rates after state/domain validation.

The conservative diagnostic domain chooses e≥0, lambda_star>kappa_star>0, -1<nu<1/2,0<phi_c<pi/2 and strictly positive-definite compression stress (Sylvester criterion). It additionally requires 0≤Fm<1,omega>0, nonzero real denominators/norms, positive represented density factors and finite intermediates/results. All these are explicit diagnostic restrictions, not a complete source-domain theorem. No ASBS yield projection or initial ASBS admission is inferred. Inputs with nonfinite numbers, booleans, asymmetric matrices or singular/tensile stress reject. Overflow, underflow-to-zero factors and unresolved scalar/tensor domains reject with ValueError; this is ordinary binary64 arithmetic, not an arbitrary-precision oracle. The isotropic helper likewise rejects nonrepresentable factors. There are no hidden parameter defaults or calibration sets.

Local Python checks exercised nine isotropic loading/unloading/zero cases across three densities, with maximum absolute difference 6.99e-10 Pa per coordinate against the separately derived scalar helper; 30 seeded positive-definite/noncoaxial cases checked positive homogeneity, direction norm and mutation isolation; four malformed matrix cases rejected. These smoke checks do not replace a retained independently authored comparison suite or the parent reduced implementation comparison. No native executable or build was run.
