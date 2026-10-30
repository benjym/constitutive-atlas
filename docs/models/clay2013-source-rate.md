# Clay2013 source-rate algebra

The [typed fragment](../../catalogue/source-audits/clay-hypoplasticity-2013-rate.json) now represents the complete instantaneous zero-spin stress/void-ratio rate from the pinned2013 author manuscript. It is separate from executable models. It supplies no finite-step integrator, universal calibration,2014 anisotropy, IGS overlay, experimental validation or admission decision.

[Primary DOI](https://doi.org/10.1007/s11440-012-0199-y); [author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf), SHA256 `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`. Appendix Eqs43–58 on PDFpp13–14 were visually rechecked. The [source inventory](../reviews/clay-2013-2014-source-packet.md) preserves the online2012/issue2013 distinction and pending complete manuscript/final reconciliation. No source PDF or experimental data is redistributed.

## Represented quantities

The five parameters are explicit: phi_c in radians; lambda_star, kappa_star, N and nu dimensionless. Source reference pressure is fixed to1000Pa. The state is effective compression-positive Mandel stress plus void ratio e, seven scalar components. Input stretching is compression positive per a dimensionless caller coordinate, with zero spin. Both source signs are transformed: T=-sigma and D=-stretching. The rate is -T_circle and e_rate=-(1+e)trace(stretching). A physical clock is not a material parameter.

The [reduced evaluator](../../tools/inspect_clay2013_rate.py) interprets checked SI-typed expressions. Fourth-order tensors are eliminated through L:X=X+c trace(X)I and A:X=fs(L:X)-(sigma/lambda_star)trace(X), c=nu/(1-2nu). The independent [Cartesian oracle](../../tools/reference_clay2013_cartesian.py) instead forms81 fourth-order components, contracts them explicitly, and uses cofactor determinant and actual matrix products. See its [derivation](clay2013-cartesian-source-note.md).

## Numerical branches

For a=dev(sigma/trace(sigma)), j2=a:a and j3=tr(a^3), the source invariant quotient reduces exactly to

`Fm=(j2-3*j3)/(8/27-(j2+j3)/3)`.

The evaluator projects twice **before** normalization, `dev(dev(sigma))/trace(sigma)`. The second projection is algebraically idempotent and removes a spurious spherical residual while retaining tiny supplied pressure differences. No tensor component or invariant is clipped. The independent [180-digit diagnostics and derivation](../reviews/clay2013-algebra-review.md) verify this identity and the strict-positive-definite invariant bounds. High-precision comparisons use the exact actual binary64 inputs, avoiding comparisons with ideal states lost during input rounding.

At exact isotropy, Fm=j2=0. Eq57's Lode quotient is undefined, but Eq56 has the direction limit d=-I/sqrt(3). A placeholder cos3theta=0 is evaluated only when j2=0 and does not affect that direction; nonisotropic input with an underflowed zero j2 rejects. Near-isotropic inputs follow the ordinary equations, without a threshold norm or pressure floor. Raw Lode cosine permits a documented64ulp arithmetic margin around[-1,1] and remains unclipped.

The diagnostic domain requires e>=0, lambda_star>kappa_star>0, -1<nu<0.5,0<phi_c<pi/2, strictly positive-definite compression stress, resolved positive pe/fd/fdA/fs,0<=Fm<1,omega>0 and finite executed intermediates. Positive definiteness is checked with scaled Cholesky. These restrictions do not prove complete source/ASBS admissibility. ASBS f=Fm+(p/pe)^omega-1 is reported, not used as a yield function or projection. Extremely small angles and nearly singular stresses can lose precision or reject; the Decimal record includes a real SPD state whose Fm rounds to1. No uniform accuracy claim is made there.

## Checks and next work

```sh
python -m unittest tests.test_clay2013_rate tests.test_clay2013_invariants -v
python -m tools.clay2013_invariant_reference --output /tmp/clay-invariants.json
```

Six source-rate groups cover40 noncoaxial Cartesian comparisons and rotations, positive homogeneity, explicit units/signs, unchanged inputs, exact isotropic loading/unloading/density and zero rates, Lode endpoints, near-isotropic continuity, actual-float high-precision comparisons and invalid-domain rejection. Five independent Decimal/integrity groups reproduce19 retained fixtures at180-digit precision, including exact isotropy, both Lode endpoints, perturbations through1e-45 and rotated stresses. The [record](../../catalogue/investigations/clay2013-algebra-v1/manifest.json) binds inputs, code, source identity and limits.

Next work is a source-reviewed initial-state/ASBS policy, boundary arithmetic treatment, a coupled stress/density research model, partition/tolerance studies and controlled native/Wasm parity. Finite spin and source-matched reference/experimental histories remain separate gates. No C++ code or executable model catalogue is changed by these algebra checks.
