# Parallel model ingestion implementation plan

This is the **live work board** for model ingestion. [ROADMAP.md](ROADMAP.md) remains the milestone/research plan; [AGENTS.md](AGENTS.md) defines how agents claim and deliver this work. The older [source queue](catalogue/research-queues/parallel-source-queue-2026-10-31.json) is a historical evidence snapshot, not the live assignment board.

## Status and ownership

- `[ ]` Unstarted / available. Existing research may already exist; the marker refers to the next task below.
- `[-]` WIP: claimed by the named owner, with a start date and exclusive output directory.
- `[X]` Done: the bounded deliverable has been integrated, checked and linked here by the integration owner.

`[-]` is a plain-text convention; GitHub will not render it as a task checkbox. Keep it literal. A blocked task stays `[-]` with `BLOCKED: reason; next action` beside it. If it is relinquished, return it to `[ ]`, retain the partial packet, and record the blocker. Owner `—` means unassigned. Never infer availability from an old timestamp: ask the coordinator before reclaiming WIP.

Completion of ingestion does **not** mean executable support, independent scientific review, experimental validation or public admission. Each packet states those separately. One model can have subsequent tasks; add a new scoped task rather than erasing completed history.

## Parallel batch 1

Three independent source-ingestion packets are assigned below. Each agent owns only `docs/ingestion/<model-id>/`; the coordinator owns this board and integrates submissions. These models were chosen to broaden source coverage without duplicating the active clay2014 numerical investigation. Source acquisition, equation extraction, schema mapping and small independent Python checks can run concurrently. Native/Wasm builds remain serial, one target and one job, under the integration owner.

- [X] **ING-hca-sand-2005** — Reconcile full 9D versus symmetric 6D polarization and recording/filter equations from the pinned source; return schema/state requirements and distinguishing fixtures.
  Owner: `review_igs97`; claimed: 2026-10-31; output: `docs/ingestion/hca-sand-2005/`; evidence: [reviewed packet](docs/ingestion/hca-sand-2005/README.md); bounded task integrated 2026-10-31. Full source/execution/admission gates remain open as listed in the packet.

- [X] **ING-pm4silt** — Complete the pinned V1 manual equation, 2D scope, state and lagged-phase inventory; separate printed ambiguities from implementation choices.
  Owner: `review_sanisand`; claimed: 2026-10-31; output: `docs/ingestion/pm4silt/`; evidence: [reviewed packet](docs/ingestion/pm4silt/README.md); bounded task integrated 2026-10-31. Full source/execution/admission gates remain open as listed in the packet.

- [X] **ING-hypoplastic-isa** — Reconcile the pinned 2020 main/appendix and VW96 conflicts; map full-history initialization and a bounded supplied-host fragment.
  Owner: `review_vw96`; claimed: 2026-10-31; output: `docs/ingestion/hypoplastic-isa/`; evidence: [reviewed packet](docs/ingestion/hypoplastic-isa/README.md); bounded task integrated 2026-10-31. Full source/execution/admission gates remain open as listed in the packet.

## Further candidate ingestion tasks

Read all existing linked material first. The task is to close or precisely document the remaining source/schema gaps, not redo completed numerical studies. Acquisition blockers are historical findings to check, not claims that a fresh search has failed. Each task uses the packet template and completion gate in AGENTS.md.

