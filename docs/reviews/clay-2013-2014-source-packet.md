# Clay hypoplasticity: 2013 source inventory and 2014 dependency outline

Status: source-located acquisition/transcription packet, checked 2026-10-31. Not an executable model, independent scientific review, numerical validation, accepted schema or admission decision. Candidate statuses remain unchanged.

## Source identity and acquisition

The 2013 candidate is David Mašín, *Clay hypoplasticity with explicitly defined asymptotic states*, Acta Geotechnica 8(5), 481–496, [DOI10.1007/s11440-012-0199-y](https://doi.org/10.1007/s11440-012-0199-y). The publisher distinguishes online publication 22 December 2012 from issue 2013. The old [author university page](https://web.natur.cuni.cz/uhigug/masin/phdposition/) links this [author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf), acquired privately: 2646368 bytes, 16 pages, SHA-256 `21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281`.

The current author bibliography cautions that preprints can differ from final publication. Appendix equations 43–58 also appear on the [publisher page](https://link.springer.com/article/10.1007/s11440-012-0199-y); their displayed forms agree with the visually inspected manuscript. Full manuscript/final equivalence is unverified. Page locators below mean author-PDF page numbers, not journal pages. Visually inspected pages 1, 3, 4, 6, 7, 8, 13, 14. No PDF, extracted text or render belongs in the repository packet; author hosting does not grant redistribution rights.

The 2014 candidate is Mašín, *Clay hypoplasticity model including stiffness anisotropy*, Géotechnique 64(3), 232–238, [DOI10.1680/geot.13.P.065](https://doi.org/10.1680/geot.13.P.065), confirmed by the [primary publisher record](https://www.emerald.com/jgeot/article/64/3/232/401267/Clay-hypoplasticity-model-including-stiffness). Full text was not acquired from an author/university/publisher route in this bounded pass; publisher access is restricted and the current author bibliography links the login-gated SoilModels copy. The separate Mašín–Rott 2014 Acta Geotechnica anisotropy review is not this paper.

Initial checks found no named 2013/2014 source PDF in Downloads or canonical receipts. The relevant dataset archive member names inspected contained datasets/results rather than either paper. This was a bounded inventory, not a title-level audit of every unrelated archive. No duplicate-copy request is needed from the user at this stage.

## 2013 complete stress-law inventory

Source convention: T is the source stress, with compression negative, `p=-tr(T)/3`; D is Euler stretching, not automatically the derivative of a finite logarithmic strain tensor. Eq.(3), p.3 specifies `T°=Tdot+T W-W T`, with W the skew velocity-gradient part. The intended saturated material-point adapter treats T as effective skeleton stress; hydraulic/pore-pressure coupling is outside this packet and must be specified separately. A six-component Mandel representation is a project coordinate map, not a source-stated component ordering here. It must preserve Cartesian traces, tensor products and Frobenius norms.

Write `1` for second-order identity and `I4` for symmetric fourth-order identity; these are distinct from stress invariants I1/I2/I3. Appendix, pp.13–14:

| Equation | Exact algebra to transcribe |
|---|---|
|43|`T° = fs (L:D) - (fd/fdA) (A:d) ||D||`|
|44|`L = I4 + [nu/(1-2nu)] 1⊗1`|
|45|`A = fs L + (T/lambda_star)⊗1`|
|46|`fs = (3p/2)(1/lambda_star+1/kappa_star)(1-2nu)/(1+nu)`|
|47|`fd = (2p/pe)^alpha`, fixed `alpha=2`|
|48|`pe = pr exp((N-ln(1+e))/lambda_star)`, fixed `pr=1kPa=1000Pa`|
|49|`fdA = 2^alpha (1-Fm)^(alpha/omega)`|
|50|`Fm = (9 I3+I1 I2)/(I3+I1 I2)`|
|51|`omega = -ln(cos(phi_c)^2)/ln(2) + a(Fm-sin(phi_c)^2)`, fixed `a=0.3`|
|52|`I1=tr(T)`|
|53|`I2=(T:T-I1^2)/2`|
|54|`I3=det(T)`|
|55|`d=dA/||dA||`|
|56|`dA=-That_star + 1 [2/3-(cos3theta+1) Fm^(1/4)/4] [Fm^(xi/2)-sin(phi_c)^xi]/[1-sin(phi_c)^xi]`|
|57|`cos3theta=-sqrt(6) tr(That_star^3)/(That_star:That_star)^(3/2)`|
|58|`xi=1.7+3.9 sin(phi_c)^2`; `That_star=T/tr(T)-1/3`|

The source I2 is the negative of the commonly used second principal invariant. Changing its convention without changing the Fm formula is an error. The minus nonlinear term in Eq.(43), normalization of d, and distinct factors fd/fdA must be preserved. The scalar N intercept is unrelated to the second-order coefficient tensor denoted N in the general introductory Eq.(1).

## Density, parameters and state

Eq.(7),p.3 gives `pe_dot=-(pe/lambda_star) e_dot/(1+e)=-(pe/lambda_star)tr(D)`, hence **`e_dot=(1+e)tr(D)`**. With constant source D over a block, density alone has the analytic closure `1+e_out=(1+e_in)exp(tr(D)Delta_t)`; that does not make the coupled stress update exact. Compression-positive Atlas strain/stretching requires the opposite volumetric sign. A proposed zero-spin adapter should explicitly map `T=-sigma`, `D=-D_compression`, and negate the source stress rate; direct symbol replacement without a complete algebraic sign check is insufficient. Finite spin requires the objective transport as well.

Section 7, p.8 and final Appendix paragraph,p.14 identify five parameters and only T/e as base state:

| Parameter | Meaning | Unit |
|---|---|---|
|phi_c|Critical-state friction angle; table uses degrees, trigonometric implementation needs an explicit radians conversion|angle|
|lambda_star|Isotropic NCL slope in ln(1+e) vs ln(p/pr)|1|
|kappa_star|Controls unloading slope in the same plane|1|
|N|NCL ln(1+e) intercept at p=pr|1|
|nu|Controls shear stiffness through L|1|

Base persistent layout is six symmetric stress components plus e; no independent pc, plastic strain, fabric, IGS history or scalar hardening variable is stated for this base. Additional initialization/path bookkeeping is a solver/API concern. Table 1, p.8 includes a fictitious `eval.` set and material-specific calibrations; none is promoted to a universal default. The 2005 r parameter is not nu. Eq.(39) supplies a particular conversion depending on lambda_star and kappa_star, not interchangeable field names.

## Domains, limiting branches and temporal integration gates

The paper does not provide a complete implementation-ready domain validator. The following distinguishes literal arithmetic requirements from proposed numerical admission choices:

- Literal expressions require finite states/parameters, e>-1 for ln(1+e), nonzero lambda_star/kappa_star, nu≠1/2 and nu≠-1, tr(T)≠0, nonzero invariant denominator, positive nonzero fdA, nonzero omega and a nonzero dA norm. Fractional powers require a compatible real domain. The precise combined physical domain must be reviewed rather than accepting every individually evaluable scalar expression.
- A conservative first diagnostic scope could choose e≥0, lambda_star>kappa_star>0, -1<nu<1/2, 0<phi_c<pi/2, positive pressure and strictly compressive principal effective stresses, with checked 0≤Fm<1 and omega>0. These are **proposed project restrictions**, not a quoted source theorem or final schema bounds. Their sufficiency and margins still need proof/probes.
- Eq.(57) has0/0 at isotropic stress. At T=-p1, Fm=0 and That_star=0. For the above positive-angle scope, Eq.(56) tends to a negative spherical dA, hence `d=-1/sqrt(3)`. This is an algebraically derived proposed branch, not an evaluated printed quotient. Near-isotropic treatment and tolerances need continuity tests; an arbitrary assigned Lode angle is not a complete numerical policy.
- Finite nonisotropic stresses mathematically give cos3theta in[-1,1]. Roundoff excursions in this ratio or small negative Fm must have an explicit rejection/regularization policy; do not silently clip. At Fm→1, fdA can vanish and the response becomes singular. Near singular surfaces, require checked intermediate arithmetic and rollback, not a guessed pressure floor.
- Eq.(17),p.4 defines the ASBS `f=Fm+(p/pe)^omega-1=0`. It is not a yield function licensing a plastic return map. The same page footnote warns Fm=1 only approximately represents the boundary of compressive stresses. No general tensile-state handling follows from that construction. Initial-state/ASBS admissibility and accepted-stage overshoot policy remain open.
- The law is rate independent and positively homogeneous in D; physical time is not a material viscosity parameter. A path coordinate can integrate a zero-spin small-strain restriction with explicit sign/kinematic maps. The source uses finite-deformation objective quantities, so this restriction must be named. `||D||` is nondifferentiable at D=0 for tangent construction even though the rate has an identity zero-increment limit in an admissible state.
- Stress and e must be updated as a coupled trial state with domain checks at every evaluated stage, error control and exact rollback on failure. The paper does not select an Atlas method/order/tolerance. The author's [2017 implementation documentation](https://web.natur.cuni.cz/uhigug/masin/plaxumat/node3.html) describes an adaptive explicit RK2/3 pair with rejected substeps/global-step rejection. It describes a later combined implementation, not proof of the 2013 paper's exact numerical method or Atlas parity.

## Operation and compatibility inventory

For the isotropic base, fourth-order objects can be eliminated algebraically: `L:X=X+c tr(X)1` and `A:X=fs(L:X)+(T/lambda_star)tr(X)`, c=nu/(1-2nu). This preserves contractions without adding a general fourth-order DSL type. The reduction is a proposed transcription route requiring Cartesian comparison.

Required operations: scalar arithmetic, exp/log, sin/cos, fixed and state-dependent real powers, trace, deviator, Frobenius contraction/norm, tensor sum/scaling, determinant and cubic trace, plus explicit lazy isotropic/zero-rate branches and domain checks. Current DSL already has the main scalar/symmetric operations and cube_trace. A determinant can be algebraically expressed as `(tr(T)^3-3 tr(T)(T:T)+2 tr(T^3))/6`, but cancellation/scaling and Cartesian equivalence need testing; this is not evidence an untested compiled expression is ready. Explicit formula parsing, rank-seven state, units and zero-spin shape appear plausible; no complete parser/code-generation capability claim has been made. Finite-spin transport, domain-aware adaptive coupled integration and validated singular branches are still gates.

Minimum next bounded task: immutable Python source-rate oracle plus a separate Cartesian oracle, with isotropic loading/unloading slopes, six-component noncoaxial stress/stretching, Lode endpoints, unit/sign conversions, zero rate and singular-domain rejection. Then compare caller partitions and material tolerances on one specified path. No native build is needed for that source comparison.

## 2014 variant and dependencies: limited outline

The primary 2014 abstract identifies an explicit-ASBS clay host combined with anisotropic stiffness and evaluation against London Clay hollow-cylinder data. The author's [model documentation](https://web.natur.cuni.cz/uhigug/masin/plaxumat/node2.html) and [bibliography](https://web.natur.cuni.cz/uhigug/masin/plaxumat/node13.html) separate the 2013 host,2014 stiffness extension,2014 Mašín–Rott stiffness review and optional IGS. The prose labels its anisotropic reference “2013”, while bibliography item 6 actually gives 2014: identify by title/DOI, not that prose year. The [author's driver inventory](https://soilmodels.com/triax/) separately names explicit, anisotropic, explicit+IGS and anisotropic+IGS variants.

Do not import anisotropy/IGS parameters or evolving histories into the 2013 base. Without the exact2014 full text, this packet does **not** establish the anisotropic fourth-order stiffness entries, independent parameter set, material-axis initialization/evolution, enhanced IGS equations, normalization of A/d or admissible anisotropy bounds. Acquisition remains the next gate. The Mašín–Rott review can later support its own dependency record; it cannot substitute for the 2014 hypoplastic update law.

Preserve four identities when later transcribing:2013 base;2013+specified IGS;2014 anisotropic base;2014+its source-pinned IGS pairing. The present packet changes none of their executable/review flags. Full publisher/preprint reconciliation, independent source review, initialization, operation tests, numerical integration verification, rights for any reference code/data and experimental validation remain open.
