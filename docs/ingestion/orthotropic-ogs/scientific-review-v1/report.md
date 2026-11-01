# Independent scientific review: OGS orthotropic elasticity

Decision: **accepted for the bounded native/Wasm material-increment scope below**, 2026-11-02. Reviewer `/root/orthotropic_review` is a separate actual agent run from `/root` (delivery/transcription/backend owner) and `/root/orthotropic_source` (source packet author). I did not author the model or either existing reference. I read sources and constructed a third, separate Decimal80 Cholesky compliance oracle. I executed only source/algebra and saved-output Python checks, no author program, native/Wasm executable or build. Exact candidate SHA256 `60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14`.

The accepted scope is the complete nine-constant three-dimensional infinitesimal elastic law at pinned OGS commit `b5d0f115c75ee74a7cdbfad533625a550a416fda`, constant parameters, aligned fixed material/Cartesian axes, compression-positive Mandel stress/strain, dry total Cauchy stress specialization, through common six-component strain-increment integrate and linearize APIs. Numerical qualification covers the prospectively frozen corpus and source algebra studies; widget bounds do not establish an arbitrary near-singular or extreme-conditioning envelope. This review does not assert atlas integration, packaged browser operation, deployment, experimental calibration/validation, general mixed-control qualification or finite-element host compatibility. Those remain separately evidenced work.

## source_provenance

I inspected complete private `LinearElasticOrthotropic.h/.cpp` and pertinent Kelvin forward/inverse conversion definitions. Exact source receipts identify all seven retained files and their SHA256s, access/version identity, institution URLs and line locators. My checker rehashes all seven originals. The pinned implementation is the formulation source; it is not presented as an original theoretical publication or newer OGS variant. Header constants/reciprocity and cpp compliance/inverse/update/identity-Q branch support all required equations. No equation was inferred from search snippets. Complete source packet accurately distinguishes the aligned branch from OGS local-coordinate functionality.

## equation_fidelity

Header E/G/nu ordering is E1,E2,E3,G12,G23,G13,nu12,nu23,nu13. The implementation constructs S and inverts it, updating previous stress with C times mechanical-strain difference. Candidate residual is the same incremental law. I independently checked all six normal inverse coefficients and their determinant cross-product, all three shear coefficients 2G and their order; none is missing. Reciprocal nu_ji=nu_ij E_j/E_i produces symmetric normal compliance. Candidate uses the full nine-constant law, rather than an isotropic/transversely-isotropic substitute. No handwritten production kernel, empirical regularization or unreported branch was introduced.

## conventions_dimensions

Young/shear constants are Pa, Poisson ratios dimensionless; stress state/residual Pa and infinitesimal increments dimensionless. Kelvin originals explicitly map [xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz], so the DSL's orthonormal Mandel shear factor agrees. The source does not itself label scalar sign or pore/effective stress split: simultaneous compression-positive stress/strain conversion preserves this homogeneous relation, and dry total Cauchy stress is disclosed as the Atlas host specialization. Fixed axes, Q=I, small strain and no objective rate exclude rotating material axes or finite rotations. No physical clock is inferred.

## initialization_domain

Exactly nine parameters and six persistent stress components are complete for this incremental elastic law. All finite prestresses are valid reference states; zero stress is illustrative. No total strain or internal variable is silently discarded. Energy interpretation requires a compatible reference strain, as the packet discloses. Positive E/G, positive determinant and positive pair minors enforce positive-definite compliance; extra pair guards are mathematically redundant, not incorrect. There is no isotropic nu<0.5 restriction. The source-only study checks one admissible nu12=.8 case. Stable-elasticity checks and widget bounds are project domain choices, not falsely attributed OGS checks or a calibrated range. No broad floating-point conditioning claim is approved.

## integration_transactions

The source relation is rate independent with constant coefficients, not a time ODE. Zero increment is hold; no rate, duration, thermal strain, pore pressure, preparation density or undisclosed event enters. Trial state uses committed parent stress; rollback/recovery semantics come from Atlas, not an invented OGS API. Saved backend responses prove six exact full-state holds/backend, three domain rejections with all incoming stress components unchanged/backend, and ten chained calls/backend receiving all six actual prior returned stress components. Four identical recovery requests/backend give exactly identical complete responses, establishing repeatability independent of plotted channels. Invalid CSV/dimensions are rejected before constitutive state creation, and subsequent valid requests succeed. Partition1/2/4 and reversal/zero histories satisfy original gates. Full persistent restart state is stress plus parameters/frame; there is no hidden constitutive history. Constant tangent is source C, with all36 entries checked at four scales/backend. Variable parameters along a history and general mixed-stress host controls are not approved here.

