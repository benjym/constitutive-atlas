# S-CLAY1 — full-delivery source work, 2 November 2026

Task MODEL-s-clay1 / SRC-s-clay1-complete-v2; coordinator /root. Full E0–E8 assignment, exact Wheeler, Näätänen, Karstunen and Lojander2003, *An anisotropic elastoplastic model for soft clays*, Canadian Geotechnical Journal40(2)403–418, [DOI](https://doi.org/10.1139/t02-119). Original ingestion/metadata packet in ../README.md remains unchanged. [Full ledger](../DELIVERY.md), [complete checklist](../CHECKLIST.md).

## Identity and sources

Original journal PDF still missing. Four current/legacy publisher routes return403. Strathclyde explicitly reports no full text, Chalmers/Aalto expose metadata, and fresh OpenAlex/SemanticScholar records report closed access with no PDF.24top-level Downloads PDFs were first-page screened using Poppler; no target title/DOI found. Personal subdirectories were excluded. Fresh responses, failures, exact private paths and SHA256 are in acquisition-v2.json; screening in downloads-screening-v2.json. Source acquisition does not authorize author contact or access-control bypass.

New readable primary supporting source: Minna Karstunen, *Modelling plastic anisotropy and destructuration — S-CLAY1 and S-CLAY1S models*,2003presentation hosted by [CRISP](https://www.mycrisp.com/cugm2003/m-karstunen.pdf),16PDFpages/two slides per page. Visible presenter is Karstunen, University of Glasgow; PDF internal Author metadata is Amir Rahim and Title CRISPMK-2003.ppt, creation26September2003. Record both facts; PDF metadata is not scientific authorship. Its bibliography #7 changes the journal title and omits Lojander while retaining volume/pages, so institutional journal records establish the canonical publication identity. This is a separate presentation, not the journal original or an accepted manuscript.

Raw PDF/HTML/API responses stay in ignored .local/private-sources/s-clay1/delivery-v2/. No redistribution permission established for the slides; link/hash rather than publish bytes. Text extraction loses square-root glyphs. Coordinator visually inspected PDF2–5,8–9; source convention below follows images, not ambiguous extracted glyphs. Independent review has its own inspected-page record.

## Equations and schema crosswalk

v0.3 schema and FORMULATION_CONTRACT.md were read; no executable model record is created from an incomplete law. Notation: p is mean effective stress, s its deviatoric symmetric tensor, A the deviatoric fabric, pm yield-size stress. M and A are dimensionless. Presentation tensor order is xx,yy,zz,xy,yz,zx with sqrt(2)-weighted shears; any future transport must explicitly map repository ordering.

| Presentation locator | Observed relation | Source/schema status |
| --- | --- | --- |
| PDF2 lower | F=(3/2)(s−pA):(s−pA)−[M²−(3/2)A:A](pm−p)p=0 | Yield geometry, stress²; source-backed presentation equation, journal locator unavailable |
| PDF3 upper | p=tr(sigma')/3; A=alpha−I, tr(alpha)=3; sqrt(2)-weighted symmetric shear components | Deviatoric trace zero; not raw engineering-shear storage |
| PDF3 lower | dpm=v pm/(lambda−kappa) dεvᵖ | Size hardening; full elastic/compression/strain convention still needed |
| PDF3 lower | dA=mu[(3eta/4−A)⟨dεvᵖ⟩+beta(eta/3−A)dεdᵖ], eta=s/p | Distinct3/4 and1/3targets; exact shear increment definition and Macaulay convention need original confirmation |
| PDF5 lower | F=(q−alpha p)²−(M²−alpha²)(pm−p)p | Signed triaxial geometry; no reduction of the full delivery assignment to this equation |
| PDF8 lower | alpha initial inclination; beta proportion constant; mu rotation rate; alpha/beta estimated via friction angle; mu heuristic tied to lambda_K0 | Explicit calibration equations absent; no numeric defaults inferred |
| PDF9 upper | Cross-anisotropic A=[−alpha/3,2alpha/3,−alpha/3,0,0,0], alpha²=(3/2)A:A | Source-backed initial orientation form, not a complete preparation procedure |
| PDF9 lower | Formal elastoplastic tangent uses separate F and Q, elastic matrix De and hardening H | Does not establish Q=F, elastic moduli, active-set/finite update or failed-step semantics |

Instantaneously setting A=0 recovers MCC yield geometry; rotational hardening can subsequently create fabric. This is not proof that the evolving model reduces to MCC without further parameter/history conditions. S-CLAY1S bonding/destructuration equations shown elsewhere are excluded from this original S-CLAY1 assignment.

Candidate parameters/state/input inventory remains incomplete: visible symbols M,lambda,kappa,mu,beta and initial alpha/pm/v do not establish every independent parameter or admissible interval. Elastic Poisson ratio appears in a presentation benchmark but its complete constitutive definition must be sourced. No triaxial specimen calibration, OCR/size consistency, density initialization or off-axis orientation default is invented.

## Temporal integration and transactions

The observed plastic differential hardening relations alone do not settle the complete original time/kinematic/spin contract. No creep term is transcribed. Source stress is effective; source strain and stress sign conventions, precise plastic shear measure, associated flow, elasticity and general rotation handling still need a complete governing source.

A future Atlas discretization must explicitly declare fixed-frame/small-strain scope, complete current/committed stress+fabric+size+volume, loading/unloading/complementarity, zero/hold/reversal, simultaneous residual versus rate update, control history, parent-increment rollback/recovery and replay semantics. These are host requirements, not claims about a missing original algorithm. No schema capability gap is asserted before the complete law establishes one; no model-specific handwritten kernel is proposed.

## Public profile draft

public-profile-draft.json provides source-backed reader prose and local per-claim provenance. It explains directional yielding, evolving fabric and the separate structured-clay variant. It supplies no invented parameters or runnable example and explicitly says the original S-CLAY1 public laboratory is unavailable. Existing web profile is reading-only; this new draft is not integrated into shared web data or presented as E6 completion.

## Independent checks

ALGEBRA_POLICY.md was written before check_algebra.py ran.110exact Fraction assertions check tensor/triaxial yield equality, instantaneous isotropic geometry, intercepts, two exact inclined-ellipse points and cross-anisotropic trace/invariant. No production expressions, integrator or compiled model exist; these algebra identities do not verify elastic response, evolution integration, original-journal fidelity, calibration or predictive accuracy. Command: python3 docs/ingestion/s-clay1/delivery-v2/check_algebra.py. Result: algebra-result-v1.json. Original packet check_packet.py still passes its four metadata-only groups unchanged.

## Handoff and blocking source gate

SC-SOURCE-01 remains open: obtain the full exact2003journal paper, all403–418pages including equations, elasticity/flow, parameter definitions/calibration and preparation. An author manuscript may close it after explicit version reconciliation. A later S-CLAY1S/creep/alternative yield law is not an interchangeable source. Separate source review is in independent-review/; no E5 decision is manufactured.

Source partial; executable absent;110source-geometry algebra checks only; scientific approval absent; existing catalogue reading profile is not runnable delivery; E2–E8 remain unfulfilled. Coordinator retains the full assignment and resumes on a complete governing source. Private originals and new evidence are retained for resumption; no worktree/build/package/preview or remote action was created.
