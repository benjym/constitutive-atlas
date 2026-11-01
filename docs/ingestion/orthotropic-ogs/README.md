# Orthotropic linear elasticity — end-to-end delivery

The exact nine-constant3D OGS formulation is transcribed into schema v0.3. [Source packet](source-v1/README.md) retains seven exact pinned originals privately and gives all equations, conventions, initialization and domains. [Delivery ledger](DELIVERY.md) and [detailed checklist](CHECKLIST.md) track E0–E8.

Dedicated native/Wasm catalogues use the unchanged common solver, all six persistent stress components and all six prescribed strain increments; no constitutive kernel is handwritten. [Prospective compiled study](execution-v1/PLAN.md) records independent compliance references, full tangents and failure/recovery gates. Scientific review and main-atlas/browser/live status remain separately recorded in the ledger.
