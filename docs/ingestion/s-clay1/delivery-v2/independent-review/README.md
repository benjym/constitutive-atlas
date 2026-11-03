# S-CLAY1 independent source-gate review v2

Reviewer run `/root/norsand_source_review`, task `REVIEW-s-clay1-source-v2`, 2026-11-02. Separate source-review run; no implementation, model, compiler, native/Wasm execution, build, author-code execution, external communication or remote mutation. The reviewer owns only this directory. Decision: **the acquired presentation supports useful partial source progress; exact original-law completeness remains blocked**. This is not E5 approval.

## Source identity and access

The target remains Wheeler, Näätänen, Karstunen and Lojander (2003), CGJ 40(2), 403–418, DOI `10.1139/t02-119`. The old `10.1680/geot.2003.53.1.41` identifies a different unsaturated-soil paper. Retain historical discovery records rather than silently rewriting pinned inputs.

I verified the private presentation against acquisition-v2: 1,500,464 bytes, SHA-256 `da7741b365c6d33d8877a9fde0e989b558f99f3f3864335f46061839f7927990`, from [the Karstunen presentation](https://www.mycrisp.com/cugm2003/m-karstunen.pdf). It has 16 PDF pages; the last contains one references slide. PDF metadata identifies `CRISPMK-2003.ppt` and creation in September 2003, but records “Amir Rahim” in its author field. Presenter identification comes from the visible title slide, not that metadata. This is a separate coauthor presentation, not the original 16 journal pages or an accepted manuscript. Its final reference 7 omits Lojander and varies the title despite matching journal volume/pages; the presentation bibliography must not replace canonical journal identity.

The retained publisher access responses are non-PDF 403 results. I checked the retained OpenAlex, Semantic Scholar and institutional responses as acquisition evidence, not equations. Independent bounded exact-title/DOI searches yielded institutional metadata and later formulations, not an accessible original or accepted manuscript. Fresh reads of [Strathprints](https://strathprints.strath.ac.uk/3809/) and [Aalto](https://research.aalto.fi/en/publications/an-anisotropic-elastoplastic-model-for-soft-clays/) exposed no original download; Strathprints explicitly reports no full text and offers a request-copy route. No request was sent. This does not prove the original is unavailable under subscribed or user-held access, and no exhaustive global search is claimed. The Downloads first-page screening is similarly bounded; absence of a filter match is not proof of absence from all local storage.

## Independent visual findings

After reading the PDF skill, I rendered and inspected PDF pages 2, 3, 4, 5, 8, 9, 10 and 16. No extracted radical or superscript was accepted without checking an image.

| Presentation locator | Supported finding | Remaining limit |
| --- | --- | --- |
| PDF 2 lower; PDF 3 upper | Full symmetric stress/fabric yield expression; deviatoric vectors use square-root-of-two shear entries. The full fabric has trace 3 and its deviatoric part has trace zero. | No automatic source-original, frame, spin or finite-strain claim. |
| PDF 3 lower | Size hardening uses specific-volume factor and lambda-minus-kappa denominator. Rotation has different volumetric and shear targets, with coefficients 3/4 and 1/3; volumetric contribution has a positive-part bracket. | Plastic shear measure, sign conventions and complete loading/flow closure require reconciliation. |
| PDF 5 lower; PDF 9 upper | Explicit triaxial yield and cross-anisotropic fabric vector `[-alpha/3, 2alpha/3, -alpha/3, 0, 0, 0]`, with y as the axial direction. Its invariant gives alpha squared. | Do not substitute scalar alpha for a general orientation field. |
| PDF 8 lower | Initial inclination and beta are estimated through friction angle; mu has an empirical estimate involving the K0 compression slope. | These are hints, not the complete original calibration equations or universal defaults. Initial inclination is an initial-state quantity. |
| PDF 9 lower | Formal elastoplastic tangent involving both a potential Q and yield F, plus size/rotation hardening contributions. The displayed shear contribution includes a square-root-of-2/3 norm factor. | Q and F are written separately: this slide alone does not establish Q=F or a complete potential. The tangent does not specify the elastic law or finite-step algorithm. |
| PDF 10 lower | A benchmark lists S-CLAY1 values including lambda 0.7, kappa 0.03, Poisson ratio 0.2, M 1.2, initial inclination 0.46, beta 0.76 and mu 20. | These are an illustrative case, not general ranges, defaults, or an independent calibration dataset. |

The separate S-CLAY1S bonding/destructuration additions must stay excluded from the requested original S-CLAY1 identity. Embankment time axes and consolidation results do not establish constitutive viscosity, creep or intrinsic physical-time dependence. Experimental curves shown in slides are source comparisons, not newly verified held-out validation.

## Algebra and unresolved gates

I independently constructed [check_algebra.py](check_algebra.py) before reading the coordinator's algebra implementation. It embeds triaxial invariants in a three-dimensional trace-free tensor and checks the scalar yield expression by exact rational arithmetic. It also supplies a nonzero rotation counterexample starting from zero fabric. The 28 exact assertions pass; see [algebra-results.json](algebra-results.json). These establish presentation identities and one evolution implication, not integration, journal fidelity or full-law qualification.

Zero fabric reduces the instantaneous yield surface to Modified Cam Clay. It is not generally an invariant full-model reduction: the displayed rotation law produces nonzero fabric at deviatoric stress. A full MCC limit needs additional restrictions, separately stated. The coordinator's 110-assertion source-geometry checker is appropriately bounded if it keeps its stated exclusion of evolution, elasticity, finite trajectories and original-journal verification.

Blocking items remain: readable complete original equations/prose and exact retained bytes; journal-versus-presentation reconciliation; elastic law and plastic potential/loading rule; complete plastic strain norm/sign and work-conjugacy conventions; initialization/OCR/inclination and calibration equations; admissibility and branch bounds; complete evolution/integration contract. The presentation tangent narrows a shear-norm question but does not resolve the entire contract. No source-derived engine capability defect has yet been demonstrated. A model cannot be created by appending guessed MCC elasticity or later S-CLAY1S equations.

The public profile can describe anisotropy, evolving yield inclination and literature examples with local provenance, but must not promise runnable laboratory support, general initialization defaults or complete journal verification. E1 remains open/blocked; E2 is partial and cannot pass; E3–E8 remain unstarted. E0 completion belongs to the coordinator after checking its claimed scope/ledger. Neither this source review nor algebra passes approve the model.

Smallest next action: obtain a lawful complete original or author accepted manuscript through user/institutional access or a concrete publisher/repository route; retain exact bytes/hash, inspect pp. 403–418, reconcile all presentation equations and complete missing contract/calibration sections. A request-copy link is a possible next acquisition route, not a copy already obtained or permission to contact the author.

## Reproduction and cleanup

Run `python3 -B docs/ingestion/s-clay1/delivery-v2/independent-review/check_algebra.py`. Exact reviewed inputs and private acquisition-byte checks are recorded in `review.json`; packet/ledger bindings, if present, are snapshots allowing later coordinator integration. Private source originals remain with the lead. Reviewer-generated temporary text/page PNGs in `/private/tmp` are disposable derivations and are removed after inspection; they contain no unique evidence. This run creates no server, build directory or worktree.
