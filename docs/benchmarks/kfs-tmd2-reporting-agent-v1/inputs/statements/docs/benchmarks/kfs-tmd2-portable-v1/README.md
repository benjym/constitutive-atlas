# Portable local TMD2 benchmark

1 November 2026. **The single-command fresh online run succeeded:** download, archive/member/content checks, normalization, one serial native build from the archived source, three fixed full-range paths, source/refinement assessment, figure and tables. Its complete numerical summary is byte-identical to the [preceding frozen study](../kfs-tmd2-research-range-v1/README.md). No source bounds, material constants, initial state or numerical settings changed.

## One command

From the repository root, with Python 3.10+, CMake 3.20+, a C++20 compiler and Matplotlib installed:

```sh
python3 tools/benchmark_tmd2.py --output /private/tmp/tmd2-local-reproduction
```

Choose a fresh writable output directory. The command fetches the pinned original TMD1–5 archive from the author, validates its SHA-256 and the TMD2 member, normalizes TMD2, extracts the verified frozen Atlas source, and builds only `atlas_solver --parallel 1`. It then freezes the exact artifact/data/inputs before three serial calls. No author implementation code is executed. There is no fitting, alternative strain-convention sweep, Wasm build or remote CI/deployment.

For offline preparation, add `--archive /path/to/KFS-TMD1-5.zip`. To avoid rebuilding on the coordinator's machine, add `--solver /path/to/the/recorded/atlas_solver`; reuse accepts only the exact artifact from the preceding study. Omit `--solver` for a portable build of the archived source. A solver supplied from a different build is deliberately not inferred to be equivalent. This command targets the historical frozen benchmark, not whatever model/compiler changes happen to be in the current worktree.

The output includes `report.md`, `results/reproduction.png`, `results/summary.json`, every native stdout/stderr, controls, command logs and receipts, plus private local raw and normalized data. Existing output directories are refused. Any failed process or numerical gate produces a nonzero command status; its retained evidence must be inspected. Command success is a bounded operational-reconstruction result, not model admission.

## Content identity and prospective gates

The original archive is pinned to `c83098bca222dbcbb67b7cb4fa4e57c300d22cad2d71211e6393c85c3a74c712`, TMD2 member to `dbd60b1aab4608766e5d002f513ae31e8cda7898a4babe32afea89f997229667`. The normalized semantic hash is `11e6ecfb2d77f4db92ab1a167ead4b0d13de7a89031f72bbe05cab1df1bd90dc`. Only `provenance.normalized_at` is excluded from semantic identity; every measurement, header, warning, convention, initial value and other provenance field remains covered. Fresh normalization keeps its truthful new timestamp, and its exact file hash is frozen separately before material calls.

The previous source reference, requests, protocol, settings, runner and assessor are copied byte-for-byte and verified against their pinned packet. Only local artifact/data paths, exact file hashes and reproduction receipts change. Preparation builds occur before the material-call freeze. The prospective case phase itself performs no build and runs each of the three requests once. The archived model catalogue must match exactly. No new compilation is accepted solely because its curves look similar.

[Verification](verification.json) and [run result](run.json) record the actual fresh online execution. [Generated report](report.md) contains the resulting figure and tables. The command's exact executed source is saved as validated-command.py; it is a historical byte copy, not the supported CLI location. All three path receipts bind artifact and input-freeze hashes. Raw stdout remains in the recorded local output directory, avoiding another redundant numerical archive; the complete saved raw results of the preceding equivalent study remain committed. Do not describe this reduced receipt packet as a self-contained new raw-output archive.

The copied portable freeze refers to identical shared input files in the preceding packet, plus the copied source-pins.json and portable-command.json here. It is an execution receipt, not an assertion that every input file is duplicated in this directory. The local full output contains all of them.

## Data access and publication scope

The [author's general remarks](https://www.torsten-wichtmann.de/KFSDB-general.htm) and [TMD downloads](https://www.torsten-wichtmann.de/KFSDB-TMD.htm) were checked again on 1 November 2026: they provide original research data downloads, but no explicit redistribution grant was found on the inspected pages. This command downloads into the user's local research directory. **It does not grant permission to redistribute those original measurements.** See [the reuse review](../../DATA_REUSE.md). The separately licensed 4TU compilation remains paused per the existing review; this command does not silently substitute its curves.

No raw/normalized measurements or measured plot samples are in this packet or public website assets. The committed plot shows source model coordinates and Atlas predictions only; reported measurement errors are aggregate statistics. The source calibration campaign was already exposed, so errors are descriptive and not held-out validation. Historical strain conversion and independent scientific review remain open. Keep the entire command output local until applicable measurement reuse terms are resolved.

BENCH-03 local reproducibility is delivered, but its roadmap checkbox stays open pending the public data-permission/release gate. Public measurement bundling and a licensed public benchmark release remain incomplete. BENCH-01/02 qualifications from the previous study are unchanged. The next roadmap priority is independent source/model review and the six-model collection, not a larger reproduction framework.
