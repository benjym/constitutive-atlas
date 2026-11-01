# Independent native max-history crossing failure analysis

Reviewer `/root/duncan_complete_review`,2026-11-01. Source/reference and retained raw-response analysis only. No compiled artifact executed and no production material update/build. **Native full study remains FAIL.** No success case is reclassified, no gate/settings changed and no E5 approval is supplied.

Independently replayed assess-v2.py on saved native-results.json. The resulting assessment exactly equals native-assessment.json: all twelve reported assertions arise from four incomplete loose max-crossing paths and their incomplete restarts. All other frozen assertions pass in that retained assessment. The independently reproduced report remains a failure.

## Actual no-unsplit-root gaps

For each first failed external call, decoded initial state/loading directly from retained call arguments and raw stdout. The external state is restored exactly. The wire normal stiffness shape is B_i=de_i/(1+nu)+nu*trace(de)/[(1+nu)(1-2nu)]. Write k=B_x-B_y>0, b=B_y, D(E)=D_n+E*k and averaged confinement cbar(E)=c_n+E*b/2. This includes the actual rounded radial strain coupling rather than assuming exact mathematical fixed confinement.

At E_*=(h_n-D_n)/k, D reaches its historical maximum. For every valid unloading candidate E<E_*, the source unloading modulus is bounded below by the confinement-interval minimum shown below and exceeds E_*. For every primary candidate E>=E_* with Sbar<1, the source primary modulus is bounded above by its maximal positive-confinement factor and minimal strength fraction, below E_*. S(E) is independently checked increasing over this interval. Thus neither equation can have a branch-consistent root. The numerical failure-modulus root has D<h_n and also cannot satisfy its branch. This is a source-derived finite residual discontinuity, not evidence that a valid unsplit root merely escaped Newton.

| Outer partitions | Incoming D /Pa | Boundary E_* /MPa | Unload lower bound /MPa | Primary upper bound /MPa |
| --- | ---: | ---: | ---: | ---: |
|16|91063.7474|47.6600|109.5033|9.98195|
|32|91063.7474|95.3200|109.5033|9.98195|
|64|96196.7159|81.1367|109.5033|9.59791|
|128|98763.2001|52.7701|109.5033|9.40871|

The raw diagnostics retain9/10 accepted tentative substeps and15 rejected solves, far below max_substeps20000. Their fractions approach h; the independent source estimate of remaining stress difference is1.178/.552/.238/.082Pa. Frozen advance_recursive attempts dyadic subdivisions until max_depth14, then refuses depth15. These observations are consistent with a depth-limited partition continuation exhausting its budget near a branch gap. This review does not infer hidden Newton iteration traces from aggregate diagnostics; any isolated trace has its own identity.

## The overall path is possible with another subdivision

The independent script constructs, for each same incoming state and total stored loading, a first source unloading piece ending at h-delta, delta=(h-D_n)/100>0. Its remaining proportional loading has a bracketed primary root beyond h. Constructed first fractions are0.430886,0.861771,0.733543,0.477085; final stress differences are100898.68,100031.45,100078.32,100101.75Pa. This proves path advancement is not intrinsically impossible. It does not make the frozen dyadic study pass and is not a proposed handwritten material kernel.

A generic bounded alternate partition retry can therefore be investigated under a distinct source/algorithm/study identity. A fixed1/3 then2/3 split is a heuristic without a general success guarantee. Any implementation must preserve entire-parent rollback before retry, exact final physical constraints and residual gates, global tentative-work budgets, actual non-dyadic fraction diagnostics and explicit loading-roundoff treatment. It must not silently reset budgets, perturb history, change the source branches or reclassify the frozen failed paths. No alternative implementation is approved here; separate design/code/execution review is required.

Exact source proof bounds, constructive roots, raw input hashes and reproducible analysis are retained in analyze.py/results.json; the replayed failed assessment is preserved separately. Run analyze.py from repository root to reproduce without compiled execution.
