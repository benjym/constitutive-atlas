# Linear elasticity independent AI technical review v1

**Verdict: accepted for the exact legacy definition and bounded scope below.** Task SCI-linear-elastic-agent-v1, child of SCI-baseline-reviewed-scope-v1 / MODEL-linear-elastic. Reviewer run `/root/linear_elastic_agent_review`, 2026-11-01. Review-start `git rev-parse HEAD`: `9e7cab5ed107ed14f19166dddc3096f75496c922`. Model SHA-256: `33387b2058a3f54ed611949318289db24ab2d5b8edd172d0a2454042c7975041`.

I am a separate reviewing agent run with no prior authorship of this transcription, source packet or historical numerical reports. The coordinating packet author is `/root`. The coordinator reports that no reliable historical transcription/evidence author run IDs are available; those identities remain unknown. This is an AI technical review, without claimed human credentials or signature. All writes are confined to this directory; no compiled artifact/author kernel was executed and no source/model/registry was modified.

## Scope and findings

Acceptance covers constant E/nu, 3D infinitesimal fixed-frame/zero-spin material-point elasticity, compression-positive Mandel effective Cauchy stress, explicit caller-supplied sigma/e and parameters, uncoupled positive-e Atlas bookkeeping, and the named inspected tensor/control cases. The current definition remains schema 0.1. The v0.3 crosswalk was validated in memory; migration is a separate definition/build task. Low-level legacy default substitution is not claimed to enforce explicit input. Historical saved native and Wasm interfaces support the bounded cases; acceptance does not qualify the current checkout's binaries, a release, public website or browser UI.

No blocking scientific finding remains within that scope. Retain these limitations:

1. **Historical preflight failure retained.** `python3 -B docs/admission/production-readiness-v1/check.py` exits 1 with `Admission packet preflight failed: pinned input changed: docs/FORMULATION_CONTRACT.md`. A complete independent pin scan finds exactly three mismatches: that contract, `docs/RESEARCH_CHARTER.md`, and `schemas/model-v0.3.schema.json`. The relevant Git deltas add total-stress profile scope, optional physical solution constraints, and agent-review authority. None changes this legacy elastic definition or its pinned source/numerical artifacts. Current crosswalk validation passes. I do not repin or report the historical packet as passing. This review creates its own current bindings; full E2 migration and release qualification remain open.
2. **Finite stress can violate the project scalar domain.** With e_n=.7, the admissible compactive net trace must be below ln(1.7)=.5306282510621704. Trace .5406282510621704 gives e=-.009950166250831893 although the elastic stress formula is finite. This is a counterexample to unrestricted finite-increment admissibility, outside the small verified paths. It must fail and return the parent, not clip e or reinterpret the update as a physical large-strain law. Source inspection of `integrate` establishes complete-parent return on failure; saved failed-prefix/recovery and independent synthetic rollback results supplement it. No fresh compiled elastic domain-boundary trial was run.
3. **Conditioning is bounded.** Positive K/G throughout the declared parameter box is analytical, not proof of solver accuracy for every E/p_ref/nu combination. Numerical tensor evidence covers nu=-.2,.25,.49, while exact stiffness algebra includes -.99 and .499. No near-incompressible FE qualification, complete-update host tangent, finite rotation, variable E(t,x)/nu(t,x), thermal-strain source interface, poromechanics, specimen preparation or experimental prediction is accepted.
4. **Evidence provenance limits.** The 29-case native record is historical and does not attest every current engine source to its old binary. The separately frozen q-correction backend package binds its unchanged elastic model, saved responses, source freeze and successful build receipts. I checked retained bytes/results, not present binaries or browser behavior. Other models in shared manifests were hash-checked as package integrity only, not scientifically reviewed.

## Source provenance and equation fidelity

I read the complete original OGS `LinearElasticIsotropic.h`, `LinearElasticIsotropic.cpp`, and `KelvinVector.h` at `/private/tmp/atlas-elastic-review-v2/`, then verified the identical durable copies at `.local/private-sources/linear-elastic/` using the additive retention-v1 receipts, checked their exact sizes and all three receipt hashes, and inspected the material coefficients, stiffness assembly, mechanical-strain incremental update and Kelvin conversion. Exact source URLs/hashes/paths are in `check-results.json` and `inputs.json`. These are commit b5d0f115c75ee74a7cdbfad533625a550a416fda primary implementation sources, not a claim to have read an original elasticity research publication or OGS process/thermal/poroelastic host code.

The header constructs C=lambda*(I tensor I)+2mu*I_sym; the cpp returns sigma_prev+C*(eps_m-eps_m_prev), ignoring dt. For constant parameters, lambda=E nu/[(1+nu)(1-2nu)], mu=E/[2(1+nu)], K=lambda+2mu/3. Consequently C:d=K tr(d)I+2G dev(d). Every implemented stress term and both derived constants match. The source may evaluate coefficients at t,x; the Atlas specialization holds them constant. No other source branch or state evolution is silently imported.

## Conventions and dimensions

KelvinVector.h explicitly orders xx,yy,zz,xy,yz,xz and multiplies each tensor shear by sqrt(2). It therefore matches Atlas Mandel storage; engineering gamma=2 epsilon_xy yields Delta sigma_xy^M=2G Delta epsilon_xy^M. Changing both stress and strain signs preserves the law by linearity. I do not infer a sign declaration from these source snippets. E,K,G,lambda and sigma have units Pa, nu/e/de are dimensionless; p_ref is positive numerical stress scaling only. No physical clock or objective transport is supplied. Exact oblique passive covariance was independently checked and does not establish finite-rotation objectivity.

