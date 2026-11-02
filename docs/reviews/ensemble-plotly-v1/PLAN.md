# Prospective Plotly browser qualification — 3 November 2026

Reuse the retained qualified /private/tmp/mc-current-shared-package-v3/site common
engine read-only. Overlay only current ensemble modules, ensemble.css and the
pinned local Plotly assets. No compilation, native/scientific run or full-site
build. No model, measured data, solver or two-worker policy change.

Before observing results, require:
- Home route does not load Plotly. First ensemble visit loads pinned local
  Plotly basic 4.1.1 once, with no external runtime network dependency.
- Both charts initialize, retain all 1,438 measured rows and each available
  response prefix, identify baseline/variation/measurement styling and units,
  and preserve numerical outcomes and export identity against the preceding
  serial/parallel retained export. Stops are retained, not fixed or hidden.
- Hover values, real curve click selection, drag zoom, pan/reset toolbar and
  PNG image export work. Model visibility and run selection preserve zoom;
  starting a new study resets it. Work remains independent from plotting.
- Desktop, 390px mobile resizing and leaving/re-entering the route fit the
  actual chart container; charts do not overflow. Console has no app errors.
- Source tests cover physical values, no mutation, stable IDs, serialization,
  coalescing and disposal; packaging retains pinned bytes and MIT notice.

Retain failures as failures and diagnose without relaxing numerical policies.
Stop task-owned browser/server, preserve required evidence privately and remove
only task-owned duplicate downloads or temporary scripts after retaining hashes.
