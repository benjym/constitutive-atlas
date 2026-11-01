# Full-range ensemble checks — 2 November 2026

Frozen before observing full-range compiled results. Default replay uses all 1438
acquired OPARA-TXCD-100 rows in source order, ending at axial strain 0.1599.
No interpolation, model, preparation, solver or timeout changes. Both plots show
all measurements by default; remove the obsolete prefix/context toggle and marker.
Retain source identities and old 95-row exports with their exact replay window.

Acceptance: all 15 default requests contain every source endpoint; full-range
export/import preserves exact requests and rejects tampering. Existing ensemble
and packaging regression tests pass. Execute the existing matching Wasm serially,
without a rebuild. All five elastic requests must complete all 1438 points and
match the existing independent elastic stress/volume formulas at every point,
with unchanged tolerances .05 Pa + 1e-7*abs(stress) and
1e-9 + 1e-7*abs(volume). Preserve DP/MCC completions or stopped prefixes and
errors without changing gates or numerical settings. Verify actual browser run,
full plot range, selected result, export/import and mobile layout in an isolated
preview. No live delivery claim or remote action.
