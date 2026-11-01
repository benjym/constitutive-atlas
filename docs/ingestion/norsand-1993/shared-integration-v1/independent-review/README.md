# Independent controlled-path shared integration review

Task `REVIEW-controlled-path-shared-v1`; reviewer `/root/norsand_path_review`,
2026-11-01. Exclusive reviewer output is this directory. This is a new review
identity; the prior `e2-v3` reviews remain unchanged. The reviewer did not author
the shared installation, durable generator/CMake target or source-preservation
scripts. Scope is static integration and prospective target assessment, not E5
model approval or new compiled/browser execution.

**Accepted for the exact V2 shared static integration scope.** All 15 files in
`integration-freeze-v2.json` match. No blocking static finding remains. The new
durable CMake target still requires its own serial native/Wasm qualification;
prior staged qualification is separately retained and does not constitute an
execution of that new target.

The shared candidate, Python controlled-path runtime, generic C++ runtime and
compiler match the accepted staged formulation. Schema changes from the accepted
stage alter only the description from staged to installed. Root model validation
adds explicit routing guards; no material formula or integration algorithm is
changed. The generator accepts only explicitly selected controlled-path models
and the common compiler rejects mixed catalogues. The separate CMake source
routes generation through that tool, tracks the declared model/schema/Python
dependencies, includes root headers, and retains the qualified floating-point
and Wasm export/exception settings. The default candidate is a research draft,
not a new public approval entry.

V1 had a blocking routing gap: legacy evaluation/initialization treated path
models as ordinary nonphysical incremental models. Autonomous path equations
could therefore silently bypass coordinate/control context. V2 centrally rejects
path models in `evaluation_environment` and explicitly rejects incremental
preparation; legacy `initialize_state` inherits that rejection. The new autonomous
regression checks interpretation, preparation and initialization. The reviewer
independently ran that regression with Python bytecode writes disabled: PASS.
The 25-test retained suite passes with three explicitly disclosed native opt-in
skips. The earlier 24-test migration-header failure is preserved; selecting the
profile's actual generated header retains exact equivalence assertions.

The reviewer independently compared all three root-generated path files against
the accepted staged files: byte-identical. The two retained legacy catalogue
files before/after installation are byte-identical for 13 models. The named loose
constant-cell example matches its qualified request's complete initial state,
parameters, coordinate, progress and retained endpoint state/observables. Its
definition hash matches the unchanged research model. Its description correctly
limits it to a source-reference numerical example with admission pending.

Source preservation was independently rechecked read-only. All 179 planned
receipt bindings resolve to the stated exact-hash snapshots. All original V1
integration-freeze receipt bindings also resolve after the V2 routing repair.
Both retained inventories were checked: all 3348 previously resolvable pairs in
`frozen/bindings-before.json`, and all 3336 in
`frozen/bindings-before-v2.json`, resolve now with no failure. Historical
sidecar-entry references were checked against exact snapshot/live bytes;
ordinary receipt references use `checked_receipt`. Details are in
[preservation-recheck-v1.json](preservation-recheck-v1.json).

Inventory filename order is not chronology: `bindings-before-v2.json` precedes
the failed V2 sidecar writes, while `bindings-before.json` is the V3 input after
those writes. Their 220 and 217 originally unresolved rows are historical
inventory classifications. Three differences concern Burgers/Drucker-Prager
receipts; all three resolve now with unchanged original receipt document hashes.
Those counts must not be described as verified-current unresolved totals.
The first planning failure wrote no sidecars; the second failure occurred after
sidecar extension; both failures and scripts are retained. A later unrelated
full-scan failure from unsafe absolute source-map references does not invalidate
the bounded recheck of exact prior inventories, and does not prove a new global
source-inventory pass.

No new compiled artifact, E5 model approval, public atlas admission, packaged
browser use or live delivery is accepted here. Those remain distinct gates. The
reviewer performed no builds or compiled candidate calls.
