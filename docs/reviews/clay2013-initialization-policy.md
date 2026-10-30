# Clay2013 initialization and ASBS policy: bounded source review

Status: design proposal plus local source-rate diagnostic, 31 October 2026. No model admission, validation, native run or constitutive integration is claimed.

## Source and scope

Pinned author manuscript: David Mašín, *Clay hypoplasticity with explicitly defined asymptotic states*, Acta Geotechnica 8, 481-496 (2013), DOI [10.1007/s11440-012-0199-y](https://doi.org/10.1007/s11440-012-0199-y). Author URL: https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf . SHA256 `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`. Page numbers below are printed manuscript pages (also one-based PDF pages). The manuscript may differ from the publisher version. Equations on pages 3-4 and appendix pages 13-14 were visually inspected; extracted text was searched for preparation/initial-state statements throughout. This packet contains no source PDF, images or extracted manuscript text.

## Finding: ASBS is not a universal hard acceptance barrier

Page 4 Eq17 defines the ASBS by the equality `f = Fm + (p/pe)^omega - 1 = 0`, with invariants in Eqs18-21 and omega in Eq25 (fixed a=0.3). It does not specify a universal initial-state inequality or a yield-return algorithm. Page 4 footnote explicitly cautions that Fm=1 does not exactly represent the boundary of compressive stresses. Therefore neither the algebraic surface nor Fm is a substitute for a compressive-stress domain check.

Page 9 Fig10 starts from an arbitrary state *within* ASBS, providing evidence of that example's preparation, rather than permission for arbitrary initial states outside it. Page 9 discussion says normally consolidated undrained compression approximately follows ASBS; exact invariance is not asserted. Page 10 Fig11 uses initial states along a K0 unloading line. The kaolin example on pages 9-10 loads isotropically to 1000 kPa and then unloads to p0/OCR. These support preparation through loading history. No explicit source prescription admitting or rejecting all outside-ASBS initial states was located. Absence of a ban is not evidence that arbitrary outside states are physically meaningful.

More decisively, the source-rate field can point outward at a regular state on ASBS. The witness below means a hard `f<=0` check at every accepted material stage would impose an extra law inconsistent with this rate field. This is a local mathematical diagnostic, not a claim of calibrated physical validity outside ASBS or of integrated-path convergence.

## Reproducible outward-rate witness

All tensors are Cartesian, symmetric, compression positive; source signs are converted by T=-sigma, D=-E; spin is zero. Parameters: phi_c=0.5 radians, lambda*=0.1, kappa*=0.01, N=0.9, nu=0.2. Stress in Pa: diag(160000,90000,50000). Compression stretching: diag(0.008,0,-0.01), per arbitrary caller coordinate. Mean pressure is 100000 Pa. Fm=0.21632653061224466; omega=0.3727297772767159. Density is constructed algebraically on ASBS: pe/p approximately 1.9232057687487762 and e approximately 0.45365872198939217.

The independent Cartesian source oracle (explicit fourth-order contractions of appendix Eqs43-58) returns stress rate approximately diag(-24212.59998079,2822.45829876,-26514.65125579) Pa per coordinate and e_rate=0.002907317443978784. All oracle domain/factor checks pass. Analytic differentiation of Eqs17-21,25,48 gives f_dot=+0.06127039683203732. Tangent-state central differences with h=1e-3,1e-4,1e-5,1e-6 give respectively 0.06127041409,0.06127039700,0.06127039683,0.06127039710. Every positive tangent probe has f>0. Initial f is 6.53e-17, an algebraic-roundoff residual.

The analytic derivative uses the invariant quotient derivative and independent density evolution: log(pe)_dot=-e_dot/[(1+e)lambda*]. No derivative is estimated by differentiating the oracle code. The finite differences perturb sigma and e along the returned rate; they are not time steps, solved trajectories or a temporal convergence study. A regular positive directional derivative establishes local outwardness of the continuous field, subject to the stated source-rate/domain interpretation.

## Density initialization algebra (source-derived)

Page 3 Eq5 and page 13 Eq48 give `pe = pr exp[(N-ln(1+e))/lambda*]`, pr=1000 Pa. For explicit positive R=pe/p:

`e = expm1[N-lambda* (ln(p/pr)+ln R)]`.

R must not silently be called OCR: outside isotropic preparation it is a density-normalization ratio. On the isotropic ASBS, Fm=0 and p=pe, hence `e_NC(p)=expm1[N-lambda* ln(p/pr)]`. At fixed nonisotropic stress with 0<=Fm<1 and omega>0:

`R_boundary=(1-Fm)^(-1/omega)`

`e_boundary=expm1[N-lambda* ln(p/pr)+(lambda*/omega)ln(1-Fm)]`.

Within this domain, `f<=0` is equivalent to e<=e_boundary. If the computed boundary e is negative, no nonnegative-e state lies on or inside that surface for this stress/parameter set; do not clamp the result to zero. Page 3 Eq7 becomes `e_dot=-(1+e)tr(E)` in compression-positive convention.

The exact isotropic instantaneous rate derived separately from Eqs43-58 is `p_dot = p/2 [(1/lambda*+1/kappa*)v + (p/pe)^2 (1/lambda*-1/kappa*)abs(v)]`, v=tr(E). At p=pe it gives p*v/lambda* for compression and p*v/kappa* for unloading. These are instantaneous slopes: finite unloading changes pe/p, so a global straight unloading line with constant slope kappa* is not established by this local identity.

## Proposed isolated research contract (project choices)

Require explicit five parameters, six initial stress components and e. Do not infer e, preconsolidation pressure, OCR, spin or preparation. State is stress6+e, with common solver strain state separate. The diagnostic scope is zero spin, finite SPD compression-positive stress, e>=0, 0<phi_c<pi/2, lambda*>kappa*>0 and -1<nu<0.5. Require 0<=Fm<1, omega>0 and positive finite required constitutive factors, nonzero source direction norm and finite rates. These are conservative project restrictions for an evaluable research branch, not a claim of the paper's full admissible domain. Exact isotropy needs its analytic branch; no arbitrary direction or near-isotropy clipping should be invented. Direct determinant Fm evaluation can lose precision near isotropy, so this independent oracle's near-isotropic rejection is not a physical boundary.

Default initialization: validate the algebraic research domain; report ASBS residual/log-gap and declared preparation without imposing ASBS containment. A separately requested prepared-on/inside policy may reject an initial state by an explicit, recorded project tolerance, but must be labeled a preparation constraint, and must not become a continuous yield barrier. Outside initial states remain research inputs requiring explicit provenance; no source-backed physical-validity claim follows.

For robust classification use dimensionless `gap = omega*ln(p/pe)-ln(1-Fm)`; `f=(1-Fm)*expm1(gap)` has the same sign. Use a declared symmetric numerical tolerance on gap for diagnostic labels; do not mutate the input to satisfy it. If optional residual exponentiation overflows but the gap/material evaluation is finite, report the residual as unavailable rather than silently clip it or reject solely for a diagnostic. The simple witness script is intentionally bounded to its moderate regular inputs; it is not a production full-range input validator.

At each trial/stage: validate actual material domains and finite rates/state; let the common solver's residual/error checks determine numerical acceptance; roll back failures transactionally. Record ASBS excursions separately. Do not project onto ASBS, clip Fm/e/pressure, add a plastic return, or reject solely because f>0. Testing and calibrated preparation/experimental comparison are still needed before making scientific-use claims.

## Reproduction and checks

From the repository root (source PDF remains private and is not required to replay the pinned diagnostic):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m tools.clay2013_asbs_diagnostic --output catalogue/investigations/clay2013-initialization-v1/outward-asbs-evidence.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_clay2013_initial_policy.py -v
```

To additionally verify the private original manuscript, pass `--source /absolute/private/path/masin-2013-author.pdf` to the diagnostic command. The retained evidence was generated with this verification; omitting it changes only the source-file-verification flag. Both the oracle's declared source hash and actual Python-file hash are checked on every witness call. Source receipt binding does not replace access to the manuscript for independent scientific review.

Four test groups pass: isotropic ratio-density round trips; nonisotropic boundary/signs; rejected invalid/negative-density conversions without clipping; outward derivative versus independent central differences. Evidence binds source, oracle and diagnostic script hashes; the manifest binds repository-relative installed file paths. No native code or integration was run. Remaining source gap: a universal physical initial-state policy is not established by the manuscript and must not be presented as source-defined.
