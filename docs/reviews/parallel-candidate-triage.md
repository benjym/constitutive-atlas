# SoilModels candidate acquisition and transcription queue

Prepared 2026-10-31. Read-only triage of the retained 2026-10-30 directory snapshot, catalogue candidates, source receipts, research dossiers, and local source inventory. No new web verification, equation admission, builds, native execution, or independent scientific-review completion is claimed. Priority below is a proposed engineering order, not a scientific ranking. Terra Cotta and both PM4Sand identities are intentionally excluded because separate agents own them.

## Coverage and practical order

The snapshot has 13 main directory entries. Excluding PM4Sand leaves 12 entries mapping to 16 atlas identities: 14 non-executable candidates plus the existing public VW96 and IGS97 formulations (transcribed and draft, respectively). Clay-2005 is an additional dependency/lineage candidate, not a separate mapping in this snapshot. Do not count an extension, family page, release placeholder, or reduced interface law as an admitted new 3D formulation.

Recommended first work packets:

1. **Close SANISAND's source/algorithm decision**, building on the original paper and substantial research implementation already present. Avoid another broad OpenSees build.
2. **Acquire a source batch for clay-2013, clay-2014 and clay-barodesy-2017**, then extract clay-2013 and barodesy independently. These offer comparatively direct tests of the existing scalar/symmetric-tensor rate-law representation; that compatibility remains a hypothesis until equation inventory.
3. **Acquire generalized-IGS-2024 and ISA's exact 2020 source**, and define host/overlay pairings before coding. Reuse existing IGS history checks only when equations justify it.
4. **Source-screen EMC and PM4Silt in parallel**; their numerical/capability decisions should precede transcription.
5. **Extract HCA's full algorithm from its already available manuscript** and design a distinct cycle-count driver. Do not add it to the instantaneous strain-path API.
6. Interface, multilaminate, thermal cycles and VIBE should first produce bounded capability/source records. Their distinct contracts justify separate implementation projects after sources are pinned.

## Candidate queue

### A1 — SANISAND-2004 (`sanisand-2004`)

**Identity:** Dafalias & Manzari (2004), *Simple Plasticity Sand Model Accounting for Fabric Change Effects*, Journal of Engineering Mechanics 130(6), 622–634; [DOI](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130:6%28622%29). Preserve original-paper identity separately from OpenSees's pinned implementation and Atlas's fixed-memory / parent-reset backward-Euler research variants.

**Available:** Original PDF in Downloads, pinned in `catalogue/source-audits/original-papers-2026-10-31.json`; original-equation, initialization, limit and integration audits; two research JSONs; fixed-memory, reset, transaction and mixed-control evidence. The manifest's “full original-paper extraction pending” wording predates the current partial extraction and should be reconciled, without closing its remaining gaps.

**Missing/decision:** Canonical first-yield and reversal/initialization semantics, complete matching reference histories, and reconciliation of source continuous law with each proposed discrete algorithm. OpenSees current-void-ratio/initial-density elasticity, low-pressure changes, memory resets and projections must not silently become the original law.

**Capability:** 26-component residual research model fits the 32-component capacity; tensor square and experimental parent resets exist. Event-location semantics, nonproportional/branch-boundary tangents, full 3D control validation and source-matched external reference evidence remain distinct gates.

**Small next task:** Produce a one-page decision table for first yield, reversal and memory reset: original-paper locator, OpenSees pinned-code locator, each Atlas research choice, and one distinguishing path. Select the next reference experiment only after that table.

**New local lead, not accepted reference:** `~/Downloads/VIBEPaperDataset.zip` contains `VIBEPaperDataset/lintriax/umat.f`, whose header identifies **Dafalias–Manzari (2004) SANISAND**, not VIBE. The 130,716-byte member has SHA-256 `f74cce87eb77e05b9cddbe77b9a4a6a05c4feac0371825f61089fdff9e5260ae`. Source provenance, version, rights and numerical differences are not reviewed. Inspect metadata/comments first; do not compile or assume equivalence.

### A2 — Clay hypoplasticity-2013 (`hypoplastic-clay-2013`)

