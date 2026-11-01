# AUDIT-occ-delivery-v1: independent technical blocker assessment

Date: 2026-11-01. Reviewer: actual separate agent task `/root/occ_delivery_audit`, dispatched by `/root` after the board claim. This run did not author the retained OCC packet or smooth reference, implement a candidate, or run compiled artifacts. This is a scoped E1/E2 technical assessment, **not E5 approval**. There is no complete candidate whose bytes could be approved. Owned output is only this new directory; historical evidence and shared code were read, not edited.

**Verdict:** a complete faithful executable OCC formulation is not yet justified. The retained analytical evidence is useful and reproducible. The claim that a new DSL primitive is necessarily required is not established. Source fidelity, explicit corner interpretation, strain-control selection and a qualified residual/solver construction are distinct remaining decisions. A blanket claim that the source cannot support any invariant OCC extension is also too strong.

## Source reading and exact identity

Read the supplied private `book.txt` Chapter 6 governing sections and summary, and Appendix C, alongside existing packet/crosswalks and source receipts. Applied the PDF skill: rendered and visually inspected printed pp95,101,114,217 (one-based PDF pages106,112,125,228) using Poppler. Images remain private under `/private/tmp/occ-review-p*.png`. The exact private PDF SHA256 is `638e0ee7dc238ae8922b79983433be7d12ad30450098efe395968f7eeed13cb2`. Source/evidence hashes are in `evidence-hashes.json`. No source PDF, extracts or page images are copied to this public directory.

The artifact is a readable electronic transcription, not an authenticated 1968 publisher facsimile. The visible p101 sentence contains a nonsensical numeral where the equal-radial strain symbol would be expected. This is a genuine visible defect, not just text extraction loss. It does not negate the adjoining coherent cone discussion; it prevents certifying the exact edition through this artifact alone. A faithful scan crosscheck of governing pages is proportionate; reacquiring every unrelated chapter is not necessary to test the specific equations. Coordinator reports a durable same-hash private copy; this run verified the originally supplied path. Read access establishes no redistribution permission.

## What the source actually fixes

Printed p95 Eq6.7 explicitly sets recoverable distortion to zero. This means infinite shear stiffness/zero shear compliance, never G=0. Nonlinear bulk recovery and packing dependence are as transcribed in the retained packet. The smooth signed yield branches can be written

```
f_plus  =  q + M*p*ln(p/pc) <= 0
f_minus = -q + M*p*ln(p/pc) <= 0
pc = exp(1)*px
```

Both inequalities describe the same domain as the absolute-value yield locus. Associated scalar branch multipliers a,b >= 0 give distortion `dEs=a-b` and plastic volumetric strain `dEv_p=(a+b)*M*(1+ln(p/pc))`. Complementarity is `a*f_plus=0`, `b*f_minus=0`. These are a mathematical residual construction, not a published finite-step update. At the vertex p=pc,q=0 they produce `dEv_p=M*(a+b)` and hence `abs(dEs)<=dEv_p/M`. Pure isotropic compression is included when a=b>0.

Printed p101 explicitly admits vectors between the limiting plastic normals, including isotropic compression, and p102 uses the corner for the K0 case M<=3*Lambda/2. Therefore corner selection is not wholly absent from the source. An imposed strain vector can select a direction in that cone; the source does not prescribe a Newton implementation or a universal unique response for all controls.

There is an important corner qualification: smooth Eq6.9/6.10 dissipation uses absolute net distortion. At the vertex, the cone's isotropic plastic compression has positive stress work but zero net distortion. The two-branch construction gives plastic stress work `M*p*(a+b)`, whereas the smooth absolute-shear expression gives `M*p*abs(a-b)`. These differ when both multipliers are positive. The source's admitted interior cone is thus a corner extension/relaxation of the smooth mechanism, and cannot silently be checked against the smooth equality everywhere. The exact chosen source interpretation must state this and distinguish total signed distortion from summed mechanism magnitudes. This is a source/contract issue; neither adding finite G nor smoothing the yield locus resolves it faithfully.

## 3D identity: narrow finding

The retained packet correctly observes that Appendix C starts with Granta-gravel and retains its `pu=exp((Gamma-v)/lambda)`. Copying that history variable into OCC would erase kappa recovery and be wrong. However printed p114 expressly connects generalizing p,q in **OCC Eq6.17** to the Mises plastic-rate construction to be introduced in Appendix C. Appendix C supplies the invariant geometry and principal plastic normal derivation. Combined reading provides a defensible source-supported route to

```
p = trace(sigma)/3
qstar = sqrt(3/2 * dev(sigma):dev(sigma))
F = qstar + M*p*ln(p/pc)
pc = p_ref*exp(1+(Gamma-v-kappa*ln(p/p_ref))/(lambda-kappa))
```

Here pc is a packing/history coordinate held fixed in the partial stress gradient, not differentiated as though current v were independently fixed. With qstar>0 the plastic normal is `3*dev(sigma)/(2*qstar) + M*(1+ln(p/pc))*I/3`. Bulk recovery and zero recoverable deviatoric strain are supplied separately by Chapter 6. This combination reduces correctly to both signed triaxial branches. It is a derivation from source sections, not an unrelated modern finite-G augmentation. Its fixed-frame infinitesimal tensor interpretation and corner normal-cone extension still need an explicit crosswalk and independent candidate review. No objective finite-rotation law follows from it.

