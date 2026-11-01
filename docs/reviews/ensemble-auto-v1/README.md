# Automatic ensemble updates — 2 November 2026

Removed Run ensemble. The default study starts on the first explorer visit;
it does not run while the visitor stays on the home page. Parameter, initial
history, variation and model-inclusion edits schedule a fresh study after350ms
without another input. Enter submits immediately. Visibility toggles only
redraw existing curves.

An edit invalidates pending imports, marks prior results stale, cancels an
active queue and replaces the debounce timer. A new study waits for the old
queue to settle before creating work, then checks the revision again. Cancel
clears pending updates and stops active work; a later edit starts a new study.
Import clears the pending timer and retains exact-input replay. Current selected
job is preserved when its identifier remains present. Pagehide invalidates and
cleans pending/active work. Removed the obsolete Runbutton styles.

Regression checks:11ensemble/queue tests plus22catalogue/package Node tests
and2Python package tests pass. Syntax/owned whitespace checks pass. No model,
solver, numerical settings, source data or full-range replay changes.

Browser fixture-v1 initially expected15runs after changing E to36MPa; that
matches an existing variation and correctly produces14runs. Observed14completed
and no overlapping workers; retained failed transcript and fixture note.
Browser-v2 corrects the expected count and uses a fresh instrumented browser.
Final results and exact artifact hashes are retained alongside this README.

Preview reuses the qualified matching common engine package from
/private/tmp/atlas-occ-shared-app-v2/site-v2, with current frontend changes at
/private/tmp/atlas-home-sand-style-v1/site-v2. No runtime rebuild, fresh full-site
qualification, commit, push, deployment or remoteCI.

Final browser-v2 PASS: first-visit15full-range runs; rapid-edit debounce; invalid
input recovery; active cancellation/settling and latest-input selection; explicit
Cancel stability;25MBexport/import during a pending edit; model inclusion
auto-update; desktop/mobile layout. Instrumented10worker lifetimes,116realWasm
requests, maximum1active ensemble worker and0remaining. Mobile screenshot
visually inspected. Temporary preview server stopped after qualification.

The first immediate post-resize mobile screenshot showed a capture artifact
(repeated viewport tiles). A separate settled capture
output/playwright/ensemble-auto-v1-mobile-settled.png is correct and visually
inspected; no production change was needed. Original capture retained.
