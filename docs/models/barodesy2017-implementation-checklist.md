# Barodesy2017 body-law research fragment: implementation checklist

Read-only preparation31October2026. No builds, author-code execution, git operations, repository changes or model admission. Source: Medicus–Fellin, *An improved version of barodesy for clay*, Acta Geotechnica12,365–376(2017), DOI10.1007/s11440-016-0458-4. Publisher receipt1492680bytes,SHA256`bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15`,12PDFpages, printed page = PDFpage+364. Existing original and independent source inspections establish the locators below; this packet does not newly inspect or redistribute source pages.

## Smallest executable next step

An isolated **instantaneous** typed seven-state fragment, tentatively named `barodesy-clay-2017-body-zero-spin-research`, plus an independent Cartesian/scalar rate oracle. Four explicit parameters and initial sigma/e; no parameter defaults universal to clay. Keep it outside the public runnable catalogue until rate and branch gates pass. It may use the new checked `expm` implementation, subject to its retained operator evidence; existing source dossiers' statements that expm is absent and operator contract is merely planning are historical, not a current capability audit.

Deliver a typed source-linked JSON fragment, evaluator, independent oracle, exact branch/domain metadata, and retained rate cases with hashes. First compare instantaneous outputs; common midpoint integration/refinement is a separate next packet. No history schema or capacity increase is needed.

## Identity choices that must be explicit

- Select **body Eqs1–10**, especially Eq8's `2p/sigma_star`, supported by Appendix2Eq32. Keep Appendix3Eq41's distinct `6p/sigma_star` reading as an unresolved source difference; no claim of erratum or all-formula equivalence.
- Zero spin W=0 only. Sourcep366's printed spin relation repeats WT terms; no finite-spin commutator is selected.
- Incompressible solid grains, sourcefootnote13p374, supplies void-ratio closure.
- Rate independent: a dimensionless path increment `de` can drive the common legacy `integration:rate` interface through positive homogeneity. It represents path-integrated stretching under fixed zero-spin kinematics, not arbitrary finite additive-strain equivalence or time-dependent creep. Input history ordering remains caller-owned.
- No2012clay/sand/2020IGS/ISA/reloading extension, preparation reset, hidden NCL initialization or internal auxiliary fabric.

## Dependency graph and typed expressions

Use compression-positive sigma:Sym(Pa), e:scalar(1); four independent scalars phi_c(rad treated dimensionless),N,lambda_star,kappa_star. Fix sigma_star=1000Pa and c4=1. Reference pressure must carry units; do not call it an extra independently calibrated soil parameter. Model parameters currently support scalar Pa/1, so a fixed Pa quantity can be a pinned singleton-bound parameter if no literal dimensional constant facility exists.

| Stage | Expression / requirement | Exact source |
|---|---|---|
| Constants | s=sin(phi_c); c2=-(3sqrt2+3)/2; c1=(1-s)/(2c2²s); c5=(1+s)/(1-s) | Table1p367,Eqs17,21,23,25,29 |
| Constants | t=c5*lambda_star; c3=(-sqrt3/lambda_star+sqrt3/kappa_star)/(2^t+(1/500)^t-2) | Table1p367; embedded extension-pressure ratio §4.3p369 |
| Constants | c6=1/[2(-sqrt3/(c3*kappa_star)+2^t-1)] | Table1p367 |
| Parent density | p=trace(sigma)/3; density=(1+e)/(exp(N)*(2p/sigma_star)^(-lambda_star)) | BodyEq8p367; p definitionp366 |
| Loading | r=norm(de); U=de/r if r>0; delta=-trace(U) | Eqs1–5p366–367, sign map T=-sigma,D=-de |
| Regular direction | q=norm(dev(U)); m=-sqrt(3/2)*delta/q; x=c1*(m-c2)^2; K=x/(1+x); a=log(K)/(sqrt(3/2)*q) | Algebraically equivalent Eqs4–5p366–367 for norm(U)=1; original q denominators derive from q²=1-delta²/3 |
| Normalized direction | B=expm(-a*U); P=B/norm(B) | Eq3/footnote5p366 and normalization convention |
| Hydrostatic direction | P=I/sqrt3 at exact nonzero dev(de)=0 | Derived normalized isotropic exponential limit; explicit research continuation |
| Scalars | Lambda=-(lambda_star-kappa_star)*delta/(2sqrt3)+(lambda_star+kappa_star)/2; beta=-1/(c3*Lambda)+(2^t-1)/sqrt3 | Eqs9–10p367 |
| Scalars | f=c6*beta*delta-1/2; g=(1-c6)*beta*delta+density^c5-1/2 | Eqs6–7p367 |
| Stress rate | sigma_rhs=c3*(f*norm(sigma)*P+g*sigma)*r | Eqs1–2p366–367, c4=1 and compression-positive zero-spin mapping |
| Void rate | e_rhs=-(1+e)*trace(de) | Footnote13p374 |

