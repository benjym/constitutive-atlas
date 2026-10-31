# SANISAND-2004 loading-process source follow-up

Task: ING-sanisand-2004. Owner: sanisand_loading_source. Date: 2026-10-31.
Scope: exact Dafalias (1986) Part I acquisition, loading-process/conjugacy reconciliation and explicit v0.3 crosswalk. **Source acquisition remains blocked.** This packet adds a current bounded search receipt, a schema/integration decision inventory and three exact conditional-algebra witnesses. It does not supply missing 1986 equations or choose a canonical event rule.

## Identity and sources

The required article is Yannis F. Dafalias (1986), *Bounding Surface Plasticity. I: Mathematical Foundation and Hypoplasticity*, Journal of Engineering Mechanics 112(9), 966-987, [publisher DOI](https://doi.org/10.1061/%28ASCE%290733-9399%281986%29112%3A9%28966%29). Its 22-page range and title are confirmed by publisher metadata and the [author's UC Davis publication list](https://faculty.engineering.ucdavis.edu/dafalias/publications/). This is not Part II, a 1990 sand model, SANISAND-Z or the 2004 paper. No full-text bytes, equation locators or visual review are claimed for 1986. [sources.json](sources.json) records the fresh access results and private 2004 receipt.

The follow-up scanned the first pages of 37 unarchived PDFs in Downloads and `paper/results/sources`: no exact 1986 candidate and no extraction failures. This expands the older 34-file bounded inventory; it is not an exhaustive local search. Archives, other directories and non-first-page title placement remain outside the scan. Full unrelated filenames/hashes stay in the private working log; the packet retains aggregate results to avoid publishing unrelated Downloads metadata.

Fresh direct publisher PDF access returned HTTP403 via the browser tool; `epdf` returned a cache miss. Targeted author/institution searches did not locate a readable original. The author list has a bibliographic entry without a source link. The previously noted third-party mirror remains unused: no provenance/redistribution permission was established. Search results, later models and abstracts cannot close the missing equation contract. No authentication or access control was bypassed.

Dafalias and Manzari (2004), *Simple Plasticity Sand Model Accounting for Fabric Change Effects*, [DOI](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29), is readable in the user's Downloads. SHA256 `b6e0f6ccfd018729a9bbd8492745af649c7682a8a1e929348ae25a728917e023`, 289863 bytes, 13 PDF pages, printed622-634. This worker rendered and visually inspected complete PDF page10 / printed631, especially Eq24 and the following paragraph, and Eqs23,25-27. Text extraction was used for navigation. The PDF, extracted text and page image remain private and are not bundled. No redistribution right was established.

## Existing work and added boundary

Read the existing [1986 gap audit](../../reviews/sanisand-1986-loading-process.md), [2004 extraction](../../models/sanisand-2004-original.md), [decision review](../../reviews/sanisand-2004-decision.md), [event fixtures](../../SANISAND_EVENT_FIXTURES.md), [regular hardening limit](../../models/sanisand-2004-hardening-limit.md) and [parent-reset variant](../../models/sanisand-2004-parent-reset-be.md). Their historical evidence remains unchanged. Existing elastic-entry, rate, BE/cyclic and rollback studies were not repeated.

The newly inspected 2004 p631 supports `h=b0/((alpha-alpha_in):n)` and identifies alpha_in with alpha at initiation of a new loading process. It calls for updating that memory when the denominator becomes negative, referencing 1986 rules. It distinguishes its denominator from the 1986 distance-difference expression. It does not define the unavailable conjugate-point mapping or a finite-step event algorithm. The p631 fabric evolution remains distinct from the anchor memory and supplies no fabric reset at reversal.

## Equations and schema crosswalk

[Crosswalk](crosswalk.json) targets schema_version `0.3` and explicitly records the complete candidate zero-spin, small-strain contract plus its restriction/authority. It is **not an executable model document** and must not be passed to the model validator as one. Existing 0.1 research records remain untouched; their migration belongs to the coordinator/contract owner.

The source equations are continuous strain increments with rate-independent loading and no seconds-based duration. A `strain_path_rate` profile can describe smooth source branches, but elastic interior/yield entry and unresolved process changes prevent presenting a globally complete rate record. `incremental_residual` describes the separately named BE research discretizations; it is not the source's finite-step equation. `physical_time/ode` is unsupported by these sources and must not be selected merely because the paper uses dots or increments.

| Source / identity | Quantity | v0.3 representation | Boundary |
| --- | --- | --- | --- |
| 2004 Eq3 p623, existing extraction | G,K from current e,p | Pa-valued derived scalars; G0,nu dimensionless | Initial-density implementation differs; source-parameter domain not completed here. |
| Eqs13-17 pp627-628, existing extraction | effective sigma; p,s,r; alpha | persistent symmetric sigma in Pa, alpha dimensionless; Mandel tensor storage | Fixed spatial zero-spin is the Atlas specialization, not a finite-rotation source claim. |
| Eq24 p631, newly visual checked | alpha_in and denominator | persistent dimensionless symmetric loading-process memory | Cannot replace source loading-process event with parent-direction reset by naming it alpha_in. |
| Eqs23-24 p631 | h,Kp | derived scalar, Kp in Pa | h infinite at initiation; a hardening cap is an implementation change. |
| Eq25 p631 | dilatancy D | dimensionless scalar derived from tensor contraction | Preserve noncoaxial tensor direction dependence. |
| Eqs26-27 p631 | z / fabric | persistent symmetric dimensionless fabric-dilatancy tensor | Evolve during plastic dilation; no inferred reversal reset. |
| Eq20 p629, earlier visual extraction | loading index | dimensionless incremental loading quantity | Existing explicit missing-K correction stays identified; this worker did not independently reread p629. |
| Project closure, not numbered source equation | void ratio e | persistent scalar invariant | Incompressible-grain volume closure/preparation remains a declared project choice. |
| Project finite-product BE variant | gamma=Delta_lambda*h | temporary dimensionless plastic_multiplier slot | Not cumulative plastic strain or physical history; gamma's source is a project rearrangement. |

Parameter inventory: G0, nu, M, c, lambda_c, e0, xi, m, h0, ch, nb, A0, nd, zmax, cz are dimensionless; p_at is Pa. Printed e0 is the critical-state intercept, not the specimen's initial e. Source Table1 values and Figure3 zmax override remain in the linked original dossier; this follow-up does not turn calibration examples into universal validity bounds. Real-valued interior requires p>0 and e>-1, and elastic/constitutive denominators must be nonsingular. Full physical admissibility is still open.

State layout for the existing research variants is sigma6,e1,alpha6,fabric6,alpha_in6,gamma1: 25 persistent components and one temporary component, 26 total. A source smooth-branch rate system would not contain the BE gamma unknown. Tensor histories require deviatoric consistency where assumed by equations; merely giving six numbers does not enforce that invariant. Under a passive spatial basis change, source tensor identities support `symmetric_spatial_tensor` for sigma,alpha,z,alpha_in in a fixed frame; no finite-spin transport is implied.

## Temporal integration, initialization and events

Supply complete sigma,e,alpha,fabric,alpha_in and complete resolved parameters. v0.3 `explicit_state/examples_only/domain_and_initial_checks` means no silent adoption of illustrative 100kPa or zero-memory values. An arbitrary stress and density do not identify preparation or prior loading processes. Starting alpha_in=alpha gives zero denominator, so initial-state acceptance requires an explicitly scoped finite-product/regular-limit policy; it cannot be solved by dropping the memory field. Initial fabric zero is a named preparation assumption, not a universal paper condition.

Keep the source unresolved cases separate: initial loading; elastic unloading/re-entry; a change in multiaxial direction; nested reversal/reloading; zero-distance initiation and simultaneous-zero hardening. For each, the missing 1986 definitions include conjugate coordinates, image-point motion, normal choice and stored process history. The condition at exact equality and its directional continuation are not inferred from the strict-negative phrase. A discrete endpoint predicate is not evidence of event location along the path.

A proposed numerical contract must specify event isolation, one-sided branches, memory updates, state ordering and tangent treatment. Trial calculations read the same committed parent; commit all accepted persistent history together; restore the complete parent after failure, including memory and fabric. These are software requirements, not attributed to either paper. Cutback must not commit an earlier tentative process update. The existing parent-reset algorithm freezes its selected anchor across internal substeps and can depend on caller path partitioning; the fixed-memory variant never updates it. Both remain explicit research variants.

At zero imposed strain, a rate-independent smooth regular branch has no new deformation-driven evolution. That does not make the singular original expression `0/0` at initiation defined or authorize a reset on a hold. A physical-time creep/relaxation law cannot be inferred. Tangents through event selection are generally branch-dependent; a smooth residual AD Jacobian with frozen memory is not the complete update tangent across reversal/yield events.

## Independent checks and handoff

Run `python3 -B docs/ingestion/sanisand-2004/check_conditional_mapping.py` after integration, or run the same script at its staged path. Three exact-rational cases verify the conditional distance identity and supply witnesses that moving conjugate images can produce a different denominator or even a different sign. This is new minimal algebra, not a rerun of existing trajectories and not an attribution of assumed coordinates to unavailable 1986 definitions. [results.json](results.json) preserves the observations; no native/Wasm/author-code execution took place.

Files: README.md, sources.json, crosswalk.json, check_conditional_mapping.py, results.json, manifest.json. Manifest hashes only this immutable packet; relevant private source bytes are pinned in sources.json. Mutable AGENTS.md/implementation-board bytes are not equation dependencies.

**Blocker SAN1986-SOURCE:** readable exact Part I pp966-987 unavailable through the checked routes. Smallest next action: obtain an institutional/library or author/user-provided copy, record private byte hash/version, then visually inspect the complete conjugacy/loading-process pages before choosing equations or events. No missing equation/page numbers are guessed. After acquisition, compare scalar, multiaxial, elastic-re-entry, nested-reversal and zero-distance rules against 2004 Eq24, keeping image-motion terms explicit. Event-location and algorithm-review tasks follow separately.

Source completeness: partial, not source-complete. Executable support: existing named research variants only; none added. Numerical verification here: three conditional exact algebra witnesses only. Scientific review/admission: open. No model promotion, shared edits, builds, commits, push or deployment.
