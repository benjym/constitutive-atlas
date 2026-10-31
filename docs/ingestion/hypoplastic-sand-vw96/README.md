# VW96 source reconciliation and v0.3 contract

This bounded review reconciles the full original [von Wolffersdorff (1996) paper](https://doi.org/10.1002/%28SICI%291099-1484%28199607%291%3A3%3C251%3A%3AAID-CFM13%3E3.0.CO%3B2-3) with the existing executable host. The second-agent [original-equation review](original-equation-review-v2/README.md) covers all21 pages, with visual inspection of pages1–20. Eqs1–2/40–46 and AppendicesA–C support the rate factors, signs and invariants in the inspected common domain. No material-law correction was identified. This is technical reconciliation, not signed independent scientific admission.

[formulation-crosswalk.json](formulation-crosswalk.json) maps all18 derived quantities, both evolution equations and all9 parameter declarations (eight material constants plus project scale). Its complete v0.3 profile declares compression-positive Mandel tensors, infinitesimal strain-path rates, effective Cauchy stress and a fixed spatial zero-spin restriction. Persistent sigma and scalar e require explicit initialization, with no inferred preparation or projection. The original source objective rate needs additional transport outside that restriction. The root remains byte-identical and is not migrated by this packet.

The IGS root has exactly the same first18 derived expressions and first8 guards. Host parameter defaults, bounds and units also agree; six descriptive labels differ. The original VW96 TableI has beta=1.5, the later IGS original host specializes beta=1, and current illustrative defaults use beta=1.05. These are distinct parameter identities.

Two qualifications need explicit decisions before claiming broader applicability or reproducing original figures:

- AppendixC describes its shape function for u=0 or 0<u<sqrt(2). Current guards also admit sigma=diag(450000,-75000,-75000)Pa at e=.7: u²=49/8, cosine=-1, F=1. This demonstrates wider algebraic continuation, not a demonstrated Eq40 defect or a source instruction to add a guard. The separate diag(-100000,300000,300000)Pa witness lies inside that shape range yet has a tensile principal stress. No universal principal-sign rejection rule was found in the full paper. Strict density bounds also exclude source limiting states e=ed and e=ei. Physical applicability and numerical admission remain distinct.
- Figure10 text and curve legends give different density labels. For Figures13/14, the body gives e=.67 before isotropic preparation and .633 afterward, while captions label e=.67 at shear start. Both locators are retained; this packet chooses no preparation interpretation or reproduction deck. Source warns about deficient cyclic reloading stiffness for some multiple-reversal paths.

[27 standalone algebra checks](original-equation-review-v2/checks.json) and [13 parent contract checks](crosswalk-checks.json) pass. Parent checks validate an in-memory v0.3 candidate, explicit initialization, missing-field rejection, zero-load rates, host identity and both domain witnesses through current Python initialization. A diagnostic pass means the documented behavior was reproduced, not that a mixed-sign state is physically valid. The first witness produces binary64 cosine -1.0000000000000002; the saved exact algebra gives -1. No clamp or domain change was introduced.

Historical evidence is retained: v1 failed reference convergence, while v2 passed229 numerical checks. [historical-evidence-checks.json](historical-evidence-checks.json) verifies their saved report hashes only. Neither historical suite nor a compiled backend was rerun for this source review. The original dossiers/review records remain unchanged; the additive [pending v2 review](../../../catalogue/reviews/hypoplastic-sand-vw96-source-v2.json) narrows the remaining gaps. REV-04 and scientific admission stay open.

Reproduce without compilation:

```sh
python3 docs/ingestion/hypoplastic-sand-vw96/original-equation-review-v2/check.py
python3 docs/ingestion/hypoplastic-sand-vw96/check_crosswalk.py --repo .
```

Next bounded action: resolve and document the source-versus-numerical applicability policy for this shared VW96/IGS host, using these witnesses. Any resulting guard change needs a separate revision and frozen checks. Original-figure reproduction additionally needs an explicit curve-specific initialization interpretation. No solver expansion, new calibration, publication, push or deployment is part of this packet. Source PDFs/images/full extraction stay private; persistent links and checksums are retained.
