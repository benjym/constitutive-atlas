# Y-only near-constant plot range proposal v8

Independent review rejected the v7 generic condition because representably separated physical times such as[1e9,1e9+1e-6] were padded as near constant relative to their large origin. V7 remains unchanged as a rejected proposal; no previous review/failure is relabeled.

V8 adds `axisRange(values,nearConstant=false)`. The original exact-constant case remains unconditional; the64EPS near-constant condition runs only with explicit opt-in. The chart opts its y domain into this behavior and leaves x calls unchanged. No plotted/exported array, data value, normal domain padding or other chart behavior changes.

app-prior.js retains the current isolated source, app-proposed.js and app.patch are the narrow proposal, and proposal.json pins exact bytes. Parent archival/insertion and independent review remain required; no shared app has been edited.

`node --test docs/ingestion/kelvin-voigt-comsol63/interface-v8/test_axis_proposal.mjs` passes4 tests. They extract actual axisRange/chart source; cover original x behavior including supplied positive/negative large-origin short-time examples; y constants/near-roundoff/normal domains/threshold boundaries; and execute the actual chart with a small SVG adapter to prove only y opts in, input arrays remain unchanged, the1e-6s horizontal span remains over200pixels while roundoff y spread remains below1e-8pixels. results.log retains output.

No compiled calls, builds, browser actions, approval or Git mutations occurred. Actual-browser requalification and separate review remain pending.
