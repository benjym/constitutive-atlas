# TMD2 paper tables and refinement figure

This is an author handoff from the exact independently accepted six-question TMD2 reporting decision. It produces reusable manuscript inputs without modifying the separately owned paper tree, rerunning a fit or making a new constitutive-material call.

- [Readable tables and qualifications](generated/tables.md)
- [LaTeX table fragment](generated/errors-tabular.tex)
- [Standalone vector figure](generated/refinement.svg) and [PNG preview](generated/refinement.png)
- [Caption and interpretation](generated/CAPTION.txt)
- [Full-precision public scalars and exact input identities](generated/reporting.json)
- [Original accepted reporting review](../../benchmarks/kfs-tmd2-reporting-agent-v1/README.md)

The table contains all three retained research-range paths (400,800,1600 caller intervals), all18 descriptive RMSE/MAE/maximum-error scalars, and the four saved path-pair refinement checks. SI values remain unchanged in JSON. Display conversions are Pa to kPa and dimensionless accumulated trace-volume strain error to percentage points. The original three ordinary-API zero-point rejections and exit23 assessor false-pass/corrected-guard witness remain explicit and distinct from passing research-range results.

The figure plots saved path-pair differences divided by their frozen limits. It does not estimate physical integration error or convergence order. The scalar experimental errors are descriptive calibration-campaign results, with no held-out validation, model ranking or uncertainty claim. Operational accumulated coordinates, zero spin, nominal direct initialization without consolidation replay, project numerical choices and unverified historical decks/strain conversion remain qualifications. General model admission and measurement reuse rights are not established.

Only public reviewed scalars are read. No measurements, source PDFs, raw trajectories or binaries are copied. Matplotlib Agg renders the figure without invoking LaTeX or a material engine. The coordinator visually inspected the generated PNG for legible units, legend and the comparison-limit line. Runtime/font are recorded; byte-identical rendering is checked in the recorded environment.

Reproduce all integrity, arithmetic, seven changed-input rejection tests and deterministic artifacts:

    python3 -B docs/paper-inputs/tmd2-qualified-reporting-v1/check_saved.py

Generate into a new destination (existing paths are refused):

    python3 -B docs/paper-inputs/tmd2-qualified-reporting-v1/build.py --output /private/tmp/atlas-tmd2-paper-new

Independent projection review is a separate record under independent-review/. This handoff is not manuscript integration, scientific milestone completion, a public data licence, current-source/Wasm qualification or deployment.
