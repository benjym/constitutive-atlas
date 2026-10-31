# Recorded import cancellation — 1 November 2026

Bounded WEB-06 fix. A superseded file read or example fetch could launch a replay after a newer selection or cancellation. An old read failure could also overwrite the current status; an old worker continued running while the replacement file was read.

The recorded view now invalidates prior reads/work before awaiting a source, clears exportable results, exposes Cancel during reading and checks the request generation before loading. Late read errors and worker replies are ignored. The file input resets immediately so the same file can be selected again. Current invalid/oversize sources still report rejection. Cancelling an import asks the user to load a path again; cancelling a running replay retains the supplied specification for restart.

## Verification

[Before](before.log): five of six regression cases failed against the unchanged old module. [After](after.log): all six pass, plus their standard Python discovery wrapper and four existing recorded browser/evidence tests.

The deterministic JavaScript suite imports the actual view and supplies deferred file reads/fetch bodies, a minimal DOM, fake timers and worker messages. It checks latest-file selection, cancellation during loading, file superseding example, stale read failures, immediate old-worker termination/late-response suppression and invalid/oversize imports. These are interaction checks, not constitutive numerical references.

The actual in-app browser, under `/constitutive-atlas/`, loads the elastic example and reports **5 ordered observations / 6 material trials**, with replay and exports enabled. The old complete preview package was reused with only the edited view copied in; no fresh packaging or Wasm/native build was done. The browser check confirms the normal flow; deterministic tests cover the races rather than timing-dependent manual clicks.

Terminal trailing whitespace is trimmed in the saved test logs; test messages and outcomes are unchanged.

## Preservation and limits

Old module SHA-256 `2741fa1be8c03a3388370c1e4a996af9f0d717eb792b5bbdaf8467cd375fcd3f` is preserved at [its exact source snapshot](../../../catalogue/source-snapshots/2741fa1be8c03a3388370c1e4a996af9f0d717eb792b5bbdaf8467cd375fcd3f/web/recorded-view.mjs). Four affected original source bindings resolve through additive archive maps: total-stress source pins, nine-model integration inputs, DP prospective freeze and recorded-restarts manifest. Previous sidecar bytes are archived. Original receipts and acceptance policies are unchanged; this does not certify every historical manifest.

Cancellation invalidates reads and prevents replay/status changes; it does not abort the underlying browser file read or fetch. The existing 10 MB import ceiling and 60-second replay timeout are unchanged. No solver/model/schema changes, numerical study, scientific admission or deployment. WEB-06 remains open for its other release checks.
