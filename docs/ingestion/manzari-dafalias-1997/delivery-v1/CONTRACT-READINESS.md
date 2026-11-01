# MD1997 contract readiness — prospective, source-dependent

Original1997 source equations have not yet been received. This inventory identifies actual current engine capabilities; it does not select equations or source conventions.

The v0.3 schema/contract read at assignment are bound by `assignment-inputs.json`. Four supported profiles are incremental residual, strain-path rate, physical-time ODE and dimensionless controlled-path ODE. Small-strain Cartesian zero-spin components, compression-positive Mandel order and explicit complete initialization are required. No automatic finite-rotation transport is supplied. State capacity is32 scalar components. Root schema/compiler migration belongs to another task.

Incremental residuals can use persistent committed states and temporary plastic multipliers; solution-state constraints are separate from equation-evaluation domain checks. The experimental parent-increment reset reads the committed parent and applies simultaneous changes before internal integration. It does not locate reversals or events. None of these features establish the original1997 law or authorize borrowing SANISAND2004 reset semantics.

## Required source decision before transcription

Every original equation, surface mapping, elastic branch, critical-state relation, flow direction, multiplier, hardening, loading/unloading and memory rule must be source-located. Full original dimensional scope and original specimen/preparation rules must be known. The source worker must distinguish source-stated behavior, project numerical choices and unresolved behavior.

Choose a supported profile only after the complete state, controls and history contract is mapped. A source-derived unsupported operation requires its own generic-capability task; no model-specific kernel, source-only completion claim or silently restricted replacement is allowed.

## Prospective qualification structure

Freeze concrete parameter/state vectors, cases, references and numerical tolerances after source extraction and before any compiled observations. This document is a gate structure, not a frozen numerical policy and not evidence of a pass.

1. Independently verify every surface and normal, source triaxial compression/extension reductions, state-parameter/critical-state identities and exact elasticity. Independent Cartesian differentiation or separately derived analytic reductions must not copy production expressions.
2. Select a source-backed complete prepared state and useful public example; include all internal histories. Check admissible and invalid initialization, source boundaries and singular limits. Record unsupported physical regions explicitly.
3. Verify monotonic loading, first yield, unloading/reloading and all source-required memory events. Histories, event timing and caller partition dependence must be explicit. Do not use2004 behavior as1997 reference.
4. Establish reference convergence and independent numerical error bounds before normal-engine native/Wasm parity. Freeze full-state comparisons, derivative/covariance cases where meaningful and useful preset behavior.
5. Preserve failed parent increments exactly, recover from the same parent, and replay/restart every persistent history. A stress-only match is insufficient.
6. Obtain separate nine-item exact-byte model review, then coordinator atlas integration and current complete-package regressions. Browser qualification must exercise the actual complete model, source/review disclosure, edits, initialization, reset, invalid recovery and exact exports/import/replay.
7. Prepare a scoped tested release and obtain only any remaining remote authorization. Push/CI/Pages/live identities and an actual live model run remain necessary E8 gates.

No compiled artifact or author binary has been run. Existing source-gap records are preserved byte-for-byte.
