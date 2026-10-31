# Terra Cotta / Terracotta 2024: Figure 1 ingestion handoff

Task: ING-terracotta-2024. Owner: ingest_terracotta. Date: 2026-10-31.
Scope: consolidate the available source-to-schema and physical-time contract; identify exact journal and external-history blockers. This is a bounded handoff, **not source-complete ingestion or scientific admission**.

## Identity and source receipts

Max Wiebicke and Itai Einav, *A simple hydrodynamic model for clay*, Journal of the Mechanics and Physics of Solids 192 (2024), 105789, [journal DOI](https://doi.org/10.1016/j.jmps.2024.105789). Immediate formulation: simplified Figure 1, fixed-axis triaxial invariants. Existing research ID: `terracotta-2024-fig1`; public discovery ID: `terracotta-2024`.

The [author implementation](https://github.com/MaxWiebicke/Terracotta-pq/tree/a4039d0124d8ff61e766f5201f44ddc163c4cff5) is pinned to `a4039d0124d8ff61e766f5201f44ddc163c4cff5`. Locally retained functions, main and equation image were read/hashed again; all three match the prior source audit. The equation image was visually inspected in this task. [source-receipts.json](source-receipts.json) records the private paths, complete hashes and access distinctions. No author code was executed or copied into this packet.

The complete journal PDF is still missing: every current Downloads PDF first page was searched using `pdftotext` for hydrodynamic/Wiebicke/Einav/105789, yielding no match. This is a first-page search, not proof that every unnamed archive contains no copy. Primary DOI and pinned GitHub/raw routes failed in the browsing tool; the [author-uploaded journal text](https://www.researchgate.net/publication/382467665_A_simple_hydrodynamic_model_for_clay) remains readable. It is not a page-image reconciliation. The [SSRN predecessor](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4699137) has a separate identity/version and must not substitute for journal pagination, defaults or Appendix numbering. Its landing page explicitly retains rights; the author repository's [MIT licence](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/LICENSE) applies to code, not automatically to journal figures or external experimental data. This packet redistributes no source images, PDF, author code or measurements.

## Existing work and what this adds

Read the existing [brief](../../models/terracotta-2024.md), [audit](../../models/terracotta-2024-source-audit.md), [transcription](../../models/terracotta-2024-transcription.md), [TC-01 reconciliation](../../models/terracotta-2024-tc01-reconciliation.md), [parallel review](../../reviews/parallel-terracotta-review.md) and [creep reference](../../TERRACOTTA_CREEP_REFERENCE.md). Existing evidence includes five prescribed-rate author-RHS histories, generic initialization, boundary/decay checks and a separate nine-run prepared-creep native/Wasm comparison. Those were **not rerun**. Their source/engine identities remain their recorded identities; this new receipt of current files does not renew historical compiled evidence after common-code changes.

This packet adds a single explicit temporal/transaction contract, current byte receipts, an operational source-gap list, and 17 independent scalar/rational algebra checks. It does not repeat or promote the prepared-creep study. Existing briefs contain dated statements preceding later accomplishments; follow the linked detailed dossiers rather than reading those early statements as current missing features.

## Equations and schema crosswalk

All expressions below were rechecked against the pinned author equation image; journal locators are inherited from the source dossiers and remain **journal-image pending**. Symbols K/G mean intrinsic coefficients, not constant tangent moduli. Compression is positive. Fixed x is axial, y/z equal radial, all shear zero. `Dv=tr(D)`, `Ds=2(Dxx-Dyy)/3` is signed; `stress=p I+q B`, `B=diag(2/3,-1/3,-1/3)`, so `stress:D=p Dv+q Ds`. Signed extension must not be replaced with a tensor norm.

| Source locator | Expression | Current schema / units |
| --- | --- | --- |
| Eqs23-24, Figure1 | `pe=phi^6*(K*ev_e^2+3*G*es_e^2)/2`, `qe=3*G*phi^6*ev_e*es_e` | derived pe/qe; Pa |
| Eq43 | `pc=p1*phi^Lambda` | derived pc; Pa |
| Eqs42,48,51 | `a=sqrt(eta/alpha)`, `b=-a*qe/(M^2*pe)`, `c=sqrt(eta/gamma)/(M*omega)+a/M^2` | derived a/b/c; 1/(K s); common 1/pc is outside matrix |
| Eq32, Figure1 | `(ev_e_dot,es_e_dot)=(Dv,Ds)-Tm/pc*[[a,b],[b,c]]*(pe,qe)` | four-state ODE, first two equations; 1/s |
| Eq36 p10, Figure1 | `Tm_dot=alpha*Dv^2+gamma*Ds^2-eta*Tm^2` | equation Tm; K/s; **unhalved** |
| Eq6, Figure1 | `phi_dot=phi*Dv` | equation phi; 1/s |
| Eqs29-31 | `pv=2*alpha*Tm*Dv/Gamma`, `qv=2*gamma*Tm*Ds/Gamma` | algebraic observables; Pa |
| Eqs37-38 p10, Figure1 | `pt=Tm^2/Gamma`, `p=pe+pv+pt`, `q=qe+qv` | observables, not persistent stress state; Pa |
| Eq54 p16; elastic stability / Onsager conditions | current model uses nonstrict ratio ordering, transport determinant and elastic stability | exact journal inequality/equality admissibility remains unresolved |
| Appendix B p26 | additional elastic thermodynamic pressure and modified transport coefficients | absent; separate formulation and source audit required |

Persistent scalars: `(ev_e,es_e,Tm,phi)`, units `(1,1,K,1)`; total accumulated strain belongs to loading history. Loading inputs are physical stage time in seconds and Mandel strain-rate tensor in 1/s. Current numerical scales/bounds are Atlas choices, not calibration confidence intervals.

Parameters: K=13e9 Pa, G=5e9 Pa, M=.73, omega=.6, p1=543e6 Pa, Lambda=10, alpha=gamma=6e5 K s, eta=150/(K s), Gamma=.001 K²/Pa. These are the named **rounded author-code kaolin preset**. Gamma=1 K²/kPa converts to .001 K²/Pa. The journal's reported rounded phi1=.267 implies `p1=1000/phi1^10` Pa, a distinct preset. Table1 p14 and Appendix C pp27-28 need image verification; the SSRN preprint has different displayed numbers and pagination and cannot close this gap.

Current guard policy: ev_e>0, pe/pc>0, 0<phi<=1, Tm>=0, transport determinant>=0, `K*ev_e²>=3*G*es_e²` and stress-ratio ordering. The phi upper bound is an explicit physical guard. Nonstrict equality may be singular under mixed control; current code acceptance is not evidence the source prescribes equality. No clipping, hidden temperature floor or extrapolation.

Initialization: at specified total P/Q, phi, Tm and incoming Dv/Ds, subtract pv/qv and pt first. Require pe>0 and real discriminant. Select positive stable root
`ev_e=sqrt(pe/(K*phi^6)*(1+sqrt(1-K/(3G)*(qe/pe)^2)))`,
`es_e=qe/(3G*phi^6*ev_e)`, then check every domain condition. This is an Atlas algebraic branch choice based on the author inversion, not a consolidation/preparation model. The generic [initialization recipe](../../../initialization/terracotta-2024-fig1-total-stress.json) already represents it. Changing parameters requires rerunning initialization; nonzero Tm total-stress initialization requires the incoming rate.

## Temporal integration and transactions

[temporal-contract.json](temporal-contract.json) separates constitutive requirements, author numerical choices, existing Atlas semantics and proposed next study. The material law is a physical-time ODE coupled to algebraic rate-dependent stress. Zero imposed strain rate gives `Tm_dot=-eta*Tm²` and generally nonzero elastic relaxation; it is not a no-op. A stress hold is an algebraic rate solve and generally creeps.

At a prescribed rate discontinuity, all four persistent states and accumulated strain are continuous. Total pressure/q can jump by `2 alpha Tm deltaDv/Gamma` and `2 gamma Tm deltaDs/Gamma`. Always retain left/right rate metadata; stress-controlled transition rates may be unavailable in the current driver. Under positive Tm, instantaneous total-stress inversion is `Dv=Gamma*(P-pe-pt)/(2 alpha Tm)`, `Ds=Gamma*(Q-qe)/(2 gamma Tm)`. At Tm=0 it is singular; no hidden regularization is authorized.

Transactions are Atlas software policy: pure stages use matching trial state/time/rate; Newton trials do not mutate committed history; failed output intervals restore their incoming state/strain/time, retaining prior committed samples and any valid committed entry transition. This is not an assertion of an author transaction API. Restart needs parameters, four states, accumulated strain, endpoint physical time and one-sided endpoint rate; a null-rate transition alone is incomplete. Existing backward-Euler step doubling/AD Jacobian is a numerical choice, not the author's BDF. Author differentiated viscous stresses use acceleration approximated with previous rate and outer dt; that outer partition is provenance for exact author-path reproduction.

## Independent checks and retained conflicts

Run `python3 -B docs/ingestion/terracotta-2024/checks.py`. [checks.json](checks.json) retains 17 passing checks: exact rational signed kinematics/work conjugacy, five 80-digit positive stable-root pressure/q reconstructions, outside-cone discriminant, positive-temperature hold capture/inversion, positive/singular rate Jacobians, SI conversion and distinct rounded presets. No Atlas, NumPy, SciPy or author imports; no native/Wasm calls or integration. These are algebra checks by an AI worker, not independent scientific authorship or a journal audit.

Confirmed code conflict remains: [TmRate lines139-146](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/code/Terracotta_functions.py#L139-L146) is unhalved; [mixed residual line301](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/code/Terracotta_functions.py#L301) halves it. The author image supports the unhalved equation. No corrected author branch was selected or run. The initial main.py line36 also adds Tm² to both stress entries without Gamma; its zero-Tm default masks this discrepancy. Preserve both findings.

## Handoff and next action

**Source completeness:** partial, TC-01 open. **Executable support:** restricted research draft already exists; no new integration. **Numerical verification:** this packet's 17 algebra checks only; prior named studies retain their own scope/identities. **Scientific admission:** unchanged; no full-3D, experimental or public timed-browser claim.

1. Obtain complete authorized journal PDF, or complete legible pages2,10,14,16,26,27-28 first, followed by pages containing Eqs23-24,29-32,42-43,48,51. Pin bytes and independently inspect Figure1, Eq54 strictness, Table1 and AppendixB/C. No source acquisition by unauthorized access or redistribution.
2. After source reconciliation, commission a **new end-to-end preparation/hold** study with independent full-path reference. Carry computed preparation state/strain forward, capture P/Q from the declared incoming rate at hold entry, retain one physical clock, freeze separate preparation/hold bounds before compiled observations. Do not reuse the frozen-preparation comparison as end-to-end evidence.
3. External source-matched histories remain absent: current five histories use an adapted author RHS boundary policy; nine creep runs use a separate Atlas mathematical reference. For exact author `integratePath` reproduction, pin source, environment, test type/durations/rates, outer dt and defaults; resolve temperature conflict in a separately hashed correction, retain unmodified results and refine outer partition. Do not silently relabel that correction as original source.
4. Browser timed presets and experimental clay comparison/reuse are separate tasks. Karlsruhe sand overlays do not validate clay. Current source does not justify general 3D, rotations, finite deformation or poromechanics. No immediate shared-schema change is requested: existing ODE, observables, explicit initialization and ordered component-control capabilities represent this bounded Figure1 contract.

Exact owned files are enumerated with byte lengths and SHA-256 in [manifest.json](manifest.json). Coordinator alone reviews, integrates and updates the task board. Integrating this consolidation must not mark source-complete ING-terracotta-2024 done while the above source/history blockers remain.