Appendix C10's distortion equality at qstar=0 is a limiting surface-normal relation. Applying it to every cone direction would exclude the isotropic direction expressly allowed on p101. State which corner interpretation is used; do not use C10 to discard p101. Authentication of relevant pages would help distinguish transcription defects from the book's own limiting argument. The smallest blocker is this documented reconciliation and numerical closure, not an unbounded demand for a wholly separate 3D publication.

## Engine evidence and counterexamples

Inspected `atlas/dsl.py`, `atlas/model.py`, `atlas/compiler.py`, `cpp/include/atlas/solver.hpp`, tensor AD operations, schema v0.3 and formulation contract. Existing residual algebra supports logs, tensor operations, temporary increment unknowns, and scalar complementarity expressions. v0.3 has no general mixed stress/strain equation input or DAE profile, but a strain-increment residual can contain algebraic stress constraints; absence of a DAE profile alone does not prohibit this route.

1. **Automatic predictor obstruction is real but role-specific.** `implicit_step` replaces each `plastic_multiplier` equation by its zero-value equation until a predictor converges. A shear-rigid residual `dEs-a=0` with imposed dEs!=0 and a=0 has no solution. Its local `(q,a)` Jacobian block is `[[0,-1],[0,1]]`, singular. Subdivision does not remove the contradiction for nonzero strain. This is a minimal structural witness for the ordinary finite-compliance predictor path, not proof that all generic residuals fail.
2. **Current route worth testing before engine changes.** Declare these temporary solve variables as `increment_unknown`, not `plastic_multiplier`, and retain the actual complementarity equations throughout Newton. Their reset/lifecycle semantics fit trial-local variables. The two scalar signed branches avoid division by q for the axisymmetric cone. This can be represented with current algebra. It remains unqualified: starting at zero multipliers, nonsmooth AD, line search, physical constraints and stress nonuniqueness may prevent convergence. A 3D cone needs its own algebraic formulation and witnesses; the scalar route does not establish that implementation.
3. **Source nonuniqueness is intrinsic.** At p=100000 Pa, pc=200000 Pa, M=1.2, any `abs(q)<83177.661667... Pa` is admissible. q=0 and q=10000 Pa both admit zero strain, no plastic increment, unchanged pressure/volume/packing. Therefore strain input alone does not select the final interior deviatoric stress. Zero hold identity, neutral stress tracking or another selection is an explicit numerical/API convention. Finite-G elasticity would select it by changing the constitutive law.
4. **Interior strain loading is discontinuous.** Any positive prescribed distortion needs plastic flow and an active positive branch, even when incoming stress is strictly interior. The response can reach a finite yield stress as imposed strain tends to zero from above. A continuous strain-path-rate evaluator through that jump is not justified. A residual endpoint relation and explicit selection/event treatment are plausible; the existing smooth RK4 reference does not resolve this.
5. **Ordinary controls need qualification.** The current drained/stress-control wrappers repeatedly call a strain-driven update and use finite-difference outer Newton. A rank-deficient or discontinuous inner map is not automatically a usable stress-controlled material. This is an interface/algorithm qualification gate, not evidence that the source is incomplete.

`witnesses.py`/`witnesses.json` reproduce items1,3 and the corner work distinction without a material implementation. A residual proof or minimal witness should precede any generic engine task. No proposed residual has been loaded, compiled or approved in this audit.

## Reproduced checks and limits

All commands ran from repository root with exit status0:

```
python3 -B docs/ingestion/original-cam-clay/check_packet.py --source /private/tmp/atlas-ingest-occ-20261031/private/schofield-wroth-1968.pdf --output docs/ingestion/original-cam-clay/delivery-review-v1/packet-replay.json
python3 -B docs/ingestion/original-cam-clay/test_packet.py
python3 -B docs/ingestion/original-cam-clay/smooth-reference-v1/reference.py --output docs/ingestion/original-cam-clay/delivery-review-v1/smooth-replay.json
python3 -B -m unittest tests.test_occ_smooth_reference -v
python3 -B docs/ingestion/original-cam-clay/delivery-review-v1/witnesses.py
```

Six packet tests and six smooth-reference tests pass. The frozen smooth study passes unchanged: finest scaled error1.0864287978620268e-8, adjacent improvements17.291934293284434/16.638893321088386. Source hash verification passes. No new trajectory campaign, native/Wasm call, build, browser run, experimental comparison or approval occurred. No failed executed checks were observed; the singular predictor and nonuniqueness are retained mathematical findings, not hidden failed compiled runs.

## Smallest next action

Coordinator should freeze a short, named full-law interpretation: Chapter6 packing/bulk law plus p114/AppendixC invariant geometry; explicit p101 normal cone and its dissipation exception/interpretation; supported control/selection policy including interior holds and strain-triggered jumps. Crosscheck the relevant pages against an authenticated printing when obtainable. Then assign a bounded **current residual capability experiment**, first the signed axisymmetric two-mechanism construction with increment_unknown variables and prospective corner/interior/reversal/rollback checks. Only a demonstrated failure that cannot be addressed within the declared generic semantics justifies a separate runtime capability task. This experiment is a child toward the full requested law, not a substituted completed restricted model. Full 3D, native/Wasm, independent E5 review, atlas/browser and live delivery remain unfulfilled.
