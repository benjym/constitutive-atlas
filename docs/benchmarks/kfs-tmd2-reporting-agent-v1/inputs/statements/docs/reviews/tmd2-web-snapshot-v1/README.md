# TMD2 website snapshot — bounded provenance increment

1 November 2026. **The Methods card now links to a generated read-only benchmark page containing the exact archived definition and inputs.** This advances WEB-04's curve-to-input traceability without rerunning the constitutive study or granting scientific admission.

`tools/build_benchmark.py` checks each selected asset against the existing TMD2 packet manifest, reads the original model directly from its checksum-verified Atlas source archive, and checks its identity against both the source manifest and case receipt. Named published-case parameters and nominal initial state must match every frozen request. It copies six explicitly selected public assets and renders their hashes, constants, initialization, settings, coordinate limitations, source links and local reproduction command. The archived definition remains in its historical schema, separately from live defaults and new v0.3 ingestion.

`tools/build_web.py` invokes this step during regular Pages packaging. The Methods link and snapshot assets use relative URLs beneath the project prefix. No JavaScript or solver worker is needed to inspect the snapshot. The snapshot directory is replaced to remove stale files; unrelated package assets remain outside its ownership.

The case receipt contains private measured first-row values, so it is read for binding checks but **not copied**. Original/normalized measurements, source PDFs and author implementation code are excluded. The published result summary contains only the already committed aggregate errors and gates; the figure contains published model coordinates and Atlas results. No new data permission is inferred.

## Verification

- Four focused tests cover exact historical identity, byte-for-byte asset copies, request/input mismatch rejection, corrupt input rejection before output, private first-row exclusion, independence from live defaults, explicit sibling exclusion and stale-file removal.
- Those four plus fourteen existing archive tests pass: `PYTHONPATH=tests python3 -B -m unittest test_web_benchmark test_evidence_archives -v`.
- A full package built with the previously verified Release Wasm artifact contains nine models and 628 public experiment records. Static package validation passes; all ten local snapshot links exist and remain under `/constitutive-atlas/`. This task did not rerun those model calculations or decode every experiment.
- Actual in-app browser inspection followed the new Methods link to the snapshot and displayed the model-only figure, published-case values, exact initial state, asset identities and pending-review notice. Desktop-native inventory was unavailable while the Mac was locked; the in-app browser remained usable. No desktop unlock was requested or attempted.

[Verification receipt](verification.json) pins implementation and emitted snapshot files. The local screenshot remains at `/private/tmp/atlas-tmd2-web-snapshot-v1/snapshot.png`; it is not an archival substitute for the recorded numerical study. Initial sandbox loopback binding failed; the authorized retry succeeded. No numerical failure or acceptance policy was changed.

## Limits and next gate

Independent scientific review remains unsigned and unassigned. Historical plotting/strain conversion and original-measurement reuse permission remain open. The native 25% research path does not extend the browser laboratory's 10% limit. Reproduction uses the existing portable command and its frozen source, not live catalogue defaults. No native/Wasm build, material call, model/schema change, push or deployment occurred. Existing paper work is untouched.