## Host semantics, initialization and domain

The e equation is absent from OGS and remains an explicit Atlas convention: 1+e_new=(1+e_n)exp(-tr de). It describes constant-solid-volume logarithmic bookkeeping, composes under additive trace, and is independent of stiffness. Exponentiation does not change the infinitesimal stress kinematics. Effective stress is the Atlas host interpretation; OGS material files supply mechanical stress without a complete coupling process. `solver.hpp` reconstructs laboratory pore-pressure change from the imposed undrained effective-stress boundary, not from an additional constitutive law.

The complete persistent state is sigma (six finite Pa components) and e>0. E>0,-1<nu<.5 gives positive moduli; the model's stricter finite boxes and p_ref>0 are project restrictions. Tension is admitted; no tensile cutoff/plastic history exists. Explicit stress/e offsets are acceptable mechanical inputs without implying calibration or preparation. Eight rerun contract/initialization checks verify the full crosswalk, missing-field rejection, e=0 rejection, unchanged explicit state and tensile-state admission. They test a v0.3 copy, not changed legacy entry-point behavior.

## Integration, transactions and restart

This is a path-increment residual, without physical time. Zero load holds state; reversal has no yield event or reset. Constant elastic increments add; the exponential void factors multiply. All material memory is sigma/e. My noncollinear split/restart algebra reproduces the total update within 0 Pa stress and 2.22e-16 in e. This is an algebraic explicit-state restart assessment, not qualification of a recorded/restart transport API.

I inspected `implicit_step`, `advance_recursive`, `integrate`, `controlled_step`, and `run_protocol_impl` in current `cpp/include/atlas/solver.hpp`. Each trial uses committed input, the public update initializes its result to the incoming state and commits only successful trial output, and laboratory failure retains the last committed point. No model reset program exists. The frozen q-study elastic failed-prefix case returns only the initial point on both backends; its recovery run succeeds. A separate saved synthetic transaction study's original assessor passes both backend outputs (11 API rows/3 preparation witnesses); this supports generic transactions and is explicitly not an elastic source benchmark. Stress tangent is constant C; e derivative is -(1+e_new)tr(delta de), checked by a supplemental central difference. No FE-host tangent interface claim follows.

## Independent numerical and backend evidence

`check_review.py` is independently authored here and uses only the Python standard library; it imports neither the model interpreter nor the project's analytical oracle. It verifies:

- Three original source hashes/sizes; 30 exact rational stiffness columns at five nu values; exact oblique tensor covariance; void composition, domain counterexample, derivative diagnostic and explicit-state restart algebra.
- All 29 saved expected **and actual** native endpoints against newly calculated Lamé/Mandel/void values using the original report's 1e-4 Pa + 1e-10 relative and 1e-10 void + relative budgets. No native solver is called.
- The frozen q-study's 246 source/evidence manifest entries, pre-observation freeze and successful native/Wasm/post receipts, including the exact current elastic model hash.
- Raw-to-report binding for all 382 shared transport rows, then independent elastic analytical control/strain/stress/e/pore-reconstruction checks at 1,634 points in 13 native/Wasm pairs: current and legacy protocols 0–4, default run, limited-prefix failure and recovery. The worst elastic component budget fraction is 9.915710529085339e-5. These supplemental post-observation checks do not rewrite the earlier prospectively frozen study or its gates. References use caller controls, not solved strains. Other models' equations are not assessed.

The packet's `check_crosswalk.py` is separately rerun after source inspection; its eight contract checks, 30 columns and 29 expected residual checks pass. Saved synthetic rollback assessors pass. `command-log.json` retains exact invocations, outputs and the failed preflight. No broad campaign was performed. The old q-observable failure remains historical; the inspected q-correction README expressly retains it. No failed elastic native case is concealed in the 29-case report.

## Reproduction, inspected materials and rights

From the repository root:

```sh
python3 -B docs/reviews/linear-elastic-agent-v1/check_review.py --repo . --output /private/tmp/elastic-agent-check.json
python3 -B docs/ingestion/linear-elastic/check_crosswalk.py --repo . --output /private/tmp/elastic-crosswalk-check.json
python3 -B -m atlas.agent_review docs/reviews/linear-elastic-agent-v1/agent-review.json --for-approval
```

The first command requires the three retained originals at their recorded durable private paths; a fresh public clone must acquire the exact linked revision and verify hashes. Failure to access those files is a reproducibility limitation, not permission to substitute source versions. The repository copy was run with an absolute `--repo` path, as recorded in `command-log.json` and validation output. `inputs.json` distinguishes direct source/technical inspection, relevant instruction/status excerpts, saved-data inspection, and integrity-only manifest checks. `manifest.json` gives exact output hashes, excluding itself to avoid recursion. Source files identify BSD-3-Clause; none is redistributed here. No copyrighted PDF, proprietary binary or experimental data is added. The independent checker is original review algebra.

EL-01–05 are supported within the precise restrictions in `decisions.json`. The coordinator's smallest next action is to validate/integrate this accepted record for the unchanged legacy hash, preserve the historical preflight failure, then separately complete v0.3 migration and freeze/qualify the actual reviewed release. Model approval does not complete E2/E6–E8 or authorize deployment.
