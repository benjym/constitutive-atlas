# Clay2005 actual-input boundary precision study v1

Task REV-clay2005-boundary-precision-v1; worker clay2013_source_closure; 2026-10-31. This is an independent, source-only numerical diagnostic for the five retained finite-only parity failures and six prospectively selected controls. No builds, compiled calls, Atlas interpreter, existing source-oracle evaluation or material integration were run. No model, domain, reference, budget or support classification changes.

## Frozen inputs and precision policy

`prospective-freeze.json` was written and its SHA256 `0572dfb4a7c3fefbe5935be1ac7b0b9eb46ffbfb1acd0e2e4082bb64f1ad2ca7` sent to the coordinator **before** high-precision evaluation. It pins the retained v3 protocol/model/raw journals/comparison, old source oracle/reference/correction and source corpus. Each selected literal is recorded with its parsed binary64 hexadecimal value and exact integer numerator/denominator. Source calculations reconstruct those integer ratios at each precision, rather than reading decimal strings as ideal real inputs. Off-diagonal Cartesian components divide the exact Mandel input by high-precision sqrt(2). The actual oblique matrix is never replaced by a rotation of an ideal eigenvalue spectrum.

The frozen precisions are 80, 160 and 240 decimal digits. Predeclared convergence gates are scaled seven-rate difference and relative Cartesian det(H) difference <=1e-50 for 80/160 and <=1e-120 for 160/240. The scaled rate metric is max_i |a_i-b_i|/max(1,|a_i|,|b_i|), with separate per-component backend diagnostics. These are precision-convergence checks for new descriptive estimates, **not retroactive source-accuracy gates** for finite-only rows. All eleven cases pass both gates; original41source vectors/budgets remain byte-pinned and unmodified.

`freeze.py` selects exactly the five unique failed IDs from the retained comparison, then six explicit controls: nonisotropic mixed, exact100kPa sphere loading, rotated mixed, safe sphere, oblique-safe and shear-near-positive-interior. The duplicated physical inputs tiny-positive-interior/scaled-positive-1.0 retain both historical identities.

## Source identity and independent route

