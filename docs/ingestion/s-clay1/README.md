# s-clay1 - ingestion packet

Task ID: ING-s-clay1
Owner / date: review_sanisand / 2026-10-31
Scope / remaining work: bounded original-publication identity and acquisition review. Original full-text access remains blocked. This is not a source-complete equation extraction or an executable formulation.

## Identity and sources

The intended publication is S.J. Wheeler, Anu Näätänen, Minna Karstunen and Matti Lojander (2003), **An anisotropic elastoplastic model for soft clays**, Canadian Geotechnical Journal40(2),403-418, [DOI10.1139/t02-119](https://doi.org/10.1139/t02-119). Identity is independently confirmed by the author institutional records at [Chalmers](https://research.chalmers.se/en/publication/173097) and [Strathclyde](https://strathprints.strath.ac.uk/3809/) and by [publisher-deposited Crossref metadata](https://api.crossref.org/works/10.1139/T02-119). The sixteen pages are a bibliographic span, not inspected PDF pagination.

**The discovery DOI supplied in the claim and catalogue is wrong for S-CLAY1.** [DOI10.1680/geot.2003.53.1.41](https://doi.org/10.1680/geot.2003.53.1.41) identifies Wheeler, Sharma and Buisson, *Coupling of hydraulic hysteresis and stress-strain behaviour in unsaturated soils*, Géotechnique53(1),41-54. [Its publisher-deposited Crossref record](https://api.crossref.org/works/10.1680/geot.2003.53.1.41) confirms the distinct authors, title and journal. Shared first author/year is not model identity. Coordinator correction of the live discovery link must preserve existing hash-pinned snapshots and historical queues.

[Source receipts](source-receipts.json) pin the four successfully acquired metadata responses with URL, private local path, byte length and SHA-256. These are **metadata hashes**, not original-paper hashes. Original PDF path/hash are null. No original equation was visually inspected. The PDF skill was read before attempted source inspection; no unavailable page was represented as inspected.

Bounded acquisition results:

- All20 top-level Downloads PDFs were first-page text-screened after a filename search. No target DOI/title/name match was found. Opaque filenames were checked rather than presumed unrelated. This does not exhaust every directory on the machine.
- Strathclyde explicitly has no deposited full text. Its request-copy link is an acquisition option, not authorization for contacting anyone; no request was submitted.
- Chalmers exposes bibliography and abstract, with no downloadable original-paper attachment observed. Aalto also has a metadata-only record; its displayed author order/issue metadata differ, so it was not selected for canonical bibliographic ordering.
- Current publisher landing/PDF/epdf, DOI resolver and the old NRC publisher PDF endpoint were tried through primary routes. Publisher PDF, old NRC PDF and resolver returned HTTP403. No authentication or access control was bypassed.
- The Crossref TDM-license link is not evidence of permission to redistribute a publisher PDF or author code. No PDF, source response, rendering or extracted original text is bundled here.

The source abstract confirms that anisotropy and rotational hardening are central, and that the paper addresses initial inclination and two additional constants. It does **not** establish the actual equations, independent state count, normalizations, sign conventions or complete parameter list. Destructuration is described as a limitation in the original abstract; this does not license importing later S-CLAY1S evolution laws.

## Existing work and gaps

Existing discovery entry: `catalogue/manifest.json`, entry `s-clay1`; live task: `IMPLEMENTATION_PLAN.md`, ING-s-clay1. No complete S-CLAY1 definition/source audit was found in the inspected repository dossiers. This packet adds verified bibliographic correction, pinned acquisition receipts and a bounded extraction checklist. It does not reuse the existing Modified Cam Clay definition as proof of S-CLAY1 elasticity or hardening.

Later S-CLAY1S, Creep-SCLAY1S, logarithmic-contractancy extensions and vendor implementations require separate version identities. Their tensor laws, compression/shear measures, Lode choices, numerical regularizations and calibration defaults cannot close the original2003 gate. No later equation is transcribed as an original here.

## Equations and schema crosswalk

| Required original section | Equation / quantity | Schema representation / units | Status / ambiguity |
| --- | --- | --- | --- |
| Yield-surface definition and any generalization | Yield criterion, inclination and size | Exact original invariants and stress powers required | Full text missing; no equation number inferred |
| Flow/loading statement | Plastic potential, multiplier and loading/unloading | Typed residual/flow direction; normalization and signs required | Original associativity/branches unverified |
| Elastic law | Bulk/shear stiffness, strain decomposition | Stress/strain work conjugacy, modulus units and domain | No MCC substitution |
| Size hardening | Preconsolidation/size evolution | Original stress measure and plastic volume measure | Unverified |
| Rotation hardening | Anisotropy evolution | Scalar versus tensor, plastic shear norm and orientation | Unverified; no later S-CLAY1S borrowing |
| Parameter calibration and initial inclination | Constants and initial state | Symbols, units, ranges, K0/OCR/void consistency | Exact procedure/parameter count unavailable |
| General stress and numerical treatment | Scope, domain, spin, critical state and singularities | Explicit declared support and transactional solver contract | Cannot assume full3D/objective continuation |

[Machine-readable crosswalk](crosswalk.json) records ten pending extraction items with null original locators and no guessed typed expressions. Parameter/state lists and scalarized storage count remain null. A general finite-element tensor law cannot be reconstructed safely from a triaxial ellipse alone. No source-derived shared schema extension is requested before the missing laws establish a need.

## Temporal integration and transactions

The following are **Atlas acceptance requirements for a future adapter**, not verified statements about the inaccessible original algorithm:

1. Establish rate/increment versus physical-time semantics from the original. Do not add viscosity, creep or hold evolution from later variants. Define exact zero-increment behavior after the law is known.
2. Record stress and strain signs, effective stress, tensor/shear basis, objective rate/spin support and full3D extension before applying six-component Mandel transport. Triaxial signed q is not a general tensor orientation variable.
3. Caller supplies a fully documented initial state or an explicit preparation history. Initial inclination, yield size/OCR and density must be mutually admissible; no hidden K0 consolidation or guessed anisotropy initialization.
4. Each internal material trial starts from an immutable accepted parent. Candidate plastic multiplier, stress, size, anisotropy and volume updates commit together only after all declared checks succeed. A failed full caller increment returns the exact original parent; intermediate accepted substeps remain trial-local.
5. State evolution must specify simultaneous versus ordered old/new dependencies; do not update anisotropy in place while evaluating another residual from the old parent. Source-provided lagged quantities, if any, must be separated from solver caches.
6. Document loading/unloading, yield entry, softening, critical-state and pressure/anisotropy boundary handling. Numerical tolerances, apex/tension extensions and clipping are independent algorithmic choices requiring explicit evidence.
7. Tangent verification must differentiate the actual accepted integration map, including hardening and preparation semantics. Interpreter/native/Wasm agreement would not independently establish the original transcription.

The original's exact event chronology, zero-load behavior, dimensional scope, return algorithm, consistent tangent and boundary continuations are **unverified because the full text was not inspected**, not claimed absent from the publication.

## Independent checks

No constitutive algebra test is justified without the original equations. `check_packet.py` instead performs four bounded integrity/identity checks: local-relative file hashes; distinct exact publication identities; inaccessible-original flags/empty transcription; all20 first-page screening results with valid byte hashes. It does not contact the network, read private sources, execute author code or certify equations.

Run from any directory:

```sh
python3 /absolute/path/to/docs/ingestion/s-clay1/check_packet.py
```

Retained output is [check-results.json](check-results.json). Private Crossref-response hashes and metadata fields were checked against the acquired bytes before the packet was frozen; these private bytes are not required for the portable packet integrity check.

## Handoff

Public whitelist: `README.md`, `source-receipts.json`, `crosswalk.json`, `check_packet.py`, `check-results.json`, `manifest.json`. The manifest uses names relative to this directory. Private source/receipt responses and helper scripts are outside that whitelist.

Smallest next action: obtain the exact2003 CGJ paper (all403-418 pages, including the original equations, calibration/preparation discussion, any general-stress extension, tables and references) through a lawful subscribed publisher download, library document delivery or a user-supplied copy. Pin exact PDF bytes and visually inspect the mathematical pages before assigning equation numbers or implementing. A separate author manuscript is acceptable only with explicit version/locator differences retained. Do not request a later S-CLAY1S manual as a substitute.

Once acquired, close the ten extraction rows, independently verify an isotropic reduction and a source-defined anisotropy evolution/loading case, then freeze a declarative candidate and a reference protocol before any compiled observations. Full3D closure must be sourced or separately derived/reviewed and named; it cannot be silently attributed to the original.

Current status: **identity verified/correction proposed; original source incomplete; no executable support added; metadata integrity checked; constitutive verification and scientific admission pending**. This packet can close the bounded acquisition/identity subtask only. ING-s-clay1 full ingestion remains blocked on SC-SOURCE-01.
