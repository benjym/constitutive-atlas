# Native fixture identity correction v2

Independent v1 review `0a657dad…0125faae` found B1: the new numerical mode retained the legacy output label. This revision preserves the complete original implementation and its failed review, then changes exactly two strings in a new isolated copy:

1. A new-mode-only stdout branch emits the distinct positive label frozen in the accepted CI dispatch plan. Both original labels and every legacy branch remain unchanged.
2. The new-mode pairing error uses that same accepted plan's exact contract string. Its condition and all rejection behavior remain unchanged.

All numerical instructions, probes, scales, domain/branch checks, derivative inequalities, rotation inputs and covariance checks are byte-identical after reversing those substitutions. The original 582-file model-study source and prior 582-file fixture source remain immutable. The new tree also contains exactly 582 files; only `tests/test_solver.cpp` differs from v1.

`source-freeze.json` binds the new tree, prior implementation/review and separately accepted CI plan/review. `identity.diff`, `checks.json` and `verify.py` expose the exact correction. No build or compiled call has occurred. Separate prospective re-review is required before execution, and no compiled numerical success follows from this identity fix.
