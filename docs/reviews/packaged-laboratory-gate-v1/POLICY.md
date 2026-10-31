# Packaged laboratory release gate v1

Frozen before observing this new gate. Test the completed package, not a separate build directory. Require unique matching executable/catalogue IDs, exact parsed model JSON definitions, nonempty HTTP(S) source links and corresponding schema files. Resolve HTML local asset links under `/constitutive-atlas/`, rejecting missing assets or paths outside that prefix. Do not fetch external links or claim their availability.

For each packaged model, run the packaged Wasm through the packaged numerical-settings module with explicit parameter defaults and complete illustrative state. Use the current browser default: drained triaxial, target 0.01, 100 steps, zero cycles, default settings. Require success, 101 finite state/strain/p/q/u points, exact initial state and model catalogue hash, and matching settings. Preserve results and any failure. No tangent, independent scientific accuracy or experimental applicability claim. Existing five-model tangent checks remain separate. No numerical tolerances are introduced or relaxed.

Run negative static tests for stale definitions, mismatched executable IDs, unsafe source URLs and broken/project-root asset paths. Wire the gate between packaging and Pages upload. Remote CI and deployment require separate authorization.
