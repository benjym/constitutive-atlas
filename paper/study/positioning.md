# Paper positioning audit

Audit date: 30 October 2026. This targeted check informs the study design; it is not the systematic formulation survey. [The evidence ledger](related_work.json) records queries, primary-source locators, access limitations and unresolved questions. No independent review is claimed.

## What the paper must add

The useful intended contribution is a source-traceable account of **which mechanisms improve which predictions, with which calibration and initialization information**. The survey supplies breadth; a smaller comparable benchmark supplies predictive evidence. Neither a model count nor an automated fitting pipeline establishes that contribution.

Prior work already covers important parts:

| Precedent | Consequence for this paper |
| --- | --- |
| [D’Onza et al. (2011)](https://eprints.gla.ac.uk/56619/) | A collaborative constitutive benchmark included an undisclosed test. Our inspected development responses do not have that status. |
| [Machaček et al. (2022)](https://link.springer.com/article/10.1007/s11440-022-01669-4) | Automatic fitting, optimizer/metric comparisons and parameter dispersion are established. Repeated runs alone are insufficient novelty. |
| [Machaček et al. (2023)](https://doi.org/10.1007/978-3-031-12851-6_14) | Multi-model automatic calibration is established. Distinguish fixed physical error scales and supplied information explicitly. |
| [Zeng et al. (2026)](https://www.sciencedirect.com/science/article/pii/S0266352X26001151) | Dataset composition and weighting already motivate calibration design. Extend the question across formulations; do not claim a first study of experimental-data value. |
| [Wichtmann et al. (2019)](https://www.torsten-wichtmann.de/paper/journal/2019-SDEE-Check-constitutive-models.pdf) | Its calibration and history assumptions make supplied information central to a fair comparison. Targeted methods and table review is now recorded. |

## Consequences for the study

1. Keep RQ1–RQ3, but link the eventual calibration-design results to mechanism and formulation differences. More sweeps of the present three development models would not establish the intended contribution.
2. Review at least one credible parent–extension pair if available. Separate independent recalibration from a mathematically justified mechanism reduction. Record when reductions change admissibility or initialization.
3. Account explicitly for information supplied outside the fitted curves: index tests, literature constants, imposed parameter relations, measured initial state and inferred history. Equal fitted counts or test counts do not guarantee equal information.
4. Show paired per-test tradeoffs and completion before aggregate comparisons. Develop conclusions about declared tasks, rather than general prevalence or universal rankings.
5. Keep a claim–evidence map: each proposed contribution needs both a prior-work comparison and a completed scientific result. An intended distinction remains a hypothesis until that evidence exists.

## Open review tasks

Both previously inaccessible studies now have local, checksum-pinned full-text copies. The ledger records targeted methods review and visual checks of the parameter tables. The 2026 study's full-dataset score includes calibration members, so it cannot be equated with our disjoint-test score. Its prescribed fabric state also illustrates why initialization belongs in the information account.

The [development information ledger](calibration_information.json) records the present pilot's fixed quantities and their roles. It does not change frozen fits or establish equal-information admission. The four supplied hypoplastic constants are not knowledge obtained from the declared shear-test packages.

Independent review and a complete protocol comparison remain open. Next expand the positioning check to ExCalibre, the 2021 three-model implementation study, parameter identifiability and discriminating-experiment studies. Review broader surveys separately; this targeted ledger cannot establish literature completeness.

The atlas charter also requires comparison with MFront/TFEL, MGIS/MTest, OpenSees and other relevant infrastructure before any language or tooling novelty claim. The scientific manuscript does not currently make such a claim.