## independent_numerical_evidence

Parent references solve the source compliance by Fraction Gaussian elimination, separately from production cofactors. I independently solve the normal compliance by Decimal80 Cholesky plus direct Kelvin shear and do not import either parent or production implementation. All648 prospective endpoint components and144 tangent values match at float rounding. Both actual saved backends independently pass648 state comparisons and144 tangent comparisons; maximum stress error is9.313225746154785e-10Pa, below unchanged state budget5e-10Pa+2e-11 max(Ei,Gi). Tangent gate remains1e-7Pa+2e-10 max(Ei,Gi). Corpus121/backend includes six independent axes,48 varied parameter/prestress/mixed-increment cases, auxetic and isotropic limits, modulus scales, public mixed shear/reversal/zero, zero/hold, partition1/2/4, derivative checks,13 negative/recovery pairs. Source-only algebra additionally checks128 endpoints/768 residual components,576 exact inverse identities and128 energy values across16 parameter sets, including nu>.5. Backend parity is supporting evidence, not the equation-verification oracle. No acceptance gate was relaxed after results.

## backend_delivery

Saved native and Wasm requests/responses both satisfy original prospective gates. Both embedded describe objects equal the same generated metadata containing the exact model object, schema/profile and catalogue identity. I rehashed the retained native executable, ES module, Wasm and generated metadata against artifacts.json; all four match. Build receipts identify AppleClang21 and Emscripten6.0.8 and serial explicit-target coordinator builds. Freeze-v2 identifies the committed engine and exact source/tool/reference hashes. The first configure/build failure (missing optional scalar-functions include unavailable in that committed engine) remains retained. Conditional include in v2 repaired configuration without model, equations, references or gate changes; successful subsequent builds are separately saved. Native/Wasm parity648 state pairs and144 tangent pairs passes, with max state difference1.1641532182693481e-10Pa. Only the tested integrate/linearize strain-increment APIs are accepted. Browser packaging/live remain E7/E8 and are not inferred from a separate executable.

## applicability_claims

Illustrative constants are visibly identified, not a measured material. The law is reversible elastic anisotropy with no damage, plasticity, viscosity or hidden state. Complete3D does not imply finite strain/rotation, arbitrary axis updates, thermal/poro coupling or arbitrary conditioned parameter stability. Restricted fixed-axis identity is explicit. No experimental comparison/calibration/FE-host validation or general mixed-control claim is made. These limitations are appropriate, and absence of experimental validation does not invalidate the checked mathematical implementation.

## reproducibility_rights

The proposal binds exact candidate, durable source receipts, source study, prospective freezes, raw native/Wasm observations, toolchain/artifact identity, numerical assessments and this reviewer checker/report using repo-relative SHA256 artifacts. Originals remain ignored private files under their BSD-3-Clause terms; no source binary/vendor execution or private asset publication occurred in this review. Public packet links/hashes readable originals. Initial dimensional-zero syntax failure and original configure failure remain identifiable; neither was hidden nor used to change a gate. The coordinator must preserve exact review bytes when copying into the approval registry and keep model metadata unchanged or obtain a new binding/review.

## Reproduction and findings

From repository root:

```
python3 -B docs/ingestion/orthotropic-ogs/scientific-review-v1/check_independent.py docs/ingestion/orthotropic-ogs/execution-v1/native/raw.json docs/ingestion/orthotropic-ogs/execution-v1/wasm-raw.json
```

This source-only saved-output audit rehashes the seven private originals, validates exact model identity and independently checks all numerical state/tangent endpoints. `transactions-identities.json` records my additional direct saved-response comparisons described above. No blocking scientific findings remain. Earlier prospective backend status was pending because evidence did not yet exist; it is now satisfied by actual retained output, not a waived requirement. Parent remains responsible for accepted-record integrity validation, approval registry integration and E6–E8 completion.
