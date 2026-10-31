# VW96 development inputs: bounded crosswalk

1 November 2026. Coordinator review of existing records, not a new independent
scientific review or fresh inspection of the original PDFs. This closes the
input-accounting/definition-difference task only.

## Formulation and parameter roles

The existing [original-paper reconciliation](../../models/hypoplastic-sand-vw96-original.md)
locates the eight-constant VW96 host: stress rate Eq.(40), friction factor
Eq.(41), shape Eq.(42)/AppendixC10, limiting densities Eq.(43), density factors
Eqs.(44)–(45) and barotropy Eq.(46). This differs from the seven-constant
beta=1 host discussed in the IGS97 reconciliation. The pilot fits arbitrary beta
and must retain its VW96 identity. Zero-spin, infinitesimal-strain scope remains
explicit; no finite-rotation or physical-time validation is inferred.

| Input | Pilot treatment | Value or exploratory bounds | Representation/source role |
| --- | --- | --- | --- |
| phi | Fitted | 0.45–0.70 rad | Friction factor and constitutive geometry |
| hs | Fitted | 5e8–2e10 Pa; log search | Granular hardness/pressure dependence |
| alpha | Fitted | 0.05–0.40 | Density influence factor |
| beta | Fitted | 0.5–4.0 | Stiffness density factor |
| n | Literature-fixed | 0.27 | Pressure dependency exponent |
| ed0 | Literature-fixed | 0.677 | Dense limiting void ratio at zero pressure |
| ec0 | Literature-fixed | 1.054 | Critical-state void ratio at zero pressure |
| ei0 | Literature-fixed | 1.212 | Loose limiting void ratio at zero pressure |
| p_ref | Fixed numerical scale | 100000 Pa | Project scaling, not a ninth VW96 material constant |
| Initial stress, void ratio | Per specimen from normalized file | Full recorded values, not fitted | Measured-file initialization; conflicting source values remain unresolved |

The pilot baseline cites Table 3 of the 2026 Machacek/Tafili/Grandas Tavera source
[via DOI](https://doi.org/10.1002/nag.70375). Its full material seed is phi 33.1 degrees,
hs 4e9 Pa, n 0.27, ed0 0.677, ec0 1.054, ei0 1.212, alpha 0.14, beta 2.5. The existing
[transfer parameter record](../../../benchmarks/parameter_sets/kfs-hypoplastic-literature.json)
records conversion and scope. This review checks consistency with that record,
not the publisher table itself. Four constants remain inherited throughout the
pilot; additional prior information is not eliminated by fitting four others.
Do not describe these fits as full calibration or equal-information comparisons
with elasticity or Drucker–Prager. The bounds are exploratory analyst choices.

## Archived versus current definition

The [audit](audit.json) verifies the archived VW96 model hash against each saved
run. Comparing the entire parsed archived/current definition shows only source
metadata and six parameter labels changed: n, ed0, ec0, ei0, alpha and beta.
After removing those descriptive labels and source metadata, every field is
identical, including equations, derived quantities, state, parameter order,
defaults, limits, units, domain and integration declarations. No physical
parameter-default or parameter-bound change was found for VW96.

This removes the definition-level ambiguity for this formulation. It does not
establish current-versus-archived engine equivalence or re-execute the current
solver. Keep all result labels tied to the archived executable hash until a
separately specified current-engine replay. The current DP model has actual
equation/derived-expression differences and cannot receive the same conclusion.

## Decisions and next action

- Complete: separate eight material constants from numerical scale and initial state; expose four fitted/four inherited inputs; distinguish VW96 from the IGS97 host; resolve the current VW96 definition difference as descriptive metadata only.
- Open: independent equation/scientific review, source-table verification of inherited calibration information, source-matched published baseline, initial-void-ratio conflict, engine replay and publication rights for measured curves.
- Next bounded action: BENCH-01, inspect existing source material for one complete published model/parameter/material case that matches an implemented formulation. Record eligibility and exact mismatches before choosing a prospective replay. No new optimizer sweep, data family or generic engine feature is needed for that source decision.

TMD12/13/14 remain development-only under the declared file-state assumption.
Choosing an original/later value by whichever produces lower error is not an
acceptable resolution. The original Hochstetten example in VW96 is a separate
material and is not a substitute KFS parameter set. None of these records closes
M1/M4 admission.
