# Observed executed-expression results

Both serial Release builds completed: native and Emscripten/Node each produced all 1620 ordered rows with exact expected boolean statuses; complete backend parity passed. The frozen expected corpus and production source snapshots are identical to v1. The original v1 native build failure and logs remain retained in that separate directory. No acceptance changes followed observations.

This establishes expression/helper acceptance for this corpus. Full generated material/scale/reset context routing and committed solver rollback remain separate pending studies. Acceptance controls include subnormal and signed-zero expressions, but no C++ output-bit accuracy claim is made here. Frozen headers isolate these runs from concurrent schema migration.
