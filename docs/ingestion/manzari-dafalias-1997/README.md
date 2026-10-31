# manzari-dafalias-1997 - original-source acquisition gap

Task ID: ING-manzari-dafalias-1997
Owner / date: review_igs97 / 2026-10-31
Scope: exact1997 source, surfaces, memory, initialization and schema/integration inventory. **Original full text was not obtained; this packet is an acquisition gap report, not completed source ingestion.**

## Identity and sources

Target: M. T. Manzari and Y. F. Dafalias (1997), *A critical state two-surface plasticity model for sands*, Géotechnique47(2),255-272, [DOI10.1680/geot.1997.47.2.255](https://doi.org/10.1680/geot.1997.47.2.255).

The [UC Davis author bibliography](https://faculty.engineering.ucdavis.edu/dafalias/publications/) supports the title, authors, year, volume47 and pages255-272. The [George Washington author profile](https://cee.engineering.gwu.edu/majid-manzari), under constitutive modeling, instead lists volume49 and pages252-272. That discrepancy is retained explicitly rather than interpreted as a different model. The DOI target and UCD citation identify the selected47(2),255-272 article, with issue/DOI corroboration from bibliographic indexes and later publisher reference lists. An original title-page check is still required.

The [NTUA institutional item](https://dspace.lib.ntua.gr/xmlui/handle/123456789/12121) indexes the exact title/authors/year. Its search-indexed record says there are no associated files; direct access timed out, so this is not a freshly verified live absence. The [ICE original PDF route](https://www.icevirtuallibrary.com/doi/pdf/10.1680/geot.1997.47.2.255) and article page returned403 in the web tool. DOI and legacy Emerald PDF/HTML routes were inaccessible. These are access outcomes in this session, not proof that no authorized copy exists elsewhere.

Downloads and the existing private source inventory were checked first by filename. Only the supplied2004 paper was located among matching original-paper names; no exact1997 PDF was found. Arbitrarily named files were not exhaustively content-indexed. Targeted UCD, GW, NTUA and other institutional searches returned later literature and reference lists. The [source audit](source-audit.json) records scope and route outcomes.

No1997 PDF bytes, hash or equation images were received. Byte count and SHA256 are null. No equation/page rendering or visual source check is claimed. The already-read PDF skill remains applicable when an authorized copy becomes available. No source PDF, page render, extracted text or author code is redistributed.

## Existing work and gaps

The [live board](../../../IMPLEMENTATION_PLAN.md) and [historical queue](../../../catalogue/research-queues/parallel-source-queue-2026-10-31.json) identify original-source acquisition as the gate. Existing [2004 source extraction](../../models/sanisand-2004-original.md) and [2004 decision table](../../reviews/sanisand-2004-decision.md) are later-formulation evidence. Their equations, event fixtures and implementation choices remain unchanged and do not verify1997.

Several accessible sources describe related but distinct laws. The [Aalborg2012 institutional record](https://vbn.aau.dk/en/publications/modified-critical-state-two-surface-plasticity-model-for-sands/) explicitly identifies a LeBlanc-modified formulation. A [micropolar paper by the original authors](https://www.gruppofrattura.it/ocs/index.php/ICF/ICF11/paper/download/10122/9504) extends the family with couple stresses. Neither is selected as the original1997 law. An implementation called ManzariDafalias can also target a later formulation; class name alone is not source identity.

## Equations and schema crosswalk

The [ledger](schema-integration-ledger.json) contains source questions, not invented equations. No executable schema or state capacity is proposed.

| Original content needed | Future representation to settle | Status |
| --- | --- | --- |
| Stress/strain definitions and elasticity | Effective/total stress, sign, tensor map, moduli and domain | Original unavailable |
| Critical-state line and state parameter | Pressure normalization, density state and calibration | Original unavailable |
| Yield, bounding and dilatancy surfaces | Independent centers/sizes, derived images and shape functions | Original unavailable |
| Flow and plastic multiplier | Nonassociativity, consistency, softening and singular branches | Original unavailable |
| Kinematic/isotropic hardening and memory | Full history layout and reversal/reset events | Original unavailable |
| Initialization and preparation | Stress, density, all surface variables and loading-process memory | Original unavailable |
| Parameter tables and demonstrations | Named source calibration, units and supported histories | Original unavailable |
| Numerical implementation discussion | Continuous law versus finite update, tangent and event policy | Original unavailable |

In particular, no2004 critical-state curve, current-density elastic law, rational Lode function, fabric tensor, loading-process anchor or reversal criterion is transplanted into1997. This is a prohibition on unverified substitution, not a claim that all such quantities are absent from the original. Parameter counts, physical bounds and total state size remain unknown until source inspection.

## Temporal integration and transactions

Original rate/incremental form, physical-time dependence, loading inputs, zero-load response and old/new history ordering remain unverified. Cyclic examples do not by themselves specify finite-step reversal semantics. No first-yield or anchor update policy is inferred from later source code.

The following are Atlas implementation requirements, not instructions attributed to unseen original text. Trials read immutable parent stress, density, surface variables and memory. Success commits the complete state atomically; failure/cutback restores it. Any event predicate, first-yield split and reversal reset must have declared scope relative to caller increments and accepted substeps. Preparation must retain all histories, not only nominal stress and void ratio. Continuous constitutive tangent, algorithmic Jacobian and numerical return mapping must remain distinguishable.

## Independent checks

No independent algebra fixture is justified without exact equations. No constitutive calculation, native/Wasm solver, build or author software was executed. JSON, relative manifest hashes, explicit missing-source values and trailing whitespace were checked; these are artifact-integrity checks only.

After acquisition, start with an independent Cartesian surface-normal check and source triaxial/critical-state reductions. Then create prepared states that distinguish memory and reversal rules. Comparing those against2004 is meaningful only after both formulations and their parameter meanings are separately pinned. A later implementation agreeing with itself does not independently verify1997.

## Handoff

Owned files: README.md, source-audit.json, schema-integration-ledger.json and manifest.json. All manifest entries are local relative files. No untracked paper-tree dependency or private source is required to read this packet.

The next action is authorized acquisition of the exact1997 original, followed by byte/hash receipt, visual title/equation inspection and completion of the ledger. A differently paginated report or manuscript requires explicit equivalence checking. No author was contacted and no request form was submitted. No generic operator or shared-code request is justified by the unavailable equations.

Source completeness: blocked at original full text. Executable support: none added. Numerical verification: none claimed. Scientific admission: unchanged, not established. The coordinator should retain a blocked ingestion entry unless separately recording completion of this bounded acquisition-gap subtask.
