# Duncan-Chang 1970 - delivery source gate v1

Task: MODEL-duncan-chang-1970 / SRC-duncan-chang-delivery-v1. Coordinator / 2026-11-01.
Scope: resume the first unclaimed source-lane model under E0-E8, preserving the historical packet. This additive packet follows the ingestion template. Overall delivery is blocked at E1; it is not completed ingestion.

## Identity and sources

Target: James M. Duncan and Chin-Yung Chang, *Nonlinear Analysis of Stress and Strain in Soils*, September 1970, volume96(5), pp1629-1653, [original DOI](https://doi.org/10.1061/JSFEAQ.0001458). Separately reconcile the [November 1971 erratum](https://doi.org/10.1061/JSFEAQ.0001706), volume97(11), p1597. The publisher labels the correction free access, but no correction text was obtained. Do not assume what it corrects.

[Source receipts](source-receipts.json) distinguish unavailable original/correction bytes from two actually downloaded and hashed ITCOLD contents scans, retained in ignored private storage. Both PDFs have five pages; PDF page4 / printed iv was rendered and visually inspected. April1971 contents place Bolognesi's discussion at p702; May1972 contents place the authors' closure at p495. Neither contains that text, original equations, or erratum. No redistribution permission was established, so scans, OCR and page images remain private.

Fresh network requests outside the restricted DNS sandbox reached the publisher but returned HTTP403 for both original and erratum PDFs. The web reader also could not open these PDFs. This demonstrates failure of these routes, not a universal paywall or absence of an authorized copy. ITCOLD's media/search endpoints were reachable but did not yield the original. Exact-title Berkeley/Geo-Institute searches found bibliographic records or later work, not a readable original. [WorldCat OCLC1157071665](https://search.worldcat.org/title/nonlinear-analysis-of-stress-and-strain-in-soils/oclc/1157071665) is a concrete Berkeley departmental eBook/reprint lead; no full text or journal equivalence is established.

The [local screen receipt](downloads-screen.json) records first-two-page text extraction from all20 direct-child Downloads PDFs, with zero extraction failures and no matching title/author combination. This improves on filename-only screening, but is not exhaustive full-text indexing. Unrelated filenames/excerpts are private.

## Existing work and gaps

Read and preserve the [historical acquisition packet](../README.md), [audit](../source-audit.json), [closure ledger](../schema-integration-ledger.json), and [publication identity work](../../classic-publications-v1/README.md). [Input pins](input-pins.json) bind these historical bytes and the current schema/contract/checklist. Prior completed acquisition reports are not source-complete law or executable evidence. The live board alone tracks ownership; the historical JSON queue was not edited.

## Equations and schema crosswalk

Target: [schema v0.3](../../../../schemas/model-v0.3.schema.json) and [explicit formulation contract](../../../FORMULATION_CONTRACT.md). No candidate is fabricated from later manuals or familiar hyperbolic formulas.

| Required source locator | Quantity / v0.3 mapping | Current decision |
| --- | --- | --- |
| Original primary-loading equations, unreceived | Stress-strain relation, tangent vs secant; parameter units/ranges | Unresolved |
| Original unloading/reloading text, unreceived | Complete persistent state, branch predicate, history maximum, rejoin event | Unresolved; no guessed memory |
| Original pressure dependence and strength, unreceived | Normalized parameters, admissible pressure/strength domain, failure/asymptote | Unresolved |
| Original lateral/volumetric and FE equations, unreceived | Complete tensor action; small-strain vs other kinematics and dimensional scope | Unresolved; no inferred 3D closure |
| Original conventions, unreceived | Frame/objective rate, stress/strain signs, tensor/shear basis, effective/total stress binding | Unresolved; no defaults |
| Original preparation/calibration text and tables, unreceived | Explicit initialization, required persistent fields, example recipe and valid parameter envelope | Unresolved |
| Erratum p1597, unreceived | Corrected source identity and affected equations | Unresolved |

Time dependence and equation form cannot yet be assigned to strain_path_rate, incremental_residual or physical-time ODE. No top-level integration field or legacy fallback is introduced. A source gap is not yet a demonstrated DSL/runtime limitation; no shared capability request is justified before exact equations are known. Actual engine APIs, capacity and browser controls must be compared after this gate, before freezing references and acceptance policy.

## Temporal integration and transactions

Original independent variable, history ordering/lagging, zero/hold behavior, reversals, discontinuities, stress-dependent inversion, tangent and uniqueness remain unverified. Future Atlas trials must read immutable committed state and atomically commit all physical history on success; failures, cutbacks and retries must preserve the parent. Restart must serialize complete source-defined state. These are project requirements, not unseen-source claims. Do not invent physical-time creep, rate independence or a sign-only unloading rule.

No numerical acceptance thresholds are frozen yet because the exact law is missing. After source closure, prospectively freeze source-derived differentiation/integration of the primary relation, prepared unloading/reloading and rejoin cases, domain/initialization rejection, finite paths, full-state rollback/recovery/restart and applicable tensor covariance/tangent checks. Add complete public preset/browser contracts before compiled observations. Later E3-E8 stages remain unstarted rather than waived.

## Independent checks

No independent constitutive algebra or numerical verification is claimed. Reproduce receipt and historical-byte checks with:

```sh
python3 -B docs/ingestion/duncan-chang-1970/delivery-v1/check_receipts.py
python3 -B -m unittest tests.test_ingestion_packets.IngestionPackets.test_duncan_chang_original_and_correction_remain_unverified -v
```

The first command optionally verifies private downloaded bytes when present; its report identifies unavailable private files. Packet integrity is distinct from numerical qualification. Separate source-gate reviewer evidence is under [independent-review](independent-review/); it is not E5 model approval. No native/Wasm builds, compiled calls or author/vendor execution occurred.

## Handoff

[Delivery ledger](../DELIVERY.md) tracks every phase. E0 is complete; E1 is blocked; E2 requirements are recorded but unresolved; E3-E8 remain unstarted. Source completeness, executable support, numerical qualification, agent approval, atlas inclusion, packaged browser, live delivery and experimental validation are all unestablished for this model.

Smallest next action: obtain readable original1970 pp1629-1653 and correction1971 p1597 via authorized institutional access or an author/institutional copy, recording exact bytes and source equivalence. Follow the WorldCat departmental record as a concrete lead. If original path/branch claims require it, acquire actual discussion/author-closure pages separately; contents scans do not satisfy that dependency. Resume with full visual equation inventory, then a source-supported v0.3 contract and prospective gates before implementation/build/browser work. Do not repeat unchanged denied routes without a new lead. No remote publication authorization is inferred from this ingestion instruction.
