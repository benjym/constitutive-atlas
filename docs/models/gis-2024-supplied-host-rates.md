# GIS2024 supplied-host directional-rate fragment

Draft source fragment only. No complete HP+GIS model, admission, finite-step update or independent implementation review is claimed.

Source: Mugele, Stutz & Mašín (2024), *Generalized intergranular strain concept and its application to hypoplastic models*, Computers and Geotechnics 173, 106480, DOI [10.1016/j.compgeo.2024.106480](https://doi.org/10.1016/j.compgeo.2024.106480). Primary [institutional PDF](https://publikationen.bibliothek.kit.edu/1000171366/153009465), private SHA256 `39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3`. Equations33–35,39–43, printed/PDF pp5–7 were visually inspected under the PDF skill. Convention verified AppendixA p12. Source PDF/extractions/renders are private and not in this stage.

## Exact boundary

`catalogue/source-audits/gis-2024-supplied-host-rates.json` contains typed existing-DSL expressions and source locators. `tools/inspect_gis2024_rates.py` validates dimensions using `atlas.dsl.infer`, interprets expressions with the restricted DSL, and binds a supplied host linear action. It does not use Python `eval`, generate C++, integrate a material state or call the solver.

`de` denotes the strain derivative with respect to a dimensionless path coordinate, rather than a finite step whose response can be committed. Outputs `h_rhs`, `Omega_rhs`, and `sigma_rhs` are instantaneous directional rates. Degree-one homogeneity allows the same algebra to act on direction/increment-sized arguments, but does not make Euler integration exact.

The host must explicitly supply normalized `m`, scalars `C,S`, homogeneous correction `f`, and a finite 6x6 Mandel matrix representing `E` at this state. The test runner applies this matrix once to the DSL-computed `effective_de`; `E_effective_de` is a typed Pa tensor binding, not a new DSL primitive. The outer factor `k` then multiplies the entire action. `f` is explicitly required, including zero for the selected HP host; it is not silently inferred from a model ID. The host is responsible for `E,m,C,S,f` construction, compatibility, physical domains and `f` homogeneity. No HP inverse or ASBS projection is implemented here, and no assumption of symmetric/positive-definite E is imposed by the fragment runner.

## Sign mapping derivation

The paper uses tension-positive stress and extension-positive stretching (p12 AppendixA). Define Atlas variables `sigma_A=-sigma_source`, `de_A=-de_source`, `h_A=-h_source`, `m_A=-m_source`, and `f_A=-f_source`. Euclidean norms are unchanged; normalized directions change sign; therefore `dot(hdir,de)` and its loading/unloading branch are unchanged. Eq33 transforms into the same algebra in Atlas variables. In Eq40, the entire inner strain-like argument changes sign; multiplying the source stress rate by minus one leaves the same operator E acting on the Atlas inner argument. Thus E's Cartesian linear action is unchanged, while `C,S,rho,k,chi,gamma,Omega` are unchanged. Convert all tensors to Mandel components using sqrt(2) shear factors. h is a full symmetric strain memory, with no deviatoric projection.

This is a convention mapping for zero-spin instantaneous material algebra. The source's objective Zaremba–Jaumann stress rate does not establish a full finite-rotation adapter.

## Zero direction and bounded audit domain

Eq39 contains a normalized strain direction. It has no unique value at `de=0`; this ambiguity concerns the diagnostic k, not the rates. For finite admissible state and host quantities, k and the suppression factor are bounded over direction, while the stress-rate inner argument, h rate and Omega rate vanish linearly with strain-direction magnitude. The runner therefore uses an explicit analytic zero-rate continuation: exact-zero `de` requires exact-zero `f`, returns zero rates and `effective_de`, and reports `q`, `k` and `suppression` as `None`. It does not invent a direction or assign k=m_R. No epsilon norm is used. A nonzero input whose DSL norm underflows is rejected rather than treated as zero. This continuation is a derived mathematical policy, not a claim that the paper or author code specifies the same discrete branch.

The JSON distinguishes its selected positive-parameter audit domain from exhaustive source parameter limits. It checks finite typed inputs without bool-to-number coercion, normalized m, and h/Omega bounds. It permits norm(h) up to `R+16*ulp(R)` to allow component roundoff in a prescribed fully mobilized hydrostatic initial h. This does not alter h or project it onto the radius. No endpoint clamp, reset or integration policy follows from this narrow arithmetic tolerance.

The nested exponent is `S**(k**gamma)`. `gamma_Omega` is independent from `gamma`: Table1 p8 supplies gamma_Omega=1, while gamma varies with Omega through Eqs41–42. The optional textual identification with gamma in some HP coupling is not automatically selected. Omega can decrease, so it is not a monotonic accumulated-history counter.

## Independent checks and reproduction

Nine test groups pass in pure Python. They cover typed units, nested exponent, zero h, full isotropic/nondeviatoric h, exact-zero direction, positive/negative/tangential loading, fully mobilized 0/90/180-degree checks, Omega increase/decrease, independent gamma_Omega, S=1, supplied nonzero f, bad types/domains and norm underflow. Forty deterministic non-axisymmetric randomized cases compare DSL rates to independent Cartesian 3x3 contractions and a supplied anisotropic host action. Each also tests oblique rotational covariance with the host operator rotated consistently, the source/Atlas sign transformation, and degree-one strain-direction scaling. The oracle uses ordinary Cartesian matrix arithmetic, not DSL tensor norm/dot/action helpers. These are algebra tests, not material validation or reference-code equivalence.

Run from the repository root:

```sh
python -m unittest tests.test_gis_fragment -v
```

Next gate: independent equation/sign review, then the separate selected HP/extracted-ASBS host-action fragment with Cartesian oracle. Source-code discretization, initialization and reference equivalence remain separate pending work. This packet adds Python-only algebra; no native build or executable-model admission is supplied.

A reviewed algebraic rewrite evaluates Eq39 as convex interpolation in t=rho**chi_R and q. At t=q=1 it retains k=1 even for m_T=1e20, where the direct source expression loses the unit term by cancellation. Exact0/90/180degree large-ratio regressions pin these limits. Raw q has an explicit64ulp arithmetic margin and remains unclipped; an unresolved nonpositive k is rejected. Numeric inputs must roundtrip exactly through binary64, and all executed expression intermediates are checked.
