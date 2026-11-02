# Live delivery v2 — Barodesy sand

Exact release revision: `e6f06114cc1d415daf95e4e334a43b822b85ded7`. Full workflow: [41365126545](https://github.com/benjym/constitutive-atlas/actions/runs/41365126545); controlled-path workflow: [41365126532](https://github.com/benjym/constitutive-atlas/actions/runs/41365126532).

This revision includes the published Barodesy sand delivery `a1f9bac7` and subsequently published memory-bounded public-data checks and explicit GEOLAB/Estefania source-identity assertions. The current test keeps the original exact-byte rebuild comparisons and all curated record checks. No model, runtime, profile, builder, acceptance policy or workflow bytes changed from the reviewed release. See the separate composition/helper review in `interface-review-v3/live-e8-v2/`.

The earlier release run was superseded. Its Linux native job ended with a runner-shutdown signal; the macOS native job was explicitly cancelled after the published shared fix became available. Those logs, the actual earlier tested upload and an interrupted local test-only alternative remain under `live-release-v1/`. Neither that run nor the interrupted test is claimed to pass. The alternative was never integrated.

The shared preservation change omitted deep historical receipt mappings. `deep-map-repair-v1/` adds the missing mappings without changing original receipt bytes: all181 original bindings and97 reverse-map bindings pass. Separate review accepts all26 additive maps and exact prior-byte snapshots. This documentation-only repair is separate from the executable revision tested by the release workflow.

E8 remains in progress until every required job, exact deployment, tested-upload comparison and actual live Chrome assessment passes. Original numerical gates and scientific scope are unchanged.