Stress rate output is Sym(Pa) per dimensionless path; void rate scalar1. Under physical stretching input E(s^-1), identical algebra produces Pa/s and1/s, but a physical-time ODE wrapper must not suggest relaxation or add time parameters. Scalar powers/logs have dimensionless bases/arguments. `expm` accepts dimensionless Sym only; `exp` stays scalar-only. Frobenius/Mandel shear factors are mandatory.

The merged stress expression removes a removable sigma/norm(sigma) division, but does not make p=0 valid. Avoid NCL `e=...` recomputation on every evaluation; e is retained independently. Coefficients,normalized directions,P,critical density and beta are derived only, never independent history.

## Branch implementation order

Shared-derived expressions are eager in both Python and generated material evaluators. A later domain condition cannot guard an earlier division/log/exponential. Each branch-dependent derived expression must itself be total on its declared inactive branches through nested lazy `select` or a reviewed host evaluator.

1. Validate shape/finiteness and parameters/parent support. Invalid parameter constants may fail explicitly; they must not silently fall through a zero-loading success.
2. For exact zero loading r=0, produce sigma_rhs=0,e_rhs=0 without evaluating U,m,a,logK or expm. Domain support of parent state remains explicit. A convenient placeholder U=0 on this branch is not a physical direction; never expose it as source-defined.
3. For r>0 and exact hydrostatic stretching dev(de)=0, set delta=-sign(trace(de))*sqrt3 and P=I/sqrt3. Skip m,a,K calculations. This includes compression and expansion. No epsilon-sized neighborhood is flattened.
4. For regular nonzero deviatoric direction, evaluate q from deviatoric norm rather than subtracting delta² from3. Evaluate x,K,a and checked expm; reject unsupported domain explicitly. Stable `x/(1+x)` avoids catastrophic subtraction in `1-1/(1+x)`, but computing x can still overflow; reject or separately prove a stable equivalent implementation.
5. Compute scalar density/Lambda,beta,f,g and final rates, then verify all values and Jet derivatives required by the evaluation contract. No clipping or spectral projection.

Current generic operator bound||-aU||F<=64 means |a|<=64 mathematically. This is an algorithm support domain, not a source law. `norm(expm(-aU))` is finite under that bound (though conditioning can be poor); normalized-output/AD accuracy still needs model-level checks. Do not silently bypass operator bound by clipping a. Scalar identity shift cancels in P and could be an explicitly reviewed algebraic optimization later; it is not needed for first transcription.

At zero loading the directional nonlinear law generally has no unique six-dimensional derivative. An AD continuation returning zero is a **chosen numerical derivative**, not proof of a Fréchet tangent. Do not advertise zero-step tangent correctness from primal zero-rate tests. At exact hydrostatic loading, derivative continuity needs independent perturbation checks; computing the branch's literal constant P alone is not a proof that all directional derivatives agree with nearby regular paths.

## Explicit supported/rejected domains

| Case | First-fragment policy | Distinguish fact from restriction |
|---|---|---|
| phi outside(0,pi/2),lambda<=kappa or kappa<=0 | Reject | Conservative parameter support; also verify finite nonzero c3/c6 denominators individually |
| c3<0 | Accept when all other gates pass | All three complete Table2 calibrations have negative c3; no positive-h guard |
| e>=0,finite p>0,finite compressive sigma | Accept within declared stress cone | e>=0 and SPD restriction, if chosen, are research support restrictions, not a proven full paper domain |
| 1+e<=0,p<=0 or sigma=0 | Reject | Density powers/source normalizations are undefined; no pressure floor |
| Hydrostatic stress pI,p>0 | Accept for supported loading | No stress Lode angle/divided deviatoric stress appears |
| Zero loading | Exact no-rate continuation | Homogeneity-based research extension, not a printed numerical algorithm |
| Nonzero hydrostatic stretching | Exact P=I/sqrt3 continuation, both signs | Normalized exponential limit, not raw m/a evaluation |
| m=c2 / x=0 / K=0 | Reject | logK singular; no unresolved limiting projector invented |
| x overflow,K nonfinite,K not in(0,1),nonfinite a | Reject or independently reviewed stable equivalent | No epsilon K and no arbitrary denominator floor |
| |a|>64 | Unsupported operator range failure | Not physical inadmissibility; retain reason in fragment diagnostic |
| Small nonzero q,K very small,nearzero lambda-kappa | Evaluate only if checked arithmetic/support pass | Accuracy/convergence tests required; no blanket neighborhood flattening |
| General spin or finite rotation | Unsupported | Source objective-rate print unresolved; no silent correction |

