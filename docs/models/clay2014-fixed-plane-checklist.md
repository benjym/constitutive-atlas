# Clay2014 manuscript: fixed-plane base-law implementation checklist

Read-only source review,31October2026. Target DOI10.1680/geot.13.P.065, *Clay hypoplasticity model including stiffness anisotropy*. The pinned16-page author manuscript is dated26November2013; it is not verified final publisher text. PDF SHA256 `2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202`, [author URL](https://web.natur.cuni.cz/uhigug/masin/download/Masin_Geot14-pp.pdf). All pages below are one-based manuscript PDF pages. PDF skill read; complete relevant page images2,3,9,10 visually inspected. No source files/renders/text are part of the public whitelist.

## Exact typed formulas

Let r=alpha_E, g=alpha_G, v=alpha_nu, nu=nu_pp; all dimensionless. Distinguish `a_peak` (source a=.3 choice), `a_f` from Eq50 and `alpha_f` from Eq49. These are three different quantities.

| Derived scalar (unit1) | Exact expression | Locator |
|---|---|---|
| B | 1-nu-2*r*nu^2/v^2 | p2 Eq4 factor |
| a1 | r*B | p2 Eq4 |
| a2 | r*nu*(1+r*nu/v^2) | p2 Eq5 |
| a3 | r*nu*(1/v+nu/v-1-r*nu/v^2) | p2 Eq6 |
| a4 | r*B*(1-g)/g | p3 Eq7 |
| a5 | r*(1-r*nu^2/v^2)+1-nu^2-2*r*nu*(1+nu)/v-2*r*B/g | p3 Eq8 |
| printed_Am | nu^2*(4*r/v-2*r^2+2*r^2/v^2-1)+nu*(4*r/v+2*r)+2*r+1 | p3 Eq14 |
| a_f | sqrt(3)*(3-sin(phi_c))/(2*sqrt(2)*sin(phi_c)) | p10 Eq50 |
| log_argument | (lambda_star-kappa_star)/(lambda_star+kappa_star)*(3+a_f^2)/(a_f*sqrt(3)) | p10 Eq49 |
| alpha_f | log(log_argument)/log(2) | p10 Eq49 |

Source phi_c must have an explicit angle convention; an implementation takes radians. Neither alpha_f=2 nor independently calibrated alpha_f is the selected Eq49 variant. The manuscript explicitly permits calibrated alpha_f as another choice (p10); identify it separately if needed.

For P=n outer n (unit1 symmetric), n unit normal to the symmetry plane, and symmetric E (unit1/s), the p2 Eqs2–3 action is

`L:E = a1*E + a2*I*trace(E) + a3*(P*trace(E)+I*dot(P,E)) + a4*(P E+E P) + a5*P*dot(P,E)`.

L:E has unit1/s. For compression-positive Sigma in Pa and p=trace(Sigma)/3, p3 Eq15 gives

`fs = 9*p/(2*printed_Am)*(1/lambda_star+1/kappa_star)` (Pa), hence fsL:E in Pa/s.

Preserve the a1/2 in the fourth-order source Eq2: the symmetrized four-term product in Eq3 supplies the compensating factor. Contracting a1*E is correct for symmetric E. Source a4 does NOT carry another factor1/2 after contraction.

## Newly demonstrated source discrepancy: do not silently repair

Direct contraction of Eqs2–8 gives

`trace_L_I = 3*a1+9*a2+6*a3+2*a4+a5`

`=2*r+1+nu*(2*r+4*r/v)+nu^2*(4*r/v-1)`.

Therefore `trace_L_I-printed_Am=2*r^2*nu^2*(1-1/v^2)`. It vanishes in tests restricted to v=1 or nu=0, including the fully isotropic limit. For g=2,r=2^1.25,v=2,nu=.1, printed_Am=6.6609096228707845 while trace_L_I=6.74576243661317. Independent reviewer confirmed the image transcription and identity. Four staged arithmetic tests retain this witness and its hidden special cases. Neither quantity is automatically substituted for the other. A literal printed-Am manuscript fragment is defensible for research, with both outputs reported; it cannot claim the isotropic-unloading calibration derivation in Eqs12–15 is consistent at arbitrary anisotropy. This issue is independent of the already documented AppendixB factor4.5 normalization conflict.

## Full-base composition: exact source differences and signs

Manuscript p9 Eq34, with source compression-negative stress T=-Sigma and stretching D=-E, maps at zero spin to

`Sigma_dot=fs*L:E + (fd/fdA)*(fs*L:d-(Sigma/lambda_star)*trace(d))*norm(E)`.

The plus preceding the nonlinear term follows from negating the source stress rate; the dyadic stress term remains negative inside the action. Source normalized T/trace(T) is invariant under this sign reversal, so d/dA are unchanged; do not negate d twice. `edot=-(1+e)*trace(E)` is inherited incompressible-grain host closure, not restated as a new2014 equation.

Both p9 Eq36 and Eq38 must change when choosing Eq49:

`fd=(2*p/pe)^alpha_f`, `pe=pr*exp((N-log(1+e))/lambda_star)`,

`fdA=2^alpha_f*(1-Fm)^(alpha_f/omega)`.

The factor2 in fd is mandatory. d=dA/norm(dA) (Eq44), and Eqs39–48 retain the2013 ASBS invariant/direction structure; use its source-located Cartesian reference rather than copying only an isotropic branch. In particular, Fm uses the paper's signed I2=(T:T-tr(T)^2)/2; this is negative conventional second invariant. Compression sign changes I1/I3 together and leaves their ratios unchanged. No new fourth-order primitive follows from the tensor action alone.

## Declared support and bounded implementation sequence

1. First fragment: typed inputs Sigma symmetric Pa,E symmetric1/s,P symmetric1 plus explicit scalar parameters; outputs a1..a5,printed_Am,trace_L_I,fs,L:E,fsL:E,a_f,alpha_f. No hidden defaults, IGS or state evolution. Selected implementation uses three dimensionless scalar parameters n1,n2,n3 in [-1,1], with abs(n1^2+n2^2+n3^2-1)<=64 machine epsilons and no normalization. Construct P=sym(n1^2,n2^2,n3^2,sqrt(2)*n1*n2,sqrt(2)*n2*n3,sqrt(2)*n1*n3) in the existing orthonormal Mandel basis. This avoids vector-valued parameter extensions and redundant six-projector constraints. Preserve these actual components unchanged in the fixed global material frame; finite-spin transport unsupported.
2. Validate all three scalar axis components and their declared squared-norm tolerance before constructing P; reject invalid orientation rather than normalizing it. Exact unit n gives symmetric,trace1,idempotent,rankone P. At the accepted 64-epsilon tolerance these identities and exact SPD proof are approximate: retain actual P and require numerical tests of the composed action rather than claim exact invariance. Test n and -n equivalence, rotated P/E covariance, in-plane/transverse shear ratio, arbitrary full noncoaxial E, isotropic coefficient limit and the Am discrepancy. A fixed-plane restriction is research kinematics, not evolving fabric.
3. Require g,v nonzero for literal arithmetic; physically selected support should additionally use positive g,r,v, positive lambda_star,kappa_star,lambda_star>kappa_star, positive pressure,1+e>0, nonzero printed_Am and positive Eq49 log argument. The selected implementation additionally uses B>0 and printed_Am>0 with nu_pp in [-.9,.49]; these are engineering support restrictions, not published calibration intervals. For EXACT unit orientation, the printed stiffness is positive definite when r>0,g>0,B>0,nu>-1: in an aligned frame its normal block has diagonal x=r-r^2*nu^2/v^2 for xx/yy and t=1-nu^2 for zz, offdiagonals y=r*nu+r^2*nu^2/v^2 and z=r*nu*(1+nu)/v. Its second leading minor is r^2*B*(1+nu), determinant r^2*B^2*(1+nu)^2; x>0 follows from x-y=rB and x+y=r*(1+nu). The three Mandel shear eigenvalues are rB,rB/g,rB/g. This derived Sylvester factorization is separate from the Am discrepancy. Near degeneracy, finite precision and the accepted approximate-unit axis still need explicit numerical checks/margins; do not describe the support as complete physical admissibility.
4. Matrix multiplication P E+E P must be typed bilinearly; P and rate E cannot be added in `(P+E)^2-P^2-E^2`. Use direct Cartesian component construction or separately justified normalized-rate polarization; the latter must have a lazy exact-zero branch. Do not introduce a dimensional inconsistency to avoid an operator.
5. Only after independent fragment comparison, compose full7-state stress/e base law with explicit a_peak and alpha_f Eq49. Confirm all inherited ASBS denominator,log,power and normalization domains, hydrostatic/zero-rate continuation and full transaction rollback. Isotropic direction is mathematically singular in the printed Lode expression; do not rely on multiplication by zero. Use existing2013 continuation only with separately reviewed mathematical/source equivalence. No arbitrary epsilon flattening.
6. Full integration, preparation/reference histories and independent scientific review remain later gates. No IGS, material-axis evolution, final-publisher equivalence, source calibration consistency or complete-model admission follows from this fragment.

## Selected full-base scope after synchronization

The author is implementing the complete instantaneous seven-state stress/e base rate, using scalar n1,n2,n3 orientation, literal printed Am and proposed Eq49 alpha_f. This is allowed as an explicitly identified manuscript research variant with the Am conflict retained, not as a repair or calibration-consistent final-publication law. The initial typed-fragment sequence above describes decomposition for review; it does not prohibit full-base composition once independently compared. AppendixB remains excluded. The four original source-witness tests remain unchanged.
