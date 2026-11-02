# Owned temporary-input cleanup audit

Source-only specialist `/root/hill_interface`; 2026-11-02. **No deletion or process stop was performed.** No Git mutation, build, compiled material call or browser call was performed. The current `release-v2/`, `site-v1/`, private originals, durable qualified artifacts and other-task assets remain untouched.

Only the obsolete `/private/tmp/atlas-interface2016-delivery-v1/release/` is a prospective cleanup candidate. The coordinator confirms it was never packaged and has no intended running consumer. Its initial base is `feba9188376939a727fe8e69ba62cc3ca6ae73ca`; preparation and preservation receipts remain in the model packet. All six preservation preimages match that git base, and all seventeen earlier preservation events resolve to the recorded exact source/map bytes. No whole-tree identity or unique-file proof is inferred from that bounded check.

| Owned temporary directory | Logical size | Estimated allocated bytes released by unlinking its file entries | Decision |
| --- | ---: | ---: | --- |
| `release/` | 3,368,765,618 B | 399,769,600 B (381.25 MiB) | Prospective only, after immediate consumer confirmation |
| `source/` | 898,361 B | 1,224,704 B | Retain for saved-review replay |
| `em-cache/` | 44,061,002 B | 48,259,072 B | Retain for repeat builds |
| `native/` | 859,110 B | 1,093,632 B | Retain qualified original replay location |
| `wasm/` | 522,678 B | 729,088 B | Retain qualified original replay location |

The obsolete release contains 36,573 regular file names, including 34,383 hardlinked names. Its apparent 3.37 GB size substantially overstates recoverable storage: approximately 3.05 GB of allocated data still has links outside that tree. An eventual removal must unlink entries only; changing permissions or file contents could affect historical evidence through shared inodes. The estimate uses `st_blocks` and inode link counts, excludes directory blocks and cannot promise actual APFS free space because clones/snapshots may retain storage.

Six temporary qualified artifacts match their durable private copies exactly. All 119 frozen source-closure files match both the source snapshot and own commit `e6f734d`. These checks establish retained byte identities; they do not make the old execution paths disposable. `approval-v1/check_saved_build.py` explicitly reads the original `source/`, `native/` and `wasm/` paths and compares native-generated files to Wasm metadata. Removing those directories would break the saved checker despite durable copies. Keep them. The parent also retains the 46 MiB allocated Emscripten cache for repeat builds.

Process-command inspection was unavailable under the sandbox (`EPERM`). This audit therefore makes no claim that all consumers are absent. Before any later parent cleanup, confirm that no process, open file, worker or working directory uses the exact obsolete `release/` path. Keep `release-v2/` and `site-v1/` excluded. Resolve the exact prospective path and reject symlink escapes. Preserve these receipts before action, then record the actual unlink action and before/after free space separately. This packet authorizes no cleanup execution.

`audit.json` records inode-aware sizes, largest files, durable artifact hashes, 119 source snapshot/commit checks and bounded model-evidence references. `provisional-release-provenance.json` records the old base/preimage/preservation checks. `cleanup-plan.json` gives exact retained paths, reasons and prospective release-only preconditions. `audit.py` is read-only with respect to all audited inputs and never follows directory symlinks. `audit-summary.json` is the retained compact output. Re-running the audit records a new observation; no current numerical or scientific admission decision is changed.
