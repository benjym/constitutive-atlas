# Independent VIBE source/reference/transcription review v1

Reviewer `/root/vibe_numerical_review`, task `REVIEW-vibe2026-reference-transcription-v1`, 3 November 2026. This is a separate agent run that authored neither the candidate nor the reference. Ownership is only this new review directory. I read AGENTS.md, the review policy, relevant board/source/design records and the research/status context, and used the PDF skill to inspect the original rendered Appendix pp15–16, Tables1–2 p4 and derivation p13. Original PDF and every private receipt artifact verified by exact hash. No vendor code, compiled model, build, browser, commit or shared-file edit occurred.

**Decision: accept the exact revision3 source transcription and independent reference evidence within the scope below.** This is a bounded intermediate review, not a nine-item E5 approval, backend qualification, catalogue admission, experimental validation or website delivery. The candidate remains a draft. `decision.json` and `input-bindings.json` bind the exact assessed bytes; `reviewed-candidate.json` retains a durable exact copy.

## Identity and equation audit

The target is D. Mašín, *Viscohypoplastic bentonite (VIBE) model*, Engineering Geology370 (2026)108827, DOI10.1016/j.enggeo.2026.108827, **published explicit Appendix A**, original PDF SHA256 `90b1c3bc56bacf1294e3e8ea60a217ffa1651981c86c63b0c0d9354534764912`. Source-v2 manifest is `90603c5756a0a1a8f2edd8cbdcb6d21ad639f51796d2dba78ceaca04047f442c`; reference-v1 manifest is `04dd3a8831e83cada428a38479f72908f8f1ed03ea640df4b4c9826dabf0d079`. Reviewed candidate revision3 SHA256 is `29d104bf55ec3225030e8710ee342f96b6518bd8a4434e784e455da300d08778`.

I compared all A1–A35 formulas visually against both the declarative builder/model and the independently authored Cartesian oracle:

| Source | Checked construction |
| --- | --- |
| A1–A4 | All six external rate terms and the physical-time viscous term; NE versus NVE factors, reference strain rate, separate absolute hydraulic/thermal rates |
| A5–A10 | Hydraulic and thermal linear/nonlinear couplings, signs and factors; exact B composition and nonsingular inverse; identity completions below |
| A11–A14 | L and A tensor actions, normalized flow direction, Heaviside/sign branches and macrostructural effective stress |
| A15–A20 | Persistent void/scanning rates, global/macro saturation, current-temperature microvoid/macrovoid and all retention/microvoid partial derivatives |
| A21–A28 | Both collapse derivatives, micro/macro pressure, density/stiffness, ci, scanning retention, thermal/hydraulic NCL shifts and active slope |
| A29–A35 | Overconsolidation, density coupling, stress invariants/Lode quantity, asymptotic void ratio and temperature-dependent viscosity |

No equation discrepancy remains within the selected identity. A7's missing final second-order identity is uniquely supplied by body Eq39; A9's omitted dyadic factor follows from body Eq42. I independently checked 36 exact rational inverse components. The stable deviatoric Fm formula is exactly A30, checked independently on nine rational Cartesian cases, including shear and hydrostatic cases. It is not a regularization. Full A12 direction converges to the isotropic limit along three unrelated deviatoric approach families; the undefined hydrostatic Lode coordinate alone is not assigned physical meaning. At zero suction rate the fscan placeholder has no constitutive effect because every dependent term multiplies zero suction rate or its absolute value.

The main-text Eq27 combined absolute value differs from A1/A6/A8 under opposing hydraulic/thermal contributions. The candidate and reference both implement the complete **separate Appendix contributions** and disclose that identity. Their agreement does not establish Eq27 equivalence, author-code equivalence or reproduction of every paper simulation.

## Parameters, conventions and domain

All 22 BCV material values and seven hidden constants agree with source Tables1–2 after degrees-to-radians and kPa-to-Pa conversion. Dr=.5e-6/s, pr=1000Pa and Tr=294K are explicit. The thermal multiplier uses b in 1/K; A35 uses the numerical Kelvin temperature difference, represented dimensionally by normalization with one Kelvin. Parameter edit intervals are project study guards, not calibration confidence bounds or proof that every combination is admissible.

The source uses compression-negative mechanical tensors and positive suction. Both constructions negate net stress and prescribed strain rate at the Atlas compression-positive Mandel boundary, and negate the final source stress rate. Mandel contractions preserve tensor norm; e_dot=-(1+e)trace(strain_rate). Net Cauchy stress is bound explicitly; the macro effective stress includes positive S*s in compression-positive coordinates. Scope is fixed-spatial, zero-spin, small-strain 3D; finite rotation, FE host tangents and pore-pressure solution are excluded.

Eight persistent scalar components are net stress6/e/a_scan. Current suction and temperature are external fields; every algebraic micro/macro quantity is recomputed from the current stage, with no hidden old-temperature lag. Initial states are illustrative constructed states, not experimentally reconstructed preparations. The near-SBS pressure is independently bisected to OA=1.005; the dry source example has effectively negligible relaxation and is not the meaningful relaxation demonstration.

The qualified reference region has strictly positive suction/temperature, valid retention interior, positive micro/macro pressures and voids, positive active slopes/viscosity, scan in [0,1], 0<=Fm<1, nonsingular denominators and OA>=1. Saturated starts/endpoints, ae=1, state projection/clipping and representational retention underflow are excluded. Stronger candidate omega>0 is a declared restriction within the sampled parameter study, not a universal source necessity.

