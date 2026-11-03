# Scoped commit and push qualification

Based on published main 60e5c7bfbc090628419af81d34c099e8c5c6223a. The shared workspace was left untouched. The isolated checkout carries only the all-tests frontend, its packaging/tests/evidence and one task-board row. Separate pre-existing optional constant-confinement and Open-in-Model-testing changes remain excluded, as in the previous ensemble push. The drained recorded and undrained constant-volume paths are preserved; source metadata determines the loading protocol during import.

The exact isolated source passed 24 Node tests and 4 package tests. The one original constant-confinement test is outside this scope, accounting for the difference from the original shared-checkout total of 25. The original full browser evidence remains unchanged and is scoped to the broader shared source; no fresh browser or compiled build is claimed here. Source hashes and the deterministic preparation script identify the narrowed commit inputs.

User explicitly authorized commit and push to current main, without force. Normal repository workflows may run; no verified live-delivery claim follows. The clean sparse checkout is disposable once its commit is retained remotely, and exact push/cleanup receipts are retained in the shared evidence directory.
