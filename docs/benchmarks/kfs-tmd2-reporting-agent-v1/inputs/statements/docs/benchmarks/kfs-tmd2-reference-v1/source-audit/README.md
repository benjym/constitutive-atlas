# KFS TMD2 bounded source-reference audit v1

1 November 2026. Source-only review, before material observations. Own output is this staging directory. No Atlas evaluator, author code, compiled artifact, solver or helper was executed. This is a bounded technical cross-check, not independent scientific-authorship admission.

## Findings

The loose model curves in 2019 Figure 3a,b are the lowest-stress blue curve and highest-volume blue curve. Six independent 300 dpi raster spot measurements at axial 5%, 10%, 20% support the parent's selected vector chains: maximum center discrepancy is 0.899 kPa and 0.02115 volumetric percentage points, each less than one raster pixel. Three blue runs occur at each sampled column. This extraction did not read the SVG or import the parent extractor. It uses the parent's frame coordinates; frame labels and endpoint calibration were independently visually checked against the rendered PDF, rather than independently refitted at subpixel resolution. The tests support chain selection, not every vector vertex.

The q axes span 0..25% and 0..500 kPa; volume axes span 0..25% and -12..+2 percentage points. The proposed two-full-stroke construction recomputes to horizontal half widths 0.002314622312837401 (q) / 0.002313645897177734 (volume) in strain, vertical half widths 6327.138689336569 Pa / 0.0017715988330142395 strain. A horizontal-window envelope, then vertical expansion, is appropriate; replacing this by a vertical-only tolerance would miss steep early curves. Clip the horizontal window only to the published domain; retain the plotted origin offset. Fixed 101 points at 0.0025 strain spacing is a declared comparison grid, not evidence of independent measurement resolution. The refinement limit of one tenth of the vertical half width is a prospective project numerical requirement, not an author setting.

These bounds describe digitization uncertainty under the chosen coordinate mapping. They cannot establish historical strain conversion, quantify parameter uncertainty, or justify fitting. Do not use them to absorb an unverified finite-strain transformation.

## Source and initialization cross-check

Visually inspected 2019 PDF pages 3–4 and 2016 pages 4–5, and text-inspected the 2016 page 3 history passage. The 2016 Table 3 / Figure 4 match is TMD2: p0=100 kPa, relative density .21, initial void ratio .975. 2019 Figure 3 uses this same loose pressure/density pair; it is a published calibration reproduction, not held-out validation.

Both parameter tables agree: phi_c=33.1 degrees, hs=4000 MPa, n=.27, ed0=.677, ec0=1.054, ei0=1.212, alpha=.14, beta=2.5, R=1e-4, mR=2.2, mT=1.1, beta_r=.1, chi=5.5. The column order mR/mT reverses between tables; map symbols, not positions. p_ref is a project scale, not an additional published material constant.

Published fully mobilized isotropic history h_ii=-R/sqrt(3) under source tension-positive convention becomes +R/sqrt(3) under Atlas compression-positive convention. All shears vanish; nominal stress is 100000 I and e=.975. Do not silently substitute the measured first point. Nothing in this review changes or promotes the model record.

## Coordinate evidence and unresolved limit

Read-only mirrored incrementalDriver.f: *TriaxialE1 maps to *LinearLoad (lines 392–399); lines 892–903 divide deltaLoad by ninc for dstran and explicitly comment logarithmic strain; lines 632 and 664–668 accumulate and output stran. This supports direct accumulated driver coordinates and outputting their normal trace as an operational reconstruction. It does not identify the exact 2016 or 2019 deck, driver revision, Abaqus UMAT setup, or historical plotting conversion. Uniform vector x vertices are corroboration of a uniformly sampled plotted coordinate, not a unique proof of the deck or conversion. The e1/ev expressions around lines 1301–1304 are EXITNOW condition evaluation, not plotting output, and should not be cited as proof of plotting conversion.

Thus direct axial accumulation 0..0.25 and summed normal strain are defensible as explicitly scoped source-informed operational coordinates. The original historical conversion remains open. Do not claim original-code equivalence or finite-strain admission. If exact historical replication is the gate, the deck/plotting provenance remains a blocker; if an explicitly qualified operational reconstruction is the gate, no curve-selection/parameter/history blocker was found.

## Reproduction and preserved failure

Run `python3 check_source.py` with Pillow and the private rendered source at private/2019-p4-300.png. Render using `pdftoppm -f 4 -l 4 -r 300 -png <2019 PDF> <output prefix>` and rename that page image. The script also reads the pinned parent reference path; sources.json records exact bytes. It only performs image/source analysis. Result: six raster comparisons plus four width recomputations pass. The first script attempt used the wrong parent channel key 'volume'; retained-initial-check_source.py and retained-initial-failure.txt preserve that tooling failure. Correction changes the key to 'volumetric_strain'; no bounds or numerical policy changed.

Private PDFs and renderings are excluded from this public packet manifest. They remain local reproduction dependencies. Sources.json pins them; the manifest pins only this small audit's deliverables. Smallest next action: parent freezes the qualified coordinate statement, extracted reference, bounds and input hashes before the already scoped serial material paths. No convention sweep or engine expansion is requested.
