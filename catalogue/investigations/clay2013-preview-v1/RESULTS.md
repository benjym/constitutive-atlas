# Clay2013 actual-driver preview v1 — required default gate fails

Both serial one-target native and Wasm collections completed. The [unchanged frozen assessment](assessment.json) fails on the actual browser default in both backends: drained compression,100kPa spherical effective stress,e0=.8,1% axial strain,100steps, original explicit settings. Failure is at the first increment; only the committed initial point is retained. No public candidate is installed and no gate is relaxed.

The ten 10kPa small-amplitude monotonic/cyclic protocol runs pass, with396 accepted caller points/backend across the successful run requests. Zero updates, three negative cases and their recovery checks pass. Maximum independent void-closure error is4.1637138181727096e-10 against1e-6; maximum scaled native/Wasm difference on successful physical channels is2.8978507326692877e-16 against1e-10. Backend agreement does not establish independent equation verification or explain the failed default.

## Additive default-state diagnosis

The distinct [diagnostic collection](default-diagnostics-v1/observations.json) reuses the exact pinned native artifact. Fourteen explicit strain updates—seven radial/axial ratios each at10 and100kPa—succeed with unchanged settings. Thus the frozen failure is not evidence that every update at100kPa fails. Initial rate values in this diagnostic are Python interpretation, separately labelled; they are not an independent compiled-rate oracle.

An [independent spherical specialization](default-diagnostics-v1/analytical-bound.json) of the source equations yields radial stress rate R=A*x+B*y-C*sqrt(x*x+2*y*y), for positive axial rate x and equal radial rates y. At100kPa with the frozen illustrative parameters, A=1208333.3333333335Pa,B=6041666.666666667Pa,C=5377856.783314532Pa. Since C²>B²/2, its maximum over every real y is x*(A-sqrt(C²-B²/2))=-2058236.0484931972Pa*x<0. A differentiable drained path with positive axial rate therefore has no constant-radial-stress tangent at this exact initial state under the selected law/parameters. This does not prove absence of every finite endpoint root, or provide a general admissibility rule for all stress states. The outside-ASBS label alone was not used as a rejection criterion.

The14 source-specialized initial radial rates agree with the interpreter within the diagnostic comparison bound; no compiled acceptance policy was revised. Original study manifests/requests/acceptance/build/runtime/raw receipts are unchanged. Diagnostic scripts/outputs have a separate manifest.

## Next implementation decision

The laboratory currently supplies a universal100kPa confinement while loading the selected model's remaining example fields. This can create an incompatible example. The v0.3 contract already calls all field initial values examples, not preparation prescriptions. Design an explicit, source-labelled model example action that loads the complete declared stress and persistent state together, exposes the selected values and limitations, and preserves manual editing/import. Test that behavior independently before a separately frozen candidate study. Do not relabel the failed100kPa run as a success or imply experimental preparation. Numerical-domain validation alone cannot promise mixed-control solvability.

Scientific admission, experimental calibration, objective transport, high-precision boundary accuracy, source completeness and consistent update tangent remain open. Seven local/five hosted runnable models remain unchanged. No push or deployment.
