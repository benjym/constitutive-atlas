# Clay barodesy 2017: original-source inventory

This packet closes exact publisher full-text acquisition, not formulation reconciliation, implementation, or scientific admission. Reviewed against repository `b547f44fd02e83f0d983dc7fa94e20ad7de83017`; queue: [candidate triage A3](parallel-candidate-triage.md) (lines46–56) and `catalogue/research-queues/parallel-source-queue-2026-10-31.json:585–603`.

## Exact source and access record

Gertraud Medicus and Wolfgang Fellin, *An improved version of barodesy for clay*, Acta Geotechnica12(2),365–376(2017), [DOI10.1007/s11440-016-0458-4](https://doi.org/10.1007/s11440-016-0458-4). Online publication was2May2016; the issue identity is2017. [Publisher article](https://link.springer.com/article/10.1007/s11440-016-0458-4), [publisher PDF](https://link.springer.com/content/pdf/10.1007/s11440-016-0458-4.pdf). Acquired privately31October2026:1492680bytes, SHA256`bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15`,12PDFpages corresponding to printed365–376. Printed373 identifies CC BY4.0. No PDF, extracted text or render belongs in this deliverable.

The [author's university profile](https://www.uibk.ac.at/de/geotechnik/bodenmechanik/team/gertraud-medicus/) lists this exact paper and a [full-text institutional resolver](https://resolver.obvsg.at/urn%3Anbn%3Aat%3Aat-ubi%3A3-6399). The latter returned403 during this review; no distinct author version acquired. The [base implementation package page](https://soilmodels.com/download/barodesy-umat-plaxis-zip/) was read: publication22January2018, page modification24July2018, advertised6.65MB, UMAT source/Plaxis DLL/manual and related publications. Its download requires login. No archive was acquired, so source version, actual license files and source hash remain unverified. No external code was executed. The [2020 extension](https://soilmodels.com/barodesy-download-package-including-small-strain-stiffness-and-strength-reduction-umat-and-plaxis-dll/) explicitly adds intergranular strain and strength reduction; it is not a replacement source for this base law. Sand,2012clay, later reloading and ISA variants remain separate.

Visual inspection covered PDFpages2–6,9–11: notation, Eqs1–10, Table1/2, calibration and Appendices1–3. Source locators below are printed pages. Metadata and scalar diagnostic are under `catalogue/source-audits/barodesy-clay-2017-{source-v1,algebra}.json`.

## State, input and sign/unit contract

| Item | Source definition and locator | Proposed mapping/remaining decision |
|---|---|---|
| Effective Cauchy stress T | Symmetric, compression negative, §2p366 | Six Mandel components, Pa; Atlas compression-positive stress is sigma=−T |
| Void ratio e | Vvoid/Vsolid, §2p366; footnote13p374 gives edot=(1+e)trD | One scalar; Atlas edot=−(1+e)trE for E=−D |
| Stretching D | Symmetric velocity gradient, p366footnote3 | Six components, s^-1; logarithmic strain rate only for rectilinear stretching |
| Spin W | Antisymmetric velocity gradient, §2p366 | Needed for finite rotations; printed objective-rate definition is inconsistent (below) |
| Pressure p | −trT/3, §2p366 | trsigma/3, Pa |
| Normalized X0 | X/|X| with Frobenius norm | Undefined at zero; separate zero branches required |
| delta | trD0 in [−sqrt3,sqrt3], §2p366 | −trE/|E| for E=−D |
| State memory | T and e only, §6p373 | Seven scalar state components; scalar h in Eq2 is a rate coefficient, not history memory |

Section1p366 explicitly excludes rate dependence, creep and relaxation. This is a rate-independent objective rate law, not a physical-time relaxation model. Integration parameter and imposed stretching must still preserve the source kinematics. A first research transcription can explicitly restrict W=0; general shear/rotation needs a separate objective transport contract. No fluid, pore pressure or hydraulic state is supplied by the base equations.

## Equation and parameter inventory

Define `delta=trD0`, `a=lnK/sqrt((3−delta²)/2)`, `m=−3delta/sqrt(6−2delta²)`, `K=1−1/(1+c1(m−c2)²)`. Equations1–5p366–367 give

`Tcircle=c3|T|^c4 (f R0+g T0)|D|`, `R=−exp(a D0)`.

The exponential is a **tensor/matrix exponential**, not entrywise exponentiation. Footnote5p366 defines it through eigenvalues and a diagonalizing transformation. This is an established requirement from the source, not an inference from the model family.

Equations6–10p367 give `f=c6 beta delta−1/2`, `g=(1−c6)beta delta+((1+e)/(1+ec))^c5−1/2`, `beta=−1/(c3 Lambda)+(2^(c5 lambda*)−1)/sqrt3`, and `Lambda=−(lambda*−kappa*)delta/(2sqrt3)+(lambda*+kappa*)/2`. Body Eq8 defines `1+ec=exp(N)(2p/sigma*)^(−lambda*)`, with fixed sigma*=1kPa=1000Pa. Appendix3Eqs36–43p375 repeats the law with a different ec expression; see discrepancy below.

Independent material inputs are phi_c (critical friction angle), N (NCL intercept), lambda* and kappa* (logarithmic compression/unloading slopes). Table1p367 and Eqs17,21,23,25,29 define the dimensionless coefficients:

- `c2=−(3sqrt2+3)/2`; `c1=(1−sinphi)/(2 c2² sinphi)`.
- `c4=1`; `c5=(1+sinphi)/(1−sinphi)`.
- `c3=(−sqrt3/lambda*+sqrt3/kappa*)/[2^(c5 lambda*)+(1/500)^(c5 lambda*)−2]`.
- `c6=1/{2[−sqrt3/(c3 kappa*)+2^(c5 lambda*)−1]}`.

The c3 calibration uses the chosen asymptotic extension ratio p_-i/pe=1/1000 (§4.3p369); this choice is embedded in the improved law, not an additional independently measured soil parameter. For Table2 examples c3 is negative: do not impose a positive-c3 or positive-h guard.

Table2p368 provides complete examples: Londonclay `(22.6deg,1.375,.11,.016)`, Dresdenclay `(35deg,.622,.038,.008)`, Wealdclay `(24deg,.8,.059,.018)`. SanFranciscoBayMud has only phi and is unsuitable as a complete four-parameter calibration. The JSON diagnostic records the complete examples and derived constants; it is illustrative source algebra, not experimental validation.

## Initialization and domain

The paper supplies T and e as initial state, not a hidden plastic/preparation memory. Equation11p368 defines NCL `ln(1+e)=N−lambda*ln(p/sigma*)`. For NCL reference pressure p=1kPa, e=exp(N)−1. Overconsolidated initial densities are also used; NCL is not a universal admissibility boundary. Equation12's numerical equivalent pressure must regain a pressure factor when expressed in Pa: `pe=sigma*exp((N−ln(1+e))/lambda*)`, derived dimensionally from Eq11.

Conservative candidate research guards (not claimed as a source-proved complete domain): finite inputs/derived intermediates; 0<phi<pi/2; lambda*>kappa*>0; physical e>=0; positive effective compression and p>0; nonzero stress norm; nonzero parameter denominators. An SPD compression-positive stress restriction is a possible stronger research domain, to be labeled as such. Do not infer arbitrary stress floors, tensile clipping or projection from Fig2's qualitative compression-regime result. Mathematical density power needs1+e>0 and1+ec>0. Directional singularities require explicit policy:

- D=0 makes D0 undefined; rate homogeneity suggests zero continuation but no finite numerical branch is specified.
- At delta=±sqrt3, m diverges and Eq4 becomes a0/0form. Independent limit: a→0, so R0→−I/sqrt3. This needs a reviewed limiting branch, not clipping of delta.
- At m=c2, K=0 and lnK diverges. The corresponding delta is approximately1.495 (exact expression and computed value in the diagnostic). A normalized exponential directional limit may exist, but repeated minimum eigenvalues and numerical underflow need analysis; no canonical finite branch is admitted here.
- T=0 and zero norm are not directly evaluable. Do not interpret source asymptotic stress-free extension as permission to divide by zero.

`atlas/dsl.py:103–107` provides scalar exp/log and tensor trace/dev/dot/norm/square, but no generic symmetric matrix exponential or eigensolver. An operator extension is needed unless a separately proven equivalent full3D expression is supplied. A normalized symmetric exponential could factor out a scalar/eigenvalue shift to prevent overflow, since only R0 is used; this is a design proposal requiring degeneracy, covariance and numerical tests. An axisymmetric diagonal formula does not establish full3D/noncoaxial compatibility.

## Discrepancies and independent distinguishing algebra

**ec body versus appendix.** Body Eq8p367 uses2p/sigma*. Appendix3Eq41p375 uses−2trT/sigma*=6p/sigma*. Section2p366 explicitly defines p=−trT/3. Section3p367 defines the same N and sigma*=1kPa. Appendix3 introduces no alternate pressure, stress normalization, N or sigma* definition and refers to the same Tables1/2. Appendix2Eq32p374 also uses2p. Thus there is a source-internal discrepancy after checking definitions; this packet does not assert an externally confirmed erratum.

Independent isotropic reduction selects T=−pI and D=−vI/3 with compression-positive v>0: `dlogp/dv=c3/sqrt3*(A−1−sqrt3 beta)`, `A=((1+e)/(1+ec))^c5`, `de/dv=−(1+e)`. On Eq11NCL, body Eq8 gives A=2^(c5lambda*) and exactly dlogp/dv=1/lambda*, matching Appendix2Eq26/30. Appendix Eq41 instead gives A=6^(c5lambda*) and a different slope. The independent JSON evaluates both with all three complete Table2 soils. Regenerate it with `python3 tools/barodesy2017_source_algebra.py --output /private/tmp/barodesy-clay-2017-algebra.json`; the output should match the retained JSON byte for byte. This is a distinguishing consistency check, not a complete model test. An explicitly named body-law research transcription is actionable with this discrepancy retained; it must not be called proven equivalent to every printed equation.

**Objective-rate print.** Section2p366 prints Tdot=Tcircle−WT+WT: identical products cancel. This does not specify the expected nontrivial corotational commutator. Zero-spin restrictions avoid the ambiguity; finite-spin implementation needs an independently pinned convention or matching author-source comparison. No silent correction is made.

## Next bounded implementation packet

1. Independent reviewer checks the body-law selection, constants, compression signs and Pa scaling. Keep both unresolved source readings in provenance.
2. Specify normalized tensor exponential and hydrostatic/zero/singular-direction domains. Test diagonal/repeated-eigenvalue/rotated tensors independently; do not claim matrix support from scalar exp.
3. Transcribe a zero-spin, seven-state research rate; compare instantaneous isotropic NCL, unloading at the source-specific density, noncoaxial rates and rotations before integrating. Kappa is not a universal unloading tangent: Eq22p370 attaches it to a particular density ratio.
4. Establish independent isotropic finite-path solutions/reference convergence and common-engine rejection/rollback/refinement evidence. Pure isotropic limits are part of the transcription contract, not an optional edge test.
5. If ordinary authorized access becomes available, statically inspect the exact2018base archive/manual for ec and spin choices, version and license; hash files before comparison. No downloaded-code execution is necessary.

Source acquisition alone does not support public solver admission, general finite-spin equivalence, experimental validation or use of sand/ISA parameters. Figures are comparison targets only after experimental provenance, units, loading controls and reuse rights are separately established.
