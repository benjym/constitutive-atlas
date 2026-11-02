# Preseal source inspection (not a verdict)

Task REVIEW-bingham-final-imported-context-v1. No sealed author manifest/outcomes exist yet; acceptance is pending.

Current prepare.py builds `catalogue` only from path-prefilter candidates. Its later `parents` expansion does not load remaining immediate JSON siblings before building `edges`. An independent reconstruction of this exact initial logic found396parent contexts and573 immediate sibling documents with recognized pairs absent from catalogue, including canonical Ramberg51, Barodesy45 and linear-elastic26 pairs. These counts identify a source coverage gap, not a numerical or preservation failure. Author/coordinator notified before sealing; supplemental full-sibling expansion can retain the initial attempt and close coverage.

Exact-text JSON parse memoization preserves checked_receipt control flow: checked_receipt/contains_receipt only read parsed documents/maps; they do not mutate them. Cache keys are complete immutable text, so any changed map text is separately parsed. Hashing, per-document sibling pin checks, path containment and resolver errors are still executed. Cached parsed-object reuse is safe for these observed read-only calls; independent replay must not cache outcomes or hashes.

Source/provider restoration is bounded to exact matching hashes; declaration/current failures must remain explicitly classified as restored versus retained. Root CMake/common compiler units remain current; old source capsule snapshots must bind historical bytes rather than claim live-source equality. All copied namespaces remain exact archives; no stale root maps may be transplanted.
