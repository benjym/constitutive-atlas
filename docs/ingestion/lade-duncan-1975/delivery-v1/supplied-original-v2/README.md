# Lade–Duncan1975: readable-original source packet v2

Task: SRC-lade-duncan-delivery-v1 under MODEL-lade-duncan-1975. Lead: coordinating parent /2026-11-01. Exact target remains the original1975 full elastoplastic theory. This packet supersedes the *current* source-access blocker, preserving all earlier denied-access receipts and the separate1977 supporting-source identity.

## Identity and sources

Poul V. Lade and James M. Duncan, *Elastoplastic Stress-Strain Theory for Cohesionless Soil*, Journal of the Geotechnical Engineering Division101(10/GT10),1037–1053, October1975. [DOI10.1061/AJGEB6.0000204](https://doi.org/10.1061/AJGEB6.0000204). Exact title/authors/year checked visually on PDF page1; original pagination1037–1053 spans all17pages, equations1–19, figures1–8, Table1 and reference appendix. The attachment filename's2021 is not its publication year.

[Source receipt](source-receipt.json) binds user attachment and durable ignored private copy to SHA-256 `bdebd928dbe9e4bac47c0a0328ed0bab79ab3e440a25390f1d646e9ed3749fc5`. All17pages were rendered and visually inspected; embedded OCR is only navigation. No raw PDF, page images or whole-paper text is redistributed. ASCE copyright is retained; user supply does not grant publication rights. No supplied binaries/code were executed.

The [earlier identity packet](../../identity-v1/README.md) distinguishes unrelated DOI0000208. [1977 supporting paper](../supplied-1977-identity-v1/README.md) remains a distinct curved-yield-surface extension. It cannot supply missing1975 equations or cap/plastic-collapse behavior. Source completeness means the complete named article is readable and its laws inventoried; it does not mean it prescribes every modern numerical/host convention.

## Existing work and gaps

[Previous checkpoint](../manifest.json) and its separate source-access review record the then-unavailable original. No prior executable Lade–Duncan candidate was identified. This packet adds actual source locators, complete equation/parameter inventory, tensor conversion, history and numerical-interpretation issues, plus independent algebra checks. No shared schema/compiler/catalogue/model/browser implementation is changed here.

## Equations and source-to-schema crosswalk

Notation in this packet: S is the compression-positive symmetric mechanical stress tensor; I1=tr(S), I3=det(S), f=I1^3/I3. Source sigma1≥sigma2≥sigma3 denotes ordered principal stresses in its test conditions; sigma3 is also called confining pressure. For a general3D implementation, using current λmin(S) in pressure-dependent coefficients is a numerical/embedding interpretation requiring explicit review, not an extra source equation.

| Source locator | Equation / quantity | Intended v0.3 mapping / units | Status |
| --- | --- | --- | --- |
| p1039 Eq1 | dε=dεe+dεp | Symmetric strain increment, unit1 | Infinitesimal/additive embedding; no finite-deformation rule |
| pp1039–1040 Eq2 | Eur=Kur·pa·(sigma3/pa)^n; generalized Hooke law | Pa; νi=0 for both Table1 sets | Evaluation point of variable modulus not prescribed |
| p1040 Eq3 | I1^3−κ1 I3=0 | Failure event f=κ1; dimensionless κ1 | Not the whole model; post-failure continuation unprescribed |
| p1041 Eqs4–5 | I1=sum normal stresses; I3=σxσyσz+2τxyτyzτzx−σxτyz²−σyτzx²−σzτxy² | trace/determinant of S, Pa and Pa³ | Source lists full off-diagonal determinant |
| pp1041–1042 Eq6a/b | f=I1³/I3; f=κ1 at failure; hydrostatic f=27 | Scalar stress level; separate persistent maximum/current yield level h | Current f alone loses unloading history |
| p1042 loading rule | Plastic only for increasing f on current yield surface; interior/df≤0 neutral/unloading elastic; highest prior surface retained | h=max(prior h, reached f), plus threshold ft | No plasticity on increasing proportional stress at constant f, explicitly p1050 |
| p1043 Eq7 | g=I1³−κ2 I3 | Pa³ potential; κ2 held fixed for stress derivative | Do not differentiate κ2(f(S)) as part of g |
| p1043 Eq8 | Δεp=Δλ∂g/∂σ | Δλ units Pa^-2 | Numerical scaling needed; schema plastic_multiplier is dimensionless |
| p1043 Eq9 | normal rows: Δλ(3I1²−κ2 cofactor_ii); shear yz row:2Δλκ2(σxτyz−τxyτzx), cyclic rows zx,xy | Source shear entries interpreted as engineering shear for work conjugacy; permute yz,zx,xy to Atlas xy,yz,xz and divide engineering strains by sqrt2 | See algebra checks; source does not explicitly spell out engineering label |
| pp1044–1045 Eq10a/b | −νp=Δε3p/Δε1p=(3I1²−κ2σ1σ3)/(3I1²−κ2σ3²) in triaxial compression | Calibration relation, not an extra evolution state | Denominator must be nonzero |
| p1045 Eq11 | κ2=3I1²(1+νp)/[σ3(σ1+νpσ3)] | Calibration of flow | Equivalent algebra checked independently |
| p1045 Eq12 | κ2=A f+27(1−A) | Dimensionless derived coefficient | Re-evaluate between stages; freeze within ∂g/∂σ |
| pp1045–1046 Eq13 | Wp=F(f), positive monotone F | Plastic work density, Pa | General prose; pressure-dependent fitted F creates interpretation issue below |
| p1046 Eq14 | Wp=∫{σ}ᵀ{dεp} | Pa; Mandel work dot(S,dεp) | Full six-vector work consistent with engineering source shear |
| p1046 Eq15 | Δλ=dWp/(3g) | Pa^-2; from homogeneity at fixed κ2 | Avoid hydrostatic g=0; threshold branch must bypass division |
| p1046 Eq16 | f−ft=Wp/(a+d Wp), no plastic work for27≤f≤ft | Wp=a(f−ft)/[1−d(f−ft)] when a fixed | Not a prescribed total derivative for changing a |
| p1046 Eq17 | a=M·pa·(sigma3/pa)^l | a in Pa; M,l dimensionless | Same pressure/evaluation-point issue as Eq2 |
| p1047 Eq18 | rf=(κ1−ft)/(f−ft)ult; (f−ft)ult=1/d | d=rf/(κ1−ft), unit1 | rf<1 as stated; κ1>ft |
| p1047 Eq19 | dWp=a df/[1−rf(f−ft)/(κ1−ft)]² | Local plastic work increment for newly increased f | Literal law contains no da; source calls f current and df successive-state difference |

The tensor gradient in a work-conjugate basis is N=3I1²I−κ2 cof(S), where cof(S)=S²−I1 S+I2 I and I2=[I1²−tr(S²)]/2. This is an algebraic restatement of Eq9, not a new evolution law. In Mandel order [xx,yy,zz,sqrt2·xy,sqrt2·yz,sqrt2·xz], both stresses and tensor strains carry sqrt2 shear factors. In source engineering order [x,y,z,yz,zx,xy], stresses carry no shear factor and strains carry2. Using Eq9's factor2 directly as a Mandel component would give wrong work and Euler normalization.

### Parameters and source examples

All nine Table1 parameters are dimensionless. pa is an atmospheric reference pressure with stress units (Pa in Atlas); the paper requires common units but supplies no exact SI value. Choosing101325Pa is a disclosed conversion/reference convention, not a fitted Table1 value.

| Parameter | Dense Monterey No.0 sand | Loose Monterey No.0 sand | Meaning / locator |
| --- | ---: | ---: | --- |
| κ1 |103|58| Failure level, Eqs3/6 |
| ft |40|33| Plastic threshold, p1046 |
| A |0.44|0.39| Flow slope, Eq12 |
| rf |0.957|0.970| Hyperbola failure ratio, Eq18 |
| M |2.55e-4|6.80e-4| Hardening amplitude, Eq17 |
| l |1.32|1.17| Hardening pressure exponent, Eq17 |
| Kur |2300|1600| Elastic modulus number, Eq2 |
| n |0.80|0.86| Elastic pressure exponent, Eq2 |
| νi |0.0|0.0| Elastic Poisson ratio, p1040 |

Table1 is on printed1048. The two named sets are evidence-backed examples, not validation of an interpolated/global range. Figure2 identifies initial void ratios0.57 dense/0.78 loose for the failure data; no explicit void-ratio evolution law is supplied. Do not make e a required evolving state without a separate relation. Physical restrictions for a proposed pre-failure implementation: positive principal stresses/pressure, Kur>0,M>0,κ1>ft≥27,0≤rf<1; Table1 has0<A<1 and νi=0. These are source-example/analytical admissibility restrictions, not source-published universal calibration bounds. Require finite values and a nonzero hardening denominator.

### Explicit formulation and state decisions still required

New records must target [schema v0.3](../../../../../schemas/model-v0.3.schema.json) with the complete [formulation contract](../../../../FORMULATION_CONTRACT.md), without legacy top-level integration. This packet is not a model JSON.

- Equation form/time: source differential/incremental stress-to-strain relations without physical clock, viscosity or aging law. A strain_path incremental_residual realization is plausible; finite backward-Euler versus stage integration is an explicit Atlas choice. No physical_time ODE relabeling.
- Kinematics/frame: source additive strains and fixed Cartesian stresses support a restricted small_strain_3d/fixed_spatial/objective_rate:none embedding; source does not define finite rotation, stress transport or an objective rate. Rotating principal *stress directions* in torsion is not finite-spin host qualification.
- Signs: compressive principal stresses and axial strain are positive in equations/plots; Fig1/7 distinguishes positive compression and negative volume expansion. Preserve this convention. Basis conversion as above.
- Stress output: source names mechanical stresses, with no pore-pressure variable, total/effective decomposition or coupled update. It does not explicitly identify Cauchy/effective/total nomenclature. A v0.3 scope must be justified by a bounded uncoupled/drained or zero-pore-pressure embedding and reviewed; do not guess effective by default or advertise undrained capability. This remains an E2 decision.
- Persistent state: sigma first (six Mandel entries); historical yield level h≥ft carrying maximum reached f; accumulated Wp if reported/restarted; optional accumulated plastic tensor strain for diagnostics, explicitly committed. Source Wp is work per volume, not a plastic multiplier. Density example labels remain fixed. Required initial state must specify all selected persistent fields; temporary solve variables have zero initial values and no committed history.
- Temporary state: a scaled plastic flow magnitude can be dimensionless (e.g. γ=Δλ·pa²) and N/pa² dimensionless. Do not declare source Δλ as a dimensionless physical parameter. Whether ordinary increment_unknown or specialized plastic_multiplier semantics apply must be checked against the actual solver/predictor; no schema flag is selected merely by the word multiplier.
- Initialization: source experiments begin isotropically consolidated (Fig8), while a general arbitrary-state constructor is not given. An explicit isotropic prepared example S=p0I,h=ft,Wp=0 is a relative reference from onset of shearing, not a simulation of consolidation or a universal specimen default. Overconsolidated/reloaded initial states require the true history h and compatible work, not h=f(S) after unloading. Arbitrary initial Wp/h consistency depends on pressure-history interpretation.
- Domains/events: I3=0/zero or tensile confinement outside contemplated positive-confined example support; reject rather than clip. ForTable1/pre-failure f≤κ1, g>0 above ft. The paper does not prescribe post-failure softening evolution or FE localization treatment; reject/stop at failure unless a distinct extended formulation is qualified. Hydrostatic f=27,g=0 must use elastic branch without division.

## Temporal integration and transactions

The source's constitutive driver is stress change, with strains calculated from the elastic plus plastic parts. A strain-controlled Atlas host must solve that relation implicitly; its choice of integration is not author code. No seconds, strain-rate history, hold aging or creep state are required. A zero mechanical increment must preserve all persistent state. Unloading and reloading inside the retained surface are elastic; crossing the prior maximum reactivates plasticity. Constant-f loading must remain elastic even as pressure rises. h is never reset at each increment or on unload.

**Pressure/history reconciliation:** Eqs13/16 describe Wp as a function of f, while Eq17 makes the fitted coefficient pressure dependent. Literal Eq19 gives only a·df divided by its squared denominator. Differentiating a current-pressure global Wp=a(f−ft)/[1−d(f−ft)] would add a da term and create plastic work on some constant-f paths, contrary to p1050. Therefore the smallest defensible numerical interpretation is to use Eq19 locally, evaluating a at declared stages, retaining accumulated work and maximum f separately, and not impose the global algebraic Wp formula on changing-pressure paths. This interpretation still needs independent contract review and a named frozen numerical study; it is not a mathematical impossibility or proven missing generic engine capability.

A possible finite residual would consume only the newly reached stress-level excursion above max(h_n,ft), with threshold/prior-surface event splitting. Endpoint-only branch selection can miss an excursion that loads and unloads inside one large strain-controlled segment; substeps/events must resolve it. Choose and freeze start/end/midpoint pressure sampling, f/κ2 sampling, integration order, event tolerances and refinement before compiled results. Work and flow branches must use consistent Δf. Do not differentiate κ2 when evaluating the fixed-potential flow direction, but derivatives of the full constitutive residual can include its state dependence.

Atlas requirements (software, not author algorithm): each trial starts from the same complete committed parent; successful solve commits all history together; failure returns the full incoming state, including temporary slots; no partial substep work survives failure. Repeated trial/retry and full-state restart/replay must agree. Stage holds with no change have no source mechanism for evolution. Physical time durations must not affect results. Pressure discontinuities, reversals and control changes require resolved segments. A tangent is generally nonsymmetric due to nonassociated flow; gradients of λmin are nonsmooth at repeated minima, including common triaxial compression. Existing spectral-value/predicate support must not be mistaken for qualified repeated-eigenvalue AD/tangent support.

## Independent checks and prospective study

[check_policy.json](check_policy.json) fixes the algebra cases and tolerances before running [check_algebra.py](check_algebra.py). The checker uses exact rational directional interpolation of the cubic potential (fixed κ2), independently of the engine/production model, to test all six Eq9 components and Euler3g/work. It also checks Eq11 calibration inversion, Eq16→19 differentiation for fixed a, hydrostatic f27/zero flow, Table1 constraints and finite failure-work denominator. This is equation verification only, not a constitutive path solver or author-figure replication.

Commands: `python3 -B docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/check_algebra.py`. Results in `algebra-results.json`. No native/Wasm builds or executable model runs were performed.

Next qualification must freeze a separate identity before observing compiled results: both Table1 sets; hydrostatic/proportional paths; triaxial compression and extension; full off-diagonal shear; unload/reload crossing h; threshold and failure events; varying-pressure paths contrasting local Eq19 with the invalid global da interpretation; rotated Cartesian covariance; repeated eigenvalue derivatives; path refinement; invalid/tensile input; full-state rollback, recovery and restart. Compare an independently stress-driven reference with strain-controlled inversion, with source/example applicability separately stated. No numeric path tolerance is invented before selecting the discrete method and reference convergence.

## Handoff and phase status

Readable original source: acquired and all pages inspected. Complete available equation/parameter inventory: above. Source conventions unspecified by the paper: explicitly marked, not filled from1977. E2 contract: open pending independent source/interpretation audit, mechanical stress scope, pressure sampling/discretization, history initialization, spectral tangent behavior and prospective numerical gates. These are separately resolvable interpretation/qualification tasks; no unsupported capability is asserted without a reproducible example. E3 transcription/E4 native-Wasm/E5 model approval/E6 atlas/E7 browser/E8 live: not done. Experimental reproduction: not performed; paper figures are published author comparisons, not new Atlas validation.

Exact additions live under supplied-original-v2/. Earlier source failures and hash-bound checkpoint remain historical. No public model, handwritten production kernel, build, shared-runtime change, publication or remote action is claimed. Independent source review is not E5 acceptance.
