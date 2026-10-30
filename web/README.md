# Constitutive Atlas browser distribution

This directory contains the static material laboratory in the main GitHub repository. The authoritative model definitions, compiler, C++ engine, tests, data tools and manuscript live in the parent research workspace.

Run `python3 tools/build_web.py` from that workspace after native/Wasm tests. It copies this UI, the compiled engine and canonical catalogue into `dist/`. The catalogue hash in the runtime and browser metadata must agree. GitHub Actions publishes `dist/` to GitHub Pages after native and Wasm verification. All asset URLs are relative to support the `/constitutive-atlas/` project path. Source references, model JSON definitions, and schemas are bundled; raw measurements are excluded. The optional Sites publication helper also packages `dist/` using `.openai/hosting.json`.

The [public GitHub Pages laboratory](https://benjym.github.io/constitutive-atlas/) is an experimental research preview. Five models are executable; the 32-entry catalogue includes research candidates. Public measurement assets are generated only for approved archive revisions, and no model is described as independently source-reviewed or experimentally validated.

For Sites publication, use a separate Sites checkout and copy this directory plus the freshly generated `dist/` into it. Do not initialize another Git repository inside `web/`. The pre-migration Sites history is preserved locally in `.local/sites-source.git` at the research repository root.

## Developer build and local preview

Requires Node.js 24 (specified in `.nvmrc`) and Emscripten (tested with 6.0.8). GitHub Actions reads the same Node version file. From the repository root:

```sh
EM_CACHE="$PWD/.cache/emscripten" emcmake cmake -S . -B build-wasm -DCMAKE_BUILD_TYPE=Release
EM_CACHE="$PWD/.cache/emscripten" cmake --build build-wasm --parallel 2
node tools/test_wasm.mjs
python3 tools/build_web.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory web/dist
```

Open <http://127.0.0.1:8765> for development. The native build must exist before running the parity check. Packaging rejects stale model definitions.

## Live laboratory controls

The laboratory recalculates automatically when a model, protocol, slider or numeric field changes. Rapid edits are coalesced into updates every 100 ms; the Wasm worker is reused and only the latest settings may replace the plots. Sliders supplement precise numeric inputs, with logarithmic scaling for wide positive parameter ranges. Numeric inputs retain their declared bounds even when a slider uses a narrower exploration range.

Initial state details, material parameters, solver settings, measurements and sources expand on demand. Reset restores the current model’s defaults and recalculates. Invalid inputs pause updates with an inline explanation; exports remain disabled until a response matches the current settings. Cyclic presets increase increments to the minimum required resolution. On small screens the section links stay available when scrolling between controls and plots.

## Built-in experimental comparisons

The experiment selector loads a compact, checksum-verified test from `experiments/` on demand and caches it for the session. The default picker filters by drainage protocol, observed loading direction and verified axis pairs. It clears incompatible selections when controls change. Tests are grouped by material and drainage protocol and labelled with available initial radial stress and void ratio. Every admitted observation is retained in order for the plotted channels; the column-based JSON format removes repeated field names without rounding, interpolation or sampling. Missing optional channels are represented by null and omitted from the corresponding plotted series. The UI keeps attribution, source and licence links, without a dataset download step.

**Use initial state & protocol** applies only available initial stress, void ratio and drainage conditions. It preserves material constants and loading amplitude; a monotonic measured path resets cyclic loading to a monotonic ramp. No calibration or experimental validity is implied. Selection and overlay visibility do not rerun the solver; applying test conditions does.

Original Wichtmann archives are allowlisted through `data/experiment_releases.json`. That grant list remains empty pending permission. Separately licensed public-source assets are pinned in `data/public_sources.json` and `data/curated/index.json`: the builder verifies processed-file hashes, source archive hashes and matching source-specific attribution/licence fields. The curated source catalogue contains 628 measurement records with 3,595,092 observations, spanning 23 surveyed candidates. These comprise 49 normalized overlays, 485 native measurement series and 94 summaries or grain populations; acquisition blocks are not counted as independent specimens. Curated assets build without upstream access or source-reader dependencies. Pending original Wichtmann assets cannot leak from a previous preview because experiment outputs are rebuilt from scratch, and previews use a separate ignored directory.

OPARA records preserve all HDF5 channels, author-supplied corrected stresses, source attributes and inputs. GEOLAB records preserve reviewed native worksheet blocks, independent curve coordinates, source row numbers, material properties and original references. Finnish oedometer series, rockfill summaries, Castlegate acquisition blocks, Hurley macro/grain populations and LEAP histories retain their own native-unit contracts. Source summaries and grain populations are never treated as SI triaxial overlays. Where source stress meaning or copied initial-state metadata is unresolved, overlays show only interpretable channels and retain warnings. Baskarp volumetric strain is withheld pending independent review; native values remain archived. These overlays are data comparisons, not validated model predictions.

To review all 17 locally cached Wichtmann tests:

```sh
python3 tools/fetch_data.py
python3 tools/build_web.py --preview-experiments
python3 -m http.server 8765 --bind 127.0.0.1 --directory web/preview
```

This local preview is not a public deployment artifact. See the [data reuse review](../docs/DATA_REUSE.md) before registering grants or publishing measurement assets.

Local TMD/TMU `.dat` and Atlas experiment JSON comparison remains available in **Compare your own measurements**. Those files stay in browser memory. Clear removes only local files; built-in tests remain available.

Verification:

```sh
python3 -m unittest discover -s tests -p test_web_experiments.py -v
node tools/test_experiments.mjs
```

Browser packaging converts explicitly labelled source units to SI with `atlas/measurement_units.py`, preserving original units and scale/offset metadata on every converted channel. Unspecified units, source-native time notation and logarithms with a source pressure reference remain unresolved and are excluded from chart axis choices. Conversion alone never establishes effective stress, specimen strain or a sign convention. **Browse all source records** retains access to these records and their data notes; only reviewed normalized records overlay model plots. Comparison axes display kPa and percent. Loading-direction filtering ignores excursions below 5% of the measured strain span to avoid treating acquisition jitter as a reversal; it does not establish matching frequency, cycle count or control waveform.

Native series use `atlas-source-columns-v1` and [the source-measurement schema](../schemas/source-measurement.schema.json), with selectable chart axes, explicit units and missing channels. Normalized overlays retain `atlas-experiment-columns-v1`. Values are not rounded or resampled during unit conversion and packaging; the chart displays at most 350 measured markers while preserving every observation in the loaded record.

Rebuilding originals uses `tools/ingest_public_data.py --download` with the optional `data` dependencies. DesignSafe files resolve through official public preview links; selected Castlegate mechanical files use HTTP ZIP ranges with member CRC and SHA-256 verification. Ordinary site builds use committed curated assets and make no upstream requests.

## Publication evidence browser

`publications.html` renders the canonical publication lineage records with search, version/formulation filters, correction notices, DOI/source hyperlinks, evidence locators and shareable anchors. Its assets are included by the existing Pages packaging. Bound model source panels link directly to the corresponding publication records; publication identity remains separate from executable model admission. All current lineage evidence awaits independent review.

To review this static page without compiling or running the solver, use `python3 tools/build_publications.py --output /private/tmp/atlas-publication-preview` and serve that directory locally. This page loads no Wasm; the standalone preview does not contain the laboratory. The full website still requires its existing native/Wasm verification and packaging workflow. See [publication lineage](../docs/PUBLICATION_LINEAGE.md) for source coverage and verification limits.

LEAP 2018 adds 17 simple-shear acquisitions and nine torsion specimens. Torsion raw acquisitions, calibrated phase histories and cycle summaries remain separate records because they overlap and use different coordinates. Repeated raw files are checksum-deduplicated. To rebuild just these sources while verifying and retaining the rest of the catalogue, use `python3 tools/ingest_public_data.py --raw-dir PATH --source leap-2018-dss --source leap-2018-torsion` (add `--download` to retrieve pinned originals). XLS reading additionally requires the optional `xlrd` dependency. Hosted records are limited to 32 MiB; the longest full-resolution torsion history is 26.5 MB.

## Numerical settings and reproducible runs

The expanded Solver settings panel exposes residual/rate tolerances, per-candidate Newton iterations, subdivision depth, accepted-substep budget and line-search halvings. These numerical choices use the model state scales and apply per material increment; they are not material parameters or a bound on total solution error. Controls recalculate the response, participate in validation/cancellation, and reset to the engine defaults.

The worker uses `atlas_run_with_settings` and checks the returned settings before accepting a response. Numerical settings are saved in both the exported specification and engine result. Import restores them before replay; older runs lacking this object explicitly receive the documented defaults. Unknown versions/norms/fields and invalid values are rejected, while older engines that do not report settings cannot silently supply plots.

`node tools/test_numerics.mjs` checks the browser contract without compiling or executing native code. Add `--wasm PATH/atlas.js --native PATH/atlas_solver` for 17 serial native/Wasm pairs spanning all five public models, configured protocols, default/configured full-update tangents, rejected settings and limited-run rollback. GitHub Actions runs these after the existing parity suite. See [the browser verification record](../docs/BROWSER_NUMERICS.md).

For isolated local verification, `tools/test_wasm.mjs` accepts `--wasm-dir DIRECTORY --native EXECUTABLE`, and `tools/build_web.py` accepts `--wasm-dir DIRECTORY --output DIRECTORY`. Defaults retain the normal build/package paths; an isolated engine directory must contain `atlas.js`, `atlas.wasm`, and the exact current `generated/models.json`. Packaging still checks canonical model equality and measurement release permissions. No build is implied by either option.
