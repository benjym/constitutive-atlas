# Current TMD7 saved-evidence recovery v1

1 November 2026. **The preserved snapshot reconstructs the exact original public
TMD7 scalar result without reading original study file contents during the audit.**
All 88 saved requests and complete predictions are checked by the unchanged
frozen audit mathematics. No solver was executed.

This advances the private reproducibility part of BENCH-03/REL-01. It is a
relocated saved-only audit on this machine, not a fresh material replay,
clean-machine environment, independent scientific review or release.

## Binding and result

The [preservation receipt](../current-kfs-tmd7-preservation-v1/receipt.json) binds
226 files through private inventory hash
`a9427d8b5cedc2221769e1fc96013f89eee954bbd2695ac98f1e5437536ae485`.
The recovery [policy](policy.json) and [harness](recover.py) were
[hash-frozen](freeze.json) before observations. Acceptance requires exact parsed
scalar equality to the original hash-pinned result, unchanged snapshot bytes,
88 verified saved requests, four rejected original-location probes and zero
original-study content-read attempts during reconstruction.

[Result](results.json): all conditions pass. The guarded reconstruction reads
223 snapshot files; the full 226-file inventory verifies both before and after.
The original scalar file is SHA-256
`f77a9342f095e74314db635734dabfd522e333d1f6322ca048be7a33a39f5d75`.
The current/archived model, parameter, initialization, metric, seven compatibility
gates and original predictions retain their exact identities. In particular,
this does not convert the separate original refinement FAIL into a pass or
extend the current replay beyond its existing TMD7 development window.

## What relocation changes

The byte-identical saved source tree executes from `payload/repository`; current
and archived receipts come from `payload/current` and `payload/baseline`.
Two explicit I/O substitutions replace baseline lookup and engine setup:

- Baseline files are read from the snapshot and checked against their original
  frozen hashes.
- Copied executables/models are read for identity. The adapter's physical
  executable location is translated back to its original logical `argv[0]`
  before the existing saved tracker checks the full request. Every other
  argument, state, parameter, count and request order is unchanged and validated
  by that tracker. No native process is launched and no original receipt is edited.

The source laws, policies, input JSON, reconstruction and comparison functions
are not patched or retranscribed. The adapter still checks executable hashes,
catalogue identity and model equality against saved metadata.

During reconstruction, file-content opens under the original checkout, current
receipt directory, baseline directory and current executable path are rejected.
All four protections are deliberately probed before the audit. Process-launch
and write-open events are rejected too. This is a Python audit-event guard,
not an operating-system sandbox or a claim about every filesystem metadata
query. The public recovery harness, policy and preservation verifier load before
the guard; the study's frozen code and data then load from the snapshot.
Python/interpreter/system dependencies remain supplied by the current environment.

## Reproduce

With the private snapshot available, from this repository root:

```sh
python3 -B docs/benchmarks/current-kfs-tmd7-recovery-v1/recover.py '/Users/bmar5496/Library/Application Support/Constitutive Atlas/private-evidence/current-kfs-tmd7-v1-20261101'
python3 -B docs/benchmarks/current-kfs-tmd7-recovery-v1/test_recovery.py -v
```

The snapshot may be supplied at another physical location outside the original
study roots; it must retain the inventory's exact bytes. This command does not
restore files to original paths, download data or regenerate solver outputs.
A public checkout without the private snapshot cannot reproduce the audit.

The [execution receipt](execution.json) records an explicit zero Python exit
status, complete stdout/stderr hashes and the exact command. The first saved-only
observation had no separately captured process-status receipt; its retained
private output agrees exactly with this explicitly recorded second audit.
Three synthetic tests pass: only the executable location changes, an unexpected
physical executable is rejected, and changed numerical arguments still fail
saved-request matching. The original snapshot remains unchanged.

Raw private assets are neither committed nor published. The snapshot is local
same-computer storage, not public hosting or off-machine disaster recovery.
Data rights, independent scientific decisions, broad model admission and
clean-environment reproduction remain open. No new native calls, fits, builds,
model/schema changes, push or deployment.
