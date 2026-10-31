# Spectral integration: four-source binding audit v1

2026-10-31; AUDIT-spectral-dsl-source-bindings-v1. Read-only before planned spectral DSL integration. Exact scope: `atlas/dsl.py`, `atlas/compiler.py`, `atlas/history_compiler.py`, `atlas/model.py`. No shared writes, source edits, builds, author execution, commits or sidecar mutation. The old normalized-determinant scanner is preserved byte-for-byte as `original-scan.py`; `scan.py` changes only its target set by adding model.py. It calls the current checked_receipt verifier with Python bytecode writes disabled.

## Findings and strongest safe next action

Before changing any of the four sources, the coordinator should preserve the four exact current source bytes and bind37 current-hash pairs in23 immutable documents. `supplement.json.current_archive_plan` is the exact actionable list: document SHA, current resolution, source path/SHA, canonical archive destination, sibling map path/SHA, and whether that map already pins this document. It identifies17 existing sibling maps and6 new map locations. Do not edit any primary document or recompute an expected source identity from revised source. Verify every current pair through checked_receipt after archival and before source edits. A byte-identical snapshot already present can be reused only after verifying its exact hash.

Current identities:

- DSL: `f9524adc98691bd2f7108754b744c8b5f40135bfd25edb62e2fe6988facbe233`.
- Compiler: `e8a224661b479dc65e4e5113bff64a73535e9d08658902793fee034a36b63b1f`.
- History compiler: `0215cb448d4433a7f75843e8659dcb35624ac2fbef02b0209072276de0b8e479`.
- Model: `f1a8ff24d2d6fdb663436e7e29fa3c1b2a61e5bebca58edd5aa99e0114824d6d`.

All four were unchanged between inventory and availability checks. `source-bytes/<sha>/<original-path>` holds verified copies of these four sources and the17 existing maps requiring prospective additions. These staging snapshots do not themselves register receipt resolution and do not authorize mutation of historical originals. The coordinator owns archival.

The scanner finds no secondary source-map hash references pointing to the proposed current sidecar locations. Nevertheless preserve each existing map's exact pre-append bytes: changing any sidecar alters its identity. The full scanner's prospective closure also includes unresolved historical sidecars; this is a conservative list, not a recommendation to amend them now. No reverse edge required a further map mutation in this scan. If a different sidecar is changed, rerun reverse-reference closure before that mutation.

## Inventory and historical gaps

`inventory.json` scans1585 non-snapshot JSON documents;641 snapshot/frozen documents excluded; no parse errors. It contains341 unique primary document/source/hash pairs across116 documents:293 archived,33 live,15 unresolved.37 pairs equal current source hashes, of which33 resolve live and4 currently fail because their document is not registered in an existing sibling map. The exact primary receipt/pointer/source/document identities are retained for every occurrence.

The4 current failures are all in `docs/reviews/nine-model-lab-integration/integration-inputs.json`. Its sibling map currently registers only `historical-catalogue-archive.json`. checked_receipt reports `original evidence document changed after archival` both for an absent document pin and a changed pin; inspection establishes the former here. There is no old integration-inputs document pin being overwritten. Add its exact current document pin and four current source entries while preserving existing historical mapping content and prior map bytes.

The11 remaining unresolved primary pairs are historical and must remain explicit, independently of the new spectral integration:

- Three solver-rollback compiler d241f835... pairs: exact bytes remain in `catalogue/investigations/solver-rollback-v1/frozen/atlas/compiler.py`; no registered canonical redirect.
- Three solver-rollback model d1e539f6... pairs: exact bytes remain in the corresponding frozen/atlas/model.py; no registered canonical redirect.
- Three complete-receipt-audit old_sources summary pairs in dsl-identity-v5: all exact canonical snapshots exist; that summary document has no registered sibling redirect.
- Compiler147a9c54... and model b835fa18... in `docs/reviews/solver-rollback-design-v1/source-checks.json`: no exact matching repository basename copies or source-changing git versions found. git-availability.json inspects12 compiler and9 model source-changing versions across all local refs; unreachable git objects, renamed external files and external archives are outside this search. No replacement identity inferred.

