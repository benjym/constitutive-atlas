# Generic near-constant plot range proposal v7

FIX-kelvin-flat-plot-axis-v1. Parent actual-browser qualification observed held-stress variation around1e-14kPa magnified into a full-height zigzag by an axis range padded solely as7% of its tiny nonzero span.

The one-condition proposal treats `hi-lo <=64*Number.EPSILON*max(1,abs(lo),abs(hi))` as near constant, using the existing constant-value padding `max(abs(lo)*.05,1e-3)`. It preserves normal span padding exactly. It does not edit, round, flatten or hide any plotted/exported numerical values; only the plot viewport range changes. Both axes use the same generic function, so physically separated time values and tiny but resolvable spans are explicitly checked.

`app-prior.js` preserves exact current isolated source; `app-proposed.js` and app.patch form the reviewable one-condition change. proposal.json binds both exact sources. No shared app was edited.

`node --test docs/ingestion/kelvin-voigt-comsol63/interface-v7/test_axis_proposal.mjs` passes5 tests using the actual extracted original/proposed function. Cases cover empty/zeros, positive/negative exact constants, actual48/-24kPa roundoff, near-zero roundoff, threshold boundaries, resolvable physical spans, small and large time origins, unchanged caller data and exact preservation of the complete chart function. results.log retains passing output. results-first.log preserves the first4pass/1failure test run: the chart-preservation assertion incorrectly reused original character offsets after the longer axis condition shifted its position. Extraction now uses each source’s own boundaries; the production proposal and acceptance checks are unchanged. The near-flat48kPa test projects a sub1e-8px spread on the existing211px chart height, while unchanged physical data remain in the polyline and export.

No compiled calls, builds, browser actions, shared source mutation, approval or Git operation occurred. Coordinator archival/insertion and independent review plus actual-browser requalification remain required.