**Identity:** Mašín (2013), *Clay hypoplasticity with explicitly defined asymptotic states*, Acta Geotechnica 8(5), 481–496. This is not the 2005 model or the separate 2014 anisotropic-stiffness extension. Discovery route: [author model documentation](https://web.natur.cuni.cz/uhigug/masin/plaxumat/node2.html), retained via [SoilModels clay entry](https://soilmodels.com/hypoclay/).

**Available:** Candidate metadata and retained bibliographic references; no full-text receipt identified in the canonical source receipts, Downloads inventory or inspected paper-side local-source directory.

**Acquire:** Exact 2013 paper and any author equation/implementation supplement; resolve DOI and version before assigning a definitive source record. Prefer author's university-hosted manuscript or publisher record.

**Capability:** Likely scalar/symmetric-tensor state and ordinary objective rate-law algebra; complete state layout, normalization, asymptotic-state domains and singular functions must be inventoried before claiming current DSL suffices. Existing rate integration has no finite-spin support.

**Small next task:** Pin paper bytes/title page, extract only the complete stress law, density state, parameters and admissible domains with page/equation locators; list every missing DSL operation. No default calibration or public model yet.

### A3 — Clay barodesy-2017 (`barodesy-clay-2017`)

**Identity:** Medicus & Fellin (2017), *An improved version of barodesy for clay*, Acta Geotechnica 12(2), 365–376, the formulation named for the directory subroutine. Keep sand barodesy and overlays separate. [Directory](https://soilmodels.com/barodesy/).

**Available:** Candidate identity only; no verified local full-text receipt found in the inspected inventories.

**Acquire:** Exact 2017 paper and author university-hosted implementation/manual if available, with separate version and reuse records. No DOI invented from the directory label.

**Capability:** Stress/void-ratio objective rate law is the likely representation, but inspect matrix/spectral/exponential and normalized stretching operations before asserting compatibility; the present DSL supports scalar exponentials, not a generic matrix exponential or eigensolver. Establish zero-stretch and hydrostatic limits and zero-spin scope.

**Small next task:** Create operation/state/domain inventory and one independent isotropic/axisymmetric algebra reduction from the original equations. This can proceed without a native build.

### A4 — Generalized IGS-2024 (`hypoplastic-generalized-igs-2024`)

**Identity:** Mugele, Stutz & Mašín (2024), Computers and Geotechnics 173, 106480; exact host/extension pairing is unresolved. It is not IGS97 or ISA. [Overview](https://soilmodels.com/istrain/).

**Available:** Directory/candidate metadata. No matching original identified locally. The three generic `1-s2.0-*.pdf` files in Downloads were title-screened and concern other granular fabric/contact topics, not this article.

**Acquire:** Article 106480, supplementary derivation and author code/release if present; pin exact article title/DOI and intended host law.

**Capability:** Extra history, history-band constraints, reversal rules and host/overlay interfaces. Existing IGS97 tensor memory, initialization tests and accepted-substep evidence are reusable infrastructure, not proof of equation equivalence. Determine the resulting state count against 32.

**Small next task:** Source-backed dependency matrix: allowed host(s), independent extension parameters, additional states, evolution and initialization; then select exactly one paired formulation identity.

### B1 — Anisotropic clay hypoplasticity-2014 (`hypoplastic-clay-2014`)

**Identity:** Mašín (2014), *Clay hypoplasticity model including stiffness anisotropy*, Géotechnique 64(3), 232–238. Preserve dependency on the 2013 host and separate optional IGS pairing. [Directory](https://soilmodels.com/hypoclay/).

**Available:** Candidate only in inspected inventories.

**Acquire:** Exact 2014 original and its 2013 dependency together; author implementation documentation with version/date.

**Capability:** Anisotropic stiffness representation and material orientation/initialization. Existing six-component tensors can represent a symmetric fabric only if the source uses one; do not infer fourth-order contractions, basis updates or finite rotations are supported. Determine fixed versus evolving anisotropy.

**Small next task:** Inventory independent anisotropy parameters/state, initialization axes and all contractions, then demonstrate one rotated material-axis algebra comparison against a Cartesian reference.

### B2 — ISA cyclic-mobility variant (`hypoplastic-isa`)

**Identity:** Fuentes et al.; the candidate explicitly targets the **2020 cyclic-mobility variant**, [DOI](https://doi.org/10.1007/s11440-019-00846-2). The DOI's 2019 component is not a reason to relabel the retained formulation. Do not conflate ISA with IGS97 or the 2024 generalized concept.

**Available:** DOI and candidate gap only; no matching local primary receipt found.

**Acquire:** Exact paper/full author list/title, supplement and paired host-law source; pin publication-year/version discrepancy explicitly if metadata requires it.

**Capability:** Intergranular backstrain/history evolution and initialization; possible additional branch/event semantics. Count scalar components and identify loading-history transactions before code generation.

**Small next task:** Extract source state/evolution/initialization table and one reversal example, contrasting it with IGS97 without merging their parameters or names.

### B3 — Extended Mohr–Coulomb-2013 (`extended-mohr-coulomb-2013`)

**Identity:** Doherty & Muir Wood (2013), Géotechnique 63(8), 661–673; complete hardening formulation combining Mohr–Coulomb yielding, Cam Clay flow and asymptotic hardening. Not generic perfect-plastic Mohr–Coulomb. [Directory](https://soilmodels.com/emc/).

**Available:** Candidate bibliographic summary; no pinned full source locally in inspected inventories.

**Acquire:** Original article and any author algorithm/calibration supplement; pin exact title/DOI rather than substituting a later implementation's simplified law.

**Capability:** Complete flow/hardening variables, nonsmooth face/edge/apex returns, unloading and admissible domains. Existing smooth-cone Drucker–Prager restart success does not establish a Mohr–Coulomb edge solver or active-set policy.

**Small next task:** Extract full closures and an analytical face/edge/apex test inventory. Decide if multisurface/principal-stress machinery is needed before proposing JSON.

### B4 — PM4Silt (`pm4silt`)

**Identity:** Version 1 (2018), report UCD/CGM-18/01 is the **retained source candidate**, not a verified latest release or pinned implementation. [Directory](https://soilmodels.com/pm4silt/). PM4Sand sources do not identify this model.

**Available:** Candidate only; no exact manual/release receipt found locally.

**Acquire:** Author-listed numbered manual and matching code/release/change log. Pin bytes, date, dimensional scope, calibration revision and implementation identifier. Resolve the candidate's family placeholder before transcription.

**Capability:** Stress-history initialization, cyclic fabric/memory, low-pressure rules, possible plane-strain restrictions, source integration and state capacity. No unrestricted 3D admission inferred from a plane-strain implementation.

**Small next task:** Source/release table and initial-state audit covering OCR/consolidation, material stage and dimensional restrictions. Coordinate findings with the separate PM4Sand agent while retaining distinct identities.

### B5 — HCA sand-2005 (`hca-sand-2005`)

**Identity:** Niemunis, Wichtmann & Triantafyllidis (2005), *A high-cycle accumulation model for sand*, Computers and Geotechnics 32(4), 245–263, [DOI](https://doi.org/10.1016/j.compgeo.2005.03.002).

**Available now:** Author-hosted 16-page manuscript at `paper/results/sources/niemunis-2005-hca.pdf`, hash independently checked against existing paper-side record: `ecf856384f0c77d5440a2aeb28c96420e609ed7cefffab9f19a0b8e141a796ce`. Existing draft `paper/study/source_formulations/hca-sand-2005.json` records partial visual inspection; `paper/study/hca_normalization.md` covers scalar normalization only. These paper-side artifacts are supporting draft evidence, not a canonical model transcription or a completed review. [Author PDF link](https://www.torsten-wichtmann.de/paper/journal/2005-CG-a-high-cycle-model.pdf).

**Missing/decision:** Complete amplitude/polarization/history, initialization, recording/control-cycle and companion constitutive-model algorithm. The paper-side bibliography record notes a conflicting DOI in an author-list entry; preserve the independently cross-checked DOI above. No need to ask user for another copy of this manuscript.

**Capability:** Cycle count N is a distinct evolution coordinate with rates per cycle, not seconds and not merely the recorded API's dimensionless path-order label. Need tensor amplitude, cycle recording/update schedule, cyclic preloading and back-polarization history, and coupling to a companion response. Existing timed ODE support does not license relabeling N as physical time.

**Small next task:** Produce a source-located algorithm flowchart/data contract for one recording cycle plus one accumulation block, distinguishing input amplitudes, evolving histories and companion-law evaluations. No full solver or curve overlay yet.

### C1 — Hypoplastic interface-2016 (`hypoplastic-interface-2016`)

**Identity:** Stutz, Mašín & Wuttke (2016), *Enhancement of a hypoplastic model for granular soil–structure interface behaviour*, Acta Geotechnica 11, 1249–1261, [DOI](https://doi.org/10.1007/s11440-016-0440-1). The paper-side draft identifies its HvWE enhancement and separate AH/AHE comparators/roughness alternatives; the 2017 general conversion approach remains a different lineage question.

**Available:** `paper/study/source_formulations/hypoplastic-interface-2016.json` records text-only author-manuscript access and publisher/author-list identity cross-checks. Its PDF download was 403; no local bytes/hash or visual equations are recorded. Do not describe it as a received original PDF.

**Acquire:** Author manuscript or journal PDF with equations visually readable; reconcile 2016 enhancement and exact roughness scheme before transcription.

**Capability:** Traction, normal/tangential slip, shear-zone thickness, reduced in-plane stress, initialization and local frame. Current bulk six-stress/six-strain contracts do not supply these semantics. Normal-load, constant-volume and constant-normal-stiffness tests are separate constraints.

**Small next task:** Pin PDF, visually reconcile only Eqs. (30)–(33) and the thickness conversion, and write an interface state/input/unit table. Do not count it as a general 3D bulk law.

### C2 — Multilaminate (`multilaminate-schadlich-schweiger`)

**Identity:** Schädlich's 2012 thesis versus 2013/2014 Schädlich–Schweiger extensions remains unresolved. **No exact formulation identity is yet pinned.** [Directory](https://soilmodels.com/multilaminate/).

**Available:** Candidate family description only; no thesis/paper receipt found locally.

**Acquire:** Original thesis plus the referenced 2013/2014 papers and implementation manual. First decide whether small-strain anisotropy, overconsolidation and Hvorslev modifications belong to the chosen variant.

**Capability:** Plane quadrature/orientations, plane-to-bulk transformations, per-plane histories and active surfaces; likely a state-capacity or parameter-array/code-generation extension. Count actual state components before claiming the 32-state bound is sufficient or insufficient.

**Small next task:** Version/dependency comparison and explicit `(number of planes) × (state per plane)` budget. Select one complete variant before an implementation schedule.

### C3 — Thermal-cycle hypoplasticity-2017 (`hypoplastic-thermal-ma-2017`)

**Identity:** Ma, Ng, Mašín & Zhou (2017), Canadian Geotechnical Journal 54(6), 896–901; fine-grained-soil thermal-cycle volume-change extension. [Directory](https://soilmodels.com/hypotherm/).

**Available:** Candidate identity only; no matching primary receipt found locally.

**Acquire:** Original 2017 paper, base mechanical host source, supplement and exact initialization/calibration path. Pin title/DOI from primary evidence.

**Capability:** Temperature path, thermal strain and stabilization history. SI temperature dimensions are representable, but current timed and recorded drivers do not accept a general prescribed temperature channel. Determine whether the law evolves with temperature increments, physical time, or both; thermal cycling alone does not establish creep.

**Small next task:** Extract thermal input/history equations and a mechanically constrained heating–cooling path, then propose the smallest input-channel extension justified by those equations.

### C4 — VIBE-2026 (`vibe-2026`)

**Identity:** Mašín (2026), viscohypoplastic bentonite, Engineering Geology 370, 108827; [DOI](https://doi.org/10.1016/j.enggeo.2026.108827). This is a specific double-structure THM model, not a synonym for thermal clay hypoplasticity.

**Available:** Local `VIBEPaperDataset.zip`, recorded SHA-256 `4c868a57158ffb96015a4359268a004d03fefc6f1b81d67441280c4945a811c2`; private bentonite normalization/checks are recorded with `public_hosting:false` and `model_overlay_eligible:false`. Dataset archive availability is not full-text/model-source availability or public redistribution permission. The archive's `umat.f` header identifies SANISAND, as noted above: it is not yet a VIBE implementation reference.

**Acquire:** Original article, author VIBE equation/code release and manual, and dependency papers for double-structure initialization/retention/thermal coupling. Confirm complete code identity rather than matching an archive name.

**Capability:** Physical-time creep/relaxation plus prescribed thermal/hydraulic channels, macro/microstructure variables and consistent coupled initialization; potentially algebraic retention/constraint equations. Current physical-time ODE support is useful infrastructure, but does not implement general THM channels or a DAE solver.

**Small next task:** Source/dependency/state/input matrix, followed by one isothermal fixed-hydraulic creep/relaxation reduction if source equations allow it. Keep the local dataset private and do not infer overlay eligibility from the eventual model implementation.

### C5 — Sand barodesy (`barodesy-sand`)

**Identity:** Unspecified placeholder. The directory names a family and its named code maps to **clay-2017**; it does not pin a sand formulation. [Directory](https://soilmodels.com/barodesy/).

**Available:** Discovery placeholder only.

**Acquire:** Select an exact author publication and matching implementation version from primary university/publisher evidence before acquiring equation fragments. Record why it is a complete sand law, not just a failure surface or the clay law with a different calibration.

**Capability:** Unknown until formulation selection; likely objective rate-law/tensor spectral operations warrant investigation. No executable-coverage credit yet.

**Small next task:** Compare two or three explicitly dated author formulations and choose one candidate identity with citation, state/parameter inventory and scope. Do not spend time transcribing an unselected family.

## Existing formulations within the directory: closure queue, not new models

- **VW96 (`hypoplastic-sand-vw96`)**: original PDF is present and equations reconciled at draft level. The parallel bounded visual audit found no Eqs. (40)–(46) transcription/sign errors. Next task is a source-matched Hochstetten preparation/trajectory plus explicit stress-domain and isotropic-limit tests; Karlsruhe defaults are separate. Fixed-frame covariance is not finite-spin objectivity. Scientific review stays open.
- **IGS97 (`hypoplastic-sand-igs97`)**: local filename says 1998 but pinned journal identity is 1997; keep the 1997 ID. Original overlay source and selected analytical histories exist. Next task is exact host/parameter specialization plus boundary/zero-history numerical treatment and a matching independent reference history. Keep the recent recursion-depth diagnosis separate from claims of global error control or physical validity. Do not count generalized-IGS/ISA as “already implemented” because IGS97 runs.
- **Clay-2005 (`hypoplastic-clay-2005`)**, outside the directory's selected 2013/2014 mapping: preserve as a separate source variant and extract only when needed for lineage or its existing roadmap wave. Do not silently replace it with the 2013 law.

## Evidence inspected and limits

Canonical evidence: `catalogue/discovery/soilmodels-2026-10-30.json`, `catalogue/manifest.json`, `catalogue/source-audits/original-papers-2026-10-31.json`, SANISAND source/research dossiers, `docs/STATE_CAPACITY.md`, `docs/TIME_ODE_API.md`, `docs/TIMED_SCHEDULES.md`, and roadmap expansion waves. Supplemental draft evidence: `paper/study/source_formulations/{hca-sand-2005,hypoplastic-interface-2016}.json`, `paper/study/hca_normalization.md`, and local source directory. Dataset provenance: `docs/data-license-evidence/user-download-review-2026-10-31.json` and `private-bentonite-verification.json`.

“Not found locally” means no matching receipt/filename in those inventories and the inspected Downloads/paper-side directories; it is not a whole-machine search or proof a source cannot be acquired. Existing URLs are acquisition routes recorded by the project, not newly tested live links. Do not duplicate existing user-supplied papers, invent DOI metadata, redistribute copyrighted sources, promote draft review flags, or equate a candidate source audit with complete executable model admission.
