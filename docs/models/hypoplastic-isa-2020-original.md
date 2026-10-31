# ISA cyclic-mobility 2020: exact source receipt and admission dossier

Research candidate; no executable definition or scientific admission. The full publisher PDF was acquired privately on31October2026. It is **not** a newly inferred blend of IGS97, GIS2024 or later semifluidized ISA.

## Exact identity and receipt

William Fuentes, Torsten Wichtmann, Melany Gil and Carlos Lascarro, *ISA-Hypoplasticity accounting for cyclic mobility effects for liquefaction analysis*, Acta Geotechnica15(6),1513–1531(2020), [DOI10.1007/s11440-019-00846-2](https://doi.org/10.1007/s11440-019-00846-2). The title page and Crossref agree on online publication1July2019; the publisher identifies June2020 as the issue date. Keep both dates; retain the candidate's2020 formulation label.

Primary PDF: [publisher endpoint](https://link.springer.com/content/pdf/10.1007/s11440-019-00846-2.pdf). Private path `/private/tmp/atlas-isa-source-20261031-v1/private/publisher-pdf.pdf`; 4,502,870bytes; SHA256 `97b8762b7773e86a7778835f24f46734bb82522052c0856f63e42bc98ba76821`;19pages; no encryption or JavaScript reported by pdfinfo. **One-based PDF page = printed page−1512.** Metadata says created1July2019, modified13May2020; these are file metadata, not a separate publication version. The title page visually matches the DOI, authors and issue pagination. Relevant printed pages1513–1519,1526,1528–1529 were rendered and visually inspected.

The publisher HTML initially presents subscription preview to the web reader; the normal PDF endpoint returned an actual19-page PDF through the authorized network fetch. No authentication, third-party delivery service or contact was used. A cookie-error query appeared in the final redirect URL despite a successful PDF response; canonical URLs and byte hash identify the receipt. Public artifacts exclude the PDF, HTML, text, screenshots and raw Crossref response. Read access is not redistribution permission.

## Paired host and lineage

| Layer | Exact source/dependency | Consequence |
|---|---|---|
| Host | vonWolffersdorff1996 sand hypoplasticity; source Sec2 p1514, AppendixC Eqs36–41 p1529, reference49 | Host depends on stress and void ratio; its density factors are modified by the new mobility law. Host interchangeability is not established. |
| ISA | Fuentes–Triantafyllidis2015, DOI10.1002/nag.2370; Poblete–Fuentes–Triantafyllidis2016, DOI10.1007/s11440-016-0492-2; also2017 chapter reference12 | Two intergranular tensors, elastic yield locus and accumulated-history exponent. This is not the IGS97 single-tensor differential law. |
| Selected new extension | Main Sec3 Eqs6–12 pp1515–1517 | Adds Z, modifies fe/fd and replaces beta_h by a mobility/transverse-loading law. AppendixC's older beta_h Eq33 must not override main Eqs11–12. |
| Numerical lineage | Sec4 p1519 extends reference35's FORTRAN Abaqus UMAT; cites Wang etal.2018, *Numerical integration and FE implementation of a hypoplastic constitutive model* (reference44) | Explicit small subincrements and elastic predictor; this packet does not pin or execute that implementation. The reference44 DOI was not independently verified here. |
| Supplement/reference access | No supplementary keyword or archive/code link found in downloaded publisher HTML. [Author-upload SoilModels package](https://soilmodels.com/download/download-package-of-isa-cyclic-hypoplasticity-for-abaqus/) is listed as2018; access timed out here. | No exact supplement or code-to-article version pair acquired. A2018 package label alone does not prove2019/2020 algorithm equivalence. Do not infer license/reuse rights or execute it. |

A separate implementation's [numgeo documentation](https://j-machacek.github.io/numgeo/2026-09/theory/constitutive-models/mechanical-models/hypo-isa.html#comparison-to-the-soilmodels-com-reference-implementation) explicitly reports different phantom-elasticity behavior and fixed beta_h0 versus recursively evolving beta_h in the SoilModels code. This is a primary statement about **numgeo's implementation**, not proof of the exact uninspected author archive. It is a warning to pin variants before reference comparison; neither rule is silently selected here. The2024 pre/post-liquefaction ISA-SF model is a distinct formulation.

## State, preparation and units inventory

| Quantity | Conservative retained shape/unit | Source role and initialization evidence |
|---|---|---|
| Effective sigma | symmetric3D,6stress components | Eq1 p1514 /Eq25 p1528. Source compression-negative; p=−trace(sigma)/3. |
| e | scalar,dimensionless | Host state; supplied initial density in tests. A general e evolution/constant-solid-volume closure is not written in the inspected equation list and must be independently sourced from the paired host. |
| h | symmetric3D,6strain components | Intergranular strain, Eqs3–4 p1514 and31 p1528. Full tensor: Sec5.2 p1526 initializes h33=−R in the FE example; do not replace by its deviator. |
| c | symmetric3D,6strain components | Back-intergranular strain/yield center, Eq32 p1529. FE example c33=−R/2, same gravity direction; no universal initialization prescribed by that example. |
| eps_acc | scalar,dimensionless | Eq34 p1529; controls chi through Eq35. A general initial value/reset rule was not identified. |
| Z | symmetric3D,6dimensionless components | Eq6 p1515, full N-driven recent large-strain history. A universal initial value was not identified. Figure4 shows initially zero Z11, not a complete initial tensor specification. |

This is26 scalar retained slots using full symmetric tensors, **not a proved minimal independent layout**. A temporary multiplier can be algebraic/trial-local; no new state capacity follows. e/h/c/eps_acc/Z are physical or constitutive histories; N, rho, m, chi, beta_h, fz, fh, Fd, fe/fd, L/Nhyp and image tensors are derived stage quantities. The selected paper does not make beta_h an extra independently evolving state. A reference implementation that recursively updates it needs a separate numerical-variant identity/history contract.

Table1 p1516 gives16 parameters: eight host inputs(phi_c,hs,nB,ed0,ec0,ei0,alpha,beta), seven ISA inputs(mR,R,beta_h0,beta_hmax,chi0,chimax,ca) and cz. The JSON retains the exact table calibration, **not universal defaults**. phi_c is tabulated in degrees; hs in kPa; all others dimensionless. R/h/c are strain-valued despite dimensionless SI strain. AppendixC's closing parameter list omits mR as well as new cz; do not let that list drop Table1 parameters.

The FE initialization at p1526 is a specific preparation: geostatic self-weight/K0, surcharge, h33/c33 above and e0=r0*ec0*exp(−(3p/hs)^nB), r0=.85. It is not a material reset prescription and does not specify all histories for element-test Figure4. Pore-pressure Eq21 and water bulk modulus are host/coupling inputs, not extra effective-stress kernel parameters. Ordinary restart must restore the supplied complete histories without replaying geostatic preparation.

## Literal source conflicts and domains requiring resolution

1. **Eq29 p1528:** the printed strain rate in yh is not normalized; no arrow is present in the inspected PDF. This makes m depend on rate magnitude despite its stated bounded amplitude-factor role. The retained scalar diagnostic shows m changes under doubling that rate. Do not repair it using IGS/GIS or numgeo typography.
2. **Eq38 p1529:** the fb bracket uses beta rather than the cited host's alpha. With exact Table1 values, that bracket is−0.7982194216919165; the alpha alternative is+5.737083878852044. This diagnostic selects no repair, but demonstrates a material consequence. The corresponding source-independent scalar calculation is retained.
3. **Eq39 p1529:** the PDF prints a reciprocal tan(psi) term after the square root and a2+2sqrt(2)*tan(psi)*cos(3theta) denominator, conflicting with the cited host's usual form. At hydrostatic stress the printed reciprocal term is singular. Eq40 prints positive sqrt(6) in the Lode expression. Reconcile the entire F/Lode convention with the pinned VW96 original, rather than fixing one sign alone.
4. **Main11–12 versus Appendix33:** different beta_h laws belong to the paper's extension versus older summary. Main fh uses current strain-direction mapping; Appendix33 uses hb direction. Resolve this composition explicitly. No persistent beta_h recursion is specified by main Eq11.
5. **Elastic/plastic selection:** source Eq3 distinguishes FH<0 andFH=0; Appendix31 does not repeat that guard. Full algorithm must define boundary entry, unloading, overshoot return and tolerances; FH>0 is not an admitted constitutive branch merely because an explicit predictor lands there.
6. **Normalized-zero directions:** N=(h−c)/norm(h−c), strain-rate normalization in cb/fh, and normalized db can vanish. The elastic reversal chord passes h=c. Source-defined finite/lazy continuations at these points remain open; multiplying an undefined direction by zero is not validation.
7. **Domain and bounds:** p/trace denominators, e,ec−ed, noninteger powers, fb/Fd denominators and1+N:cbar require finite domains. Claimed fz bounds require suitable Z norm; explicit integration must preserve or check them without hidden clipping. Zero strain rate, p→0, initial isotropy/Lode and e≤ed require source choices. These are mathematical domain observations, not a complete source parameter-admissibility theorem.
8. **Sign/kinematic scope:** AppendixA p1528 states compression-negative sigma/epsilon. Atlas compression-positive mapping must change the tensor signs consistently, including full h/c/Z and N; derive it before a typed rate fragment. Objective-rate/spin transport for all histories is not specified in this bounded extraction; initially declare zero-spin scope. q in AppendixA is a norm while cyclic plots show signed triaxial q: the benchmark needs an explicit axis/extension plotting convention.

## Reversal evidence and smallest executable fragment

Figure4, pp1517–1518, is the source-defined target: e0=.8,p0=100kPa,qamplitude=60kPa, Table1 calibration. The authors describe mobility activation around the fourth cycle and plot Z11/N11 histories. This is a **qualitative target, not a reproducible acceptance fixture yet**: full h/c/Z/eps_acc initialization, preparation, precise signed stress schedule, numerical tolerances and numerical reference points are missing.

A narrower source-derived elastic-memory fixture is supported by Eqs3–5/27/32: start at h=R*B,c=R*B/2 for unit symmetric B, reverse by−s*B. On the elastic chord, h=(R−s)B,c=R*B/2 and FH=abs(R/2−s)−R/2; the interior0<s<R is elastic. The retained fixture tests geometry only, with its elastic-branch hypothesis explicit. It also exposes undefined N at s=R/2. It is **not** a stress/Z trajectory and does not choose a finite singular continuation or a source return-mapping algorithm.

Next bounded task: independently reconcile the four appendix conflicts against the pinned VW96 source and a version-identified author/numgeo code listing (read-only), then transcribe a **supplied-host ISA elastic/plastic rate fragment** with full h/c, eps_acc and Z and explicit supported domains. Dyadic action can be expressed as Nhyp*(N:de); no general fourth-order primitive is necessary solely for that term. Generic history transport can already retain26typed slots; actual event location, predictor/return rules, zero-direction continuation and source initialization still gate full integration. Obtain reference35 and nag.2370 before declaring the summarized history algorithm source-complete.

Sec4 p1519 specifies explicit substepping with norm(Deltaepsilon)<R/4 and an elastic predictor. It does not specify a complete error estimator, exact update ordering, return-map details or rollback protocol. Atlas candidate isolation/full rollback remain required engineering properties; they cannot make an unreviewed backward-Euler approximation the paper's discrete algorithm. No kernel, model admission, code-license conclusion or native comparison is supplied by this packet.
