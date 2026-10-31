# duncan-chang-1970 - acquisition and closure-gap packet

Task ID: ING-duncan-chang-1970
Owner / date: review_igs97 / 2026-10-31
Scope: acquire the original formulation, separate later variants and identify exact source/schema/integration gaps. **Blocked at original full-text acquisition; this is not source-complete ingestion.**

## Identity and sources

The verified target is James M. Duncan and Chin-Yung Chang (1970), *Nonlinear Analysis of Stress and Strain in Soils*, Journal of the Soil Mechanics and Foundations Division 96(5), 1629-1653, September 1970. The [publisher record](https://ascelibrary.com/doi/10.1061/JSFEAQ.0001458), [DOI](https://doi.org/10.1061/JSFEAQ.0001458) and [publisher issue contents](https://ascelibrary.com/toc/jsfeaq/96/5) identify the same article. The publisher's online date in 2021 is digitization metadata, not a new constitutive version.

A separate [1971 erratum](https://doi.org/10.1061/JSFEAQ.0001706) by the same authors is listed in volume97(11), p1597, November 1971. The [publisher correction page](https://ascelibrary.com/doi/10.1061/JSFEAQ.0001706) labels it free access. Its correction text was not acquired, so this packet does not state which equation, example or discussion it changes. Original-only and original-plus-correction identities must remain distinguishable until that text is inspected.

No original or correction PDF bytes were received. Their byte lengths and SHA256 values are therefore null in [source-audit.json](source-audit.json), not invented hashes. No original page/equation was visually verified. The PDF skill was read in preparation, but there was no received PDF to render. Bibliographic HTML inspection is not visual equation inspection.

The filename inventory of Downloads and the existing private source directory was searched first. No matching Duncan/Chang/hyperbolic/nonlinear-analysis original was found by those patterns; arbitrarily named PDFs were not exhaustively content-indexed. Publisher PDF/EPDF routes failed in the web tool. Local Python HTTPS requests failed at DNS resolution, which establishes neither a paywall nor the absence of an accessible copy. Targeted Berkeley, eScholarship, Virginia Tech and NIST searches returned later literature or reference lists rather than the exact original. The audit records these as a bounded search, not an exhaustive absence claim.

A [DIANA publication page](https://dianafea.com/publication/nonlinear-analysis-of-stress-and-strain-in-soils/) offers a request form, not directly readable original equations. No request was submitted and no author/vendor was contacted. Unverified third-party upload snippets were not used for transcription. Current publisher access options and prices are not needed for this packet and are not retained as a stable access guarantee.

## Existing work and gaps

The [live board](../../../IMPLEMENTATION_PLAN.md) assigns this original-source task. The [catalogue](../../../catalogue/manifest.json) and [historical queue](../../../catalogue/research-queues/parallel-source-queue-2026-10-31.json) already identify the DOI and original-versus-three-dimensional-closure gap. This packet leaves those files untouched and adds a reproducible identity/access receipt, a correction dependency and a typed closure-question ledger.

No currently inspected original source settles the requested loading, unloading/reloading, lateral/volumetric closure, parameters or history. Familiar formulas in textbooks, later manuals and software are not substitutes for this specific article. Likewise, a triaxial data fit does not alone establish a three-dimensional tensor action. This packet neither certifies the original as triaxial-only nor asserts a complete3D original; the relevant full text is missing.

## Equations and schema crosswalk

No constitutive equation is transcribed or proposed as an executable schema. The [machine-readable ledger](schema-integration-ledger.json) separates required source evidence from future schema requirements.

| Required original evidence | Quantity to pin | Consequence for a future schema | Current status |
| --- | --- | --- | --- |
| Primary-loading equations and stress/strain definitions | Full test-path relation and initial slope | Separate relation, tangent and secant observables | Unavailable |
| Pressure dependence and normalization | Stress-dependent modulus and calibration exponent | Units, dimensionless ratios and positive-domain guards | Unavailable |
| Unloading/reloading text and figures | Modulus, event predicate, memory and rejoin rule | Named branches and committed history | Unavailable |
| Lateral/volume closure and any corrected passage | Poisson/compliance or bulk response | Complete admissible stiffness action | Unavailable |
| Strength/asymptote definitions | Failure stress versus fitted ultimate asymptote | Separate quantities, endpoint and postfailure domain | Unavailable |
| Original calibration procedure and tables | Parameter names, units, values and valid conditions | Source-located calibration separate from defaults | Unavailable |
| Triaxial, plane-strain and FE derivation | Supported path, dimensionality, principal-stress assumptions | Declare exact supported domain before3D generalization | Unavailable |
| Initial-state and preparation description | Reference stress, strain origin and preloading | Explicit initialized state and history | Unavailable |
| 1971 erratum p1597 | Corrected content and relation to1970 | Versioned correction record | Identity verified; content unavailable |

Sign, total/effective stress, shear ordering and small/finite strain conventions remain unverified. No Atlas Mandel conversion, pressure cutoff, constant Poisson ratio, tensile branch, elastic/plastic split or fabricated maximum-stress state is selected. No parameter count or default set is admitted from a later implementation.

## Temporal integration and transactions

The original's rate-versus-incremental form, independent path variable and use of loading history remain unavailable. Physical-time independence, creep during a hold and zero-increment identity are not certified from the title or abstract. A future implementation must explicitly distinguish a physical stress-strain tangent from a finite-step secant and from the numerical algorithmic Jacobian.

The following are Atlas design requirements for any later implementation, not claims about unseen source instructions. Each trial must read immutable committed stress, branch and history; successful updates commit them atomically; failure or cutback restores the entire parent. The recorder must retain actual stress/strain constraints, units, path and selected source version. A branch decision must be tied to its verified history measure and event ordering. A loading-sign heuristic is not a substitute for a source-defined unloading/reloading condition.

After acquisition, resolve whether the original law defines only constrained test-path increments, a multiaxial incremental compliance, or both. Establish how changing confining stress and principal directions is treated. Do not add arbitrary tensor symmetry, a three-dimensional elastic extension, or physical-time evolution to close an absent equation. These would require a separately named research choice with its own source and fixtures.

## Independent checks

No algebraic or constitutive test is justified without the original equations, so none is fabricated. No compiler, native/Wasm binary, solver or author software was executed. JSON parsing, local relative manifest integrity, explicit-null missing source hashes and absence of trailing whitespace were checked; those are packet-integrity checks only.

Once equations are verified, the smallest useful independent check is to differentiate the primary relation and compare its tangent, initial slope and secant at fixed confining stress. Then verify an unload/reload path from a prepared parent and the exact primary-rejoin condition. Only after those scalar/path rules are pinned should a tensor-action or common-engine finite-path study be proposed. The ledger lists these as future checks, not passed tests.

## Handoff

Owned files: README.md, source-audit.json, schema-integration-ledger.json and manifest.json. All manifest paths are local to this directory. Private network-error notes remain outside the public whitelist; no source text, PDF, render or vendor code is delivered.

The smallest next action is authorized access to the exact1970 article pp1629-1653 and the free-access1971 erratum p1597, then visual equation inspection. Record exact received bytes, source URL, SHA256 and equation locations before populating the ledger. An institutional/author copy with a different pagination or report identity requires an explicit equivalence check. Clarifying discussions and author closure should remain separately identified rather than silently changing the1970 law. The agent has not contacted anyone or assigned acquisition work to the maintainers.

**Source completeness:** blocked at full text; identity and correction identity verified. **Executable support:** none added. **Numerical verification:** none claimed; packet integrity checked. **Scientific admission:** unchanged, not established. No shared schema capability request is made until source equations justify one. The coordinator should retain a blocked ingestion entry or explicitly record this as a bounded acquisition gap report; it must not be marked source-complete.
