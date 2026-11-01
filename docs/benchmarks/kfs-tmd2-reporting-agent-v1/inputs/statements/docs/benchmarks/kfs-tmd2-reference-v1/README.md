# KFS TMD2 source reference and bounded execution checkpoint

1 November 2026. **Reference preparation is complete; numerical reproduction is blocked by the existing laboratory API envelope.** Three frozen native requests (400, 800, 1,600 increments to 25%) each returned `control amplitude exceeds laboratory limit` with zero material points. No model response, convergence result or experimental error can be inferred from these rejections. The original requests, outputs and failed assessment are retained.

## Source reference

The selected case is the loose Karlsruhe fine sand drained triaxial test, nominal initial pressure 100 kPa, relative density 21%, void ratio .975: TMD2 in [Wichtmann & Triantafyllidis 2016, Figure 4 and Tables 2–3](https://doi.org/10.1007/s11440-015-0402-z), compared with the blue VW96+IGS curves in [Wichtmann, Fuentes & Triantafyllidis 2019, Figure 3a,b](https://doi.org/10.1016/j.soildyn.2019.05.001). The [previous selection packet](../kfs-published-case-selection-v1/README.md) pins complete parameters, nominal initialization and source hashes. This is calibration-campaign reproduction, not held-out validation.

[Reference](inputs/reference.json) extracts only two published model polylines from the PDF vector representation: 2,001 vertices each, sampled at 101 uniform axial coordinates over the full 0–25% range. The loose curve is the lowest blue stress curve and highest blue volume curve. [Source audit](source-audit/README.md) independently checks six raster spots, initialization and parameter mapping; all spots agree within one raster pixel. This agent cross-check does not close independent scientific admission.

The frozen envelope includes the complete source polyline over a horizontal window of two full plotted stroke widths, expanded vertically by two widths. Vertical half widths are 6,327.14 Pa for q and .00177160 for volume strain. Adjacent refinement limits are one tenth of those values. These are prospective project precision rules, not author solver tolerances or statistical uncertainty. Source-origin offsets are retained.

The operational coordinate is direct accumulated axial strain and the trace of accumulated normal strain. Static review of the [pinned Niemunis driver mirror](https://github.com/j-machacek/numgeo-hardening-soil-bricks/blob/5c0d98bbd4d186805d40228ba3daeeb223a4a393/src/incremental-driver/incrementalDriver.f) supports this mapping: strain increments are divided uniformly, accumulated, and written directly. Its comments describe logarithmic strain. **Exact historical decks, driver/UMAT version and plotting conversion remain unverified.** The 2016 driver and 2019 Abaqus implementation are separate execution provenance. No finite-strain equivalence, engineering/logarithmic conversion or alternative-convention sweep is claimed. Author code was read, never executed or redistributed.

## Frozen attempt and outcome

[Freeze manifest](inputs/freeze.json) pins ten input/reference/assessment files before compiled observations, with zero material calls at freeze. [Requests](inputs/requests.json) specify all inputs, exact binary64 controls and integration settings; [source pins](inputs/source-pins.json) bind the existing executable, model, source archive and private data. There were exactly three serial native process calls, no builds, fits, model/schema edits, Wasm runs or deployment.

| Requested increments | Requested final axial coordinate | Process status | Completed material points | Outcome |
| --- | --- | --- | --- | --- |
| 400 | .25 | 1 | 0 | Existing amplitude cap |
| 800 | .25 | 1 | 0 | Existing amplitude cap |
| 1,600 | .25 | 1 | 0 | Existing amplitude cap |

The archived and current `cpp/include/atlas/solver.hpp`, line 151, reject non-stress-controlled target amplitudes above .1 before adding the initial point. The coordinator missed this source-visible boundary in preflight. This is an API-range failure, not a constitutive convergence failure. No acceptance bound was changed, test shortened, or fourth solver call made.

The frozen assessor also assumed a nonempty completed prefix. Its original [summary](initial-assessment/summary.json) retains three `IndexError` diagnostics; its false flags mean no pass was obtained, not that a computed curve failed the source envelope. The accompanying initial figure shows only the extracted source and its envelope; it is **not a reproduction result**. A separate post-observation [saved-rejection assessment](rejection-assessment.json) verifies exact inputs, hashes, return codes and empty outputs without modifying the original frozen script or making solver calls.

## Reproduction and rights

Run the saved-evidence check from the repository root:

```sh
python3 docs/benchmarks/kfs-tmd2-reference-v1/check_saved_rejections.py docs/benchmarks/kfs-tmd2-reference-v1
```

It requires only Python's standard library and the bundled receipts. Full source regeneration requires the privately retained, hash-pinned PDFs and `pdftocairo` SVG: run `inputs/extract_reference.py --svg <private-page.svg> --output <fresh-file.json>`. Coordinator regeneration matched the frozen reference byte for byte. The source-audit raster check additionally needs Pillow and its private page render; see its README. Original source PDFs, page SVG/renderings, vendor source and measured rows are excluded. Extracted numerical model-curve coordinates are attributed above; measured-data redistribution remains unreviewed.

`inputs/run_study.py` is the original single-attempt runner; do not rerun as an evidence check. Re-execution requires the pinned local native artifact, a fresh output directory and a separately authorized study. `inputs/assess.py` and its initial outputs remain unchanged. Hash-pinned private paths are historical provenance, not portable dependency promises.

## Smallest next task

Design an explicit research-only path allowance for this fixed 25% operational reconstruction, keeping the interactive laboratory's current envelope. Review its kinematic scope and perform a range preflight before one serial native build. Freeze a distinct follow-up study before running the same three paths; retain this failed attempt. Do not silently raise the shared cap or truncate the published reference. Then deliver the source/model figure, refinement table and descriptive measured-data errors. Exact historical coordinate provenance and independent model review remain separate open gates. No new model, optimizer, generic time integrator or broad backend study is needed.
