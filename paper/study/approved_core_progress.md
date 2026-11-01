# Approved core: initial implementation

31 October 2026. The user's "Yes" activates the recommended core A01-A07.
Optional B01-B02 remain pending. The requested proposal is preserved in
[its original snapshot](assumption_proposal_requested_2026-10-31.md); the
[current register](assumption_proposal.json) records the approval scope.
No contacts, copy requests, shared atlas edits or new final reservations.

## DSS preparation

The [development configuration](leap2022_core_development.json) contains all32
zero-static-shear LEAP-2022 candidates, individual report void ratios, and four
assumed initial-stress tensors per candidate: primaryK0=.50, sensitivity.35/.65,
and isotropic diagnostic1.0. Stress signs are retained as explicitly
compression-positive named components for later adapter conversion; they are
not silently passed to a solver with another convention.

All32 cached source files match the public registry's byte hashes and sizes.
Only their logical CSV headers were parsed, not numeric response records.
Actual column6 headers identify24 pressure-ratio and8 excess-pressure files.
The corresponding adopted registry units are dimensionless andkPa respectively.
This resolves header-level channel families, not reference timing or physical
equivalence. Column6 remains outside scoring under A05.

Headers span6 or7 physical lines, so the plotting script's fixed8-line skip
extends beyond the logical header. One file also has three empty trailing
header fields. A future response parser must preserve the original rows and
validate these formats, rather than copy the plotting reader. No silent
pressure normalization or removal of potentially populated extra columns is
authorized by a header-only check.

Regeneration is byte-identical. The paper's current NativeAdapter accepts a
drained-triaxial experiment and does not yet admit these simple-shear controls
or their spin/history mapping. Experimental DSS replay therefore remains behind
an implementation gate, rather than an unresolved request for permission.

## Compression diagnostic completed

The [approved compression configuration](compression_sensitivity_approved_core.json)
ran192 first-loading replays on development tests OE1/OE12, using the frozen
linear-elastic and VW96 implementations, fixed inherited parameters, fourK0
scenarios, two loading coordinates, two step sizes and three start thresholds.
All192 completed successfully; frozen source/executable identity checks passed.
Earlier configurations, predictions and fits are preserved.

For VW96 the largest paired initial-stress scenario difference is about22.2kPa,
while the largest paired step-refinement difference is about6.19Pa. Each pairs
the same measured observations at a fixed start, holding the other controls
constant. These values show material sensitivity to the initialization choice
in this diagnostic; they do not establish the correct experimentalK0 or
physical prediction accuracy. Two step sizes provide a refinement check, not
a proof of convergence. Coordinate sensitivity and inherited calibration
information remain explicitly qualified.

The full local report is in
`paper/results/compression-sensitivity-approved-core-v1/report.md` with predictions
and source/code/executable snapshots alongside it. The
[tracked progress record](approved_core_progress.json) pins its bytes and
records the counts, exposure limits and remaining DSS implementation gate.
