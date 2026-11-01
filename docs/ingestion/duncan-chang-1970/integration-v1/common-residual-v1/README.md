# Common-input arithmetic and complete coverage diagnostic

This is bounded diagnosis of the retained E6/E7 failure, not a release gate replacement or scientific admission.

| Study | Frozen requests | Observation |
| --- | --- | --- |
| Complete residual |224identical inputs from first12cyclic points and signed current/previous/strain probes |12component differences in four duplicate versions of point2previous-state guess;0domain disagreement; same differences in baseline and contraction-off native |
| Isolated stiffness |24unit-shear primary/unloading probes at actual minimum previous stresses |One unloading stiffness difference survives contraction-off |
| Isolated power |36unit-shear probes with K=Kur=1/pa,nu0,distinct diagonal current=previous; exponent0/.54/1 controls |One power difference: native .9911640587065761 versus Wasm .9911640587065762 |
| Independent arithmetic |Exact binary64 base0x1.f7a75cef7f3c8p-1 and exponent0x1.147ae147ae148p-1; Decimal100/160digits |Rounded references converge for all36cases; divergent native value is−.5022658321ULP from reference, Wasm+.4977341679ULP; independent reviewer additionally checks converged generalized-binomial series |
| Full request coverage |All156original pairs,312backend runs,130same-instance export/import replays |FinalFAIL:6Duncan comparisons; original recursive comparison text and all other gates retained |

The coverage collector catches exceptions thrown by the comparison function, records the failure and continues; it is not restricted to the AssertionError class. All comparison exceptions remain failures and final process exits1. This additive diagnostic does not replace the original aborting gate. Direct same-backend equality, same-instance replay, ordinary outcome allocations and recovery assertions remain outside that catch.

Failures are legacy/current drained1, legacy cyclic stress3, legacy/current4 and ordinary defaultDuncan. Full field analysis retains29iteration differences for legacy drained; current drained additionally exceeds1e-10 on40state components,29q and29signedq outputs and3residual diagnostics. Largest current drained state scaled difference2.7100686643e-10. Cyclic stress additionally differs in partition diagnostics and small reversal stresses: largest q difference.0003563900245Pa at point32, outside the original1e-7comparison's unit floor. Default differs in71iteration counts and3error diagnostics. These differences are small relative to100kPa but the software gate remains failed; material source tolerances do not waive it.

The isolated power discrepancy is a demonstrated common-input arithmetic difference, not proof that it causes every later trial/iteration/partition divergence. Reconstructed endpoint/previous guesses are not actual internal Newton trial traces. No source-law/default/tolerance change follows from the observation.

A separately prospectively accepted [portable-power diagnostic](../portable-power-v1/POLICY.md) uses the exact MIT-licensed SDK musl power routine in a private source mirror, with contraction disabled. It is queued behind the shared serial build slot. Any resulting candidate still needs the complete original gates and separate generic/source/material qualification before production installation. Shared runtime and CMake remain unchanged.