[Mašín2005, A hypoplastic constitutive model for clays](https://doi.org/10.1002/nag.416), [accepted author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf), 718767bytes/26pages, SHA256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`. The private source remains `/private/tmp/atlas-ingest-clay2005-20261031/private/masin-2005-author.pdf`. This pass re-read the retained source/correction/audit and visually inspected original-source page10 and AppendixC pp24–25 renders using the PDF skill. The script verifies original PDF bytes against the receipt. No copyrighted PDF, page image or extracted text is bundled. Final-publisher equation equivalence remains unverified.

Source p10Eq38 has a **PLUS unloading bracket**; Eq40 and coefficient Eq41 agree with AppendixC83–85. The old minus claim was an Atlas extraction error. This study retains the corrected interpretation and does not guess another sign or source version.

`study.py` independently implements Cartesian AppendixC73–85 using standard-library Decimal arithmetic, Taylor sin/cos, and Decimal sqrt/ln/exp. It imports neither Atlas nor the old reference. The existing Cartesian oracle was read to understand prior scope, not executed or used to generate estimates. Inputs map source T=-sigma and D=-E, zero spin. The source fourth-order stiffness acts as 3[c1 X+c2 a² H(H:X)]; source74's negative flow and the stress/strain sign mapping give sigma'=fs[L:E+fd Y L:mhat ||E||]. Void evolution is -(1+e)tr(E). Five source parameters and the actual p_ref are used; the other numerical metadata are not material coefficients. No project support guard is reclassified by the source calculation; it checks strict Cartesian SPD and finite source branches for these selected actual inputs only.

The source Y is evaluated through Cartesian invariants of T=-sigma/p. Dividing T by positive p leaves Eq78's homogeneous cubic ratio unchanged. The cofactor determinant is computed from these actual Cartesian tensors at each precision. The invariant diagnostic det(H)=1/27-j2/6+tr(Hdev³)/3 is calculated separately for cancellation analysis, not used as the source-rate denominator. Exact sphere is selected only by exact stored stress equalities, not a tolerance. Adjacent binary64 perturbations replace one nonzero stored Mandel stress entry at a time up/down; rates at240digits quantify that particular input-neighbour sensitivity without claiming a global derivative/error bound.

## Results

All rates and determinant diagnostics, their 80/160/240 versions and explicit differences are in `results.json`. Stable controls have maximum scaled retained-backend/source differences about1e-17 to3e-15. The near-boundary cases differ substantially:

| Actual retained case | det(H), about | Invariant determinant cancellation | Cartesian cofactor cancellation | Original native/source | Original Wasm/source | Contraction-off/source, both |
|---|---:|---:|---:|---:|---:|---:|
| tiny-positive-interior |1.25e-11|5.93e9|1|2.22e-7|8.31e-8|8.31e-8|
| margin-above |1.005e-14|7.37e12|1|1.32e-3|1.49e-3|1.49e-3|
| scaled-positive-1.0 |1.25e-11|5.93e9|1|2.22e-7|8.31e-8|8.31e-8|
| scaled-positive-1e+50 |1.25e-11|5.93e9|1|1.03e-6|4.72e-7|4.72e-7|
| oblique-tiny-positive |7.407e-12|1.00e10|8.89e9|5.03e-7|4.42e-7|4.42e-7|
| shear-near-positive-interior, control |7.407e-12|1.00e10|1.00e10|9.22e-8|9.22e-8|9.22e-8|

The three source-error columns use the maximum componentwise scaled metric above, not percentages or relative errors in a single chosen component. At margin-above1.49e-3 is about0.149%. Output magnitudes differ greatly: the scaled1e50 case has source stress rates about1e105. Unit scaling is preserved; no idealized spectrum substitutes for its rounded binary64 input.

Cancellation is sum of absolute terms divided by absolute result: invariant terms1/27,-j2/6,j3/3 versus the three Cartesian cofactor-expansion terms. It measures arithmetic amplification for those decompositions, not an interval error certificate. The Frobenius determinant relative derivative amplification ||sigma||F ||adj(sigma)||F/|det sigma| is about1.41e10 for tiny-positive,1.76e13 at margin-above and2.24e10 for oblique/shear-near, versus3–3.7 for regular controls. This normwise measure must not be mistaken for componentwise input sensitivity. Adjacent nonzero diagonal input perturbations change rates only about1e-15 for the diagonal cases; oblique/shear-near stored-input perturbations reach about1.02e-6/1.57e-6. Those different directions are explicit in the JSON, not an uncertainty allowance excusing evaluation error at the fixed actual input.

## Additive contraction-disabled comparison

After the original precision freeze and calculation, the coordinator supplied `catalogue/investigations/clay2005-boundary-parity-v1/comparison.json`. `additive-freeze.json` separately pins those new retained files and the already-computed source results; `compare_additive.py` first requires identical literal corpus arguments. It performs **no new source evaluation or acceptance change**. `additive-results.json` records that the new study passes its original parity gates and that the five formerly failed case rate vectors are now identical across backends. Their common source errors remain those in the final column above. The shear-near control already demonstrated equal-but-inaccurate outputs in the original study. Thus contraction control repairs the observed reproducibility failure, without establishing boundary source accuracy.

## Why a naive Cartesian cofactor rewrite is insufficiently verified

The diagonal stress determinant has no Cartesian cancellation, so changing its expression could improve these examples. That is not a general remedy for retained oblique states: Cartesian cofactor cancellation remains8.89e9–1e10. `cofactor-freeze.json` prospectively identifies an additive **scalar binary64** cofactor diagnostic, separate from both source estimates and compiled studies. `cofactor_diagnostic.py` maps the actual Mandel input using binary64 sqrt(2), scales the Cartesian matrix, then evaluates ordinary cofactors. `cofactor-results.json` finds relative determinant errors1.414e-7 for oblique-tiny-positive and6.833e-7 for shear-near, versus0 or about4e-17 for the diagonal witnesses. This includes mapping, normalization and determinant arithmetic; it is not a causal isolation of one rounding operation or a complete source-rate test. It is enough to reject the assumption that naive cofactors automatically deliver1e-10 source-rate accuracy here. No1e-10 source-accuracy gate was previously declared for these finite-only cases.

The Mandel determinant contains an irrational cross-product coefficient. Rounding sqrt(2) or its reciprocal before cancellation can itself be amplified; compensation of only the final additions may therefore be inadequate. Direct Cartesian cofactors, a changed evaluation order, or contraction disabling alone cannot be asserted to meet both the unchanged parity budget and a future prospective source-accuracy policy.

## Minimum repair and remaining gates

The smallest justified implementation project is a **generic robust symmetric-tensor determinant** with explicit Mandel semantics, scaled arithmetic and sufficient compensation/expansion or higher-precision fallback for both products and the irrational cross coefficient. Establish an error assessment for the actual stored tensor; do not silently change support, project to SPD, clip determinants, or add an empirical stress floor. Its primal result and branch choices need native/Wasm trace consistency; generic material AD must differentiate the same mathematical determinant, with cofactor-based derivative identities and trace/branch tests, without differentiating a numerical compensation correction as a new constitutive law. The coordinator should separately scope and freeze that implementation and test corpus before compiled observation. No handwritten clay-specific kernel is warranted.

Use actual-input highprecision references for diagonal and oblique/rank-near cases across scales, cancellation and rotated-tensor witnesses, plus existing invalid/support/recovery cases. Retain all41original source budgets and the original1e-10 cross-backend gate. Declare any new source-accuracy budgets prospectively, after source review and before the repaired compiled outputs; do not retrofit them into this historical study. Reassess all sensitive quantities (Y, Lode/F, density/stiffness, resulting seven-rate vector), rather than testing only a determinant in isolation. AD, finite integration, frame transport, calibrated preparation and experiments remain separate work.

Precision agreement is strong evidence of numerical convergence for this source transcription, not an interval enclosure, proof of all-SPD accuracy, manuscript/publisher equivalence or independent peer admission. The same source algebra is used across precisions; a common transcription error could converge. The tested controls and source-page reinspection limit that risk without removing it. The optional Taylor/Decimal implementation is not a formally certified arbitrary-precision library. The study covers these selected actual inputs, not an exhaustive domain.

## Reproduction and receipts

All scripts require fresh output paths and standard Python3 only. Once the packet is installed, replace PACKET with its absolute directory; keep ROOT the repository root:

```sh
python3 -B "$PACKET/study.py" --root "$ROOT" --packet "$PACKET" --output /private/tmp/fresh-clay2005-precision.json
python3 -B "$PACKET/compare_additive.py" --root "$ROOT" --packet "$PACKET" --output /private/tmp/fresh-clay2005-additive-comparison.json
python3 -B "$PACKET/cofactor_diagnostic.py" --packet "$PACKET" --output /private/tmp/fresh-clay2005-cofactor.json
```

The private source PDF must remain at the recorded receipt path, or an exactly matching private copy must be made available there; no network access is required. Existing freeze files must not be regenerated over their originals. `manifest.json` pins every packet file and numerical study source identities. The original failed study, successful contraction diagnostic,41reference vectors and all budgets remain untouched. No failures occurred in the new precision/convergence checks; both old numerical failures and their distinct follow-up identities are retained in the pinned source evidence.
