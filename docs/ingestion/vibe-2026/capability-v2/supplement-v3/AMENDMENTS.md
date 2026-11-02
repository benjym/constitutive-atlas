# Prospective v3 clock/alias supplement

This supplement preserves the frozen v2 CONTRACT/IMPLEMENTATION/GATES/manifest and additive bounds/routing receipt. It precedes any production implementation, generation, build, material or compiled observations. It completes reviewer-requested explicit-clock forcing and fixes one alias policy. It does not change model acceptance tolerances after an observed result.

## C7 — Explicit nonautonomous physical-clock witness

Use a separate dimensionless persistent scalar z:

```
z_dot = time / tau**2
tau = 2 seconds
z0 = -3.5
t0 = 11 seconds
h = 4 seconds
```

Independent exact rational reference at t=t0+d is
`z(t)=z0+((t0+d)**2-t0**2)/(2*tau**2)`.
Expected z values: incoming -3.5 at11s; midpoint2.5 at13s; endpoint9.5 at15s. This fixture explicitly uses equation `time`; none of the THM value/rate witnesses substitutes for this gate. Check instantaneous RHS 11/4,13/4,15/4 per second; check 1/2/4 advance partitions and restart from13s to15s. Initialize with explicit state/time/controls/rates; evaluate time independently from external controls. A frozen-starttime evaluator would end7.5 rather than9.5 and must fail. An elapsed-time-only evaluator would end-1.5 and must fail. Record these wrong-oracle discriminators as independently computed values, not productionbug simulations.

z tolerance `1e-12 + 1e-12*abs(reference)` for Python/native/Wasm outputs at allstages/endpoints. Time and endcontrol/rate arrays exact. This polynomial is exactly integrated by ideal midpoint; no adaptiveglobalerror claim follows. Include a nonzero restart initialtime, nonautonomousfailureafterfirsthalf with exact rollback and recovery, and make explicit-clockcase mandatory in both backendpackagegates. Reference uses Fraction or Decimal80 outside production interpreter/generated equations.

## Fixed ABI overlap policy

**Reject every input/output overlap and every output/output overlap. Permit input/input overlap.** This conservative policy preserves the v2 promise that inputs never mutate on successful or failed calls. It is selected before implementation. Parent's input-copy alternative is unnecessary with this policy; implementation may still copy inputs for transactional safety after validatingranges, but copies do not authorize aliasacceptance. Never silently switch to another policy after an observedfail.

Validate all pointer/length/range arithmetic before anydereference/write. Outputranges must be nonoverlapping with all inputs and eachother, with checked uintptr_t bytecounts/endpoints. Exactalias and one-componentpartialalias reject with outputs/inputsentinelsunchanged; adjacentbuffers pass; identical current/startreadonlyinputs pass. Test output-time/diagnostics overlaps as well as state/observable/vector overlaps. The complete successful output is written only after full evaluation/domain/integration/shape/finiteness checks; exceptions cannot commit partial output. Native callers retain validallocation responsibility; checkedABI is not a memorysandbox.

## Unchanged constraints

Use newly assigned isolatedworktree based currentorigin/main31125e2e8, never dirtyrootfeba. Proposed explicitcore/browser/modelintegrationwhitelists remain in IMPLEMENTATION.md; coordinator separatelygrants work. Rootweb/app.js andtools/build_web.py have unrelatedowners. MDv5 holds serialbuildslot; this worker has no build/compiledcallauthorization. Existing oldODE/path/residual ABI and profileidentities remain unchanged. Exactoldroute rejections and flattenedbounds are fixed in BOUNDS-AND-ROUTING.md.

No production files changed, no compiled/backends/browser execution occurred, no temporary resource/process was created. Packet and freeze receipts are durable; cleanup has no temporary remainder.
