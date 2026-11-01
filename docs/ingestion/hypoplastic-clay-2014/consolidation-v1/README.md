# Clay2014: bounded ingestion consolidation

Task: **ING-hypoplastic-clay-2014**, coordinating parent, 1 November 2026.
This completes the existing consolidation assignment. Source resolution and scientific admission remain open. No source was newly acquired or visually inspected, and no build, material simulation, migration or deployment ran.

## Exact formulation and provenance

David Mašín, *Clay hypoplasticity model including stiffness anisotropy*, Géotechnique 64(3), 232–238 (2014), [DOI](https://doi.org/10.1680/geot.13.P.065). The inspected earlier work uses the [author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_Geot14-pp.pdf), dated 26 November 2013, SHA-256 `2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202`, 16 PDF pages. All equation/page locators below mean that manuscript. The [source dossier](../../../models/hypoplastic-clay-2014-original.md) records acquisition and visual-reading coverage. No private PDF path or bytes were reverified in this pass; copyrighted material is not bundled. Author hosting establishes access, not redistribution permission.

The selected research identity is **printed Eq14 Am / proposed Eq49 exponent / fixed material plane / zero spin / base law without IGS**. It is distinct from the 2013 isotropic host, optional calibrated-exponent variants, and AppendixB IGS pairing. The [retained model](../../../../models/research/clay2014/hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane.json) remains schema **0.1**, outside the top-level executable collection. The [research dossier](../../../models/clay2014-printed-am-fixed-plane-research.md) is an early checkpoint; its statements that finite paths have not run are superseded by the evidence table below, not by rewriting that pinned document.

[Input receipts](input-receipts.json) pin the current documents used here. They are consolidation identities, not substitutes for the studies' original source freezes or artifact receipts.

## Equation and v0.3 crosswalk

[Machine-readable crosswalk](crosswalk.json) supplies a **proposed** explicit v0.3 formulation plus the retained parameter/state inventory. It is not an executable model, migrated definition, or claim that old observations qualify new bytes. Read the [v0.3 contract](../../../FORMULATION_CONTRACT.md) before implementing it.

| Source | Representation and retained choice |
| --- | --- |
| pp2–3, Eqs2–8 | Fourth-order stiffness contracted to symmetric action; fixed `P=n⊗n`. Preserve the Eq2/Eq3 factors. Existing scalar component expansion avoids a new handwritten kernel. |
| p3, Eqs14–15 | Printed Am supplies barotropy; trace(L:I) is diagnostic only. Do not replace it silently. |
| pp9–10, Eqs34–50 | Coupled effective stress/void base rates; proposed Eq49 exponent applies in both Eq36 and Eq38. Source `a=.3` is distinct from that exponent. |
| Source sign map and inherited host | `T=-sigma`, `D=-E`; negate source stress RHS. Incompressible-grain `e_rate=-(1+e)trace(E)` is inherited, not a newly printed 2014 equation. |
| p2 Eq3, material orientation | Supply finite axis components explicitly; fixed spatial plane under zero spin. No fabricated fabric evolution or rotation transport. |
| p11, Eqs51–57 | AppendixB IGS is **excluded**. Its additional six memory components and normalization choice need a distinct formulation. |

State is symmetric effective Cauchy stress (six Mandel components, Pa) plus void ratio (dimensionless): seven scalars. Mandel order is xx, yy, zz, xy, yz, xz with norm-preserving shear factors; signs are compression positive. The proposed profile is `strain_path/strain_path_rate`, `small_strain_3d`, `fixed_spatial`, objective rate `none`, effective stress bound to `sigma`. These are Atlas restrictions, not a claim that the objective source law is globally small strain.

Physical parameters comprise friction angle (radians), lambda*, kappa*, N, in-plane Poisson ratio and three dimensionless anisotropy ratios; the supplied plane has three dimensionless components. The crosswalk preserves all actual numerical scale, reference-pressure and support-policy parameters separately in the retained inventory. Its initial stress/e values and parameter defaults are software fixtures, not a London Clay preparation or universal published constants.

## Temporal integration and initialization

A caller supplies a complete stress/e state, fixed axis and straight symmetric strain increment. Interpret the rate over a dimensionless path fraction from zero to one; no elapsed-time input, viscosity or aging follows. Source rate homogeneity permits this restriction; it does not select Atlas error tolerances or an integration algorithm.

At every stage evaluate stress and void rates from the same candidate state. Supply the actual axis unchanged and enforce its declared support policy; never normalize it secretly. Commit all seven physical channels together only after successful advancement. A rejected caller increment returns the exact original parent; accepted internal substeps remain trial-local. There is no source-backed caller reset, reversal write, or independent history cache in this base law.

Zero loading gives zero rates in the supported domain; a hold establishes no physical-time relaxation. Loading reversal changes the evaluated rate direction, not a discrete memory anchor. Preserve lazy zero-rate/hydrostatic branches and declared finite-domain checks. Positive pressure, admissible stress/stiffness interior, logarithm/power domains, density and orientation must be checked using the **selected implementation policies**, whose roundoff margins are not physical source limits. See the research dossier for exact margins and rejected underflow/Lode cases. No unique zero-loading material derivative or qualified algorithmic tangent is established by rate homogeneity.

Explicit initial stress/e/axis is still not a source-matched preparation history. The ambiguous London Clay AC stress label, consolidation history, material-axis preparation and external data dependencies remain unresolved. No automatic K0, IGS initialization or measured-specimen equivalence is inferred.

## Existing evidence: retain both outcomes

| Evidence | Existing result | Limit |
| --- | --- | --- |
| [Independent model algebra review](../../../reviews/clay2014-independent-model.md) | No blocking algebra discrepancy for the explicitly selected seven-state variant; separate Cartesian oracle | Bounded technical review; not signed scientific admission or publisher equivalence |
| [Instantaneous rates](../../../reviews/clay2014-rate-results.md) | 37 Cartesian cases and 16 rejection/recovery pairs per backend pass; retained serialization-audit failure has a separate additive assessment | Rates and recovery, not finite-path accuracy or preparation |
| [Original finite paths](../../../reviews/clay2014-path-results.md) | **Failed** endpoint refinement: four of 144 inequalities per backend; 24 trajectories and 288 updates per backend | Accuracy, covariance and rollback subchecks do not turn the failed study into a pass |
| [Distinct controlled hydrostatic follow-up](../../../reviews/clay2014-controlled-resolution-results.md) | 315 updates per backend; all 18 contraction inequalities pass with controlled mesh refinement | One hydrostatic reversal mechanism; does not qualify general anisotropic paths or supersede the original failure |

No study was rerun for this packet. Shared backend parity is not independent equation verification. Historical evidence keeps its exact original definition/toolchain identities.

Run `python3 -B docs/ingestion/hypoplastic-clay-2014/consolidation-v1/verify.py` from the repository to check document hashes, local links and retained state/parameter inventory. This checks packet integrity only; it does not rerun constitutive verification. The recorded result is [checks.json](checks.json).

## Remaining decisions, in order

1. Reconcile final publisher text with the author manuscript and decide the **printed Am versus trace(L:I)** discrepancy. The research law intentionally retains printed Am; a correction must receive a new explicit identity and review.
2. If AppendixB is requested, resolve its **factor 4.5** printed Eq17 versus Eq19/56 conflict. This base-law packet supplies no normalization correction or permission to substitute IGS97/GIS/ISA.
3. Review physical preparation, source parameter choices and the finite-spin/material-axis scope. No axis transport law is invented to broaden the current restriction.
4. Only after agreeing a useful scope, claim a separate v0.3 migration/qualification task: bind legacy inputs explicitly, freeze exact new definition and controls, check independent rates and selected full-state paths, then serial native/Wasm and browser gates. Old receipts are supporting history, not automatic qualification of migrated bytes.
5. Obtain independent scientific admission for the exact chosen definition; experimental applicability and calibration remain separate.

The smallest useful next action is a source/scope decision on the two printed discrepancies and fixed-plane restriction. Further generic primitives, fits, repeated rate studies or website integration are not justified by this consolidation. This task adds one navigable ingestion packet; the executable model count and reviewed-model count do not change.
