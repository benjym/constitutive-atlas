# SANISAND independent monotonic research reference v1

Completed 1 November 2026, `REF-sanisand-project-monotonic-v1`. **An independent plastic-loading reference is now available** for the explicitly named project fixed-zero-memory monotonic scope. This advances the SANISAND proof without modifying the existing research definitions, accepting canonical reversal, signing source decisions or running a candidate solver.

[Derivation and source crosswalk](DERIVATION.md) specify the [2004 publication](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29), all tensor/sign conventions, continuous finite-hardening products, exact elastic first yield and additional numerical choices. The original PDF and seven existing private page renders were rehashed; the relevant complete pages were visually read. No source image/full text is redistributed. D01–03 have the prior AI technical support; D04–06/D08 remain research choices with no scientific signature. D07 remains unresolved.

## Frozen scope and evidence

- 27 paths: three pressures × three supplied void ratios × compression, extension and general shear with all three off-diagonal components. All are proportional, constant-volume, fixed-frame paths to amplitude .02, with explicit manufactured isotropic stress and zero histories. No published experiment or calibrated preparation is claimed.
- 18 full-state samples per path: initial, exact first yield, sixteen plastic observations. Each retains sigma6/e/alpha6/fabric6/alpha_in6 and total strain6. There are **486 samples, including 432 plastic observations**; 23 final states have nonzero fabric.
- Independent Cartesian Decimal ODE implementation imports no Atlas evaluator, DSL, backward-Euler residual or author code. It does not project states onto yield. The frozen corpus, algorithm and adequacy policy precede generation.
- Local tolerances 1e-8, 1e-10 and 1e-12 at precision80 establish empirical full-trajectory refinement. At tolerance1e-12, precision50 and80 agree at every **35-significant-digit serialized value**. The worst fine/medium scaled state difference is **7.87834e-9**, below the frozen1e-8 reference gate. This is empirical adequacy, not a rigorous global error certificate.
- Independent recomputation from saved stress/backstress gives maximum yield drift over initial pressure **6.05222e-13**. All prepared-state, strain-control, fixed-memory, deviatoricity and declared-domain checks pass.
- **153** separately derived scalar triaxial, exact-rational rotation and regular zero-distance assertions pass. **Eight** saved-assessor tests pass, including seven deliberate missing/forged/failed-data challenges. Original process outputs and every generated path are retained.

`policy.json` defines reference adequacy only. Candidate integration/derivative/control/rollback budgets are not selected from these results. No mixed-volume source claim follows: the disputed printed Eq20 volumetric term vanishes on this corpus. No reset/event policy, mixed controls, nonzero prepared anchor, physical time, pore-pressure model, backend/browser qualification or experimental validity is established.

## Reproduction

Saved-only checks need Python's standard library and no private source or compiled artifact:

```sh
python3 -B docs/references/sanisand-project-monotonic-v1/verify.py
python3 -B docs/references/sanisand-project-monotonic-v1/test_assess.py -q
```

Regenerate a reference into a **new** file; generation never overwrites an existing output:

```sh
python3 -B docs/references/sanisand-project-monotonic-v1/reference.py --precision 80 --tolerance 1e-12 --output /private/tmp/NEW-sanisand-reference.json.gz
```

Repeat with precision50/tolerance1e-12 and precision80/tolerances1e-8,1e-10 to reproduce the four retained gzip documents. The exact inputs/policy/code hashes are in `prospective-freeze.json`; source, assessor and final-delivery hashes are separately recorded. All generation processes returned0; no failed reference cases or gates were removed.

## Next bounded step

Review the proposed research scope/reference, then freeze a distinct literal-binary64 v0.3 candidate and prospective backend acceptance policy before observing it. Preserve exact original research model bytes. Compare backward-Euler refinement to this continuous reference rather than requiring exact finite-step equality; map the candidate's temporary multiplier separately from the 25 persistent states. Broader reference families, transaction/control tests, canonical source decisions and scientific admission remain open on `REF-sanisand-monotonic-v1`. Use existing capacity and generic operators; this work demonstrates no new engine requirement.
