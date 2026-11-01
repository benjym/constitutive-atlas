# TMD2: full-range published model reconstruction

1 November 2026. **All three 0–25% paths pass the frozen source-precision and adjacent-refinement checks.** This is a source-informed operational reconstruction of the loose Karlsruhe fine sand VW96+IGS case, not proof of the exact historical implementation or independent scientific admission.

![Published model and Atlas paths](results/reproduction.png)

## Scope and source

TMD2: initial isotropic effective stress 100 kPa, void ratio .975, fully mobilized isotropic intergranular strain; thirteen published material constants. Sources are [Wichtmann & Triantafyllidis 2016, Tables 2–3/Figure 4](https://doi.org/10.1007/s11440-015-0402-z) and [Wichtmann, Fuentes & Triantafyllidis 2019, Table 1/Figure 3a,b](https://doi.org/10.1016/j.soildyn.2019.05.001). See the [input selection](../kfs-published-case-selection-v1/README.md) and [reference extraction/audit](../kfs-tmd2-reference-v1/README.md) for source locators, exact initial state, parameter mapping and six raster cross-checks.

The reference, its source-stroke envelope and refinement thresholds are **byte-identical to the preceding prospective packet**. The preceding three requests were rejected by the 10% interactive API cap; those [original failures](../kfs-tmd2-reference-v1/rejection-assessment.json) remain unchanged. This distinct study adds an explicit native CLI `run-research-controls` mode permitting strain amplitude up to .25. Ordinary C ABI/browser/CLI calls retain their .1 cap. No constitutive equations, model definitions, integration settings, source bounds or interactive defaults changed.

The coordinate is direct accumulated axial strain and trace of accumulated normal strain, following the source-supported driver reconstruction. Exact 2016/2019 decks, version and plotting conversion remain unavailable. This does not verify finite-strain kinematics. The native output explicitly records `finite_kinematics_verified:false`; this research scope is not importable as an ordinary browser laboratory run without separate handling.

## Frozen numerical results

A separate [freeze](inputs/freeze.json), after the one serial native build and before TMD2 calls, pins inputs, reference, assessor and runner. The compiled model metadata exactly matches the current root IGS record. Three serial single-attempt requests used 400, 800 and 1,600 cumulative increments over the full range. All returned success and retained 401, 801 and 1,601 points. No fitting, parameter adjustment, convention sweep, Wasm build/run or additional TMD2 call was performed.

All 101 comparison coordinates in both channels fall within the frozen publication-stroke envelope at every resolution. This establishes agreement only at the declared publication precision under the qualified operational coordinate.

| Adjacent paths | Maximum q change (Pa) | q limit (Pa) | Maximum volume change | Volume limit |
| --- | ---: | ---: | ---: | ---: |
| 400 → 800 | 16.9391 | 632.7139 | 6.87084e-7 | 1.77160e-4 |
| 800 → 1,600 | 5.61394 | 632.7139 | 5.74396e-7 | 1.77160e-4 |

The 101-point refinement grid is shared with the published-source comparison. These are project numerical limits derived prospectively from source stroke precision, not author solver settings or a proof of order of convergence.

## Descriptive experimental comparison

On 101 uniform coordinates over the measured overlap 0–.249529878, with nominal published initialization, the errors are:

| Increments | q RMSE (kPa) | q MAE (kPa) | q max error (kPa) | Volume RMSE (percentage points) | Volume MAE (percentage points) | Volume max error (percentage points) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 400 | 23.5369 | 16.5073 | 54.1560 | .207738 | .174208 | .452851 |
| 800 | 23.5406 | 16.5093 | 54.1679 | .207739 | .174213 | .452841 |
| 1,600 | 23.5417 | 16.5099 | 54.1712 | .207740 | .174220 | .452803 |

Measurements were already exposed development data, from the source calibration campaign. These errors are not held-out validation, model rankings or uncertainty estimates. Experimental volume is fractional volume change; comparing it to the literal source coordinate carries the unresolved historical conversion caveat. No finite-volume conversion was selected by fitting. Measured rows and measured overlay plots remain private pending reuse review; the committed figure contains only published model coordinates and Atlas results.

## Evidence and reproduction

[Machine-readable summary](results/summary.json) contains every source gate and the physical error metrics. `observations/` retains original stdout, stderr, return codes, controls and commands before interpretation. The [build receipt](build-receipt.json), [source manifest](source-manifest.json), exact source archive and generated metadata bind the executable's provenance. The executable itself remains local; the archive contains only Atlas source, not third-party author code or PDFs.

Five focused laboratory-control tests passed, including an independent analytic elasticity endpoint at .25, ordinary API rejection and one-ulp-above-range rejection. The existing initial-state check also passed. Logs are retained. The initial pre-freeze preparation used the wrong generated-metadata key; the corrected preparation and its timing are recorded in preparation-note.txt. No TMD2 observation or source bound changed as a result. The new assessor also handles an empty prefix and matches experimental results by path ID; the original previous-study assessor/errors remain archived.

To recompute the complete summary and figure without executing the solver, using the private normalized TMD2 file:

```sh
MPLCONFIGDIR=/private/tmp/atlas-plot-cache python3 docs/benchmarks/kfs-tmd2-research-range-v1/inputs/assess.py --observations docs/benchmarks/kfs-tmd2-research-range-v1/observations --data data/normalized/KFS-TMD2.json --output /private/tmp/tmd2-fresh-assessment
```

The data hash is checked. Output must be fresh. A source/reference-only saved-result verification requires no private measurements; use `check_saved.py` here. Rebuilding requires extracting source.tar.gz, configuring CMake and building only `atlas_solver --parallel 1`. Re-execution is a new study, not part of an evidence check; do not run the original runner casually. Exact artifact paths in receipts record this local run, not portable dependency promises.

## Remaining gates

BENCH-01 input freeze is complete for this declared operational coordinate. BENCH-02 has a qualified publication-precision result and its historical-coordinate discrepancy documented; this does not resolve original-code equivalence. Independent equation/scientific review and historical strain conversion remain open. BENCH-03 data acquisition/rights and a portable end-to-end command are still incomplete. The next work should address those delivery/review gates, not enlarge this study into another numerical framework. Nothing was pushed or deployed.
