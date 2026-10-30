# Wichtmann experimental data: reuse review

Reviewed 30 October 2026 for the original Karlsruhe fine sand TMD1–5 and TMU1–12 archives pinned in [data/sources.json](../data/sources.json).

## Finding

**Public redistribution permission has not been established.** This is an unresolved permission question, not a finding that reuse is prohibited. Do not bundle raw files, normalized measurements or sampled plot data in the repository, website or deployment artifact until an applicable grant is recorded.

The [author's general remarks](https://www.torsten-wichtmann.de/KFSDB-general.htm) describe the database and provide downloads. The [SoilModels dataset page](https://soilmodels.com/karlsruhe-sand-wichtmann/) describes its use for model development, calibration and verification; its [download package page](https://soilmodels.com/download/package-karlsruhe-sand-wichtmann/) provides the dataset. These reviewed pages did not provide an explicit redistribution licence for the two pinned archives. Neither archive contains a README, licence or copyright notice; they contain only the original test files. Availability for download and intended research use do not, by themselves, resolve permission to redistribute a copy on another website.

The associated publications are [Wichtmann & Triantafyllidis (2016), Part I](https://doi.org/10.1007/s11440-015-0402-z) and [Part II](https://doi.org/10.1007/s11440-015-0412-x). A licence attached to a different publication or dataset must not be assumed to cover these archives.

## Current implementation

The public laboratory links directly to the author's archives. Users download and extract them, then load original `TMD<number>.dat` / `TMU<number>.dat` files or Atlas experiment JSON from their computer. File contents stay in browser memory and are not uploaded or persisted by the application. Selecting a test or switching its overlay on/off does not change model parameters, initial state or protocol. The UI displays protocol and initial-state differences where metadata permit.

Original-file imports support these two eight-column layouts only. They convert kPa to Pa and percent strain to dimensionless strain. TMD void ratio remains dimensionless despite the source header's percent label. TMU pore pressure is displayed as a change from the first observation; no unmeasured volumetric strain or missing initial void ratio is invented. The Python importer remains the archival normalization path, recording archive and member checksums; direct browser import is a plotting convenience rather than an archived benchmark record.

The browser may display fewer points for rendering while preserving original order and retaining the full loaded record in memory. Numerical/experimental agreement is not claimed by turning on the overlay, and illustrative model parameters are not a calibration to the selected test.

## Gate for a future bundled release

1. Obtain an explicit applicable licence or written permission from the relevant rights holder covering hosting/redistribution and transformed or sampled measurements. Contact requires a separate user instruction; no request has been sent.
2. Record the grant's source, date, scope, attribution requirements and any restrictions beside the dataset manifest. Check that it covers the exact archived files and intended public use.
3. Prepare a versioned bundle with original archive/member hashes, transformation version, units, channel warnings and required attribution. Keep data terms distinct from the code's MIT licence.
4. Add a build-time allowlist so only approved dataset revisions enter the public artifact; test that a clean CI build produces the same bundle.
5. Publish selectable bundled tests with visible source/attribution links, keeping local loading available. Update this review and the README to identify the permission actually used.

This review covers the two currently pinned archives. It does not establish reuse terms for the complete sand database, kaolin database or other Wichtmann datasets.