If an SPD stress support restriction is chosen without an eigensolver, source-independent Sylvester criteria in Cartesian components can check it: xx>0,xx*yy-xy²>0,det(sigma)>0. Apply scale-aware arithmetic and consistent units; this is a new declared support guard. Do not call this source-required. A simpler first rate study can supply known-SPD cases and explicitly require SPD externally while keeping admission pending.

## Independent instantaneous reference cases

Use all three complete Table2p368 soils (London,Dresden,Weald) and pin degree-to-radian conversion. Do not fill missing SanFranciscoBayMud constants. The oracle should use stdlib Cartesian matrices and an independent high-precision exponential reference or supplied spectral construction; it must not call the production DSL expm or share the production rate expression mechanically.

1. **NCL isotropic compression.** p=100kPa; e=exp(N)*(p/sigma_star)^(-lambda_star)-1; de=I/3. Expected sigma_rhs=(p/lambda_star)I,e_rhs=-(1+e). Repeat pressure scale with e recomputed on NCL. This distinguishes body2p from appendix6p.
2. **Hydrostatic expansion at arbitrary admissible density.** de=-I/3; density d=(1+e)/(1+ec). Independent scalar formula `dlogp/dv=c3/sqrt3*(d^c5-1+sqrt3*beta_kappa)` for v=|trace(de)|, and e_rhs=+(1+e). Do not equate pressure slope to-1/kappa for arbitrary e. At the specific Eq22p370 density ratio, first pin that source reference before asserting its kappa slope.
3. **Oedometric compression attractor.** de=diag(1,0,0): delta=-1,m=1.5,a=logK,normalizedP ratios Pyy/Pxx=Pzz/Pxx=K=1-sinphi. Test P,not forced current sigma ratio. Compare full rates independently at both isotropic and anisotropic SPD stress.
4. **Isochoric shear/noncoaxial.** Full symmetric de with zero trace and nonzero offdiagonal; arbitrary SPD sigma not coaxial with de; e_rhs=0. delta0,m0,Lambda=(lambda+kappa)/2; use Cartesian spectral/Decimal oracle. An entrywise-exp implementation must fail this case.
5. **Rotation/reflection covariance.** Rotate BOTH sigma,de by fixed Q, leaving scalarstate/parameters unchanged. Rotate stress_rhs back,compare all six components,compare e_rhs. Include oblique full3Drotation and reflection; zero spin means fixed change of coordinates,not a finite-spin path.
6. **Positive homogeneity and reversal.** For fixed parent,de: rate(c*de)=c*rate(de),c>0 across1e-3,1,1e3. For-de independently recompute delta,m,K,Lambda,beta,P; do not assume oddness. Preserve no mutation of supplied parent/parameters.
7. **Zero/nonzero hydrostatic limits.** Exact de0 yields0; approach each hydrostatic direction with traceless perturbations in multiple eigenspaces. Verify rates converge to declared branch and investigate directional derivatives separately.
8. **Rejections.** p0,e-1,invalidparameterdenominators,K0,operator-bound exceed,nonfinitevalues and derivative-only failures must return no usable rates; if evaluated through a material update,exact parent retained/no partial tangent. Exact construction of nearK0directions should retain actual binary64matrices rather than claim theoretical equality after rounding.

## Required acceptance gates before integration

- Exact source identity/bodyselection/sign/units independently reviewed; all four input parameters and fixed referencepressure explicit.
- Three Table2coefficient sets reproduce retained source algebra; body NCL slope exactly matches1/lambda to floating tolerance; appendix witness remains deliberately different.
- Independent instantaneous full3Drate cases and all branch/domain results retained with input/output hashes and oracle provenance. Strong relative-plus-absolute comparisons for small/cancelled rates.
- Python typed evaluator and generated double/Jet outputs agree within an independently set accuracy budget. Sourcezero/hydro derivative assumptions are documented separately from generic expm correctness.
- No hidden preparation/reset/state capacity changes. Exact failed-candidate isolation and rollback demonstrated when later integrated.
- Current native/Wasm operator evidence is cited only for its actual frozen corpus and checked API. It is not barodesy numerical verification.

After those gates, the next packet is an isolated legacy rate-schema model and independent isotropic finite-path convergence study: compressionNCL has p(v)=p0 exp(v/lambda),1+e(v)=(1+e0)exp(-v) under matching isotropiczero-spin stretching. A finite-step midpoint update is compared by refinement,not asserted exact; reversals and nearK0rejections follow. Public catalogue admission,experiments,finite-spin support and authorcode equivalence remain separate.
