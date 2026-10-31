# Hypoplastic interface 2016 — ingestion packet

Task ID: ING-hypoplastic-interface-2016
Owner/date: review_vw96, 2026-10-31
Scope: bounded source acquisition, kinematic/operator audit and proposed integration contract. Exact original-paper visual equation closure remains blocked; no executable model draft or admission.

## Identity and sources

The target is Stutz, Mašín and Wuttke (2016), *Enhancement of a hypoplastic model for granular soil–structure interface behaviour*, Acta Geotechnica11,1249–1261, [DOI](https://doi.org/10.1007/s11440-016-0440-1). The [publisher preview](https://link.springer.com/article/10.1007/s11440-016-0440-1) confirms identity and16February2016 publication; it does not expose the full equations. Select the fully rough HvWE branch, not AH or AHE, and do not merge roughness schemes.

The existing [paper-side source review](../../../paper/study/source_formulations/hypoplastic-interface-2016.json) had text-only author-manuscript access and no PDF receipt. Downloads filenames and the private paper-side source inventory were checked; no named Stutz/interface PDF was present. This is not a claim that every unrelated filename was identified by content. The [author-uploaded accepted manuscript](https://www.researchgate.net/profile/Hans-Stutz/publication/294700890_Enhancement_of_a_hypoplastic_model_for_granular_soil-structure_interface_behaviour/links/5af2a6880f7e9ba366498567/Enhancement-of-a-hypoplastic-model-for-granular-soil-structure-interface-behaviour.pdf) remains readable through web text extraction; direct download returned403 and screenshot retrieval failed. Its cover identifies acceptance20January2016. No exact bytes/hash or visual verification of its Eqs30–33 is claimed.

A new primary source is the author's university-hosted [2016 thesis](https://www.geotechnics.ifg.uni-kiel.de/en/publications/2016-hanshenningstutz.pdf), *Hypoplastic Models for Soil-Structure Interfaces – Modelling and Implementation*. The privately retained PDF SHA-256 is `52e1eb5b510844f1d4a230935dffc03f77df149189cd8e166c9039fa3bd977ed`. PDF pages98,100,106–108 (printed66,68,74–76) were rendered and visually inspected using the PDF skill. The thesis has its own notation and equation numbers. It corroborates the kinematics and reduced algebra; it is not an exact replacement or publisher-equivalence receipt for the journal paper. Copyrighted PDF, text extraction and renders are excluded from this deliverable.

The [2017 general conversion paper](https://doi.org/10.1006/j.compgeo.2017.02.010) and [fine-grained interface paper](https://doi.org/10.1002/nag.2561) are distinct, uninspected formulations here. A combined2016/2017 software distribution cannot establish exact2016 semantics. No vendor/author code was executed.

## Existing work and gaps

This packet preserves the untracked paper tree and all catalogue entries. It adds an exact thesis receipt, visual kinematic/operator locators, an independent algebra witness and a non-executable contract. `reviewed-inputs.json` pins the read-only existing dossier, protocol, triage and catalogue bytes. The original manuscript's constant-in-plane-stress wording remains in conflict with its separate evolution discussion. Thesis printed76 explicitly describes in-plane stress evolving separately. This supports carrying sigma_p as state; it does not by itself determine the exact2016 reduced evolution algorithm.

## Equations and schema crosswalk

| Locator | Quantity | Proposed representation | Evidence/limit |
| --- | --- | --- | --- |
| Manuscript30/32, text only; thesis5.1/5.2 printed66, visual | Stress matrix with diagonal sigma_n,sigma_p,sigma_p and shear12=tau_x,13=tau_z | Four local stress components in Pa | No general arbitrary six-stress claim |
| Manuscript31/33, text only; thesis5.3/5.4 printed66/68, visual | Stretching diagonal eps_n_dot,0,0; shear halves gamma_x_dot/2,gamma_z_dot/2 | Three independent supplied stretching controls | In-plane stretching zero does not imply in-plane stress constant |
| Thesis5.23–5.25, printed74, visual | Trace, determinant, squared norm | X1+2X2; X1X2²−X2(X3²+X4²); weights1,2,2,2 | Exact independent Cartesian invariant checks retained |
| Thesis5.27,5.32–5.34 printed74–75, visual | Identity, double contraction, action, dyad | Weighted reduced algebra | Source dot product needs separate review, not a generic full3D call |
| Manuscript11 text only; thesis5.5 printed68, visual | tan(gamma_i)=u_i/d_s | Slip in m, positive thickness in m, explicit strain measure | Do not silently replace tan(gamma) by gamma |
| Manuscript4.1 text only | Initialize sigma_p before shear; suggested Jaky relation | Preparation metadata and supplied persistent state | Exact ratio orientation, sign and preparation recipe unresolved |
| Manuscript2–10 text only; thesis5.3.1, not fully visually re-audited | VW96 mechanical host | Eight named parameters and density state e | Complete host factors/signs not frozen from this packet |

Source reduced order is `[sigma_n,sigma_p,tau_x,tau_z]`, with stretching order `[eps_n_dot,0,gamma_x_dot/2,gamma_z_dot/2]`. Atlas Mandel order is `[xx,yy,zz,sqrt(2)*xy,sqrt(2)*yz,sqrt(2)*xz]`. The local embedding is `[X1,X2,X2,sqrt(2)*X3,0,sqrt(2)*X4]`; it is not the source's four-vector norm. Source2016 names normal axis1=y,tangent2=x,tangent3=z; thesis changes global names to normalz/tangentsx,y. A schema must store an explicit orthonormal local frame instead of treating these labels as interchangeable global axes. Stress sign and objective frame transport need an exact source audit before execution.

Candidate persistent state is four stresses plus e, conditional on a confirmed host/evolution closure. The host's eight parameters are phi_c(rad),h_s(Pa),n,e_d0,e_c0,e_i0,alpha,beta (remaining units1). No arbitrary range, density projection, opening/recontact law, roughness clipping or singular isotropic continuation is invented. No full-history count is frozen when IGS or later revisions are selected.

## Independent checks and the reduced-product gate

`checks.py` runs100 exact rational assertions for reconstructed Cartesian trace/determinant/Frobenius contraction, weighted identity and stress power under engineering shear inputs. Three unittest groups pass. These check representation algebra only, not source stress rates, experiments or numerical integration.

A retained witness distinguishes printed thesis Eq5.31 from full Cartesian multiplication. For reduced X=[2,3,5,7], the printed reduced dot X·X is [78,34,25,35]. Squaring its Cartesian embedding gives22=34,33=58 and23=35: it leaves the equal-in-plane/zero23 subspace. This is an algebraic witness, not an admissible constitutive calibration state. The printed reduced product is a defined reduced operation, not automatically an error; neither replacing it by full3D multiplication nor projecting an arbitrary full3D host update is justified by this packet. Review its use in cubic invariants, tangential rotation, and the stress action first. The thesis's fully-rough continuum-equivalence discussion is source evidence, not an independently proved identity.

From the installed or staged packet directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 checks.py --check check-results.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_checks.py
```

`manifest.json` lists authored files and exact hashes. No private source bytes or bytecode are shipped. The current report contains no hidden compiled calls.

## Temporal integration and transactions

`integration-contract.json` separates source statements from project proposals. The law is an objective hypoplastic rate; no physical-time viscosity is identified. A dimensionless strain-path coordinate is a possible fixed-frame research driver, but external slip remains a length. A finite-slip adapter must preserve the declared angular relation: for fixed d_s, gamma_dot=(u_dot/d_s)/(1+(u/d_s)²). If thickness varies, its derivative also enters. This derivative is a conditional calculus consequence, not a verified2016 FE stretching algorithm.

CV prescribes normal stretching zero, CNL prescribes normal stress rate zero, CNS relates them through declared K_eps in Pa. Force/displacement or traction/displacement stiffness requires area/thickness conversion. For the explicitly chosen signed linear mapping eps_n=u_n/d_s and fixed thickness, K_eps=d_s*K_u; this is a project conversion, not an inferred source normal-displacement rule.

A future solver must copy traction, in-plane stress, density, slip/frame history as one trial state and commit only accepted steps. Local solve/domain/error-budget failure must roll back all of them. No sigma_p reinitialization at reversal or failure is supported. Evaluate all factors from the same trial state; unrecorded lagging is a distinct algorithm. Zero stretching gives zero material rate only on a regular finite branch; spin/contact/creep are not covered. The source delegates Euler stretching and Jaumann–Zaremba corrections to FE kinematics. No finite-spin transport, contact event law or consistent tangent is supplied here.

## Handoff and smallest next action

Source completeness: partial, exact2016 PDF and final/manuscript reconciliation remain open. Executable support: none added. Numerical verification:100 exact representation checks and3 tests only. Scientific admission: unchanged, not admitted.

Obtain/pin a readable exact2016 accepted or publisher PDF; visually verify Eqs30–33, operator26 and Section4.1; resolve sigma_p evolution and reduced-product semantics. Then audit inherited VW96 factors, density update and singular domains, with a fully rough fixed-frame supplied-host four-stress action fixture. Freeze source/case/domain policies before any common DSL implementation or compiled observation. An acquisition gap is sufficient for this bounded handoff, not for source-complete ingestion. No shared code or schema capability is implemented and no model count is promoted.