This is the old7 compiler/DSL/history gaps plus4 newly inventoried model gaps. They are not caused or resolved by the planned source edits. A separately scoped historical recovery task may archive proven exact frozen bytes and register exact old documents after its own sidecar reverse-reference review. No all-resolved claim is supported.

## Secondary map references and consumers

There are358 secondary document/source-map/hash pairs:106 archived,180 historical sidecar-entry archives,51 live,20 live-sidecar entries,1 root-relative unresolved. The latter is `frozen-sources/docs/ingestion/hypoplastic-clay-2005/determinant-input-rounding-v1/source-archive-map.json` in clay2005-homogeneous-rates-v1/manifest.json. Its exact bytes do exist under that packet's local frozen-sources directory with the expected hash3690c261.... This is a contextual packet-local path rather than missing source bytes; root-relative checked_receipt resolution and packet-local verification must not be conflated. Original scanner status is preserved; supplement.json gives the exact matching contextual path and document/hash. The frozen copy is outside mutable sidecar closure.

Primary JSON consumers are completely enumerated within the declared scanner scope. `consumer-index.json` also records376 textual matches across179 current non-snapshot Python files for target imports/literals, checked_receipt, verify_manifest_files and archive-map/snapshot usage, with source hashes and line numbers. This is a reproducible textual index, not a proof of complete dynamic reachability. Principal APIs include atlas.evidence.checked_receipt/verify_manifest_files, tools/build_evidence.py, registered atlas.source_replay closures, study-local receipt verifiers and archive regression tests. Frozen/capsule consumers are immutable historical execution contexts, not candidates for in-place edits.

## Portable replay advice

Resolving a source file identity is narrower than reproducing execution. Do not import a lone historical model.py from its content-addressed directory with current dependencies: its package-relative imports and `ROOT=parents[1]` would bind a different package/root or current modules. Materialize a fresh original repository layout using exact document-bound bytes for the explicit trusted closure. This includes atlas/__init__.py, all required module imports (including function-local imports), schemas/model/data files, original entrypoint and expected original output. The four files alone are not a replay closure. The target modules directly import DSL/model/history/scalar_math, with further dependencies and runtime inputs beyond those imports; supplement.json records only direct top-level imports and says so.

Use existing atlas.source_replay export overrides only after checking each supplied byte string against its original pin via checked_receipt; never silently substitute a current file or a nearby snapshot. Pin the replay capsule, original evidence documents, selected entrypoint, literal arguments and expected original output. Preserve registered capsule/document bindings and old sidecar bytes. A clean source-only replay is not a native rebuild, scientific rerun, environment-bit reproduction or new model admission. Existing frozen-sources contexts may already contain the complete trusted closure; verify their own local manifest semantics before copying. This audit executed no replay.

## Checks, reproduction and limits

```
python3 -B scan.py /Users/bmar5496/code/constitutive-atlas --output fresh-inventory.json
python3 -B supplement.py
```

The supplement has explicit repository/staging paths and is a review-time tool; adjust those paths intentionally for another checkout. Reruns after archival or edits must have new result identities, not overwrite this frozen inventory. Ten pure extraction probes passed, including model.py nesting, both object hash keys, malformed nested path objects, descriptive original_path exclusion and encoded JSON exclusion. `scanner-checks.json` records each. No builds or compiled observations occurred.

Scope follows the inherited scanner: exact recursive direct path->64-lowercase-hex and {path,sha256/hash} pairs under catalogue/docs/tools/schemas/tests; source-archive-map sidecars are secondary, source snapshots/frozen trees excluded, encoded capsule payload JSON not decoded. Existing sidecar original_path entries are treated separately from primary checked_receipt syntax. Plain JSON parser duplicate-key behavior and dynamically encoded/non-JSON hash expressions are outside the audit. Source/equation completeness and numerical correctness are not implied by identity resolution.
