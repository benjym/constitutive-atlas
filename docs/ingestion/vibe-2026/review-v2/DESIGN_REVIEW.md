# Independent controlled physical-time design review

Reviewer `/root/vibe_gap_review`, 2026-11-03. Decision: **accept the v2 design together with its bounds/routing addendum and mandatory v3 clock/alias supplement for separately claimed Stage-A implementation source work.** This accepts a proposed generic contract and prospective gates, not an implemented capability, compiled result, VIBE candidate or E5 scientific approval.

The accepted input identities are the original design manifest `5c63c2d3ae7e2d8098f017c17937310f80e1f874f2d5d3f69fb667d1fef79c76`, bounds addendum manifest `c6a1a5c607dd9af123d320d9d661ec3f0aa767e94f9e1a7e44448f356b038db3` and v3 manifest `8bc98d90c131226ab3af69567035396918ef459432281db300f52d42cd487dc8`. All bound proposal bytes were checked. Original v2 bytes remain historical and unchanged.

## Contract assessment

The separate `physical_time/controlled_ode` profile, explicit symmetric strain control, scalar field values/rates and per-second state derivatives address the actual generic gap. Separating the generated catalogue/module and checked API avoids reinterpreting the dimensionless path clock or expanding the old time ABI silently. The design expressly rejects new-profile routing into old interpret/observe/initialization/history/compiler/browser consumers and preserves old net-stress exclusions. These are mandatory acceptance tests, not implementation suggestions that may be dropped.

The typed full context, exact start-control agreement, explicit incoming/next interval rate transition, staged linear histories, full-context replay and atomic parent rollback cover the relevant lifecycle. Rate-dependent observables must use the correct left/right context at a transition without inferring a material-state jump. Positive-duration holds retain true physical evolution. Negative physical timestamps are allowed only subject to model domain; duration and representably later finite midpoint/end checks remain required.

Net stress has a separate observable scope and labels. The new profile does not gain total/effective conversions or experiment compatibility by implication. The explicit flattening limits, six settings, four diagnostics, pointer lengths and prospective sentinel/range tests are adequate design boundaries. Runtime source review must still inspect actual allocation, integer conversion, pointer arithmetic and exception paths; documentation cannot prove them safe.

## Review finding and preserved correction

The original C2/C3 trajectory laws did not depend on explicit equation `time`. A faulty runtime that supplied start time at every stage could pass them. I required a prospective nonautonomous witness before implementation. The v3 supplement adds `z_dot=time/tau²`, with nonzero `t0=11s`, `tau=2s`, `z0=-3.5`, duration4s, exact midpoint2.5 and endpoint9.5. I independently computed those values with rational arithmetic. Frozen-start and elapsed-time-only errors respectively give7.5 and-1.5, so the new gate distinguishes both bugs. Partition, restart, instantaneous RHS, failure/recovery and package/backend coverage are specified. This addition precedes production observation and does not relax an observed failure.

The original overlap policy also left two alternatives. The addendum/supplement now select one: read-only inputs may overlap; every output must be disjoint from all inputs and other outputs. Full checked ranges, partial aliases, adjacency, time/diagnostics buffers and unchanged rejection sentinels are explicit. This resolves the design choice before implementation.

## Required next gates and scope limits

The independent analytical coupled-field oracle, nonautonomous clock oracle, nonlinear convergence, branches, full-state lifecycle/rejection tests, cross-backend layout/sentinel checks and old-profile compatibility tests are meaningful and remain mandatory. Freeze actual fixture bytes, reference generator, numerical settings, case corpus and implementation source/toolchain identities before compilation/material observation. A source review of the actual implementation is still required before any build, followed by the coordinator's fresh serial execution handoff. No slot is granted by this decision.

Generic capability qualification must not stand in for VIBE qualification: the exact Appendix law still needs its own independent full Cartesian/high-precision reference, current-temperature reconstruction, all six mechanical components, coupled/opposing THM rates, positive-domain reversals/holds, removable hydrostatic limits, unsupported-boundary rejection, full-state convergence and E5 review. Actual normal-atlas package/browser/live checks remain separate E6–E8 gates. No standalone page is required.

The proposed path whitelist is a proposal until the coordinator grants it in an isolated worktree. Recheck the actual chosen base and affected existing consumers before edits; a historical root hash or a changing remote branch is not a frozen implementation identity. Literal wording about “53 criteria” in IMPLEMENTATION.md is not authoritative: use the complete current canonical delivery checklist, including public-profile and cleanup requirements.

## Cleanup

This reviewer created no process, download, build, worktree, browser tab or temporary tree. Only small durable review-v2 evidence was written. Existing private renders were reused read-only. No reviewer-owned temporary remainder exists.
