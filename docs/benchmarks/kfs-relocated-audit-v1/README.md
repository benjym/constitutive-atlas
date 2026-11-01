# Relocated saved KFS reporting audit

This replay reconstructs the existing accepted [C1–C7 reporting review](../kfs-development-agent-v1/README.md) from the [durably retained campaign](../kfs-full-private-retention-v1/README.md), preserving every original result, command identity, negative control and scientific limitation. It performs no fit, new experiment, compilation or material call.

The original public input closure contained242files, plus five review outputs and its manifest. Preflight found one unavailable historical archive map. Its original three document bindings/first17entries recover bytes with exactly the review's expected SHA256fc0e1bfc…; [recovery provenance](map-recovery.json) and the expanded source map are retained. A new additive archive sidecar restores that binding without changing any review document or expected hash. The first replay also found an omitted transitive `atlas/data.py` import; the unchanged initial-repository source is frozen separately in v2. The final snapshot therefore has249public files, alongside9423retained private files. `freeze.json` preserves the original failed closure; `freeze-v2.json` is the normal default.

Reconstruct the exact public snapshot into a new directory, then replay using the private campaign root:

```sh
python3 -B docs/benchmarks/kfs-relocated-audit-v1/prepare_snapshot.py --output /private/tmp/kfs-public-snapshot
python3 -B docs/benchmarks/kfs-relocated-audit-v1/replay.py \
  --snapshot-root /private/tmp/kfs-public-snapshot \
  --private-root .local/private-evidence/kfs-development-campaign-v1 \
  --output /private/tmp/kfs-relocated-review.json
```

The existing local frozen roots can also be used with only `--output PATH`. The output must be new. Private assets must be supplied separately; their retention grants no public reuse permission. Optimized Python (`-O`) is deliberately rejected because the original auditors depend on assertions.

The compatibility harness verifies all frozen bytes before audit execution. It keeps original lexical filenames and recorded commands, relocates listed file reads/imports, rejects unlisted retained inputs and frozen writes, and prohibits process/network launches. Directory mapping supports metadata operations, not arbitrary file reads. Original-file access is blocked, including the Downloads source receipt outside the old repository. This is a harness for trusted hash-checked Python auditors, **not a security sandbox for untrusted code**.

The successful v5 transferred-root run and minimal three-file relocated-harness run produce the exact original review result: eight independent groups, eight saved auditors and8867mapped file reads. The historical calibration/evaluation/refinement/nested checks and corruption witnesses remain unchanged. The original refinement failure remains a failure; the separate nested result remains passing. Nine denied original-source probes occur during runpy's loader detection; execution proceeds using the exact retained source fallback. Scratch cleanup now runs in a dedicated temporary working directory. No original input bytes are used as fallback.

`attempt-v1.json` retains the missing-import failure; v2 retains the scratch-symlink relocation defect. The later candidate and independent-review evidence preserve the reviewer-identified unlisted-read, optimized-Python and outside-root source guard corrections. The public results contain scalar audit summaries only, matching the already public original review; no measurement/prediction arrays, raw native streams, PDFs or executables are republished.

The minimal-clone test copied only replay.py, freeze-v2.json and the retention receipt into a separate root, used a freshly reconstructed public snapshot and transferred private roots, and reproduced the same result with original reads prohibited. The transfer fixture uses same-filesystem hard links; input bytes were verified before replay and never modified. This demonstrates relocation on the recorded Python/macOS environment, not all Python versions/platforms, a rerun of numerical trajectories or resolution of the archived source/build association, specimen-state conflict, model admission, experimental validity or rights. Broader paper/release and website delivery gates remain open.

Separate interface review and its exact candidate/result bindings are under `independent-review/`. The historical scientific decision remains unchanged; this review concerns the new replay interface only.
