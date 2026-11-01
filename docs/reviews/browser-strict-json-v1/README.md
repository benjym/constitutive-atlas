# Shared strict browser JSON repair

`FIX-browser-strict-json-v1`, 1 November 2026. The shared `parseRecordedJSON` reader now rejects duplicate decoded object names at every depth and all numbers outside finite binary64 range, including unused fields. Native JSON grammar/value decoding remains authoritative; an iterative token scan checks names and numbers before returning the decoded result. Sets are local to each object, including objects in arrays. Escaped aliases and `__proto__` are handled as ordinary names.

The existing exact-integer-literal policy is retained. Decimal/exponent literals keep native finite rounding; signed zero, finite underflow, subnormals and finite extremes retain native semantics. This repair changes import validation, not constitutive calculations.

## Evidence

- Prospective five-group Node tests fail twice before repair and pass after repair; original failure output retained. The Python wrapper runs them in the normal unittest suite.
- Eight focused Python checks pass: browser decoder, recorded document round trips, laboratory document round trips and strict saved-observation decoder. The document tests use saved responses and no solver.
- The unchanged live MC collector now passes all14 manufactured paths/834 points and rejects all98 corruptions, including the original28 false passes. Its56 callback invocations return manufactured reference frames, with synthetic zero diagnostics. This establishes transport only, not numerical accuracy or a build freeze.
- All10 changed source receipt edges verify against exact archived bytes. The old failed MC packet still reproduces its28 failures with its frozen helpers. It remains failed.

The broader `tests.test_recorded_scope` suite has one failure and one error before reaching browser comparison: it assumes effective stress for every canonical model, including total-stress Tresca. The same failure is reproduced in an isolated unmodified70915f1 snapshot. Its fixed28-row assertion is also stale after catalogue growth. No change to that suite or the scope contract was made here. Baseline output and the initial incomplete snapshot setup error are retained. This prevents claiming a completely green broad suite.

## Reproduce

```sh
python3 -B -m unittest tests.test_strict_json tests.test_recorded_document tests.test_laboratory_document tests.test_strict_observation_json
python3 -B docs/reviews/browser-strict-json-v1/verify.py
python3 -B docs/reviews/mc-current-contract-preflight-v2/verify.py
```

Next: repair the separately identified stale scope-test fixture, then close the current MC collector/reference/compatibility freeze before numerical qualification. No model equations, backend calls, builds, canonical MC insertion, scientific admission, push or deployment occurred.
