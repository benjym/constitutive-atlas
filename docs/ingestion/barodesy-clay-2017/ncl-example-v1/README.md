# London-parameter analytical NCL initial-state example

This is one explicitly analytical initial-state assignment for the complete Barodesy2017 body2p/zero-spin formulation. It is not a measured London clay specimen, a matched experiment or a simulated consolidation history. The model's existing examples/defaults remain unchanged.

The paper's Table2 p368 London parameters are phi_c=22.6degrees (converted to radians), N=1.375, lambda_star=.11 and kappa_star=.016; sigma_star=1000Pa is the fixed source pressure scale. Choose illustrative effective mean stress p0=100000Pa and assign sigma=p0I in compression-positive Mandel components. Use Equation11 p368 ([exact locators](source-locators.json)), the source NCL relation `ln(1+e0)=N-lambda_star*ln(p0/sigma_star)` to assign e0. The high-precision scalar value and complete explicit state/parameters are in [example.json](example.json).

The pressure is a project example. Saturation, drainage, pore pressure, measured density, consolidation duration/history and experimental applicability are unassigned. The base model carries only stress and void ratio; no hidden OCR/fabric/preparation variable is invented. This mathematical NCL assignment must not be used to reset a later loading state or replace actual experimental preparation.

[Policy](policy.json) freezes the exact model/example hashes, 70-digit scalar reference, inverse relation and one accepted/three rejected initialization checks before observation. Run from the repository root:

```sh
PYTHONPATH=. python3 -B docs/ingestion/barodesy-clay-2017/ncl-example-v1/check.py --output /private/tmp/barodesy2017-ncl-check.json
```

This uses the common explicit-state initialization validator only; no native/Wasm build, stress-path update or experimental comparison occurs. An independent reviewer must check the source locators, values and interpretation before this supplies B17-05. Source PDF retention is documented in [retention-v1](../retention-v1/README.md).
