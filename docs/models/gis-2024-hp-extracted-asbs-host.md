# Selected HP / extracted-ASBS host for GIS2024

Draft instantaneous host-action fragment; **not a complete material model or admission**. The source is Mugele, Stutz & Mašín (2024), *Generalized intergranular strain concept and its application to hypoplastic models*, Computers and Geotechnics173,106480, DOI [10.1016/j.compgeo.2024.106480](https://doi.org/10.1016/j.compgeo.2024.106480). [Primary institutional PDF](https://publikationen.bibliothek.kit.edu/1000171366/153009465), private SHA256 `39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3`. Printed/PDF pp3–4 and12 were visually inspected. AppendixB restates von Wolffersdorff (1996) HP; this packet does not assert a new audit of the original1996 paper.

`catalogue/source-audits/gis-2024-hp-extracted-asbs-host.json` provides typed existing-DSL scalar/tensor expressions with source locators, including the derived linear actions. The current effective stress, void ratio and eight HP material parameters are explicit required inputs. There are no universal preparation values or numerical scaling parameters. The helper returns `E` as a finite6x6 Mandel matrix, normalized `m`, scalars `C,S`, and explicit zero `f`, matching the prior supplied-host GIS runner. It also returns the typed intermediates and actions for inspection. No state evolution, finite increment, ASBS preparation root or solver is evaluated.

## Source formula and inverse derivation

Let `H=sigma/trace(sigma)`, `Q=H:H`, and use the paper's `F,a` (AppendixB B.4–B.8). AppendixB B.2 gives

`L(X) = [F² X + a² H (H:X)] / Q`.

Applying the identity-plus-dyadic inverse yields

`L_inverse(X) = Q/F² [X - a² H (H:X)/(F²+a²Q)]`.

This second formula is a derived action, not a printed inverse equation. No general fourth-order storage or inversion primitive is introduced. Its derivation follows by decomposing X into its component along H and its orthogonal complement: L has eigenvalues `(F²+a²Q)/Q` along H and `F²/Q` on the complement. Both compositions are independently checked against dense pivoted elimination and arbitrary symmetric X. AppendixB **B.10 is the density factor fd, not an inverse**.

With the compression-positive nonlinear direction `N`, compute `B=L_inverse(N)` (Eq26), `Caux=L_inverse(unit(sigma))/fs` (Eq27), and the pressure derivative `G` (Eq28). `Caux` has units inverse Pa and is distinct from scalar host C. `G` has units inverse Pa. The JSON carries these dimensions explicitly.

For current-state projected asymptotic factor, set the presumed asymptotic stress/void ratio equal to the supplied current state as described after Eq32. Write `r=(1+e)/e`, `d=G-r*trace(Caux)` and `t=r*trace(B)/d`. The Eq31 bracket is

`B:B + (norm(Caux)*t)² + 2*(B:Caux)*t = norm(B+t*Caux)²`.

The fragment uses `fdAstar=1/norm(B+t*Caux)`. This is an algebraic rearrangement of Eq31, retaining its domains while avoiding subtraction of large scalar terms in the expanded bracket. It does not remove the underlying sensitivity if the vector itself nearly cancels. A separate oracle evaluates the expanded original source-sign Eq31 rather than reusing this rearrangement.

The final host interface is exactly Eqs8–12:

- `E(X)=fs*L(X)`;
- `m=-B/norm(B)`;
- `C=norm(B)*fdAstar`;
- `S=fd/fdAstar`;
- `f=0`.

This selects extracted-ASBS HP. It never substitutes the separate `S=Y,C=1` pairing. The actual ASBS reference-state search is a distinct numerical preparation task; the projected factor evaluation here is not that root search. The void-ratio evolution Eq22 would change sign under the convention mapping, but is deliberately outside this host-action fragment.

## Sign mapping

The paper uses extension/tension-positive conventions (AppendixA p12). Atlas uses `sigma_A=-sigma_source` and `de_A=-de_source`. H, F, a, fs and L are unchanged because H is normalized by trace. AppendixB B.3 defines the source positive nonlinear tensor; define the fragment's `N_A=-N_source`. Then `B_A=-B_source`, `Caux_A=-Caux_source`, and `G_A=-G_source`. The denominator d also changes sign, t is unchanged, and `B+t*Caux` changes sign, preserving its norm and fdAstar. Hence `m_A=-m_source`; scalar C,S are invariant. The original Atlas HP rate reconstructs as `E(de)+fs*fd*N_A*norm(de)`, identical to `E(de-m*C*S*norm(de))`. This closure is tested independently of the GIS k expression.

All tensor components use Mandel order xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz. phi is radians; hs is Pa. Published Table1 p8 values are fixture inputs only, converted from34degrees and111746kPa. No direct Table1 calibration claim against Wichtmann data is made.

## Limits and domains

Exact isotropy gives H=I/3, Q=1/3 and F=1. The Lode angle is undefined there; the helper stores `cos3theta=0` only as an unused diagnostic because tanpsi=0 makes F independent of Lode. The deviator is computed as dev(dev(sigma))/trace(sigma), algebraically equal to dev(H), to preserve exact spherical stress without an artificial near-isotropy threshold. It uses an exact lazy zero-j2 branch, rejects nonisotropic invariant underflow, and checks the raw Lode cosine within64 binary64 ulps of[-1,1] without clipping. The analytic checks are

`L(X)=3X+(a²/3)trace(X)I`, `B=-a/(3+a²)I`, and `m=I/sqrt(3)`.

A separate closed-form isotropic fdAstar check follows by substituting `Caux=I/[sqrt(3)fs(3+a²)]` into Eq31. Axisymmetric compression, extension, exact isotropy and one near-isotropic state are checked. These are not exhaustive floating-point limit proofs.

The audit scope requires finite typed inputs excluding bools, hs>0,0<n<1,0<phi<pi/2,alpha>0,beta>=0,ordered positive limiting void ratios, positive current pressure and `ed<e<ei`. These are explicit bounded audit restrictions, not asserted exhaustive physical parameter bounds. Every evaluated intermediate must remain finite. The helper checks F denominator/radicand, F, fs denominator, fs, inverse denominator and B norm before their dependent divisions, rejects exact-zero Eq31 denominator, and rejects zero ASBS vector norm. It adds no denominator floor, pressure cutoff, Lode clamp, state projection or tensile-principal-stress filter. Numerical underflow/overflow leads to rejection when a required finite positive factor fails; no finite reference-code-equivalence claim follows.

`catalogue/investigations/gis2024-hp-host-v1/retained-diagnostics.json` records the36 deterministic non-axisymmetric sample margins. Maximum fdAstar relative discrepancy versus the expanded original-sign oracle is `8.913718231995938e-16`; minimum scaled Eq31 denominator margin is approximately0.4193. Thus these samples are well conditioned relative to that denominator. **Near-singular Eq31 behavior is not numerically validated by this packet.** Root-factor singularities and intended host admissibility policy remain separate review/integration gates; do not regularize them silently.

## Verification and next gate

Eight pure-Python test groups pass. The independent oracle builds L by ordinary Cartesian3x3 contractions, converts its action to a dense6x6 matrix, and solves it with pivoted elimination. It evaluates N,B,Caux,G in the paper's original tension-positive convention and Eq31 in expanded form. Thirty-six deterministic positive-definite non-axisymmetric stresses across pressures are compared, along with inverse round trips and oblique covariance. Other checks cover typed units, missing inputs, invalid domains, isotropic analytic reductions, compression/extension limits, original-HP closure and compatibility with the existing GIS fragment. The covariance test rotates both stress and action argument; the resulting operator covariance is checked without assuming an isotropic frozen E matrix.

Run from repository root:

```sh
python3 -m unittest discover -s tests -p 'test_gis_hp_host.py' -v
```

Evaluator: `tools/inspect_gis2024_hp_host.py`; independent stdlib Cartesian/dense reference: `tools/reference_gis2024_hp_host.py`; tests: `tests/test_gis_hp_host.py`. The evaluator uses the existing finite-intermediate restricted history AST interpreter. The reference accepts plain sequences and calls no Atlas DSL or structured-inverse helper. The composition test imports the existing `tools.inspect_gis2024_rates` and its repository source-audit JSON. Neither native code nor material integration is executed.

Before a complete pairing is admitted: independently review source equations/signs; settle behavior near singular domains; add explicit source-backed initialization and void-ratio evolution; choose/test a discrete integration and transactional policy; inspect author code/license; and compare the paired model with independent reference histories. These host and GIS fragments provide bounded algebra evidence only. No build, native run or admission is claimed for this algebra packet.

The independent technical review identified a density-factor underflow acceptance bug in the staged helper. The strict open-density domain now requires positive finite fd, C and S (along with required density/stiffness factors), rather than allowing a numerically underflowed zero to masquerade as a source boundary. The retained regression uses nextafter(ed,+infinity) with alpha=30. Exact spherical stresses at0.1,0.3 and100000Pa and a nonzero underflowing shear invariant are also checked. Review remains an AI technical check; scientific admission is pending.

The host now feeds the [full14 research rate definition](gis2024-research-rates.md). The host-only claims and near-singular limitations above remain distinct from that engine evidence.
