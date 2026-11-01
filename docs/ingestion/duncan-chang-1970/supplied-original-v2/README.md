# Duncan-Chang 1970 - supplied-original source packet v2

Task: SRC-duncan-chang-supplied-original-v2, under MODEL-duncan-chang-1970. Coordinator / 2026-11-01. Additive resumption of [delivery-v1](../delivery-v1/README.md); earlier missing-source receipts and separate review remain historical and unchanged. [Delivery ledger](../DELIVERY.md).

## Identity and sources

The user supplied the publisher scan of James M. Duncan and Chin-Yung Chang, *Nonlinear Analysis of Stress and Strain in Soils*, Journal of the Soil Mechanics and Foundations Division96(5), September1970, pp1629-1653, [DOI10.1061/JSFEAQ.0001458](https://doi.org/10.1061/JSFEAQ.0001458). The filename's2021 does not define a new constitutive version. The first-page imprint and PDF subject identify1970; the online record previously identified2021 digitization.

[receipt.json](receipt.json) records the attachment path, durable ignored private copy, exact SHA-256, size, access date and actual page map. The PDF has25 pages but only24 distinct printed article pages: PDF19 repeats printed1645; printed1647 is absent. Both scans of1645 were visually compared; this is not merely a mistaken OCR page number. Page1646 ends mid-sentence in the FE discussion and1648 starts later in the mesh description, so missing1647 cannot be dismissed as blank. Main constitutive Eqs1-15 and Table1 are present; missing FE text/Fig17 cannot be reconstructed from adjacent pages. No attempt to repair or rewrite the supplied bytes was made.

The separate [1971 erratum](https://doi.org/10.1061/JSFEAQ.0001706),97(11),p1597, is still unavailable. It is not bundled in this article and its affected passage is unknown. Neither source-complete original-plus-correction nor final executable identity is claimed. Raw PDF, extracted text and rendered images remain private; publisher copyright/rights are retained, no redistribution authorization established.

## Existing work and gaps

The [historical acquisition packet](../README.md) and [source-gate review](../delivery-v1/independent-review/README.md) correctly described access at their dates. This new packet supersedes their missing-original claim only for the received pages. It resolves uncertainty about the original's constant-Poisson closure, full tensor compliance, actual unloading memory and source parameter examples. It preserves missing-page/correction and finite-algorithm questions rather than substituting later E-nu/E-B laws.

## Equations and schema crosswalk

Notation here: D = sigma1-sigma3 (ordered major/minor principal stresses), Df = its failure value; D is not the triaxial invariant q for a general tensor. Engineering axial strain epsilon is dimensionless. All source formulas below are transcribed mathematical relations; numerical domain restrictions and Atlas conventions are separately identified.

| Source / actual PDF page | Equation or relation | Mapping / interpretation |
| --- | --- | --- |
| p1630 /2, Eqs1-2 | D=epsilon/(a+b epsilon); epsilon/D=a+b epsilon | a=1/Ei and b=1/Dult, both inverse pressure. The transformed relation at zero is understood by limit. |
| p1631 /3, Eqs3-4 | Df=Rf Dult; D=epsilon/[1/Ei+Rf epsilon/Df] | Rf dimensionless. Failure and mathematical asymptote differ; formula beyond failure is not the complete source algorithm. |
| p1631 /3, Eq5 | Ei=K pa (sigma3/pa)^n | K,n dimensionless; pa, Ei, sigma3 pressure. pa is a reference atmosphere in the same units, not a dimensionless literal. |
| p1632 /4, Eq6 | Df=(2c cos(phi)+2 sigma3 sin(phi))/(1-sin(phi)) | c pressure; phi angle. Derived for failure at unchanged minor principal stress. |
| pp1634-35 /6-7, Eqs7-8 | Et=partial D/partial epsilon at fixed sigma3 = (1/Ei)/[1/Ei+Rf epsilon/Df]^2 | Local loading tangent, not secant or finite-step algorithmic Jacobian. |
| p1635 /7, Eq9 | epsilon=D/[Ei(1-Rf D/Df)] | Inverse of hyperbola on its admissible branch. Strain origin need not equal zero initial stress difference. |
| p1635 /7, Eqs10-11 | S=D/Df; Et=Ei(1-Rf S)^2 | S is current strength fraction; not the historical memory measure in the example. |
| p1635 /7, Eq12 | Et=[1-Rf(1-sin(phi))D/(2c cos(phi)+2 sigma3 sin(phi))]^2 K pa(sigma3/pa)^n | Primary loading modulus. Source allows consistent effective or total calibration, p1636. |
| pp1639-41 /11-13, Eq13 | Eur=Kur pa(sigma3/pa)^n | Same n as primary; Kur higher than K for tested sand. Linear near-elastic approximation to observed small hysteresis. |
| p1641 /13, Eq14 | nu=(Delta epsilon1-Delta epsilon_v)/(2 Delta epsilon1) | Measurement diagnostic; not a state evolution or stress-dependent nu law in the chosen1970 calculations. |
| pp1642-43 /14-15, Eq15a-c | Delta epsilon_i=[Delta sigma_i-nu(Delta sigma_j+Delta sigma_k)]/E | Full orthogonal3D compliance; E is selected primary or unloading modulus. |
| p1643 /15, Eq15d-f | Delta gamma_ij=2(1+nu)Delta tau_ij/E | Engineering shear gamma=2 epsilon_ij. In Mandel, Delta epsilon_M,shear=(1+nu)Delta sigma_M,shear/E. |
| pp1642,1644-45 /14,16-17, text | Use Eq13 when stress difference is below its previously attained maximum; otherwise primary-loading relation as appropriate | Memory is maximum D, not maximum normalized S. Equality, turning-point and crossing implementation still need explicit policy. |
| p1643 /15, text | Beyond complete mobilization, nearly horizontal response with a very small positive modulus | No universal value given there. p1648 /20 assigns10psf arbitrarily to failed FE elements in one example. Do not universalize it. |
| pp1649-50 /21-22, Eqs16-17 | settlement=q B(1-nu^2) Ip/E; qult=c Nc | FE/example comparison formulas, not additional material state equations. q here is footing pressure. |

The original supplies an isotropic3D incremental compliance approximation. It need not be replaced with a later3D extension, nor does it prove accurate general3D behavior: p1636 discusses the missing intermediate-principal-stress effect. pp1641-42 explicitly acknowledge anisotropy/dilatancy and choose constant nu. The six fitted parameters are c,phi,Rf,K,Kur,n; nu is an additional closure coefficient and pa a pressure reference. A constant-nu approximation cannot reproduce measured shear-induced dilatancy merely because Eq14 reports nu values above0.5.

### Parameters, initialization and admissibility

| Quantity | Unit / source value | Qualification |
| --- | --- | --- |
| c | Pa after conversion; Table1 c_d=0 | Cohesion; effective/total calibration must match selected scope. |
| phi | Table1 dense36.5 degrees, loose30.4 degrees | Store radians if DSL trig requires radians; do not silently treat degrees as radians. |
| K | dense2000, loose295 | Dimensionless, source Table1. |
| Kur | dense2120, loose1090 | Dimensionless, text p1641 and Table1. |
| n | dense0.54, loose0.65 | Dimensionless, Table1; no universal admissible range supplied. |
| Rf | dense0.91, loose0.90 | p1631 reports commonly0.75-1.00 and says less than unity; do not interpret rounded upper report as a universally safe endpoint. |
| nu | 0.3 for complex sand histories, pp1644-45 | Project candidate must declare it explicitly; not in Table1. Other FE examples use0.35/0.48. |
| pa | Atmospheric reference pressure | Complete explicit Pa value must be chosen and recorded for reproduction; paper does not define a universal exact SI number. |
| Initial void ratio | dense0.50 / loose0.67, p1636 | Calibration/specimen labels, not an evolved density field in these equations. |

Proposed pre-failure numerical domain: positive finite pa,K,Kur and sigma3; positive Df; 0<Rf<1; -1<nu<0.5 for invertible positive isotropic stiffness; nonnegative ordered D and D<=Df. These are explicit bounded implementation proposals, not all source-prescribed universal ranges. There is no source-backed automatic zero-confinement cutoff, tensile continuation, or universal postfailure regularization. A c>0,phi=0 case can have positive strength but sigma3/pa with arbitrary n still needs a defined domain. The n=0 total-stress clay example is not license to remove guards for every calibration.

Persistent state required for a proposed stress-first v0.3 residual: symmetric stress sigma and scalar maximum historical D, h (Pa); cumulative strain may be recorded by the host or a declared persistent field if needed for restart/output. e is not forced into this model. Require explicit h>=current D, including prehistory. Hydrostatic virgin illustration uses h=0 and stress>0; arbitrary anisotropic initial stress does not justify h=current D without preparation evidence. Source p1635 allows arbitrary initial stresses and an arbitrary zero-strain reference, but does not reconstruct prehistory.

### Proposed explicit v0.3 host (not a model definition)

[crosswalk.json](crosswalk.json) records a proposed effective-stress, compression-positive Mandel, small-strain3D, fixed-spatial, zero-spin, strain-path incremental-residual host with input de, no physical clock, persistent sigma/h and explicit initialization. This is a bounded Atlas choice consistent with Eq15; no finite-rotation objective law or general physical-time profile is asserted. Total-stress calibration is a separate source-supported binding choice, not a runtime pore-pressure conversion. New candidate records must use schema_version0.3 with full formulation, state semantics and initialization; top-level integration is not used.

Common engine currently has residual state/history, max/branches and symmetric principal-value primitives (atlas/symmetric_spectral.py). Source dependence on sigma1/sigma3 is not itself a missing spectral capability. However repeated principal values, branch boundaries and real derivative behavior must be qualified against the chosen exact definition; generic feature existence does not establish coverage. No shared schema/compiler change is requested on speculation.

## Temporal integration and transactions

The paper uses finite load/stress increments and accumulated strains/stresses; Eq15 is not an ODE per second. No creep clock or dwell evolution is specified. Under the proposed mechanical interpretation a zero increment is identity; actual executable rollback/zero behavior must still be checked, and time independence applies only to this declared approximation, not to all soil behavior mentioned in the introduction.

p1642 uses average sigma1 and sigma3 to select E, and p1645 uses average confinement for changing-confinement examples. p1646 estimates average FE stresses by extrapolating prior load-induced stress and adding gravity stress. A fully implicit average-endpoint material residual is a project numerical choice; it is not exact reproduction of that extrapolated FE algorithm. For rotating/noncoaxial loading, eigenvalues of the average tensor and average endpoint eigenvalues need not agree. Restricting to coaxial paths initially or choosing/reviewing a named averaging convention is required before any full3D numerical claim.

A finite trial needs a branch policy that handles departure from a historical maximum, reload crossing h, changes of principal ordering, a crossing of Df and the all-zero increment. Merely selecting E by endpoint D<h can miss an unload/reload excursion within a caller segment. Split known reversals/crossings or define an event/partition algorithm before qualification. Commit h only after successful advancement; cutback and failure must restore sigma,h and any cumulative strain. Restart/replay must preserve h and all source-selected state. Temporary trial values cannot masquerade as persistent history. Tangent differentiability is limited at branch switches and repeated eigenvalues; source does not supply a consistent Newton tangent.

Pending decisions: recover1647/erratum; select original-plus-correction identity; select supported pre-/postfailure scope without shrinking a full-law assignment silently; define equality, finite averaging, history/event ordering and exact initial preparation. Freeze references, accepted/rejected domains, finite paths, failure/recovery/restart, tangent/covariance limits and preset before compiled observations. No executable candidate is installed while these are unresolved.

## Independent checks

[check_algebra.py](check_algebra.py) uses exact rational quotient differentiation of the original a,b hyperbola, its inverse and transformed line; compares them with the independently parameterized stress-only tangent; derives six-component Hooke compliance/stiffness inversion and engineering/Mandel shear factors. The first checker failed a Mandel shear factor-of-two error; [the original failure](retained-failure-v1/README.md) and failed code are retained. The corrected factor follows engineering gamma divided by sqrt(2) and Mandel stress multiplied by sqrt(2). Exact rational hydrostatic and pure-shear cases, branch-memory counterexample under changing confinement, and h=0 hydrostatic preparation are included. The hyperbola sweep checks mathematical pre-asymptote identities; some probes exceed Df and do not claim valid postfailure material response. Checks do not exercise Eq5/6 trigonometric calibration, event integration or source data. They establish algebra, not a finite material algorithm or data validation. [check-results.json](check-results.json) retains the result and code hash.

```sh
python3 -B docs/ingestion/duncan-chang-1970/supplied-original-v2/check_algebra.py
```

No fitting, figure digitization, FE reproduction, native/Wasm build, compiled call or vendor code execution occurred. [Independent source review](independent-review/README.md) separately challenges the source/algorithm findings; it is not E5 exact-model approval.

## Handoff

Owned additions: this packet, receipt/crosswalk/checker/results and independent-review child output; mutable delivery ledger and board updated by coordinator. Historical packet and v1 evidence remain exact-byte unchanged. Private source/text/images are excluded from release.

Source status: major original-law equations available and mapped; complete original-plus-correction still blocked by printed1647 and erratum. Executable status: no candidate/build. Independent numerical verification: bounded source algebra only. Agent model approval/atlas/browser/live/experimental status: unestablished. Smallest next action: receive missing page1647 and erratum1597, reconcile corrected passages, then resolve named finite-algorithm/preparation decisions and freeze implementation references under a separately recorded wider whitelist. Continue from those gates; this packet does not close MODEL delivery.
