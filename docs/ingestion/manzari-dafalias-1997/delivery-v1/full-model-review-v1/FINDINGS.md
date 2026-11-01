# Full model independent review v1 — pending E4 completion

Task `REVIEW-md1997-full-model-v1`; reviewer run `/root/md1997_final_review`, a fresh separate run. This run authored neither candidate, source transcription, numerical references, runtime, policies nor actual compiled results. It executed no compiled artifact, build or production kernel. Its owned path is this directory only. Date: 2026-11-02.

**Decision: pending. No full-model approval or E5 completion.** The available scientific evidence supports the bounded formulation below. Required current C++/CI contract execution and current generic-profile regression review remain open. Positive native/Wasm material evidence does not replace them.

Exact reviewed candidate: `delivery-v1/manzari-dafalias-1997-constant-m-be-v1.json`, SHA-256 `28ea763d0d7d059335ad3375476895d551f2e71c9ab81499141db80af0339064`. Eventual approval must bind `models/manzari-dafalias-1997-constant-m-be-v1.json` with exactly these bytes. No registry record has been written.

## source_provenance

Available assessment: pass. Direct visual inspection of the private original title p255 establishes Manzari and Dafalias, Géotechnique 47(2), 255–272 (1997). The persistent DOI is `10.1680/geot.1997.47.2.255`. Readable private screenshots, their hash receipt and OCR are available; they are normal viewer captures, not publisher-PDF bytes. Figure 3 is absent in the viewer; its equations and caption are readable and suffice for the selected law. The historical acquisition-gap packet is superseded by source-v1, not rewritten. I inspected mathematical images pp257–264, p266 extension constants, p270 initialization and p272 appendix, and read the technical source reconciliation and available original text. The 2004 formulation, author software and later model-family names are not equation evidence for this selection.

## equation_fidelity

Available assessment: pass for the exact selected variant. Source Eqs7–9 give the pressure-power moduli and circular cone. The candidate's stress residual is a backward-Euler realization of Eq13. Persistent alpha follows Eqs24/26; the numerator is `abs(b:n)`, and the first source diameter alternative is retained. Negative `b:n` remains possible, correctly allowing softening. Eqs16–21 use the translated stress ratio; the normalized cubic invariant is algebraically equivalent to Eq16. Independent cancellation checks cover 600 nondegenerate directions/scales. The source's loose-state restriction is equivalent to the candidate `psi>0`/negative raw-D override. Constant m is expressly supported on p262 and p264; Appendix A evolution is a separate excluded variant. No 2004 fabric, reversal anchor or saturation terms are imported.

BE endpoint moduli/directions, the off-yield unit direction, zero direction at the origin, Fischer–Burmeister complementarity and fixed-e0 total volume closure are disclosed Atlas numerical choices. The latter extends the printed plastic-volume relation using infinitesimal mass balance; it is not falsely attributed to a numbered source equation. Complementarity sign checks confirm gamma>=0, yield<=0 and zero product. These choices require numerical evidence and are not asserted to reproduce the authors' original integration algorithm.

## conventions_dimensions

Available assessment: pass. Effective stress is explicit in the original; positive compression and volumetric dilation signs agree with the source plots and equations. Pa conversion of 31400 kPa gives 31400000 Pa; reference pressure 160 kPa remains distinct from illustrative atmospheric 100 kPa. Alpha, m, h, D, strain, e and gamma are dimensionless. Mandel contraction preserves the source tensor inner product. The complete v0.3 declaration states incremental residual/strain path, 3D small strain, fixed spatial frame, no objective rate, effective Cauchy stress and compression-positive signs. Finite spin/rotation and physical rate dependence are excluded. Full 3D equation storage is not a claim to numerical qualification of arbitrary 3D plastic histories.

## initialization_domain

Available assessment: pass within declared scope. Sigma, e and alpha are persistent; gamma is a temporary solve multiplier. The exact default is isotropic 160 kPa, e=e0=.65 and alpha=0, strictly inside the yield cone. Source p270 supplies only an approximate initial-alpha relation, so explicit alpha plus admissibility is appropriate. Fixed preparation e0 must persist through replay. Positive p/e, tracefree alpha, yield admissibility, positive compression image, Mc/Me>m and strict hardening-distance denominator are explicit. No guessed low-pressure extension or denominator regularization is installed. UI ranges are input bounds, not verified material calibration ranges; zero slope limits and optional bulk floor are excluded by this candidate's declared parameterization.

## integration_transactions

