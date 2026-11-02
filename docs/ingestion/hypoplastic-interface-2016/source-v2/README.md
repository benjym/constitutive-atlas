# Original 2016 interface law: source reconciliation v2

Task `SRC-interface2016-original-v2`, child of `MODEL-hypoplastic-interface-2016`. Source specialist `/root/hill_source`, 2026-11-02. Owned paths: this new directory and ignored `.local/private-sources/hypoplastic-interface-2016/source-v2/`. Historical packet, paper tree, definitions and shared integration files are unchanged. The coordinator continues [E0–E8](../DELIVERY.md).

## Identity, acquisitions and honest completeness

Target: Stutz, H., Mašín, D. and Wuttke, F. (2016), *Enhancement of a hypoplastic model for granular soil–structure interface behaviour*, Acta Geotechnica 11, 1249–1261, [DOI 10.1007/s11440-016-0440-1](https://doi.org/10.1007/s11440-016-0440-1). Select **HvWE at fully rough conditions**, not AH, AHE, an intergranular-strain extension, a finite-rotation host, the 2017 general conversion paper or clay interface formulation.

The old packet and paper-side source record were read first. Downloads and private-source filenames yielded no newly named original interface PDF. The existing thesis remained available at its historical private path. Its exact bytes were copied into durable assigned private storage and independently rehashed, preserving the original location and every historical receipt. SHA-256 remains `52e1eb5b510844f1d4a230935dffc03f77df149189cd8e166c9039fa3bd977ed`, 8,856,498 bytes. Author Hans Henning Stutz, *Hypoplastic Models for Soil-Structure Interfaces – Modelling and Implementation*, 2016; [university source](https://www.geotechnics.ifg.uni-kiel.de/en/publications/2016-hanshenningstutz.pdf). It is a distinct source, **not** an exact journal-PDF substitute.

New leads were checked rather than repeating the previously failed ResearchGate download. The author's [institutional publication list](https://web.natur.cuni.cz/uhigug/masin/bib/DMbib.htm) directs this paper to SoilModels. The linked [preprint record](https://soilmodels.com/download/stutz-h-masin-d-and-wuttke-f-2016-enhancement-of-a-hypoplastic-model-for-granular-soil-structure-interface-behaviour-acta-geotechnica-11-no-6-1249-1261-preprint/) requires login. Kiel's [publication list](https://www.geotechnics.ifg.uni-kiel.de/en/publications) links the publisher preview. Searches of other institutional hosts did not reveal a new exact PDF. A newly found [Scribd mirror](https://www.scribd.com/document/401598931/app1) exposes publisher-pagination text and confirms the same contradictory statements; its uploader is not an author and its raw PDF was not obtained. No login/paywall was bypassed. The mirror's AI-generated title/summary is not used as scientific evidence. Its displayed title page identifies the original DOI, authors, acceptance 20 January 2016, publication 16 February 2016 and publisher pagination. This remains text-only corroboration, not visual equation verification or a trusted accepted-manuscript provenance chain.

[receipts.json](receipts.json) pins the retained thesis and three public HTML acquisitions with exact byte hashes. All raw HTML, PDF and renders remain private; no redistribution license was established. No author contact, payment, vendor execution or new source binaries were used. Acquisition status: **new durable thesis retention and corroboration, but no exact original/accepted article PDF acquired**. A coherent fully rough inherited-host realization is now source-supported, with explicit print reconciliation below. Exact-2016 visual verification remains an independent acquisition gap.

## Visual reading and explicit inherited-host reconciliation

Applied the PDF skill. Rendered and visually read thesis PDF pages **102, 107, 108**, printed **70, 75, 76**. Also visually inspected the retained original von Wolffersdorff (1996) PDF pages **2, 12, 13**, printed **252, 262, 263**. Exact bytes, render locators and hashes are in [resource-receipt.json](resource-receipt.json). Original 1996 identity: *A hypoplastic relation for granular materials with a predefined limit state surface*, Mechanics of Cohesive-Frictional Materials 1, 251–271, [DOI10.1002/(SICI)1099-1484(199607)1:3<251::AID-CFM13>3.0.CO;2-3](https://doi.org/10.1002/(SICI)1099-1484(199607)1:3%3C251::AID-CFM13%3E3.0.CO;2-3). This is an explicitly referenced inherited source, not a replacement pretending to be the 2016 article.

The 2016 text says its fully rough interface uses the original host with the same eight material parameters and gives identical oedometer/simple-shear responses. That statement supports inheriting the complete 1996 host while changing the reduced operations and loading restrictions. The following **named typographic reconciliation** is materially stronger than an arbitrary dimensionally plausible repair:

| Printed issue | Primary inherited-source resolution | Status |
| --- | --- | --- |
| Thesis5.7/journal2 puts fs outside, while5.8/journal3 and5.9/journal7 already contain fs/fd | Original1996 Eq40 uses one fb*fe multiplier and one fd nonlinear multiplier. Use normalized L0/N0 with fs outside, or dimensional L/N once; these are algebraically the same | Explicit repair; literal duplicated-factor substitution is rejected |
| Thesis5.9 has a*F*(That+That*) | Original1996 Eq40 has exactly a*F*(That+That*) | No N-weighting ambiguity; earlier worker concern was incorrect and is withdrawn |
| Thesis5.13/journal10 omits minus in fractional pressure power despite compression-negative stress | Original1996 Eq43 uses exp[-(-trT/hs)^n], consistently with Eq46 and thesis5.12 | Explicit inherited pressure-sign repair |
| Interface section does not separately state the complete density ODE | Original1996 Eq2 explicitly gives edot=(1+e)trD with extension-positive D | Inherited primary closure is available; not a guessed conservation substitute |

[RECONCILIATION.md](RECONCILIATION.md) states the complete proposed realization and correction history. Full host equations can therefore be specified without an unresolved N-factor or density-law gap. An independent reviewer must assess this exact inherited/reconciled identity; calling the inconsistent 2016 print verbatim executable would remain false. Exact journal-page visual verification is still outstanding, and no executable record or scientific approval is created here.

## In-plane stress, preparation and operators

The source's enhanced stress vector carries four entries, local `[sigma_n,sigma_p,tau_x,tau_z]`, and the stretching vector has `[Dn,0,gamma_x_dot/2,gamma_z_dot/2]`. In-plane stretching vanishes; in-plane stress is not generally equal to sigma_n. Thesis printed76 explicitly permits sigma_p to evolve separately during continued shear and identifies the same host parameters. The original text mirror's p1253 calls the in-plane components constant, whereas p1254 discusses separate evolution and Section4.1 introduces sigma_p as an additional initialized state. Context strongly supports a dynamic in-plane state, but this is an interpretation requiring explicit reconciliation; zero in-plane stretching alone does not mean zero stress rate.

Section4.1's initialization-before-first-shear and suggestion of a Jaky estimate are not a complete stress preparation recipe. Exact orientation, sign, any stress ratio and the actual specimen preparation must be supplied rather than guessed. An admissible initial sigma_p cannot be recalculated from sigma_n after each step or reversal. No state projection or reset law was found. No universal starting specimen or material parameter set is asserted.

The reduced embedding is

```text
E(X) = [[X1,X3,X4],[X3,X2,0],[X4,0,X2]],
Mandel E(X) = [X1,X2,X2,sqrt(2)X3,0,sqrt(2)X4].
tr_r(X)=X1+2X2,
X:Y=X1Y1+2X2Y2+2X3Y3+2X4Y4.
```

The printed reduced dot operation (journal26/thesis5.31) is a defined operation, not ordinary Cartesian multiplication. The old witness `X=[2,3,5,7]` still gives `[78,34,25,35]`, whose embedding differs from `E(X)^2`. Nothing in this packet rewrites that historical true observation.

There is, however, an important **new scalar identity**. For either cubic association,

```text
tr_r((X dot_r X) dot_r X) - tr(E(X)^3)
 = tr_r(X)*(X3^2-X4^2),
tr_r(X dot_r (X dot_r X)) - tr(E(X)^3)
 = tr_r(X)*(X3^2-X4^2).
```

The Lode numerator uses `X=T_hat_star=T/tr(T)-I/3`, whose reduced trace is zero. Consequently its cubic trace agrees exactly with the Cartesian cubic trace despite intermediate product nonclosure. This resolves the **specific scalar Lode-cubic nonclosure question**; it does not authorize replacing the reduced product in every expression or resolve the isotropic normalized-direction singularity.

Independent [check_reduced_cubic.py](check_reduced_cubic.py) uses exact rational arithmetic and Cartesian matrix multiplication, with no Atlas/compiler imports. It verifies both general defects, zero-trace equality, a rational tangential rotation, and the original nonclosure witness. [cubic-results.json](cubic-results.json): **702 exact checks pass**, zero compiled calls. Reproduce:

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/source-v2/check_reduced_cubic.py
```

## Source-to-v0.3 crosswalk and conditional capability assessment

Read current schema and formulation contract, including controlled-path ODE support. No JSON model is authored by this source-only specialist. The inherited/reconciled host identity is explicit in RECONCILIATION.md; the original-article visual receipt remains open.

| Required quantity | Source support / proposed mapping | Remaining condition |
| --- | --- | --- |
| Mechanical state | Four local effective stresses, Pa; void ratio e, dimensionless | Inherited host/density closure specified; no six independent bulk-stress claim |
| Material parameters | phi_c rad, hs Pa, n/ed0/ec0/ei0/alpha/beta dimensionless | Parameter names/roles known; source-backed admissible/numerical ranges and exact default specimen not frozen |
| Geometry | Positive shear-zone thickness ds, m; local normal and two tangents | Fixed explicit aligned local basis only; distinguish geometric contact thickness |
| Loading | Normal stretching and two shear stretching controls; CV/CNL/CNS are distinct tasks | Normal strain/displacement map, shear-angle versus engineering-strain meaning and stiffness basis must be explicit |
| Objective rate | Objective stress rate, host-delegated Jaumann–Zaremba correction in original Section4.1 text | Zero-spin fixed-frame restriction can remove transport requirement; finite rotation is unsupported |
| Tensor/sign | Source local vectors with physical shear; explicit Mandel output embedding above | Source stress is effective; sign conversion must apply consistently to stress, stretching, density and pressure functions |
| Initial state | Sigma_p initialized before first shear, density and initial traction required | Jaky suggestion is not a unique preparation prescription; explicit supplied admissible state preferred |
| Time | No intrinsic viscosity identified in selected fully rough host | Dimensionless path parameter is possible; never relabel as physical-time creep |
| Events | Reversal changes loading; no source reset found | Opening/recontact, detachment, variable roughness, changing basis/thickness and thermal effects require separate laws |

It is premature to declare a compiler/kinematics gap merely because the source is an interface. For the conditional host structure `L0=c1*I+c2*T_hat⊗T_hat` and `N0=c3*T_hat+c4*T_hat_star`, weighted reduced identity/dyad contractions agree with the embedding. The trace-free Lode cubic agrees by the identity above. With stretching `D22=D33=D23=0` and stress `T22=T33,T23=0`, the embedded constitutive rate preserves that stress subspace. Thus a **fixed-local, no-spin, restricted Cartesian embedding** may legitimately fit current `small_strain_3d` controlled-path ODE mathematics with explicit constraints. This is not general full3D bulk equivalence, arbitrary frame covariance, a contact host or finite-rotation permission. It is a conditional algebraic representability finding, not execution support or a frozen approved formulation.

An eventual `path_ode` candidate could store four scalar local stresses plus e and bind a symmetric Pa effective `stress` observable through E. Required controls and derivative channels must use their actual units (dimensionless strain or m slip), be sampled together and retain full start/end controls in restart context. Define `frame=fixed_spatial`, objective rate `none` only under the disclosed zero-spin aligned-frame restriction. Persistent local component states should use `fixed_components` semantics; embedding as a spatial output does not invent a transport rule. Current schema scalar/sym capacity is sufficient for five states, but exact controls, material domains, source stress signs and profile claims must be resolved first. If a generic interface profile or host semantics are subsequently required, coordinator assigns that separate work; this packet does not modify shared code.

## Transactions and independent next study

Evaluate all factors from the same stage stress/density; no unrecorded lagging. Copy local stresses, e, coordinate, parameters and complete control context for every trial. Commit only a fully accepted advance. Any source-domain violation, failed mixed normal control, exhausted error/iteration budget or nonfinite trial rolls back the whole parent, including control/slip history. Reversal does not reinitialize sigma_p or e. Holds produce zero material rate only after every required factor is finite on a selected regular branch; they cannot be used to mask 0/0 constitutive definitions. No creep is inferred. No FE tangent is provided by a source rate law alone.

The old angular slip relation `tan(gamma_i)=u_i/ds` must remain distinct from infinitesimal engineering shear and from the symmetric velocity gradient used in Section4.1. For constant ds, differentiating that exact scalar relation gives `gamma_i_dot=(u_i_dot/ds)/(1+(u_i/ds)^2)`; this conditional calculus does not establish the FE algorithm. Variable ds adds another derivative. CNS in stress/strain units uses Pa; a displacement stiffness uses Pa/m and needs thickness and sign conversion, or area if force-based. Freeze these as part of any comparison rather than treating all CNS labels as identical.

The smallest useful next numerical study after source closure is a source-host four-stress rate fixture with unequal sigma_n/sigma_p, nonzero both shears, explicit e and admissible pressure. Compare reduced source action against independently formed embedded Cartesian scalar invariants and vector action, then fixed-frame CV/CNL/CNS paths with step refinement, domain rejection, full-state rollback/recovery and all-state restart. Freeze policy and independent references **before** compiled observations. Do not run such a fixture using a silently repaired host and label it original2016 verification.

## Public profile, status and handoff

[profile-draft.json](profile-draft.json) supplies a source-backed reading-only profile with provenance and no executable instructions or defaults. [PROFILE_AUDIT.md](PROFILE_AUDIT.md) records its scope and the existing availability prose issue. Shared profile integration and runnable examples remain E6–E8 coordinator work.

Source completeness: a complete **explicit inherited/reconciled fully rough fixed-frame realization is proposed**, but exact2016 original/accepted visual verification remains incomplete. Acquisition: durable thesis and new receipts retained; public leads exhausted. Executable status: no model or generic capability added. Numerical verification: 702 exact representation assertions only; old 100 checks remain historical. Scientific admission: unchanged, no independent review or approval. No builds, compiled calls, author binaries, shared edits, commits, messages to authors or remote release actions.

Smallest unblock: obtain the exact original/accepted PDF through the named lawful author/SoilModels/institutional route, or a normally public visually rendered publisher-document mirror, and visually verify journal Eqs2–10,26,30–33/Section4.1. Then independently review the disclosed inherited-host reconciliation and dynamic in-plane state interpretation. The exact stress preparation and selected normal/slip controls must be frozen for any executable example. The parent owns the source decision and full-delivery ledger. A completed bounded acquisition report does **not** close the source-complete ingestion task or umbrella.
