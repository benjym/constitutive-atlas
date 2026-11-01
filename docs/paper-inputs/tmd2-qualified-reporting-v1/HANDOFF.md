# TMD2 reporting inputs — accepted author handoff

The exact reporting projection has passed separate-agent review with no blocking findings. This handoff closes PAPER-tmd2-reporting-tables-v1 and REVIEW-paper-tmd2-tables-v1 only; it does not close a scientific milestone or manuscript integration.

Use [readable tables](generated/tables.md), [LaTeX fragment](generated/errors-tabular.tex), [vector figure](generated/refinement.svg), [PNG preview](generated/refinement.png) and [full-precision values](generated/reporting.json). Keep the fragments together with [the caption](generated/CAPTION.txt), the full qualifications in tables.md/reporting.json, and [the accepted scientific reporting scope](../../benchmarks/kfs-tmd2-reporting-agent-v1/README.md). The table fragment alone does not carry all qualifications.

These are descriptive calibration-campaign errors and saved path-refinement comparisons for an operational reconstruction. They do not establish held-out experimental validation, physical integration error/order, general model admission, current-engine qualification or measurement redistribution rights. Historical kinematics, direct initialization, internal-stage and source/version limitations remain explicit. Original API rejections and the process-status defect/corrected guard are retained.

Replayed successfully on 2026-11-02:

    python3 -B docs/paper-inputs/tmd2-qualified-reporting-v1/check_saved.py
    python3 -B docs/paper-inputs/tmd2-qualified-reporting-v1/independent-review/check_saved.py

The checks cover seven public inputs, 18 SI error scalars with exact display conversions, three paths, four refinement ratios, seven mandatory qualifications, three original API rejections and the exit23 witness. Seven changed-input tests reject mutations and all seven generated artifacts reproduce byte-identically in the recorded environment. The separate reviewer inspected the PNG and LaTeX source; no TeX compilation or manuscript layout qualification is claimed.

Next action belongs to the manuscript integration owner: incorporate the complete qualified fragments and check the rendered manuscript. No files under paper/ were changed, no new fits/material calls/builds were run, and no remote publication occurred. Preserve the frozen parent and reviewer files; any later changes need affected checks and review again.
