# Decision 0002: differentiate accepted updates on a fixed numerical partition

Date: 2026-10-31. Status: **experimental numerical API; broader verification pending**.

The shared Newton solver already uses AD residual Jacobians. Those are not the tangent of a complete material update: previous-state changes, memory preparation, internal substeps and rate integration must all contribute. NUM-01/02 require this distinction to be explicit.

Add an opt-in C++ `linearize_update` API alongside unchanged `integrate`. Compute the accepted state first, then differentiate its complete discrete trajectory on the accepted partition. Use implicit residual differentiation at solved roots and AD recurrence for rate updates. Differentiate the existing selected parent-preparation map by templating generated preparation over the scalar type. Preserve ordinary double-call semantics, model schemas, hashes and solver defaults.

Return material-update success separately from derivative availability. A singular derivative must not reclassify a converged material update as failed. Hold discrete branches/partition fixed and report exact-zero reset guards; do not claim a unique derivative at every yield, history or adaptation transition. Document uncovered branches and limit current use to tested local regimes.

This adds no C/Wasm export and changes no public model identity. Generated headers need rebuilding; existing binaries/evidence retain their original source hashes. Future control/time derivatives and generalized event-location derivatives require explicit contracts and matching native/Wasm evidence. The [implementation/evidence document](../UPDATE_LINEARIZATION.md) records the present scope and remaining gates.

Subsequent implementation: the [experimental native C ABI/CLI endpoint](../UPDATE_LINEARIZATION_API.md) now exposes the same opt-in result and separate status flags. This extends the initial C++ surface without changing the derivative convention; Wasm runtime verification remains pending.
