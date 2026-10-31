# Selected published case: KFS TMD2 with IGS

1 November 2026. **Source case selected; numerical reproduction not yet run.**
The next benchmark will reproduce the loose-sand curves in Wichtmann, Fuentes
and Triantafyllidis (2019), Figure 3a,b, using the complete published VW96+IGS law.
It is a published calibration-example reproduction, not held-out validation.

## What is now pinned

- [Material parameters](parameter-set.json): all thirteen constants, visually cross-checked against 2019 Table 1 and 2016 Table 2. The separate p_ref is a project numerical scale. In particular mR=2.2 and mT=1.1; the two tables reverse their column order.
- [Case inputs](case.json): nominal isotropic effective stress 100 kPa, initial void ratio 0.975 and fully mobilized isotropic history. The source's tension-positive h_ii=-R/sqrt(3) becomes compression-positive +R/sqrt(3); off-diagonal components vanish. Current example defaults are not substituted.
- [Sources](sources.json): private PDF hashes, publication links and inspected page/table/figure locations. PDF pages 2016: 4–5 and 2019: 2–4 were rendered and visually inspected. The supporting 2016 Section 3.2 history passage was text-inspected on page 3. No PDFs, extracted article text or rendered pages are redistributed.
- [Input checks](source-checks.json): all parameters fit the current declared bounds; parameter and state ordering match; 80/120-digit history construction rounds to the same binary64 value. These are input checks, not equation or trajectory verification.

The match to TMD2 is explicit in 2016 Figure 4a,b and Table 3: initial pressure 100 kPa,
relative density 21%, void ratio 0.975. The 2019 Figure 3 loose curve has that same
pressure/density pair. This avoids the unresolved TMD12–14 initial-void-ratio
conflict. The nominal published initialization remains separate from TMD2's
measured first point, which has a small stress anisotropy and e=0.975289261.
Neither is silently replaced by the other.

The [2016 paper](https://doi.org/10.1007/s11440-015-0402-z) also publishes the
complete hypoplastic+IGS equations in AppendixA and the named TMD2 calculation.
The [2019 comparison](https://doi.org/10.1016/j.soildyn.2019.05.001) supplies a
more isolated loose-sand model curve and repeats the parameters and history.
The parameter table is not being transferred to the eight-constant base law.

## One protocol gate remains before executable requests

The published curves extend through 25% axial strain. Keep that full range.
The existing 2% transfer demonstration is not a substitute for reproducing them.

At these strains, the plotted experimental measures and the constitutive driver
increments cannot be assumed interchangeable. The [data consistency check](data-coordinate-check.json)
on 445 already exposed TMD2 observations finds that eps_v matches
(e0-e)/(1+e0) to about 2.82e-10, whereas its difference from the logarithmic volume
measure reaches about 7.85e-5. The reported radial channel also follows the
additive eps_v=eps1+2eps3 convention. These are descriptive consistency results;
the channels are linked quantities, not independent validation observations.

This establishes the supplied volume-data convention, but does not establish the
original driver's axial-input or plotted simulation-volume conversion. For
example, 25% engineering axial shortening would correspond to logarithmic
compression -log(0.75), approximately 0.287682; directly imposing 0.25 as an
accumulated rate-law coordinate is a different path. Do not choose a convention
by whichever produces the smaller curve error. Atlas remains explicitly scoped
to its declared kinematics; this source decision does not confer finite-strain
capability.

The 2016 source names Niemunis's Incremental Driver; the 2019 source names
Abaqus-based element simulations with author UMATs. These are separate execution
provenances. Their exact versions/input decks and strain conversions have not
been established. The [author package page](https://soilmodels.com/download/incrementaldriver-zip/)
currently exposes a login/free-download placeholder; bounded historical-author
routes failed. No foreign source code or executable was run. Missing retrieval
is not evidence that a manual or deck does not exist.

## Bounded next execution package

1. Establish the source-driver/plotted strain conversion and digitize only the selected loose-sand model curves, with axes, line width and extraction uncertainty recorded. Freeze the comparison grid and precision-derived bounds before any candidate execution.
2. Use this exact source state and complete parameter set. Predeclared project numerical settings and 400/800/1600 outer steps are in case.json; they are not claimed to be the authors' settings.
3. Run at most three native material paths, serially, over the full published range. Retain every raw response, failure and committed prefix. Do not add a fitting sweep, model family, Wasm matrix or solver extension to this package. Verify a matching existing artifact before deciding whether a build is needed.
4. Generate one response figure and a table separating published-model reproduction, experimental error and numerical refinement. Report discrepancies and unresolved conventions; do not promote scientific admission automatically.

BENCH-01 remains open until the complete protocol/reference/acceptance freeze;
BENCH-02 remains unstarted. Independent scientific review and clean-checkout
reproduction remain open. Existing measured-data reservations are unchanged and
no new observations were acquired from reserved tests. No runtime observations,
builds, fits, model/schema changes or deployment occurred here.

## Reconstruct the source inputs

With the existing private source PDFs and normalized TMD2 file available, run
from the repository root into a fresh directory:

```sh
python3 docs/benchmarks/kfs-published-case-selection-v1/reconstruct_inputs.py --output /private/tmp/kfs-published-input-replay
```

The five generated JSON records reproduced byte for byte in the coordinator's
check. This script reads existing source/data bytes, reconstructs input rounding
and checks current parameter bounds/layout; it performs no constitutive
integration. Compare generated records with this packet before any runtime
freeze. Missing private inputs are an explicit local reproduction dependency.
