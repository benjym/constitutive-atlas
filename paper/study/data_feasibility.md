# Data feasibility before expanding the benchmark

The shared atlas now includes curated public records beyond the KFS pilot. Run the paper-specific field inventory with:

```sh
python3 paper/scripts/audit_public_feasibility.py
```

The generated [report](../results/public-feasibility/report.md) and JSON record the exact shared-manifest hashes, source identities, record hashes, channel completeness and initialization fields. The shared loader verifies curated assets and their source declarations first. Counts are records and material labels, not independently verified specimens or experimental batches. The audit computes no response errors, plots or fits.

## What the current audit permits

The OPARA triaxial records have the minimum fields checked here. They remain candidates: field presence does not establish applicability, control fidelity, preparation-history initialization or experimental validity. The associated [publication](https://doi.org/10.1007/s10706-025-03251-7) describes a sand–fines mixture with a fine-grained matrix. Treat it as a possible separate applicability panel; do not use its availability to claim a second clean-sand benchmark.

The GEOLAB normalized triaxial records retain warnings about initial state and total/effective stress interpretation. Some reported volume channels are also withheld pending review. Do not infer initialization from nominal confinement or promote a source curve merely because it plots successfully. Review the source worksheet and original experiment evidence for the selected material.

Source-defined measurement series need explicit unit/sign mapping, loading controls and initialization before prediction. A summary row is not a loading history. Several curves may share one source worksheet; the audit records that as a conservative related-record block. This does not prove specimen identity or statistical independence.

## Priority for the present material panel

The immediate common-information gap is KFS characterization and compression evidence, rather than a shortage of unrelated curves. [The characterization record](kfs_characterization.json) pins the original reported index measurements and identifies the provider's OE, OEC and ISO series. OE1 and OE12 were subsequently selected from published metadata as development endpoints; OE2–11 were reserved before raw-response inspection. Only the two development members have been extracted. OEC and ISO responses remain unassigned and unread by paper commands.

Use eligible compression evidence from the same material. Darmstadt or clay compression curves cannot supply missing KFS constants. Before replaying a compression test, check whether full initial stress and internal-history information can be established; an observed vertical stress alone does not determine the full stress tensor. Preserve loading order through unloading/reloading and review low-pressure domain restrictions.

The next scientific decisions are therefore: choose and review KFS compression-development evidence; resolve metadata for a coherent second sand material if possible; and decide whether a mixed-soil panel adds enough value to justify separate model admission. The field inventory does not close any of those gates.

## Refreshed inventory and Hostun follow-up (2026-10-31)

The preceding field audit covered 522 records under 84 material labels. The [latest collection refresh](collection_refresh_2026-10-31.md) covers 628 records under 89 labels: 485 source measurement series, 94 summaries and 49 normalized experiments. Twelve records still meet its minimum triaxial field checks; these remain candidates rather than admissions. This check does not assess eligibility for DSS, torsion, rock or grain-scale tasks. The larger inventory therefore does not by itself close the second-material gap. These are snapshot counts, not fixed manuscript results.

The [Hostun metadata review](hostun_feasibility.json) pins selected curated records and their source worksheet cells. Ten drained source series expose axial strain and deviatoric stress without volume channels. Their group labels carry different density/confinement conditions, whereas the worksheet summaries repeat a single void ratio; the second worksheet also has summary pressures that differ from its group labels. Do not broadcast those summaries into specimen initialization. Original test correspondence, initial-state timing and volume evidence need source review before the primary panel can use these curves. A separate stress-only task would require an explicit protocol and suitably limited claims. No source records or initial states were changed.
