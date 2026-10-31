# Model–experiment applicability: KFS development matrix

DATA-applicability-matrix-v1; 1 November 2026. The
[machine-readable matrix](../catalogue/applicability/kfs-development-v1.json)
records the nine current executable definitions against the exact existing
Karlsruhe fine sand development allocation. It is an assessment inventory with
source-linked prerequisites, not a signed determination of physical suitability.
This advances DATA-04; broader material/protocol coverage and scientific judgment
remain open. This document and matrix are not constitutive model crosswalks.

| Current definition | Pair assessment in this matrix | Scientific eligibility |
| --- | --- | --- |
| Linear elasticity | Unassessed; historical pilot accounting does not certify this pair | Undetermined |
| Drucker–Prager | Unassessed; historical pilot accounting does not certify this pair | Undetermined |
| Modified Cam Clay | Unassessed | Undetermined |
| VW96 sand hypoplasticity | Conditional development comparison evidence; review pending | Undetermined |
| VW96 + IGS97 | Unassessed; base-law comparison does not transfer to IGS | Undetermined |
| Hypoplastic clay 2005 | Unassessed | Undetermined |
| Hypoplastic clay 2013 | Unassessed | Undetermined |
| Barodesy sand | Unassessed | Undetermined |
| Barodesy clay 2017 | Unassessed | Undetermined |

“Unassessed” means no assessment is made by this matrix. It does not assert
physical inapplicability or that no historical calculation exists. Neither a law's
name nor successful execution assigns suitability for a material. Each row binds
exact current model bytes, source/dossier evidence, prerequisites and limitations.
Changing a definition or linked document invalidates that row's identity check;
update the assessment deliberately rather than carrying old claims forward.

The dataset scope is the [existing allocation](../studies/kfs-development-v1/allocation.json):
five unique calibration IDs across pressure3/density3 and six evaluation IDs,
eleven distinct whole tests in total. Evaluation was previously exposed during
development. Reserved IDs remain excluded by the allocation contract. This is
not the entire Wichtmann database or the set of all hosted measurements.
No observation arrays, specimen measurements or numerical predictions are copied.

## VW96 conditions and evidence boundary

The [unsigned KFS review handoff](benchmarks/kfs-development-review-v1/README.md)
supplies the comparison qualifications. Apply the exact parameter, initialization
and control policy; browser defaults are not that published/development vector.
[Decision0004](decisions/0004-vw96-igs-applicability.md) separates the source law,
project compressive-soil comparison restriction, numerical cutoff and continuation
regions. Default comparisons require strictly compressive principal effective
stresses, positive pressure and ed<e<ei, within the declared small-strain,
effective-stress and zero-spin scope. These are prerequisites for assessment,
not claims that this metadata checker verified an entire trajectory.

The [current TMD7 replay](benchmarks/current-kfs-tmd7-v1/README.md) covers only the
existing file/file development window up to the first 2% cutoff. Six-test panels
use the archived executable; their results are not automatically evidence for
all current-engine experiments. Preserve the unresolved file/table density and
historical axial-coordinate/preparation qualifications, original failed refinement,
separate passing nested regime, prior evaluation exposure and pending review.
No predictive validation, independent scientific acceptance or data-rights grant
is inferred from this inventory.

## Check without responses or solver execution

```sh
python3 -B tools/check_applicability.py catalogue/applicability/kfs-development-v1.json
python3 -B -m unittest tests.test_applicability tests.test_study_allocation -v
```

The checker validates allocation/reservation roles and byte identities, exact
coverage of all top-level current model files, source pins, explicit prerequisites
and undetermined eligibility. It rejects duplicate/missing/stale models, unsafe
paths and attempts to promote eligibility or independent review under this v0.1
contract. Evidence pins are limited to repository docs/study metadata; it does
not execute linked scripts or invoke an experiment loader, model or optimizer.
The success report is an integrity/coverage result, not a scientific pass. It
includes the matrix's own hash. Seven focused synthetic/metadata tests verify
these boundaries, including an explicit allowlist of every file opened.

Future scientific assessment needs exact material/preparation identity, applicable
source ranges, declared parameter provenance and loading windows, full-path domain
and numerical evidence, and an independently recorded judgment. Additional
materials/protocols need separate dataset scopes. The current website continues
to use protocol/channel matching only; this matrix is not silently installed as
an overlay eligibility filter and changes no simulation behavior.