Available assessment: pass for the qualified interface. The dossier separates the continuous source law from BE/complementarity and path subdivision. It states complete atomic commit, immutable parent during trials/mixed control, failure rollback, temporary multiplier reset and replay with fixed e0. No physical-time aging or hold evolution is introduced. The accepted native and paired reviews inspect all physical states, restart parents, zero/hold, invalid/recovery and forced rollback; AD/FD and branch/partition requirements are assessed within their defined smooth scope. A large caller increment is not promised exact source first-yield location. Plastic reversal/cycles and general changing-direction paths remain excluded.

## independent_numerical_evidence

Available assessment: pass for bounded monotonic paths. The source scalar reference re-derives consistency and loading elimination, uses independent RK4 with analytic elastic yield entry, and imports no Atlas code. Eight dense/loose compression/extension drained/undrained paths and six rotated coaxial interior-Lode paths include full stress/e/alpha/strain checkpoints. Interior paths genuinely test three distinct Lode eigenvalues and shear-bearing storage; they do not prove noncoaxial history behavior. Their refined source-reference differences are far below backend gates. Source hydrostatic integration and elastic return provide analytical anchors.

The resolution-study-v4 policy changes control resolution prospectively to 2048/4096 while preserving source tolerances and requiring both resolutions to pass. Native and Wasm independently reviewed actual reports have 96943 source gates each with zero failures. Native worst normalized error decreases from .5117032268 to .2569231813 and all 86 refinement checks pass. Backend agreement alone is not used as scientific evidence. Original 128/512 failures, initial predictor failures and control derivative failures remain retained; diagnostic-legacy-v8 completing all cases with 216 source-accuracy failures does not convert them into passes. The reviewed generic corrections and higher resolution have distinct study identities.

## backend_delivery

Available assessment: **pending** despite accepted bounded material runs. Native-v5 and Wasm-v5 reviews bind actual artifact/build/source identities, full raw records and request grids; both use the unchanged candidate. Paired evidence has 2204769 passing gates, and all 35 planned material cases complete. The ordinary suite has 15 successes and the one prospectively declared GIS rejection, with complete state preservation. Accepted reviews explicitly refrain from claiming full current generic CI coverage.

Blocking requirements supplied in the dispatch remain: actual corrected source-admissible MD C++ fixture execution; actual strict CI helper positive/negative contracts after the independently blocked v1 is resolved; and current seven-profile regressions (Power, Burgers, SLS, J2, orthotropic, Maxwell, NorSand) with the required independent review of the support/actual receipts. The exact historical Lade/Hill evidence must remain preserved. Source-only acceptance of a fixture or a CI helper cannot establish these runtime outcomes. Final reviewed artifacts must bind the same corrected runtime and intended installation bytes.

## applicability_claims

Available assessment: pass for exact prospective profile/support entry. The supported public examples are monotonic protocols 1/2, target .01, 100 steps, default parameters and initial 160 kPa/e=.65/alpha=0. Bounded hydrostatic protocol4 is supported only within the separately qualified envelope. Oedometer0, axial-stress3 and plastic cycles on 1/2/4 are unavailable as unqualified controls. Earlier narrower scope notes do not override the explicit public-profile-v1 entry. Source cyclic demonstrations are historical behavior claims, not qualification of this BE implementation's full plastic cycles. No experimental validation, general parameter-box guarantee, FE host correctness, finite rotation, arbitrary anisotropic preparation or general noncoaxial plastic history is accepted. Public profile review correctly leaves real browser/UI installation to E6–E8.

## reproducibility_rights

Available assessment: pass for current private-reading/public-derived evidence; final binding pending overall approval. `check_review.py` verifies 222 source/manifest/input/algebra checks with zero failures and no production imports. This includes all source receipt bytes and native/Wasm review input hashes. It independently binds reference, frozen resolution, actual qualification and profile manifests. Source screenshot/OCR bytes remain ignored/private with rights noted; public artifacts contain derived equations, links and receipts rather than copied figures or original measurement arrays. No author binary execution occurred. Actual evidence archives, retained checker failures and raw replay instructions are present. Final review must pin the installed candidate and final E4 receipts, with actual author identities; it must not silently substitute current working-tree files for frozen artifacts.

## Resumption

Coordinator supplies exact final C++ fixture/strict helper executions, current-profile support and runtime receipts plus independent reviews, intended final model path, source commit and author run IDs. Reviewer checks their scientific relevance and exact hashes before issuing a final checklist. No E6–E8 browser or live claim follows from this pending E5 review.

Reproduce available local checks from repository root:

```sh
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/full-model-review-v1/check_review.py
```
