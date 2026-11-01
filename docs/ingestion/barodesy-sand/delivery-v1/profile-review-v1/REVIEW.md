# Accepted independent public-profile review

Reviewer: actual separate agent `/root/barodesy_sand_review`, 2 November2026. Scope: reader-facing `barodesy-sand` profile only. **Accepted**, with no blocking corrections. The exact reviewed draft is retained as `reviewed-profile.json`, SHA-256 `29cacdd3a1951d2f37b0bc0ee03b6f537a2cf1b7093934b25d473ca927b20d3e`. Its parsed object matches the isolated production `web/model-profile-data.mjs` entry exactly. This review does not change immutable model/source/qualification bytes or the prior scientific decision `df0e95028f38e4af94665ea8689d58b37a92d8c84b33f6aec4c503cbbd84efc6`.

The reviewer read `docs/PUBLIC_MODEL_PROFILES.md`, the revised profile, exact source-backed definition and the qualified-scope dossier. Original2015 printed pp53–57/59 and the separate2019 Table1 were already visually reviewed for this model; printedp57 calibration/parameter discussion was visually reread for this profile task. The independent source/mathematical review remains retained under `independent-review-v1/` and `independent-review-v2/`. No builds, material calls, production edits or new scientific approval occurred.

## Behaviour, exploration and scope

The profile accurately introduces the complete2015 direct stress-rate law without a yield surface. Direction sensitivity follows Eq9 and Eq31; stress-dependent stiffness follows Eq23; density dependence and critical-state approach follow Eqs26–31. It does not promise elastic/plastic separation, experimental calibration or general material validity. “Pressure” is readable shorthand; parameter descriptions correctly use stress magnitude for the actual Frobenius stress scalar.

The proposed exploration uses real controls: `Drained triaxial`, `Load model example` and monotonic loading. `web/index.html` contains that button; `app.js` routes it through `populate`, and `state-contract.mjs` builds a complete explicit starting stress/state/parameter example from the exact definition. The example supplies equal compressive normal stresses, zero shear and explicit void ratio. Comparing starting void ratios at unchanged stress/parameters is a legitimate illustration; the prose correctly warns that changing density does not reconstruct preparation history. The public1%/100increment drained default was already part of the separately approved bounded qualification.

Scope and limits correctly disclose infinitesimal fixed-axis kinematics, compression-positive effective stress/strain, rate independence, nonzero positive-definite stress/density restrictions and absence of finite rotations/tangents/experimental validation. Mixed-control constraints are explicitly imposed at increment endpoints, not continuously at every constitutive stage. The previous claim suggesting the sand law provides a pore-pressure response is removed: the revised profile expressly says it supplies no pore-pressure evolution law. Browser controls/layout/live functionality still require separate delivery evidence.

## All seven parameter guides

| Parameter | Assessment and original source basis |
| --- | --- |
| c1, unit1 | Critical-friction direction coefficient matches Eq9 and p57 Eq32's relation to critical friction angle. |
| c2, unit1 | Dilatancy-dependent direction-mapping coefficient matches Eq9 and p57 calibration of response curvature. |
| c3, unit1 | Density weighting matches Eqs29–30, with scalar sum `f+g=delta+c3(ec-e)`; it is not called an independently measured modulus. |
| c4, Pa | Stress-valued offset in `c4+c5*stress magnitude` matches Eq23. Warning against zero-stress initialization preserves the normalization/domain restriction. |
| c5, unit1 | Stress-dependent stiffness slope and critical-density pressure dependence match Eq23 and Eqs26–27. This corrects the previous misleading generic “density coefficient” guide. |
| ec0, unit1 | Zero-stress/zero-pressure critical void-ratio reference matches Eq27 and p53 notation; no executable zero-stress start is promised. |
| emin, unit1 | Lower void-ratio reference/density boundary matches Eq23 and p55 discussion. It is not presented as a measured conventional specimen minimum. |

Names and units match the exact model definition for all seven parameters; defaults remain sourced dynamically rather than duplicated in editorial data. The separate2019 illustrative attribution and material-specific calibration warning are appropriate. Exact persistent state label `e` is correct; initial tensor content is explained in preparation prose. Both DOI references identify the intended publications; all declared local content sources exist in the isolated release tree.

## Decision and checks

The profile meets the source-backed public-content contract within this model's accepted scope. `checks.json` binds the exact reviewed entry and verifies parsed production-entry equality, parameter-name/unit completeness, local content-source availability and unchanged model SHA-256 `3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239`. Coordinator-reported structural tests are not substituted for this independent reading. No additional scientific gate or model-byte change is requested. Package/browser/live presentation remains the coordinator's separate E7/E8 work.
