# original-cam-clay - ingestion packet

Task ID: ING-original-cam-clay
Owner / date: review_vw96 / 2026-10-31
Scope: source-located Chapter6 Original Cam-clay (OCC) inventory and bounded analytical checks. This is an ingestion packet, not a new executable model or completed1968 edition certification.

## Identity and sources

Selected work: Andrew Schofield and Peter Wroth, *Critical State Soil Mechanics*, McGraw-Hill,1968; Chapter6, especially Sections6.1-6.7, printedpp93-104. Original Cam-clay is distinct from Modified Cam Clay (MCC). The authors' university independently confirms the book/year: [Cambridge Engineering](https://www.eng.cam.ac.uk/node/4054). No book DOI was verified; none is invented. Chapter6p102 refers to a research modification; p114 explicitly distinguishes the omitted smoother-corner modification from the model developed here.

**Available artifact, not authenticated first-edition facsimile:** [university-hosted electronic text](https://fme.hcmuaf.edu.vn/data/critical_state_soil_mechanics.pdf), downloaded2026-10-31 to private `/private/tmp/atlas-ingest-occ-20261031/private/schofield-wroth-1968.pdf`; SHA256 `638e0ee7dc238ae8922b79983433be7d12ad30450098efe395968f7eeed13cb2`;7,886,630bytes;229PDFpages. Cover identifies Schofield/Wroth, followed by Preface and chapters. PDFmetadata says MicrosoftWord/PDFWriter, created2005-05-26UTC, modified2005-06-12UTC, and misspells Wroth as Roth. Its first page adds a vulcanhammer notice. There is no visually verified1968 publisher/copyright leaf. Consequently its later transcription fidelity and exact printing remain an explicit source gate. Do not label this hash as original1968 scan bytes.

For the numbered body, **one-based PDFpage=printedpage+11** (e.g.p99=PDF110,p216=PDF227). Title, pp69,94,95,97,99,101,103,216-217 were rendered and visually inspected under the PDF skill; Chapter6pp93-104 and AppendixCpp216-218 were read as text. Source equation absolute-value signs were checked visually because extraction drops them. Chapter2/general continuum discussion and Chapter7 are context, not fully reviewed here.

No matching source filename was found in Downloads or existing original-paper inventory by bounded search. Two legacy Cambridge URLs (`www-civ.eng.cam.ac.uk/geotech_new/publications/schofield_wroth_1968.pdf` and `.../schofield8wroth81968.pdf`) failed DNS in this session; web reader could not access their variants either. Public university mirror succeeded after the ordinary sandbox lacked network DNS. Private acquisition log retains outcomes. No author binary/code executed; no authentication or contact used. University hosting/read access establishes neither copyright ownership nor redistribution permission. PDF, extracted text, screenshots and raw web content are excluded from public packet.

## Existing work and gaps

The [catalogue](../../../catalogue/manifest.json) has a candidate `original-cam-clay`; the [live plan](../../../IMPLEMENTATION_PLAN.md) assigned this source task. No existing dedicated OCC equation dossier or matching Downloads PDF was found. Existing [Modified Cam Clay dossier](../../models/modified-cam-clay.md) and runtime are a separate formulation and are not inherited as an OCC closure.

This packet pins a readable source artifact, separates original triaxial closure from a proposed3D extension, derives initialization/hardening in modern pressure coordinates, and supplies analytical diagnostics. `source-receipt.json` retains exact dependency/source hashes. `contract.json` is **non-executable**; no declarative runtime draft is offered because original rigid shear response and corner selection do not fit an assumed finite elastic predictor without an explicit variant/algorithm decision.

## Equations and schema crosswalk

### Coordinates and notation

Source compression-positive stress/strain agrees with Atlas sign. In the original coaxial axial test, `p=(sigma_l'+2sigma_r')/3>0`, **signed** `q=sigma_l'-sigma_r'`; volumetric shortening increment `dE_v=dε_l+2dε_r=-dv/v`, axial distortion `dε_s=(2/3)(dε_l-dε_r)` (Chapter5 Eqs5.2-5.9,pp68-69). Work is `p*dE_v+q*dε_s` (Eq5.13p70). Source dots indicate small increments/probes, not necessarily physical-time derivatives. Its dotted `v` means compressive volume loss `-dv`, not the mathematical derivative of specific volume. In the formulas below `v'` is the true derivative and therefore `v'=-v*E_v'`. Always retain this sign distinction.

`v=1+e` is specific volume, unit1. Pressure logarithms require an explicit positive reference `p_ref`: translate source `ln p` to `ln(p/p_ref)`. The source's later calibration discussion uses1lb/in² as unit pressure (p111). Gamma and normal-compression intercepts depend on that choice; replacing pressure numbers with Pa without changing the intercept is wrong. All schema stress quantities are Pa. If p_ref changes from r1 to r2, `Gamma2=Gamma1-lambda*ln(r2/r1)`. Lambda/kappa are slopes of **v versus ln p**, not ln(v) or e versus log10(p).

### Source equations and derived equivalent state coordinates

| Source locator | Relation / schema representation | Units / status |
| --- | --- | --- |
| Eq6.3-6.5p94 | Recovery `v_b=v_a-kappa*ln(p_b/p_a)`; `w_kappa=v+kappa*ln(p/p_ref)`; `w_lambda=v+lambda*ln(p/p_ref)` | Scalars1; exact source recovery, w_kappa fixed inside yield locus |
| Eq6.7p95 | Recoverable shear increment identically zero | Original closure: shear-rigid elastic response; not G=0 and not arbitrary finite G |
| Eq6.9-6.14pp95-97 | `p*E_v^p+q*ε_s'=M*p*abs(ε_s')`; `E_v^p=E_v'-kappa*p'/(v*p)` | Pa per path coordinate; signed shear branches are essential |
| Eq6.15-6.16p97 | Critical `abs(q)=M*p`, `v=Gamma-lambda*ln(p/p_ref)` | M>0 unit1; not a yield surface by itself |
| Eq6.17-6.18p99 | `abs(q)/(M*p)+ln(p/p_x)=1`, `w_kappa` fixed on a yield curve | p_x is critical pressure on current yield curve, not its isotropic intercept |
| Eq6.19p99 | Boundary `abs(q)=M*p/(lambda-kappa)*(Gamma+lambda-kappa-v-lambda*ln(p/p_ref))` | Source boundary relation; not applicable to every interior state |
| Eq6.20p100 | Fixed-eta boundary line `v+lambda*ln(p/p_ref)=Gamma+(lambda-kappa)*(1-abs(eta)/M)` | Signed-branch extension uses abs(eta); upper-half source presentation eta>0 |
| Derived from6.17 | Define isotropic intercept `p_c=exp(1)*p_x`; yield `f=abs(q)+M*p*ln(p/p_c)<=0` | Algebraic reparameterization; **not** MCC ellipse `q²+M²p(p-p_c)` |
| Derived from6.16/6.18 | `ln(p_x/p_ref)=(Gamma-w_kappa)/(lambda-kappa)`; `p_c=p_ref*exp(1+(Gamma-w_kappa)/(lambda-kappa))` | Exact equivalent packing/hardening coordinate under this closure |
| Derived from6.11p97 | `w_kappa'=-v*E_v^p`; `p_c'/p_c=v*E_v^p/(lambda-kappa)` | Hardening for compaction, softening for dilation; true derivative signs |
| Eq6.14 and neutral normal pp98-99 | Smooth on-yield branches: `E_v^p/abs(ε_s')=M-abs(q)/p`; associated flow for fixed p_c has `f_p=M*(1+ln(p/p_c))`, `f_q=sign(q)` | On yield f_p=M-abs(q)/p. Derivative does not exist uniquely at q=0 |
| Eq6.23-6.26pp100-102 | `Lambda=1-kappa/lambda`; fixed-eta compression strain ratios and source K0 corner branch | Derived Lambda not independent parameter; corner selection remains nonsmooth |
| Eq6.27-6.31p103 | Virgin undrained exact path, given below | Independent source analytical fixture, no return mapping needed |

Source Eq6.12p97 gives a stability inequality. Sourcep99 classifies wet-side hardening as stable and dry-side softening as unstable. This is a constitutive/physical warning, not permission to suppress softening numerically or promise uniqueness under every mixed control.

### Original3D versus adopted modern3D

The Chapter6 law is developed for a coaxial axisymmetric test with signed q. Section6.11p114 postpones the generalized invariants. **AppendixC explicitly starts from Granta-gravel**, keeps `p_u=exp((Gamma-v)/lambda)`, and builds a3D principal-stress yield/potential. It does not independently rederive Cam-clay's kappa packing/hardening/recovery in3D. Do not transplant its Granta-gravel p_u into OCC as p_x or p_c.

AppendixC3pp216-217 gives `p*=tr(sigma)/3`, `q*=sqrt(3/2*dev(sigma):dev(sigma))` and an axisymmetric surface of revolution; C5-C9 give principal plastic normal action. At q*>0 its deviatoric part is `3*dev(sigma)/(2*q*)`, its volumetric part follows the yield derivative. The natural **proposed extension** is to use this invariant geometry with OCC p_x packing coordinate and zero recoverable deviatoric strain. That extension requires an explicit formulation identity and review; it is not the same as merely saying “the1968 model is3D”. Finite rotations/objective stress updates and arbitrary changing principal directions have not been certified by this packet.

If a later variant uses Atlas tensors, preserve Mandel order `[xx,yy,zz,sqrt(2)*xy,sqrt(2)*yz,sqrt(2)*xz]`. `q*>=0` equals abs(q) on axisymmetry; it loses the sign of the original axial compression/extension observable. Keep signed test q separately. Adding finite shear modulus G or Poisson ratio would also create a declared augmented variant; setting G=0 would give zero shear stiffness, the opposite of the original rigid response.

### Parameters, domains and initialization

Original inputs: M,Gamma,lambda,kappa and explicit p_ref. Require finite M>0, p_ref>0, `0<kappa<lambda` for this bounded analytical packet. kappa=0 is the separate Granta-gravel limiting case in the source, not supported by formulas dividing by kappa. Illustrative fixtures use arbitrary `(M,lambda,kappa,Gamma)=(1.2,.2,.04,2.5)` and p_ref1000Pa; these are **not source calibration/defaults**. Domain requires p>0, p_x/p_c>0, positive finite v (physical e>=0 may be a separately stricter project policy), finite logs/exponentials and admitted yield state. If requiring all principal effective stresses positive in a later3D packet, label that an additional support choice rather than infer it from p>0.

Minimal scalar-state proposal `[p,q,v,w_kappa]` retains one redundant packing check `w_kappa=v+kappa*ln(p/p_ref)`. Alternative `[p,q,v,p_c]` has the same redundancy once Gamma is fixed. The API must reject inconsistent independently supplied packing/pressure values; it must not silently change density, project stress, or recompute away supplied preparation history. An explicit constrained3D representation would be `[sigma6,v,w_kappa]` (8slots), not an independently chosen new hardening rule. Accumulated plastic/shear strains are optional observables when full packing state is supplied, not mandatory source histories established here.

For isotropically virgin compressed initial state (Sec6.7p102), `q0=0`, `v0=Gamma+lambda-kappa-lambda*ln(p0/p_ref)`; p_c0=p0 and p_x0=p0/exp(1). This is a specific preparation. For a supplied general state compute packing identity and check `abs(q)<=M*p*ln(p_c/p)`; equality is yield, strict inequality interior. Overcompressed specimens preserve packing while unloading along a kappa-line; OCR=p_c/p is meaningful for isotropic q=0 but is not a sufficient arbitrary3D history descriptor. Original interior probes have no distortion even if q changes, and volume follows the kappa recovery. Actual specimen consolidation/drainage preparation (Ch7pp118-120) is separate from constitutive initial state.

### Branches and singular cases

- Smooth branch q!=0: signed shear normal, compaction for abs(q)<Mp, dilation for abs(q)>Mp, critical zero plastic volume for abs(q)=Mp.
- Vertex q=0,p=p_c: the norm/absolute-value gradient is not unique. Sec6.6p101 discusses the cone between two limiting strain directions and includes a zero-distortion volumetric direction. AppendixC10p217 describes a limiting distortion magnitude at its Granta-gravel corner; it does not justify replacing the Chapter6 cone with a unique isotropic smooth normal. Preserve this distinction.
- Interior q=0,p<p_c has no yield-gradient evaluation requirement. Never divide by q globally merely because the chosen3D norm formula exists.
- At critical state, volumetric hardening modulus vanishes; stress control can allow indefinite distortion. Softening can cause loss of stability. A generic positive-definite elastic predictor/unique strain-to-stress assumption is not justified.
- p→0 is outside logarithm-domain support; no tension cutoff or regularization is silently appended.

## Temporal integration and transactions

The source is rate-independent infinitesimal plasticity in a quasi-static probing/test description, not a viscosity law. Chapter5p70 footnote explicitly separates the plasticity equations from physical time. Input can be ordered dimensionless path coordinate and stress/strain controls; drainage/transient consolidation times are external coupled processes. No constitutive creep/aging is inferred from a physical hold. A complete0increment accepted-state identity is a proposed API convention, not a general solution for a mixed stress hold at a critical mechanism.

Smooth trial order: read one consistent old snapshot; compute pressure/packing/yield and source bulk recovery; determine interior/entry/signed branch/vertex active set; solve yield consistency plus volume balance, zero recoverable shear and requested controls together; update v and packing consistently; check full state/yield/domain/residual/error; atomically commit. No lagged packing switch is specified in the inspected source. A plastic multiplier is trial-local. Interior shear rigidity is a constraint, so a solver must treat missing shear compliance correctly; it cannot apply an ordinary invertible finite-G elastic predictor and call it original OCC. Arbitrary imposed interior shear strain may force yield or expose nonuniqueness; mixed-control rank depends on actual active constraints.

Finite return map, event localization, branch switching tolerances, critical/vertex selections, adaptive error estimator, iteration budgets and discrete tangent are **unspecified in inspected source**. A constitutively consistent tangent on a selected smooth branch differs from the Jacobian of a particular finite update. Convex corner handling requires an explicit active-set/normal-cone algorithm and selected loading control. Do not smooth abs(q), clamp p, insert finite G or replace f by the MCC ellipse as an undocumented numerical fix.

Engineering transaction proposal: retain all old stress/density/packing and any optional strain observables; trial stages and branch data are isolated. Any failure returns the exact old full snapshot plus attempted coverage and reason, with no partially committed plastic compaction. Retry starts from last accepted state. Restart restores packing/history and parameter/reference-pressure identity; it does not set p_c to current p or reapply virgin preparation. Volume must use true derivative `v'=-v*E_v'`, not forward-add the source's positive compressive dot-v symbol. No native transaction evidence is claimed by these ingestion checks.

## Independent checks

`check_packet.py` is a source-derived analytical/algebra diagnostic, **not a general constitutive evaluator**. Virgin-undrained compression has (Sec6.7p103):

`Lambda=1-kappa/lambda`, `p_u=p0*exp(-Lambda)`, `A=M*v0/(kappa*Lambda)`,

`p(ε_s)=p_u*exp(Lambda*exp(-A*ε_s))`,

`q(ε_s)=M*p(ε_s)*[-expm1(-A*ε_s)]`, `v=v0`.

At every retained point the checker independently recomputes packing/p_c and verifies yield, volume, dissipation and the source differential relation. It also checks exact kappa recovery cycles, intercept unit conversion, signed compression/extension normals, Cartesian work, finite-difference smooth yield gradients and3D invariant reduction on axisymmetric stresses. Small-increment expm1 is used; this is numerical evaluation of the analytical fixture, not author algorithm execution. No quadrature or finite-path compiled comparison is claimed.

Reproduce from repo root after integration (source-hash check optional only when private PDF is available):

```
python3 docs/ingestion/original-cam-clay/check_packet.py --output /private/tmp/occ-checks.json
python3 docs/ingestion/original-cam-clay/check_packet.py --source /private/tmp/atlas-ingest-occ-20261031/private/schofield-wroth-1968.pdf --output /private/tmp/occ-checks-source.json
python3 docs/ingestion/original-cam-clay/test_packet.py
```

`checks.json` retains concrete inputs/results with tight declared binary64 algebra tolerances; tests include invalid Boolean/nonfinite/domain inputs and receipt hash corruption. The helper is a diagnostic for the retained moderate-scale fixtures, not a certified all-binary64-range evaluator. The initial vertex is evaluated through the exact supplied path, not through an invented unique corner normal. Ingestion equations and analytical checks are not experimental validation.

## Handoff

Owned packet contains README.md, contract.json, source-receipt.json, check_packet.py, test_packet.py, checks.json and manifest.json. Manifest binds relative authored files only; private PDF/renders/extraction/acquisition payload are excluded. Whitespace is stripped before final hashing. Coordinator integrates and updates the board; this task does not own shared code, candidates/status or historical evidence.

Remaining gates: authenticated1968 edition/facsimile crosscheck (especially absolute signs and AppendixC transcription); exact adopted3D Cam-clay versus Granta-gravel mapping; original shear-rigid constraint support; nonsmooth hydrostatic vertex; critical/softening and loading-control wellposedness; finite integration/tangent/rollback implementation with frozen references; independent source review and experimental preparation. Numerical stability of very large/small pressure ratios also requires a later bounded study. Complete general3D closure is not certified by the existence of a yield formula.

Smallest useful next implementation/reference task: a **named axisymmetric virgin-undrained OCC analytical fixture**, compare independently integrated smooth compression after a positive initial shear offset to6.30-6.31, and separately freeze corner initialization. This avoids pretending that a finite-G MCC kernel is an OCC implementation. Generic capability request: constrained zero elastic shear compliance, absolute-value/norm normal cones, branch/event-aware consistency and transactional mixed control; coordinator should select/model these explicitly before adding a new shared engine path.

**Source completeness:** bounded readable textbook transcription inventory;1968 artifact fidelity and3D closure open. **Executable support:** no admitted OCC model or shared implementation. **Numerical verification:** analytical/algebra tests only. **Scientific/public admission:** unchanged, pending review and future source-matched finite/experimental evidence.