- [ ] **ING-sanisand-2004** — Acquire exact Dafalias1986 PartI pp966-987 and map loading-process/conjugacy; keep existing2004 research event variants separate.
  Owner: —; output: `docs/ingestion/sanisand-2004/`; existing evidence: [sanisand-1986-loading-process.md](docs/reviews/sanisand-1986-loading-process.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-terracotta-2024** — Complete journal/author reconciliation and source-matched external histories; nine-case prepared creep parity already exists.
  Owner: —; output: `docs/ingestion/terracotta-2024/`; existing evidence: [TERRACOTTA_CREEP_REFERENCE.md](docs/TERRACOTTA_CREEP_REFERENCE.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-mohr-coulomb** — Pin exact elasticity, flow, hardening/perfect-plastic specialization and original source; inventory face/edge/apex algorithms before transcription.
  Owner: —; output: `docs/ingestion/mohr-coulomb/`; existing evidence: [roadmap](ROADMAP.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-tresca** — Select complete elastic-plastic closure and source/version; define corners and admissible active surfaces.
  Owner: —; output: `docs/ingestion/tresca/`; existing evidence: [roadmap](ROADMAP.md); blocker: see existing dossier, confirm when claimed.

- [-] **ING-original-cam-clay** — Pin exact Critical State Soil Mechanics edition/chapter and Original Cam Clay yield/flow/hardening/elasticity/initialization; do not substitute Modified Cam Clay.
  Owner: `review_vw96`; claimed: 2026-10-31; output: `docs/ingestion/original-cam-clay/`; existing evidence: [roadmap](ROADMAP.md); blocker: see existing dossier, confirm when claimed.

- [-] **ING-duncan-chang-1970** — Acquire DOI10.1061/JSFEAQ.0001458 and separate original loading/unloading/triaxial stress-dependent moduli from any later complete3D closure.
  Owner: `review_igs97`; claimed: 2026-10-31; output: `docs/ingestion/duncan-chang-1970/`; existing evidence: [roadmap](ROADMAP.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-lade-duncan-1975** — Acquire DOI10.1061/AJGEB6.0000208; extract full flow/hardening/elasticity and initialization, not just failure criterion.
  Owner: —; output: `docs/ingestion/lade-duncan-1975/`; existing evidence: [manifest.json](catalogue/manifest.json); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-matsuoka-nakai** — Select a named complete constitutive law/publication, then pin flow/hardening/elasticity; criterion alone is not executable coverage.
  Owner: —; output: `docs/ingestion/matsuoka-nakai/`; existing evidence: [roadmap](ROADMAP.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-norsand-1993** — Original equation images remain unavailable; acquire original bytes before certifying rigid-plastic/image-pressure closure.
  Owner: —; output: `docs/ingestion/norsand-1993/`; existing evidence: [norsand-1993-source-packet.md](docs/reviews/norsand-1993-source-packet.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-manzari-dafalias-1997** — Acquire DOI10.1680/geot.1997.47.2.255; separate1997 surfaces, memory and initialization from SANISAND2004 changes.
  Owner: —; output: `docs/ingestion/manzari-dafalias-1997/`; existing evidence: [roadmap](ROADMAP.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-hypoplastic-clay-2005** — Pin exact2005 original and matching implementation, full stiffness/ASBS/density evolution; preserve separate2005 identity despite2013 progress.
  Owner: —; output: `docs/ingestion/hypoplastic-clay-2005/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-hypoplastic-clay-2013** — Do not repeat source-rate or exact isotropic integration work. Next nonisotropic finite reference histories, near-boundary precision and physical preparation/source reconciliation.
  Owner: —; output: `docs/ingestion/hypoplastic-clay-2013/`; existing evidence: [clay2013-research-integration.md](docs/models/clay2013-research-integration.md); blocker: see existing dossier, confirm when claimed.

- [-] **ING-s-clay1** — Acquire Wheeler et al2003 DOI10.1139/t02-119; source-map rotational hardening/anisotropy orientation, parameter/state/input inventory and initialization.
  Owner: `review_sanisand`; claimed: 2026-10-31; output: `docs/ingestion/s-clay1/`; existing evidence: [manifest.json](catalogue/manifest.json); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-barodesy-sand** — Compare explicitly dated author sand formulations and select one complete identity; directory subroutine identifies clay2017 and cannot pin sand.
  Owner: —; output: `docs/ingestion/barodesy-sand/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-pm4sand** — PM4Sand2D3.3 UCD/CGM-23/01: compare pinned June2023 vendor bytes against May2024 author revision and inventory plane-strain/in-plane-mean-stress constraints separately from3D.
  Owner: —; output: `docs/ingestion/pm4sand/`; existing evidence: [pm4sand-versions.md](docs/models/pm4sand-versions.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-extended-mohr-coulomb-2013** — Doherty/Muir Wood2013 Geotechnique63(8)661-673: pin title/DOI/full source; extract complete Cam-Clay flow/asymptotic hardening, then nonsmooth face/edge/apex test plan.
  Owner: —; output: `docs/ingestion/extended-mohr-coulomb-2013/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-hypoplastic-interface-2016** — DOI10.1007/s11440-016-0440-1: existing text-only2016 manuscript is not a received PDF; pin readable equations30-33 and thickness/traction/slip/local-frame contract; separate2017 conversion.
  Owner: —; output: `docs/ingestion/hypoplastic-interface-2016/`; existing evidence: [catalogue entry](catalogue/manifest.json) (supplemental paper-side source record is local/untracked); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-multilaminate-schadlich-schweiger** — Acquire2012 thesis and2013/2014 extensions; select complete variant and tabulate number-of-planes times state-per-plane, quadrature/orientation/active surfaces.
  Owner: —; output: `docs/ingestion/multilaminate-schadlich-schweiger/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-hypoplastic-thermal-ma-2017** — Ma/Ng/Masin/Zhou2017 CGJ54(6)896-901: pin title/DOI/host/full equations; determine temperature-increment versus physical-time evolution and mechanically constrained thermal cycle.
  Owner: —; output: `docs/ingestion/hypoplastic-thermal-ma-2017/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-vibe-2026** — DOI10.1016/j.enggeo.2026.108827: acquire original/model release and double-structure dependencies, thermal/hydraulic/time/initialization table. Dataset umat.f is SANISAND, not VIBE. Keep data private.
  Owner: —; output: `docs/ingestion/vibe-2026/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-hypoplastic-generalized-igs-2024** — HP/extracted-ASBS+GIS source fragments/14-rate reference/composition already present; parent owns flattening/integration. Acquire exact author release/license/discretization separately; no IGS97/ISA conflation.
  Owner: —; output: `docs/ingestion/hypoplastic-generalized-igs-2024/`; existing evidence: [gis2024-typed-composition.md](docs/models/gis2024-typed-composition.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-barodesy-clay-2017** — Consolidate existing source, rate, derivative and finite-path research; isolate remaining source/spin/initialization gaps. Do not repeat completed numerical studies.
  Owner: —; output: `docs/ingestion/barodesy-clay-2017/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md), [barodesy-clay-2017-source-packet.md](docs/reviews/barodesy-clay-2017-source-packet.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-hypoplastic-clay-2014** — Consolidate source/version/Am/IGS discrepancies and existing rate/path research; coordinate with the integration owner before new numerical work.
  Owner: —; output: `docs/ingestion/hypoplastic-clay-2014/`; existing evidence: [clay-2013-2014-source-packet.md](docs/reviews/clay-2013-2014-source-packet.md), [hypoplastic-clay-2014-original.md](docs/models/hypoplastic-clay-2014-original.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-pm4sand3d-1.0** — Pinned June2026 manual Table3.2 steps19/20: old/new reversal anchors/accumulator and z_alpha. Resolve source gaps before generic phases/capacity/kernel; retain May/June mismatch.
  Owner: —; output: `docs/ingestion/pm4sand3d-1.0/`; existing evidence: [pm4sand3d-1.0-history-inventory.json](catalogue/source-audits/pm4sand3d-1.0-history-inventory.json); blocker: see existing dossier, confirm when claimed.

## Existing executable model review lane

These five models already execute. The tasks below concern outstanding review and source completeness, not first ingestion. They do not run concurrently with another task on the same formulation without explicit scope separation.

- [ ] **REVIEW-drucker-prager** — Reconcile existing dossier/review records, identify unresolved source decisions, and return a bounded closure or gap report. Owner: —; output: `docs/ingestion/drucker-prager/`; existing evidence: [model dossier](docs/models/drucker-prager.md).

- [ ] **REVIEW-hypoplastic-sand-igs97** — Reconcile existing dossier/review records, identify unresolved source decisions, and return a bounded closure or gap report. Owner: —; output: `docs/ingestion/hypoplastic-sand-igs97/`; existing evidence: [model dossier](docs/models/hypoplastic-sand-igs97.md).

- [ ] **REVIEW-hypoplastic-sand-vw96** — Reconcile existing dossier/review records, identify unresolved source decisions, and return a bounded closure or gap report. Owner: —; output: `docs/ingestion/hypoplastic-sand-vw96/`; existing evidence: [model dossier](docs/models/hypoplastic-sand-vw96.md).

- [ ] **REVIEW-linear-elastic** — Reconcile existing dossier/review records, identify unresolved source decisions, and return a bounded closure or gap report. Owner: —; output: `docs/ingestion/linear-elastic/`; existing evidence: [model dossier](docs/models/linear-elastic.md).

- [ ] **REVIEW-modified-cam-clay** — Reconcile existing dossier/review records, identify unresolved source decisions, and return a bounded closure or gap report. Owner: —; output: `docs/ingestion/modified-cam-clay/`; existing evidence: [model dossier](docs/models/modified-cam-clay.md).

## Additional lineage task

- [ ] **SRC-wu-bauer-1994** — Complete Appendix I and map sign/calibration/friction-angle conflicts against the retained [original-source dossier](docs/models/wu-bauer-1994-original.md). Owner: —; output: `docs/ingestion/wu-bauer-1994/`. This is outside the 32 catalogue entries; it does not increase the executable count.

## Handoff and integration queue

The integration owner is the coordinating parent agent. Agents report their task ID, exact output files, checks run, evidence links, blockers and proposed shared-code requirements. The owner updates the row and appends a handoff entry here. No entry means no completed handoff yet.

| Task | Handoff / evidence | Review and checks | Integrated result |
| --- | --- | --- | --- |
| ING-hca-sand-2005 | [Packet](docs/ingestion/hca-sand-2005/README.md) | Ten algebraic tests; source/representation review | Bounded reconciliation integrated; full model gate open |
| ING-pm4silt | [Packet](docs/ingestion/pm4silt/README.md) | Seven witnesses; visual Cpmin cross-check | Equation/host inventory integrated; full model gate open |
| ING-hypoplastic-isa | [Packet](docs/ingestion/hypoplastic-isa/README.md) | 27 packet checks + three existing tests; Mandel order corrected before freeze | Contract integrated; full model gate open |

A shared engine/schema request becomes a separate coordinator-owned task with dependencies on the relevant model packet. Do not block unrelated source ingestion while it is resolved. Integration, reference execution, public admission and deployment require their own recorded gates; no ingestion checkbox closes them implicitly.

## Coordinator integration lane

- [X] **INT-clay2014-path-results** — Integrate immutable failed native/Wasm finite-path evidence, independent whole-matrix and scalar diagnostics, and the website evidence binding. Owner: coordinating parent; started: 2026-10-31; evidence: [result review](docs/reviews/clay2014-path-results.md). Integrated: 70 focused Python groups, retained-manifest integrity and real website evidence export pass; original numerical study remains failed. This task records a negative study; it does not close model admission.
- [ ] **INT-clay2014-controlled-resolution** — Freeze a separate actual-resolution hydrostatic order study, then execute serially against independent scalar references. Depends on INT-clay2014-path-results; preserve the original failed study. Owner: —.

The [ingestion index](docs/ingestion/README.md) links completed packets and their [generic capability follow-up](docs/ingestion/CAPABILITIES.md).
