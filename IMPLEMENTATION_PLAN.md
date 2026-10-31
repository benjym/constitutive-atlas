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

- [ ] **ING-original-cam-clay** — Pin exact Critical State Soil Mechanics edition/chapter and Original Cam Clay yield/flow/hardening/elasticity/initialization; do not substitute Modified Cam Clay.
  Owner: — (released after bounded handoff); output: `docs/ingestion/original-cam-clay/`; partial evidence: [packet](docs/ingestion/original-cam-clay/README.md); BLOCKED: 1968 edition fidelity, constrained shear-rigid response, hydrostatic vertex and named 3D closure; readable transcription inventory delivered.

- [ ] **ING-duncan-chang-1970** — Acquire DOI10.1061/JSFEAQ.0001458 and separate original loading/unloading/triaxial stress-dependent moduli from any later complete3D closure.
  Owner: — (released after bounded handoff); output: `docs/ingestion/duncan-chang-1970/`; partial evidence: [packet](docs/ingestion/duncan-chang-1970/README.md); BLOCKED: original 1970 article and 1971 erratum full text unavailable; acquisition report delivered.

- [ ] **ING-lade-duncan-1975** — Acquire DOI10.1061/AJGEB6.0000208; extract full flow/hardening/elasticity and initialization, not just failure criterion.
  Owner: —; output: `docs/ingestion/lade-duncan-1975/`; existing evidence: [manifest.json](catalogue/manifest.json); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-matsuoka-nakai** — Select a named complete constitutive law/publication, then pin flow/hardening/elasticity; criterion alone is not executable coverage.
  Owner: —; output: `docs/ingestion/matsuoka-nakai/`; existing evidence: [roadmap](ROADMAP.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-norsand-1993** — Original equation images remain unavailable; acquire original bytes before certifying rigid-plastic/image-pressure closure.
  Owner: —; output: `docs/ingestion/norsand-1993/`; existing evidence: [norsand-1993-source-packet.md](docs/reviews/norsand-1993-source-packet.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-manzari-dafalias-1997** — Acquire DOI10.1680/geot.1997.47.2.255; separate1997 surfaces, memory and initialization from SANISAND2004 changes.
  Owner: — (released after bounded handoff); output: `docs/ingestion/manzari-dafalias-1997/`; partial evidence: [gap packet](docs/ingestion/manzari-dafalias-1997/README.md); BLOCKED: original1997 full text unavailable through tested routes; later2004 and modified variants not substituted.

- [X] **ING-hypoplastic-clay-2005** — Pin exact2005 original and matching implementation, full stiffness/ASBS/density evolution; preserve separate2005 identity despite2013 progress.
  Owner: `review_vw96`; claimed: 2026-10-31; output: `docs/ingestion/hypoplastic-clay-2005/`; evidence: [reviewed packet](docs/ingestion/hypoplastic-clay-2005/README.md); bounded source/schema/integration inventory integrated with40 analytical checks and six test groups. The [additive correction](docs/ingestion/hypoplastic-clay-2005/rate-review-v1/README.md) supersedes the historical Eq38 conflict claim; final-publisher equivalence and full-rate/execution/admission gates remain open.

- [ ] **ING-hypoplastic-clay-2013** — Do not repeat source-rate or exact isotropic integration work. Next nonisotropic finite reference histories, near-boundary precision and physical preparation/source reconciliation.
  Owner: —; output: `docs/ingestion/hypoplastic-clay-2013/`; existing evidence: [clay2013-research-integration.md](docs/models/clay2013-research-integration.md); blocker: see existing dossier, confirm when claimed.

- [ ] **ING-s-clay1** — Acquire Wheeler et al2003 DOI10.1139/t02-119; source-map rotational hardening/anisotropy orientation, parameter/state/input inventory and initialization.
  Owner: — (released after bounded handoff); output: `docs/ingestion/s-clay1/`; partial evidence: [packet](docs/ingestion/s-clay1/README.md); BLOCKED: SC-SOURCE-01: original 2003 full text unavailable; identity/acquisition report delivered.

- [X] **ING-barodesy-sand** — Compare explicitly dated author sand formulations and select one complete identity; directory subroutine identifies clay2017 and cannot pin sand.
  Owner: `review_igs97`; claimed: 2026-10-31; output: `docs/ingestion/barodesy-sand/`; evidence: [reviewed packet](docs/ingestion/barodesy-sand/README.md); original2015 interior sand law and separate2019 calibration pinned,13 algebra tests integrated. Zero-stress/frame/calibration and full execution/admission gates remain open.

- [X] **ING-pm4sand** — PM4Sand2D3.3 UCD/CGM-23/01: compare pinned June2023 vendor bytes against May2024 author revision and inventory plane-strain/in-plane-mean-stress constraints separately from3D.
  Owner: `review_sanisand`; claimed: 2026-10-31; output: `docs/ingestion/pm4sand/`; evidence: [reviewed packet](docs/ingestion/pm4sand/README.md); author May2024/vendor June2023 receipts, bounded equation/host inventory and eleven algebra groups integrated. Source closure remains partial with nine explicit source/host blockers; full execution/admission open.

- [X] **ING-extended-mohr-coulomb-2013** — Doherty/Muir Wood2013 Geotechnique63(8)661-673: pin title/DOI/full source; extract complete Cam-Clay flow/asymptotic hardening, then nonsmooth face/edge/apex test plan.
  Owner: `review_sanisand`; claimed: 2026-10-31; output: `docs/ingestion/extended-mohr-coulomb-2013/`; evidence: [reviewed source packet](docs/ingestion/extended-mohr-coulomb-2013/README.md). Exact publisher source, equation/state/integration inventory and nine diagnostic groups integrated. Six source/algorithm reconciliation gates remain open; no executable model or scientific admission.

- [ ] **ING-hypoplastic-interface-2016** — DOI10.1007/s11440-016-0440-1: existing text-only2016 manuscript is not a received PDF; pin readable equations30-33 and thickness/traction/slip/local-frame contract; separate2017 conversion.
  Owner: — (released after bounded handoff); output: `docs/ingestion/hypoplastic-interface-2016/`; [partial packet](docs/ingestion/hypoplastic-interface-2016/README.md). BLOCKED: exact original2016 article PDF/Eqs30–33 visual verification unavailable; primary thesis/operator/kinematics contract delivered. No full3D host substitution.

- [ ] **ING-multilaminate-schadlich-schweiger** — Acquire2012 thesis and2013/2014 extensions; select complete variant and tabulate number-of-planes times state-per-plane, quadrature/orientation/active surfaces.
  Owner: —; output: `docs/ingestion/multilaminate-schadlich-schweiger/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md); blocker: see existing dossier, confirm when claimed.

- [X] **ING-hypoplastic-thermal-ma-2017** — Ma/Ng/Masin/Zhou2017 CGJ54(6)896-901: pin title/DOI/host/full equations; determine temperature-increment versus physical-time evolution and mechanically constrained thermal cycle.
  Owner: `review_sanisand`; claimed: 2026-10-31; output: `docs/ingestion/hypoplastic-thermal-ma-2017/`; existing evidence: [parallel-candidate-triage.md](docs/reviews/parallel-candidate-triage.md). [Packet](docs/ingestion/hypoplastic-thermal-ma-2017/README.md) integrated: exact accepted manuscript, Eqs1–10/host inventory and nine diagnostic groups. Six source/algorithm gates remain open; no coupled execution or admission.

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
| ING-hypoplastic-clay-2005 | [Packet](docs/ingestion/hypoplastic-clay-2005/README.md) |40 analytical checks and six test groups; printed unloading conflict retained | Bounded source/contract packet; nonisotropic rate follow-up claimed |
| ING-barodesy-sand | [Packet](docs/ingestion/barodesy-sand/README.md) |13 algebra groups and frozen fixture replay | Original2015 interior contract; nonzero-stress rate follow-up claimed |
| ING-pm4sand | [Packet](docs/ingestion/pm4sand/README.md) | Eleven algebra groups; distinct author/vendor receipts | Partial equation/host inventory; nine source/host blockers retained |
| SRC-MD1997-identity-gap | [Packet](docs/ingestion/manzari-dafalias-1997/README.md) | Receipt/missing-source integrity checks only | Full original ingestion blocked |
| SRC-OCC-transcription | [Packet](docs/ingestion/original-cam-clay/README.md) | Six analytical test groups, portable replay and pinned files | Bounded transcription/reference packet integrated; full ingestion blocked |
| SRC-SCLAY1-identity | [Packet](docs/ingestion/s-clay1/README.md) | Four metadata/integrity groups, no constitutive checks claimed | Identity/gap packet integrated; original full text needed |
| SRC-DUNCAN-identity-erratum | [Packet](docs/ingestion/duncan-chang-1970/README.md) | Original/correction identity, missing-source flags and pinned files | Acquisition/gap packet integrated; original and erratum needed |

| ING-extended-mohr-coulomb-2013 | [Packet](docs/ingestion/extended-mohr-coulomb-2013/README.md) | Exact source receipts and nine bounded algebra groups | Partial source closure; six reconciliation gates, no execution or admission |

A shared engine/schema request becomes a separate coordinator-owned task with dependencies on the relevant model packet. Do not block unrelated source ingestion while it is resolved. Integration, reference execution, public admission and deployment require their own recorded gates; no ingestion checkbox closes them implicitly.

## Coordinator integration lane

- [X] **INT-clay2014-path-results** — Integrate immutable failed native/Wasm finite-path evidence, independent whole-matrix and scalar diagnostics, and the website evidence binding. Owner: coordinating parent; started: 2026-10-31; evidence: [result review](docs/reviews/clay2014-path-results.md). Integrated: 70 focused Python groups, retained-manifest integrity and real website evidence export pass; original numerical study remains failed. This task records a negative study; it does not close model admission.
- [X] **INT-clay2014-controlled-resolution** — Freeze a separate actual-resolution hydrostatic order study, then execute serially against independent scalar references. Depends on INT-clay2014-path-results; preserve the original failed study. Owner: coordinating parent; claimed: 2026-10-31; output: `catalogue/investigations/clay2014-controlled-resolution-v1/`; [results](docs/reviews/clay2014-controlled-resolution-results.md) integrated:315 calls/backend,18 endpoint contraction gates/backend and exact observed native/Wasm parent/state parity; original negative study unchanged. Scientific/full-model gates remain open.

The [ingestion index](docs/ingestion/README.md) links completed packets and their [generic capability follow-up](docs/ingestion/CAPABILITIES.md).

## Completed bounded acquisition/reference subtasks

These close only the deliverable named here. Their original full-ingestion tasks remain unstarted/blocked with partial packets retained; released owners work on other tasks.

- [X] **SRC-OCC-transcription** — Readable Chapter6/AppendixC inventory, rigid-shear/vertex/3D distinction and bounded analytical fixtures delivered. Evidence: [packet](docs/ingestion/original-cam-clay/README.md). Original1968 edition certification and general execution remain open.
- [X] **SRC-SCLAY1-identity** — Correct publication identity, source-route receipts and ten extraction gaps delivered. Evidence: [packet](docs/ingestion/s-clay1/README.md). The live catalogue DOI was corrected in f55cf03; the packet preserves the earlier misattached-link context. Original equations remain unavailable.
- [X] **SRC-DUNCAN-identity-erratum** — Original and1971 correction identities plus bounded source-access/closure-gap report delivered. Evidence: [packet](docs/ingestion/duncan-chang-1970/README.md). No constitutive equation verification claimed.

[Current source requests](docs/ingestion/SOURCE_REQUESTS.md) list the exact missing materials without substituting later formulations.

- [X] **SRC-MD1997-identity-gap** — Original identity, conflicting author-page bibliography and bounded source-access/closure-gap report delivered. Evidence: [packet](docs/ingestion/manzari-dafalias-1997/README.md). Original equations remain unavailable; full ingestion remains blocked.

## Source-to-execution follow-up

- [X] **SRC-clay2005-appC-rate** — Prepare a separate non-admitted AppendixC/Eq40 seven-rate draft and independent Cartesian oracle, with exact-isotropy/domain/covariance witnesses; preserve the historical Eq38 conflict claim pending review. Owner: `review_vw96`; claimed: 2026-10-31; output: `docs/ingestion/hypoplastic-clay-2005/rate-study-v1/`. No shared edits, compiled observations or admission are authorized by this packet task. Integrated [draft/oracle packet](docs/ingestion/hypoplastic-clay-2005/rate-study-v1/README.md):41 seven-rate comparisons and ten test groups; the [additive audit correction](docs/ingestion/hypoplastic-clay-2005/rate-review-v1/README.md) supersedes its false Eq38 conflict claim and identifies an unsafe SPD guard. Compiled study held for a new revision; near-isotropic gates remain open.

- [X] **SRC-barodesy2015-rate** — Prepare a separate non-admitted fixed-frame/nonzero-stress seven-rate draft and independent Cartesian matrix-exponential oracle; preserve zero-stress/frame/calibration limits. Owner: `review_igs97`; claimed: 2026-10-31; output: `docs/ingestion/barodesy-sand/rate-study-v1/`. No shared edits, compiled observations or admission are authorized by this packet task. Integrated [draft/oracle packet](docs/ingestion/barodesy-sand/rate-study-v1/README.md):37 valid rates,19 Python input rejections and13 test groups; compiled numeric proposal excludes four named/type-only cases.

## Shared research build infrastructure

- [X] **INT-isolated-research-build** — Add a reusable single-file rate/material transport target over the common compiler and engine; no public catalogue or model-specific CMake edits. Owner: coordinating parent; claimed: 2026-10-31; output: `cmake/research/`; [usage](docs/ISOLATED_RESEARCH_BUILDS.md). Native/Wasm single-file source-study builds completed serially for sand barodesy; generated files match exactly. Build logs and one retained native receipt-packaging failure/recovery are in the sand study.

- [-] **INT-clay2005-instantaneous-rates** — Freeze a generic rate corpus, source/artifact receipts and rejection/recovery assessment, then run isolated serial native/Wasm studies against the independent AppendixC oracle. Owner: coordinating parent; claimed: 2026-10-31; output: `catalogue/investigations/clay2005-rates-v1/`. Depends on the new guarded clay revision and transport completion; v1 draft must not be compiled as an accepted study. No finite-integration, material-AD or admission claim.

## Automated cross-review before compiled rate observations

These are independent automated audits of the draft mappings and study machinery; they do not confer the charter’s signed scientific review/admission. Each reviewer preserves author packets and reports exact input hashes.

- [X] **AUDIT-barodesy2015-rate** — Audit the2015 source/sign/Cartesian-vs-DSL mapping, matrix-exponential support and protocol claims. Owner: `review_vw96`; claimed: 2026-10-31; output: `docs/ingestion/barodesy-sand/rate-review-v1/`; [audit](docs/ingestion/barodesy-sand/rate-review-v1/README.md) integrated: three independent groups; frozen37 corpus replay passes, two wider-envelope oracle/domain findings retained.
- [X] **AUDIT-clay2005-rate** — Audit AppendixC/Eq40 sign/invariant/Cartesian-vs-DSL mapping, isotropic branches and protocol claims. Owner: `review_igs97`; claimed: 2026-10-31; output: `docs/ingestion/hypoplastic-clay-2005/rate-review-v1/`; [audit/correction](docs/ingestion/hypoplastic-clay-2005/rate-review-v1/README.md) integrated: four groups reproduce false source-conflict claim and unsafe SPD guard. New revision required before compilation.
- [X] **AUDIT-generic-rate-transport** — Audit literal controls, frozen identity, raw evidence, rejection/recovery and numerical-gate handling in the generic collector/assessor before its source-study execution. Owner: `review_sanisand`; claimed: 2026-10-31; output: `docs/reviews/generic-rate-transport-v1/`; [audit](docs/reviews/generic-rate-transport-v1/README.md) integrated: five initial failure witnesses retained and all five close against the installed revised Python tool. Node/protocol/build/source execution outside scope.

## Corrected rate revisions and transport follow-up

- [X] **SRC-barodesy2015-rate-v2** — Preserve v1 and its two audit findings; make a distinct oracle/draft revision with exact actual-binary64 volumetric summation and explicitly separated ideal-source versus binary64 operational support. Owner: `review_vw96`; claimed: 2026-10-31; depends on AUDIT-barodesy2015-rate; output: `docs/ingestion/barodesy-sand/rate-study-v2/`. [Revised packet](docs/ingestion/barodesy-sand/rate-study-v2/README.md) integrated:38 valid,20 operational rejections and11 groups; exact rational void channel and separate ideal/operational domains. Compiled study pending; no admission.
- [X] **SRC-clay2005-rate-v2** — Preserve all v1 bytes; correct Eq38 provenance and add independently justified conservative Cartesian SPD support in a distinct declarative draft/oracle revision. Owner: `review_igs97`; claimed: 2026-10-31; depends on AUDIT-clay2005-rate; output: `docs/ingestion/hypoplastic-clay-2005/rate-study-v2/`. [Revised packet](docs/ingestion/hypoplastic-clay-2005/rate-study-v2/README.md) integrated:41 unchanged rates,10 unchanged invalid inputs,29 support cases and18 groups. Independent guard review and compiled study pending; no admission.
- [X] **INT-generic-rate-transport** — Integrate reusable frozen-corpus evidence collection/assessment and source protocols. Owner: coordinating parent; claimed: 2026-10-31; output: `tools/research_rate_observations.py`; [contract](docs/RESEARCH_RATE_TRANSPORT.md). Native/Wasm opaque collectors and evidence-backed parity wrapper installed;11 original and eight collection/comparison synthetic tests plus five reviewer witnesses pass. First actual source corpus/build receipts/native/Wasm observations integrated in the sand study; numerical failure retained. The [collection audit](docs/reviews/generic-rate-collection-v1/README.md) identifies a parameter-layout identity gap, so this bounded infrastructure task does not certify arbitrary evidence inputs; strict supplemental actual-layout check passes for the observed study.

- [X] **INT-rate-opaque-collection** — Add generic Wasm journal collection and a parity wrapper accepting original evidence bundles rather than precomputed assessments. Owner: coordinating parent; integrated: 2026-10-31; output: `tools/collect_research_rates_wasm.mjs`, `tools/research_rate_parity.py`; [contract](docs/RESEARCH_RATE_TRANSPORT.md). Eight synthetic loader/evidence groups pass; no compiled or scientific admission claim. Depends on AUDIT-generic-rate-transport.

- [X] **INT-barodesy2015-instantaneous-rates** — Freeze the exact-v2 source oracle and a71row/backend literal corpus, then execute serial native/Wasm collection and evidence-backed comparison. Owner: coordinating parent; claimed: 2026-10-31; depends on SRC-barodesy2015-rate-v2 and INT-rate-opaque-collection; output: `catalogue/investigations/barodesy2015-rates-v1/`. [Results](catalogue/investigations/barodesy2015-rates-v1/RESULTS.md):71rows/backend retained; native/Wasm each fail the same cancellation void-rate gate while parity passes. Original negative evidence preserved. Bounded study completed; no finite-integration, AD or admission claim.

## Prospective execution review and next source acquisition

- [X] **AUDIT-barodesy2015-prospective** — Independently check source-v2 to compiled-corpus mapping, literal controls, budgets, invalid/recovery completeness and frozen dependencies before rate execution. Owner: `review_igs97`; claimed: 2026-10-31; output: `docs/ingestion/barodesy-sand/compiled-plan-review-v1/`. [Review](docs/ingestion/barodesy-sand/compiled-plan-review-v1/README.md) integrated: exact corpus/source replay and eight mutation groups; no mapping blocker. No compiled calls/admission.
- [X] **AUDIT-generic-rate-collection** — Audit the new generic Node collector and evidence-backed parity wrapper with portable synthetic witnesses; distinguish collection from scientific/source verification. Owner: `review_sanisand`; claimed: 2026-10-31; output: `docs/reviews/generic-rate-collection-v1/`. [Review](docs/reviews/generic-rate-collection-v1/README.md) integrated: nine independent groups; reversed parameter-order identity gap and inherited duplicate-key limitation retained. Supplemental actual study layout check passes; generic fix pending. No compiled calls/admission.

- [X] **NUM-trace-cancellation-design** — Derive a generic scalar/Jet tensor-trace accuracy contract and independent exact-input cases for a future repair; preserve barodesy2015-rates-v1 negative evidence. Owner: `review_igs97`; claimed: 2026-10-31; output: `docs/reviews/tensor-trace-accuracy-v1/`. [Design packet](docs/reviews/tensor-trace-accuracy-v1/README.md) integrated: eight Python groups,97 exact-input fixtures and12,000 seeded triples, including all38 Jet columns. No shared arithmetic implementation or compiled verification; repair remains a separate task.
- [X] **ARCH-frozen-source-evolution** — Propose a concrete portable archive/replay path so shared-engine changes preserve old hash-pinned studies and their negative evidence. Owner: `review_sanisand`; claimed: 2026-10-31; output: `docs/reviews/frozen-source-evolution-v1/`. [Architecture packet](docs/reviews/frozen-source-evolution-v1/README.md) integrated: seven Python groups and isolated portable replays reproduce five historical assessor defects versus zero after the fix. Production replay migration remains separate; no shared runtime edits or builds.

- [X] **SRC-interface2016-thesis-contract** — Primary thesis receipt, reduced-operator/kinematics/history contract and exact rational representation witnesses integrated. Owner: `review_vw96`; completed: 2026-10-31; [packet](docs/ingestion/hypoplastic-interface-2016/README.md).100 exact algebra checks and three groups; original article source-complete gate remains open.
- [-] **INT-rate-layout-identity** — Close the inherited descriptor insertion-order/duplicate-key identity gaps in a distinct versioned collection/comparison path, retaining frozen study tools. Owner: coordinating parent; claimed: 2026-10-31; depends on AUDIT-generic-rate-collection and ARCH-frozen-source-evolution. No silent historical tool edits.

- [X] **INT-frozen-transport-replay** — Register immutable preliminary/fixed transport source closures and execute the original witnesses in fresh isolated Python trees, separately from current-code regression. Owner: coordinating parent; claimed: 2026-10-31; depends on ARCH-frozen-source-evolution; output: `atlas/source_replay.py`, `catalogue/source-replays/transport-audit-v1.json`, `tests/test_source_replay.py`. [Replay contract](docs/SOURCE_REPLAY.md) integrated: exported no-Git closure reproduces both original outputs, corruption/source-binding failures reject, and seven independent synthetic checks pass against the common runner. Current behavioral regression remains separate. No shared engine or frozen assessor edits; no compiled execution.

- [ ] **INT-frozen-study-closures** — Migrate sand/clay v2 and affected compiled/finite-study verifier closures before shared tensor or assessor edits. Owner: —; depends on INT-frozen-transport-replay; output: `catalogue/source-replays/`. Preserve original failed studies and add current-code regressions separately; use the explicit inventory in ARCH-frozen-source-evolution.
