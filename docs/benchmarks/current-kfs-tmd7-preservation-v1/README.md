# Current TMD7 private-evidence preservation v1

1 November 2026. The existing saved-only current/archived TMD7 audit completed,
and its observed study-file read closure now has a verified persistent local
copy. This addresses temporary-asset loss for this one recorded audit. It does
not complete BENCH-03/REL-01, make the benchmark relocatable, or provide an
independent scientific review or archival release.

## What was preserved

Private snapshot directory:
`/Users/bmar5496/Library/Application Support/Constitutive Atlas/private-evidence/current-kfs-tmd7-v1-20261101`.

The snapshot contains 226 files, totaling 14,180,449 payload bytes:

| Stored namespace | Files | Meaning |
| --- | ---: | --- |
| payload/current | 92 | Current prediction, process ledger/responses and execution declarations read by the audit |
| payload/baseline | 91 | Archived TMD7 case-02 prediction and saved process evidence |
| payload/repository | 42 | Observed source, policy, model, experiment/report and reference inputs, plus public preservation declarations |
| payload/artifacts | 1 | Current executable bytes read for identity only |

The directory is mode 0700; copied files are 0600. Executable bytes have no
execute bits. Nothing was uploaded or copied into the repository, and raw
measurements, predictions and native outputs remain private. Only this guide,
the preservation script, tests and scalar/hash receipt are committed.

The original [audit](../current-kfs-tmd7-v1/README.md) reconstructs 44 current and
44 baseline process receipts, complete predictions and the exact public scalar
result. A fresh Python invocation traced its file reads while the existing audit
ran. Listed process-launch and write-open attempts were rejected during tracing;
no solver was executed. Source bytecode-cache reads were avoided so source files
were preserved. Repeated reads and final copies must retain the same hashes.
Standard-library/interpreter/OS inputs, directory metadata and unvisited branches
are excluded. This observed closure is not a complete environment or proof of
arbitrary future replay coverage.

[receipt.json](receipt.json) pins the private inventory SHA-256:
`a9427d8b5cedc2221769e1fc96013f89eee954bbd2695ac98f1e5437536ae485`.
That externally retained hash binds every stored payload file. Hashes detect
changes relative to the retained receipt; they are not signed provenance.

## Verify or make a new preservation copy

From the repository root, verification reads only the copy and needs no original
temporary evidence, compiler, executable, network or experimental provider:

```sh
python3 -B docs/benchmarks/current-kfs-tmd7-preservation-v1/preserve.py verify '/Users/bmar5496/Library/Application Support/Constitutive Atlas/private-evidence/current-kfs-tmd7-v1-20261101' --inventory-sha256 a9427d8b5cedc2221769e1fc96013f89eee954bbd2695ac98f1e5437536ae485
python3 -B docs/benchmarks/current-kfs-tmd7-preservation-v1/test_preserve.py -v
```

To capture another copy while the original inputs remain available, use a fresh
Python CLI invocation and a **new absolute directory outside the repository**:

```sh
python3 -B docs/benchmarks/current-kfs-tmd7-preservation-v1/preserve.py capture '/absolute/persistent/private/storage/new-tmd7-copy'
```

Use persistent local storage; the command does not choose a backup service or
manage retention. It refuses an existing destination and never overwrites
original evidence. On copy failure, a private partial directory is retained for
inspection. A successful copy is verified before its final directory name is
installed. The capture command requires the original study's exact private
inputs and public pinned source files; verification of an existing copy does not.

All six synthetic verifier checks pass: valid copy, overwrite refusal, changed
payload, changed inventory against the retained hash, unlisted files, unsafe
traversal/duplicate paths and symlink escape. Some checks cover multiple cases;
see [tests.log](tests.log). The real 226-file snapshot independently verifies,
with no Python bytecode or executable permissions in its payload. Original
numerical gates, model definitions and benchmark reports are unchanged.

## Recovery boundary

The private inventory records each original absolute path and its stored path.
It can support deliberate recovery after loss; **this command never restores or
overwrites original paths automatically**. Review that mapping before restoring
files. Restoring source/asset locations and replaying the full audit from a
fresh environment remains a separate bounded reproduction task. No portable
execution or restore test was performed here.

This is a persistent copy on the same computer, not off-machine disaster recovery
or public durable hosting. The snapshot includes private experimental material;
data reuse rights remain unresolved and the copy grants no redistribution right.
No full six-test current replay, new fit, numerical refinement, solver build,
scientific promotion, push or deployment follows from preservation.
