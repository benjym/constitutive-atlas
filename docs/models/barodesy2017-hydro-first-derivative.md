# Nonzero hydrostatic first derivative of the selected body-law variant

Source: [Medicus and Fellin, 2017](https://doi.org/10.1007/s11440-016-0458-4), body Eqs. 1–10, Table 2. This is original algebra for the zero-spin research selection with compression-positive stress sigma and loading E. Body Eq. 8 uses 2p/1000 Pa; Appendix Eq. 41 has the unresolved 6p equivalent. The following does not select an objective spin law or repair that source discrepancy.

Write E=tI+Z, t=s+trace(H)/3, Z=dev(H), z=||Z||, with fixed s≠0. Then r=sqrt(3t²+z²), U=E/r, delta=−3t/r, q=z/r and m=3sqrt(3/2)t/z. For source c1>0,

`log(K) = −2z²/(27 c1 t²) + O(z³/|t|³)` and `a = −2sqrt(2)z/(27 c1 |t|) + O(z²/t²)`.

The spherical factor in exp(−aU) cancels exactly on normalization. The remaining traceless argument is −aZ/r, so

`P = I/sqrt(3) + 2sqrt(2)/(81 c1 t²) ||Z|| Z + O(z³/|t|³)`.

The leading coefficient is identical for both loading signs. Thus DP=0 and Ddelta=0 at E=sI, while `Dr[H]=sign(s) trace(H)/sqrt(3)`. The estimates are uniform locally with |t| bounded away from zero.

The correction ||Z||Z is C1 with derivative zero at the origin, but not C2: a quadratic second differential would be even under Z→−Z, whereas this correction is odd. Centered first differences along pure deviatoric perturbations therefore generally converge only as O(|h|). A literal exact-hydro branch with constant P and delta can give the true first derivative, while auxiliary a/q/m need not themselves be differentiable there.

Let n=||sigma||, p=trace(sigma)/3, V=1+e, d=V/(1+ec), A=d^c5, P0=I/sqrt(3), and compute source f0,g0 at delta0=−sqrt(3)sign(s). Let `F=c3 r (f0 n P0 + g0 sigma)`.

For state perturbation (Sigma,eta),

`D_state F = c3 r [ f0 (sigma:Sigma/n) P0 + g0 Sigma + sigma A c5 (eta/V + lambda_star trace(Sigma)/(3p)) ]`.

The pressure-density term is essential: stress scaling alone is not a homogeneous response because the critical void ratio depends on p. For loading perturbation H,

`D_E F[H] = F trace(H)/(3s)`.

Void closure gives `D_state(e_rate)=−3s eta` and `D_E(e_rate)[H]=−V trace(H)`. Consequently the three normal-loading columns are identical and the three loading-shear columns vanish. These formulas define all 91 components of the 7×13 instantaneous Jacobian in the Mandel basis. They assume a supported smooth interior state and fixed material parameters, not a derivative at a support boundary.

At zero loading, positive degree-one homogeneity would force a Fréchet derivative to reproduce all directional rates. The same supplied state has generically nonodd opposing hydrostatic responses, contradicting linearity. No unique zero-loading Jacobian follows, and F/(3s) must never be extended by substituting s=0.

The independent review checked both signs, the expansion coefficient, opposite one-sided curvatures, the full Jacobian's covariance, density scaling correction, and retained directional evidence. The [separate exact-hydro generated Jet study](../reviews/barodesy2017-hydro-ad-study.md) now verifies this first derivative for 36 supplied inputs in native and Wasm; the derivation does not broaden that numerical scope. The regular-direction driver and its exclusions remain unchanged.
