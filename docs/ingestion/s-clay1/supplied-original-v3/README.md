# S-CLAY1 — original journal source and complete candidate

Task SRC-s-clay1-original-v3 / IMPL-s-clay1-candidate-v3; coordinator /root, 3 November 2026. This additive packet resumes MODEL-s-clay1. The [delivery ledger](../DELIVERY.md) tracks E0–E8; this packet alone is not website delivery.

## Identity and sources

Wheeler, Näätänen, Karstunen and Lojander (2003), *An anisotropic elastoplastic model for soft clays*, Canadian Geotechnical Journal40,403–418, [DOI10.1139/T02-119](https://doi.org/10.1139/T02-119). The supplied filename says2011 but the readable title page, DOI, pagination and copyright identify the published2003 original. [Receipt](source-receipt.json) binds all800632bytes, SHA2561923aff43b80f14970dec624deb8f78b09635f419adbf71d797fa0a1a4169511. Copyright NRC Canada; retain personal-use original privately, never package it. No supplied code or binary is executed.

Root read complete extracted text, including all16pages/appendix/table/discussion sections, and visually inspected PDF3/15/16 to resolve equation glyphs. Separate source reviewer independently visually inspected all16pages. The AppendixA12 positive-part brackets are present; extraction had obscured them. A6 makes the deviatoric plastic strain scalar a nonnegative norm. The original source therefore closes SC-SOURCE-01.

## Existing work and gaps

Earlier [original gap packet](../README.md), [presentation packet](../delivery-v2/README.md), and its independent partial review remain immutable. Their missing-source statements describe the earlier checkpoint. No later S-CLAY1S, destructuration, creep or modified yield surface is substituted. The present complete constant-M law is a source-defined option (p404; original examples pp407/413 use oneM); optional shifted-Lode-angle interpolation is not specified as a unique function and is not claimed.

## Equations and schema crosswalk

Target v0.3, [candidate](candidate/s-clay1.json). Let p=trσ′/3, s=devσ′, A=deviatoric fabric αd, a²=3A:A/2, t=s−pA. Mandel order xx,yy,zz,√2xy,√2yz,√2xz; compression positive, effective Cauchy stress Pa. Fabric is dimensionless, trace zero; full source fabric is I+A with trace3. Changes of principal directions are representable with all six fabric components; finite spin/objective transport is not inferred.

| Original locator | Complete law | Candidate / units |
| --- | --- | --- |
| p404 Eq1 | K=vp/κ; G=3K(1−2ν)/(2(1+ν)); isotropic elasticity | K,G, stress residual /Pa |
| pp417–418 A1–A10 | F=3t:t/2−(M²−a²)(pm−p)p | yield_dim /Pa²; yield_scaled=F/p_ref² |
| p404 associated flow, p418 final paragraph | dεp=dl ∂F/∂σ′ | γ=p_ref dl; flow_dev=3t; flow_volume=2M²p−3s:A−(M²−a²)pm |
| p405 Eq4, p418 A11 | dpm=vpm dεvp/(λ−κ) | pm /Pa |
| pp405/408 Eqs5,7–9; p418 A12–A14 | dA=μ[(3s/(4p)−A)〈dεvp〉+β(s/(3p)−A)dεdp] | fabric /1; dεdp=√(2 devdεp:devdεp/3) |
| p409 preparation, pp411–414 calibration | σ′,v,pm,A initialize state; λ,κ,M,ν,β,μ material constants | explicit initialization,15 total components incl temporary γ |

λ and κ are slopes of specific volume against natural logarithm of pressure (not log10 indices). λ>κ>0. ν lies in(−1,.5); M>0; μ,β≥0. Source gives no universal engineering envelopes: JSON bounds are input safeguards, not a scientifically qualified parameter range. p_ref is solely numerical scaling. v>1, p>0, pm>0, a²<M² and traceA≈0 define this candidate domain; no pressure floor or fabric cap. Initial yield F/p_ref²≤1e−8. Numerical tolerances are distinct from exact source equalities. Parameter μ=0 permits frozen fabric as limiting mathematical case, not isotropic full-model equivalence.

The demonstrator uses original p413 λ=.44,κ=.04,M=1.1,ν=.2,β=.67,μ20 and Table4 CAD2251 v3.46,pm17.6kPa. Its stress[20,12.5,12.5,0,0,0]kPa is an Atlas illustrative interior state, NOT the measured start of CAD2251; A=diag(.28,−.14,−.14) embeds source α=.42. Neither this combination nor demonstrations assert experimental reproduction. A measured stress/volume/yield size/fabric and compatible history must replace it for a specimen.

Eq13 αK0=(ηK0²+3ηK0−M²)/3 and Eq14 β=3(4M²−4ηK0²−3ηK0)/[8(ηK0²−M²+2ηK0)] approximate NC/lightOC one-dimensional preparation when plastic strains dominate. They are not generic initialization identities. HeavyOC unloading can rotate fabric. μ is fitted to tests with significant rotation; pp412/416 suggest10/λ–15/λ as an estimate, not an exact constraint. Presentation parameter heuristics do not override original journal calibration.

## Temporal integration and transactions

The source is rate independent, not a physical-time creep law. Its p413 implementation uses tiny stress increments/compliance(Eqs15–16) to reduce yield drift; no tolerance or trial lifecycle is specified. Atlas instead uses a fully implicit endpoint residual with total strain increment de, solved simultaneously for σ′,A,v,pm,γ. Every stiffness and flow direction is evaluated at the endpoint. Plastic strain increment is γ∂F/∂σ′/p_ref, with gradient of dimensionalF. The normalized yield is used only for complementarity.

Atlas finite-step choices: v=v_n exp(−trde), pm=pm_n exp(v dεvp/(λ−κ)); fabric uses endpoint A12 with positive volumetric part and nonnegative deviatoric norm. These converge to the source differential laws under refinement. Associated stress gradient expands to flow_dev=3(s−pA) and tracegradient=flow_volume. The Fischer–Burmeister residual √(γ²+y²)−γ+y=0 enforces γ≥0,y=F/p_ref²≤0,γy=0. γ is temporary, reset per solve/subincrement; it is not accumulated plastic strain.

No physical clock, strain rate, hold relaxation, external pore pressure or tensor spin is supplied. An exact zero increment should preserve all persistent state; a hold cannot cause creep. Loading/unloading use the same complementarity law. Source includes dilation with its positive-part rotational protection; this branch is retained though dry-side predictions are scientifically weak. No reset/event is required for this law. Common runtime transactional failure must preserve the full parent state; all mixed-control trials restart from that parent. Restart needs all14 persistent components and zero temporary γ, matching parameters and complete control history. AD uses existing zero-norm generalized derivative and max branch atzero; no smooth regularization is introduced. A consistent material tangent/FE host is not a public claim. Subdivision changes a finite implicit update, so convergence must be checked rather than assuming one large increment equals several small ones.

## Public profile draft

[Profile draft](public-profile-draft.json) supplies source-backed behaviours, six material-parameter meanings, preparation and limits. Runnable exploration prose will be installed only after the named experiment actually qualifies. No public availability claim is created by the candidate.

## Independent checks and next handoff

[Prospective gates](VERIFICATION_PLAN.md) are frozen before compiled observations. Independent original Eq15–16 reference is a separate agent deliverable, not backend parity. Structural loading and ordinary compiler generation currently pass; zero-load interpreter residuals vanish. Native/Wasm, all-nine agent approval, atlas/profile/browser and live delivery remain to be performed. No generic capability change has been shown necessary by this transcription;15 scalar components fit32. Reassess actual execution rather than inventing a kernel or weakening a gate.
