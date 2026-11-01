# Independent review of the KFS relocated saved auditor

**Accept the exact trusted-Python relocation interface**, subject to the scope
below. Reviewer `/root/kfs_development_review`, separate agent run, 1 November
2026. This is an interface/integrity review. The earlier C1-C7 scientific
reporting decision, archived model/source identities, original failed refinement
and separate nested pass are unchanged. This adds no scientific approval.

Final `replay.py` SHA256:
`04e56165edc3a991db4582914901ebea83e367151cafa4f3de3c4784a97b6150`.
Accepted saved-result SHA256:
`f4c1e48c354ec04de606e1f64f39859d737662a0b6a3935a74759422fae8d8ee`.
The [manifest](manifest.json) binds reviewed inputs and this packet.

## Verified behavior

- The original 248 frozen public inputs remain unchanged. Freeze v2 adds exactly
  one supplemental `atlas/data.py`, hash-bound as an initial-source import
  dependency omitted by the original closure. It does not revise normalization,
  parameters, original reviewer checks or scores. All 249 retained public files
  and 9,423 private receipt bindings independently hash-check. Four duplicate
  public/private origin keys bind identical bytes, so dictionary precedence
  introduces no conflicting identity in this exact freeze.
- I reconstructed the old `fc0e1bfc...` source map independently from the retained
  expanded map: its same three document bindings and first 17 of 19 additive
  entries, serialized indent2/newline, reproduce the expected original SHA
  exactly. The reconstructed snapshot equals those bytes. No expected hash or
  prior reviewer artifact was replaced.
- My own full saved-only replay used explicitly transferred public and private
  roots. It exited 0, reproducing the original result exactly: eight independent
  groups, eight saved auditors, all original negative-control reasons, 8,867
  mapped reads and zero builds/fits/material calls. Its command and result are
  retained [here](full-repeat-command.json) and [here](full-repeat-results.json).
  That run used candidate `41b8dfbb...`. The final candidate changes only the
  default freeze filename to `freeze-v2.json`; my explicit-v2 command is
  unaffected. I checked the exact one-line difference and reran all direct
  helper probes against the final candidate.
- Read relocation is separate from metadata relocation. A historical directory
  prefix can support stat/scandir but cannot authorize an unlisted file read.
  Direct retained reads also require exact listed-file membership. Source-loader
  reads use that same resolver and reject cached `.pyc`/`.pyo` bytes. The finder
  preserves historical source filenames/package paths rather than rewriting
  frozen commands or code. Standard-library/runtime and scratch operations
  remain ordinary Python dependencies.
- Nonexecuting synthetic probes of the actual candidate helper AST confirm
  listed historical/direct reads, rejection of existing unlisted historical and
  retained files, rejection of unlisted/cached source, and rejection of frozen
  writes. The actual hash-preflight loop rejects same-length corruption before
  audit execution. The actual optimized-interpreter precheck raises before
  optimization can disable integrity assertions.
- Synthetic calls to the actual audit guard reject subprocess, system, spawn,
  exec and socket-construction event names without launching anything. Raw
  historical opens, unlisted retained opens, and the mapped original Downloads
  PDF outside the historical repository prefixes all reject. Listed retained
  and scratch operations remain permitted. These are tests of specified guard
  behavior, not hostile-code containment.

The nine denied original script probes in the successful result are runpy's
initial source-open probes. The pinned loader subsequently supplies those exact
source bytes. They are not successful reads from the originals or solver
launches. Running from a dedicated scratch cwd removes the earlier false
classification of descriptor-relative cleanup names such as `fit-00`.

## Findings resolved during review

The earlier `replay-v3.py` allowed a prefix-mapped extra unbound file to resolve
successfully and accepted direct unlisted retained files. A nonexecuting fixture
confirmed both with zero mapped reads. Final read-file membership enforcement
fixes this for open and source-loader paths; metadata fallback remains explicit.

Integrity checks originally used assertions without rejecting optimized Python.
The final early `if not __debug__` exception prevents `-O` from bypassing them.
The subsequent `replay-v4.py` guard initially covered only directory prefixes,
leaving one exact original Downloads PDF outside them. Final guard membership
also checks original mapping keys, closing that observed gap. Earlier attempts
and code remain preserved; no original scientific failure or gate was relaxed.

No blocking interface findings remain for the exact trusted input closure.
The new `prepare_snapshot.py` helper is outside this review's acceptance; this
verdict covers the replayer, exact retained bindings, probes and saved results.

## Limits and reproduction

This is a single-use CLI compatibility harness for trusted, hash-checked Python,
**not a security sandbox**. Audit hooks/monkeypatches do not isolate arbitrary
Python, native extensions, malicious code, concurrent modification or all
possible I/O channels. It does not provide signed provenance, hermetic toolchain
reproduction, a new binary build or independent physical/model validation.
Transferred hardlinks prove path relocation; they do not create an independent
physical backup. A Python/stdlib/import environment and the named private bytes
are still required. Retention and replay grant no redistribution rights.

Run the nonexecuting probes and frozen-byte/result checks from the repo root:

```sh
python3 -B docs/benchmarks/kfs-relocated-audit-v1/independent-review/check.py --repo "$PWD" --candidate-result docs/benchmarks/kfs-relocated-audit-v1/attempt-v5.json --output /private/tmp/kfs-relocation-interface-review-replay.json
```

The checker verifies the final candidate hash before testing it. It performs
synthetic helper/preflight/guard probes and examines the existing successful
result; it does not start the full saved corpus or any subprocess. The separate
full-repeat command records the actual relocated corpus execution performed
for this review. Altering frozen source, mappings, inputs or expected outcomes
requires reassessing affected interface judgments; this acceptance cannot be
carried silently to changed bytes.