Initial candidate guards refused the published vf=0 special case and the IvT=0 study; the retained initial report has30pass/2refused. Revision2 widens only the study guards and preserves every case and tolerance: Table2 explicitly supports vf=0, while IvT=0 leaves Iv=.004 and remains viscous. Only tested endpoints/defaults are qualified, not every intermediate vf/IvT value. IvT=0 is an equation-supported sensitivity study, not the BCV table calibration.

My blocking finding was that revision2 admitted some OA<1 states while the reference domain excluded them. The coordinator retained revision2 bytes and results, and revision3 changes **only OA>0 to OA>=1**. An independent witness with OA=.9908211353321037 is admitted by preserved revision2 and refused by revision3. This conservative supported-interface restriction resolves the finding without modifying the evolution law or any acceptance gate. It does not assert that outside-ASBS literature behavior is impossible.

## Numerical evidence and integration limits

The independent oracle was authored without reading/importing the candidate, uses Decimal Cartesian tensors, assembles the complete 6x6 B action and directly solves it by pivoted elimination. The candidate expands fourth-order tensor actions declaratively and uses the analytic inverse. This is substantial independent equation verification, rather than backend parity. The oracle uses classical fixed-step RK4 while the candidate Python host uses adaptive midpoint step doubling.

I independently reran all32 point references at70/100digits and obtained exact retained JSON bytes. I reran all five trajectories at64/128/256 partitions at70digits plus256 at50digits: all numerical contents match exactly, excluding intentionally variable runtime metadata. Source/reference manifests, their entries, all private source artifacts and the original Downloads file verify. All partition and precision gates pass without changes. The reference plan was prospectively frozen at SHA256 `facc17e21d786328f4b28e8c20d9d3e5b1909becb3e3d971195ca5d7c9435a63` before reported observations.

I reproduced all32 candidate point comparisons for revision2 and revision3 through the dedicated pure-Python controlled-time interpreter:32pass,0fail,0refused for each. These cover all six positive/negative mechanical basis rates, mixed anisotropy, hydrothermal signs/opposing contributions, scan endpoints and ns/ls/lT sensitivity branches. Point gates remain stress1e-8Pa/s+1e-7relative and scalar1e-12/s+1e-7relative, with all components checked.

The five trajectory references cover1000s/3600s near-SBS relaxation,1000s dry hold,100s mixed hydrothermal ramp and an exactly split50s/50s hydraulic reversal. Complete8state and six derived dimensionless observables are retained. The parent-produced candidate trajectory reports were inspected: all five revision2 and revision3 reports pass original gates, with revision3 worst tolerance ratio about.02146. I reviewed the revision2 prospective plan before the parent reported observations. Revision3 rebinds exact bytes and keeps settings/cases/gates unchanged. Settings are absolute scale fraction1e-12, relative tolerance1e-11, maximum step10s, depth40,100000trials; t0=11s. These are bounded execution settings, not an accuracy theorem. I independently reran the reference trajectories, not the candidate trajectory integrations.

State gates remain stress.01Pa+1e-7relative, e/scan1e-9+1e-7relative, observables1e-8+1e-7relative. These five trajectories are hydrostatic and have zero mechanical rate: they do **not** establish nonproportional mechanical trajectory accuracy, every branch/parameter trajectory, broad boundary limits or experimental agreement. Point coverage does not replace those missing trajectory studies.

Seven invalid reference and candidate contexts refuse; candidate input arrays/parameters remain unchanged and immediate valid stage evaluation succeeds. The frozen invalid-temperature case first violates ASBS in the reference, so its name alone does not isolate viscosity rejection. I added a distinct reviewer witness at T200K and the dry state: the reference explicitly rejects Iv and the candidate's **only** failing predicate is Iv>0. Failure messages may arise during derived evaluation before the final guard; these checks do not promise a specific public error string. No failure clipping or state repair was added.

The parent trajectory script checks context serialization, immutable parent contexts and exact reversal splitting. Physical seconds and current-stage controls/rates are explicit. Full transactional ABI, compiled rollback/restart/failure behavior and native/Wasm delivery belong to the separately reviewed generic capability and future actual backend evidence; this review does not approve them.

## Reproduction, retained failures and handoff

Run from repository root:

```sh
python3 -B docs/ingestion/vibe-2026/reference-v1/run_reference.py points --output docs/ingestion/vibe-2026/review-numerical-v1/reproduced-reference
python3 -B docs/ingestion/vibe-2026/reference-v1/run_reference.py trajectories --output docs/ingestion/vibe-2026/review-numerical-v1/reproduced-reference
python3 -B docs/ingestion/vibe-2026/review-numerical-v1/audit.py
python3 -B /private/tmp/atlas-vibe2026-controlled-time-v1/docs/ingestion/vibe-2026/candidate-v1/compare_points.py /Users/bmar5496/code/constitutive-atlas/docs/ingestion/vibe-2026/review-numerical-v1/reproduced-point-comparison-revision3.json
```

The last command requires the exact isolated interpreter/model bindings; future drift needs a fresh receipt. `audit.py` also checks exact retained source/reference bindings, rational identities, hydrostatic approach families and revision3 domain closure. Preserve original candidate syntax/dimension failures,30pass/2refused initialpoint evidence, preimages and both trajectory study identities. None was deleted or retroactively marked passing.

No unresolved blocker remains for this review's exact bounded source/reference/transcription scope. Smallest next action: coordinator retains the reviewed candidate and evidence durably, obtains missing nonproportional references if claiming those trajectories, and continues separately owned serial compiled qualification and final all-nine-item E5 review. No admission registry record is authorized by this intermediate decision.

Cleanup: no download, worktree, build directory, dependency environment or preview/background server was created. Review artifacts and exact numerical reproductions are retained as evidence; the reused private source originals/renders belong to the coordinator and remain untouched. No disposable or uncertain resource was removed. Only this owned directory was written.
