# Implementation status — 2026-10-30

## Delivered foundation

- Restricted tensor expression language, SI dimension/shape checks, structural schemas, Python reference interpretation, deterministic C++ generation and catalogue hashes.
- Five declarative executable formulations: linear isotropic elasticity; nonassociated perfect-plastic Drucker–Prager; Modified Cam Clay; von Wolffersdorff sand hypoplasticity; hypoplasticity + IGS. All require independent source review; IGS remains explicitly draft.
- Native C++20 engine with AD residual Jacobians, implicit complementarity correction, elastic predictor, line search, adaptive midpoint rates, substepping and rollback. Initial plastic states must satisfy declared admissibility checks.
- Axisymmetric oedometer, drained/undrained triaxial, undrained signed-q control and isotropic-strain drivers, with monotonic/sinusoidal histories. No general finite-element or poromechanics solver.
- Structural/language/data/numerical Python tests, separate C++ Jacobian/covariance tests, and native/Wasm parity checks across 25 model/protocol pairs. CI definitions are supplied; hosted CI has not been executed.
- Responsive browser lab with real Wasm execution, plots, equations/source links, editable parameters and initial state, cancellation/resource limits, experiment overlay, and run/result export/import.
- Twenty-entry seed catalogue and generated SQLite view; two auditable Crossref discovery batches containing 50 unscreened records.
- Seventeen locally ingested original Wichtmann tests with raw/member hashes and normalization warnings. Five completed, early-strain drained transfer comparisons using a sourced literature parameter set; no fitting or held-out claims.
- Five-page editable/compiled methods manuscript with generated table and scientific figure. Working draft only; no paper submitted or research release archived.

## Gates that remain open

1. **Six-model proof:** source-complete SANISAND-2004 extraction; declarative load-reversal/history events and initialization; independent numerical reference comparisons. The existing five models do not close this gate.
2. **Representation v1:** event semantics/rollback; general vector/anisotropic fourth-order quantities; explicit physical-time fields; stress-measure/objective-rate declarations. Define extensions only against source-complete examples. Current YAML support is the JSON subset.
3. **Initialisation/tangents:** richer state initialization from consolidation history and a public consistent algorithmic tangent API. Current mixed controls use finite-difference update tangents.
4. **Literature review:** screen/deduplicate discovery records; perform citation tracing; source-pin exact remaining variants; record equation-level provenance and reviewers. Candidate criteria/families are not complete constitutive models.
5. **Twenty executable formulations:** transcribe and independently verify the fifteen research candidates or explicitly revise the shortlist based on source availability and scientific relevance. Do not pad the count with unnamed modifications.
6. **Data breadth:** extract initial/preparation metadata; implement cyclic sand and kaolin importers with reviewed mappings. Original TMU files omit e0; do not invent it. Review redistribution terms before bundling original data anywhere.
7. **Calibration study:** freeze whole-test calibration/held-out splits, objectives, bounds, algorithms, seeds and budgets; reproduce published baselines before fitting; include numerical failures and parameter uncertainty in comparisons.
8. **Scientific release:** establish novelty against MFront and related tools; complete analysis, authorship, independent review and manuscript; archive a reproducible version and obtain a DOI when ready. The private software preview is not that release.

## Known limitations

Verification at handoff: 35 Python tests and the C++ numerical suite pass; 25 native/WebAssembly model/protocol comparisons pass. Local browser checks cover a completed undrained Cam Clay run, catalogue filtering, and exported-run import followed by successful recomputation. The final native build also regenerated all five real-data comparisons and the manuscript. The owner-private website deployment succeeded; its hosted URL presents the expected sign-in gate. Authenticated hosted execution has not been checked.

The early-strain benchmark uses a monotonic ramp and curve interpolation, not exact replay of pauses or nonmonotonic recorded paths. Exactly repeated strain samples use the last observation; reversing histories are rejected. Hypoplastic IGS parameters in the UI are illustrative defaults, not the published KFS baseline used for the base-law demonstration. Numerical agreement among interpreter/native/Wasm paths does not independently establish equation correctness.

The language's current state limit is 24 scalars, and available declared units are `1` and `Pa`. Engine integration tolerances/limits are fixed in this initial version. The no-dependency dense solver replaces the plan's initial Eigen choice for native/Wasm portability. Built-in LaTeX compilation did not return during verification; the supplied PDF was compiled successfully using the installed TeX toolchain and visually inspected instead.
