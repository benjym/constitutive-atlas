# PM4Sand2D 3.3 — ingestion packet

Task ID: ING-pm4sand. Owner: review_sanisand. Date: 2026-10-31.

This packet inventories the available two-dimensional Version 3.3 manual and its integration contract. It pins both the June 2023 vendor copy and the author revision dated May 2024. It does not implement or admit the model. The equation ledger locates core Eqs 1–93, labels predecessor laws and calibration derivations separately, and preserves conflicts rather than selecting undocumented corrections. It is a bounded mathematical audit, not a loadable Atlas definition or a complete transcription of all calibration correlations.

## Identity and sources

Ross W. Boulanger and Katerina Ziotopoulou, *PM4Sand (Version 3.3): A Sand Plasticity Model for Earthquake Engineering Applications*, UCD/CGM-23/01. Selected source: [author May 2024 revision](https://ucdavis.box.com/s/op92sb4hxh9zzw8imfsvib16hjuepzuk), linked from the [author releases](https://pm4sand.engr.ucdavis.edu/pm4sand-files). Comparator: [vendor June 2023 manual](https://itasca-software.s3.amazonaws.com/udm-library/Boulanger_Ziotopoulou_PM4Sand_v3.3_CGM-23-01.pdf).

| Copy | PDF pages / bytes | SHA-256 |
| --- | --- | --- |
| Author: June 2023, revised May 2024 | 122 / 9,040,815 | `be3d7984f125f82ab51fa44ba088fd739342b80bb89bd3059f09ac1dabb3e0ea` |
| Vendor: June 2023 | 122 / 9,042,024 | `59b94cf0ccc02beccc078fd0c612904692fb4635f75b0fc16efa314eeccd763e` |

The cover, edition-history pages and printed p4/PDF9 of the author copy identify the October 2023 and May 2024 changes. The October 18, 2023 build fixes an error involving triangular single-overlay elements; May 15, 2024 adds the FLAC2D 9.10 build. The report describes simulations performed with FLAC 8.1 and asserts corresponding later-host results. These are author statements, not reproduced calculations. They do not establish equation-by-equation or DLL equivalence.

The source receipt records private paths, access URLs and hashes. Private PDFs, text extractions and rendered pages are excluded from this packet. Public availability does not establish redistribution rights or permission to reuse vendor implementation source. No DLL, author constitutive source or author driver was downloaded or executed. Printed pages 16–79 correspond to PDF pages 21–84; locators below use printed pages unless explicitly marked PDF.

The normalized extracted text of Tables 3.1–3.2, pp65–68, matches between the two copies; vendor pages were also visually inspected. This limited text comparison does not certify all equation glyphs or the entire report. Changed extraction pages and the exact visual-review coverage are retained in `source-receipts.json`. The author and vendor copies remain distinct source identities.

## Existing work and gaps

This extends [the version dossier](../../models/pm4sand-versions.md), [the prior manual audit](../../../catalogue/source-audits/pm4sand-manuals-2026-10-31.json), and [the parallel review](../../reviews/parallel-pm4sand-review.md). PM4Sand3D 1.0 has separate flow fragments and history inventories. None of its three-dimensional Lode, tensor or chronology laws is imported into this 2D packet.

The useful additions are the acquired author-revision receipt, explicit body/summary conflicts, a 2D equation crosswalk, a conservative retained-memory inventory, and caller-versus-subzone chronology. Full source closure is blocked by printed ambiguities and incompletely defined labels, even though both manuals are available.

## Equations and schema crosswalk

`equation-ledger.json` contains mathematical prose and source locators, not runtime DSL. `state-integration-ledger.json` records parameter units/defaults, memory roles, phases and numbered blockers.

| Source | Representation / units | Scope and remaining gate |
| --- | --- | --- |
| Eqs1–8, pp16–17 | `sym2` effective stress, Pa; tensorial strain; `p=tr2(sigma)/2` | In-plane double contraction weights shear twice. Displayed strain deviator uses `/3`, stress deviator `/2`; a generic 3D embedding is not established. |
| Eqs10–18, pp18–20 | relative density/state, `Mb`, `Md`, `M`, alpha and image tensors, dimensionless | `M=2 sin(phi_cv)`, with no 3D Lode substitution. Yield radius is `m/sqrt(2)`. |
| Eqs19–20,37–38; pp20–25 | true/previous/apparent reversal memory, dimensionless | Component extrema and true anchors differ. Zero-distance divisions and `<` versus `<=` need explicit source decisions. |
| Eqs21–35,86; pp21–24,37 | `G,K,Kp` Pa; plastic multiplier and `D` dimensionless | Stored zone coefficients enter the next subzone trial. Instantaneous consistency formulas alone are not the reported lagged algorithm. |
| Eqs39–55, pp26–29 | dilatancy and density-dependent contraction factors | Exact arcsine calibration and loose startup are separate; exact critical-state equality is omitted by startup branches. Intermediate Eq43–49 algebra remains calibration scope. |
| Eqs57–85, pp30–36 | fabric tensors, accumulators, pressure anchors, low-pressure branches | Body/summary fabric-sign and pressure-factor conflicts remain open. |
| Eqs87–92, pp38–39 | user-triggered postshaking mode, signed pressures, modulus multiplier | Body/summary exponent conflict; zero-fabric and `Mcur>=Md` divisions require lazy branch/domain policy. No inferred automatic creep. |
| Table3.1, pp65–66; Table3.2, pp67–68 | explicit host subzone/zone trial, preparation and commit phases | Ambiguous old/new snapshots remain; no hidden preparation may be inserted into material trials. |
| Tables4.1–4.3, pp76–79 | six primary plus 21 secondary inputs; diagnostic properties | Printed defaults are not universal admissible ranges. A property label is not proof of independent state. |

The body generally treats compressive effective pressure as positive. Startup and FLAC-specific postshaking expressions use negative compressive stresses, for example `sqrt(-po/pA)` and negative `psed0prime`. A declared sign adapter must cover every pressure/history field, not just negate the stress input. `phi_cv` is an external degree input but trigonometric expressions use radians. A 2D Mandel vector would be `(xx,yy,sqrt(2)xy)`; using an Atlas six-vector with a silent zero `zz` changes mean pressure.

### Parameter and domain requirements

The parameter ledger preserves printed defaults, their source locators and preparation roles. `DR_initial` differs from evolving density. Zero secondary input requests a default under the host interface (p77), so resolved parameters must be recorded separately from raw input and reset command. Dense/loose selections modify `nb`, `nd` and `Ado`; they must be frozen or updated only at source-defined preparation phases.

At minimum, evaluation must address positive body pressure, positive atmosphere/reference scale, `Q-log(100p/pA)` nonzero, `1-2nu` nonzero, positive `zmax`, square-root and arcsine domains, exponential overflow, nonzero CSR preparation denominator, and each active denominator in the ledger. The printed `CDR` default can reach zero near `DR_initial=.15`; no positive lower bound is supplied by that formula. Finite inputs alone do not establish a supported state. No speculative clipping or epsilon continuation is chosen here.

A conservative inventory lists nine full `sym2` records (27 scalar slots), 13 scalar retained/lag/preparation candidates, and 11 additional derived/cache records. This is not a minimal state count. The componentwise apparent extrema are not presumed trace-free. Some labels remain untyped or incompletely updated. Host subzone multiplicity, zone workspace and the separate parallel shear stress are additional requirements; increasing a generic state capacity would not resolve their lifecycle.

### Preparation and unresolved branches

Table3.2 starts from host stress. For compressive `sigma11<0`, it derives signed `po`, `pmin` and `pmin2`; for tensile `sigma11>0`, it replaces stress by a small isotropic compressive state. The printed table does not define `sigma11==0` or a complete mixed-principal-stress test. Density-dependent surfaces follow, with separate `xiR<0` and `xiR>0` formulas and no exact-equality clause.

The table conditionally projects an initial stress ratio outside `Mcut=max(Mb,Md)` and initializes alpha differently on the two sides. It then initializes the true reversal anchor using a `.9Mb` threshold and copies it into previous/min/max anchors. Equalities at both thresholds are omitted. Initial `G,K` are elastic, `Kp=100G`, `D=0`; fabric is zero while `zpeak=zmax/100000` and `pzp=po/100` are deliberately nonzero. `zxpPk=-zmax*po/50` is another retained regularizer. The printed `z:p` initialization is not a typed scalar/tensor definition, and `zalpha` evolution is not established here. These gaps must remain explicit in any restart layout.

## Temporal integration and transactions

Sections3.1–3.2, pp58–61 and Table3.1 describe an explicit FLAC update. Four triangular subzones and two overlaid meshes share corrected volumetric strains but different deviatoric strains. Each trial uses stored `G,K,D,Kp`; after subzone return, area-weighted zone quantities are formed, penalties applied, reversal classified, and new `D,Kp` computed for the **next caller step**. Fabric, surfaces and moduli then refresh. Steps11,16,17 do not uniquely establish all old/current/reversal-anchor dependencies. The phase ledger preserves that uncertainty.

A shear-only parallel elastoplastic element (p60) has its own stress, modulus `.01` of prepared moduli and a lower-bounded pressure-dependent strength. It cannot be silently removed from a homogeneous study while claiming vendor equivalence. The reported method does not use constitutive substepping. Global dynamic `dt` determines imposed increments; it is not evidence of intrinsic rate dependence or viscosity. `PostShake` is a user mode selected after shaking, not an elapsed-time event.

For Atlas, a proposed transaction must retain the entire committed parent: subzones, zone memory, resolved preparation/modes and parallel shear state. Every Newton or line-search candidate must start there. Only a successful whole caller publishes state; failure restores the exact parent. These are proposed integration requirements, not a claim that the source supplies a complete transactional specification. Internal adaptive subdivisions would create a separately defined numerical variant because caller-frequency refresh of lagged fields changes the path. Duplicate/zero loading needs a declared policy before it can preserve or advance memory. No physical tangent at reversal, pressure floors, projection boundaries or undefined ratios is asserted.

## Printed conflicts and independent checks

The machine ledger contains exact locators for PMS-01 through PMS-09. The most consequential are:

- Eq57, p30 versus Table3.1 step14, p66: `pos(-devpl)/D` versus `devpl/D` changes fabric-update sign during dilation.
- Eq64, p32: the literal positive-pressure expression has a pole at `p=pzp+pmin` and differs from its adjacent verbal activation description.
- Eq74, p35 versus Table2.1, p43: `pmin2` versus `pmin` changes the low-pressure dilation factor.
- Eq89, p38 versus Table2.1, p45: a squared versus linear pressure ratio changes the postshaking factor.
- Eq70, p34 versus Table2.1, p42: a negative-part guard is absent from the summary. It can coincide only within a restricted branch.

The inspected author pages preserve these conflicts; a newer cover is not a correction policy. By contrast, Eq61's denominator is `1+(2.5*pos(dtrue))^2` in both visually checked copies; no edition conflict is alleged for it.

Run `python3 docs/ingestion/pm4sand/check_packet.py` from the repository, or run the script by absolute path in this packet. Eleven bounded independent algebra groups replay exactly against `check-results.json`: 2D shear norm, 2D/3D distinction, frozen CSR, dense critical-state limit, pressure-scale conflict, postshaking exponent conflict, fabric sign conflict, literal pressure-factor pole, zero-distance reversal branch, default boundaries, and synthetic caller-lag partition dependence. The latter is explicitly a synthetic recurrence, not PM4Sand output. The dense limit follows l'Hopital's rule and does not select the missing exact-equality startup branch. No production DSL, compiled engine, author code or experimental comparison was used.

## Handoff and next bounded work

The manifest lists exact public files and local-relative hashes. Source completeness: **partial**. Executable support: **not added**. Numerical verification: **11 bounded algebra groups only**. Scientific admission: **not requested or changed**.

The smallest safe executable task is a source-located **2D yield/surface/elasticity fragment** with explicit supplied pressure, resolved `Mb/Md`, frozen CSR numerator and fabric accumulator. Test direct 2x2 matrix contractions against Mandel2, pressure/sign mapping, positive scaling and invalid domains. Keep it separate from a full model, host update or reversal implementation. Do not borrow PM4Sand3D flow laws.

Before a full material implementation, resolve PMS-01–09 with independently reviewed source decisions, pin the chosen manual and resulting research variant, type every retained field, establish subzone/zone/parallel-element scope, and specify old/new snapshots for every lagged/reset phase. Generic requirements are typed `sym2` support or an explicit plane adapter, parameter/preparation provenance, lazy active-branch evaluation, phase-scoped immutable snapshots, atomic multi-scope rollback and caller-versus-internal-step semantics. They are design requests, not authorization to alter shared code.
