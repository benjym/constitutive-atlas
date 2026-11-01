# Burgers agent checklist v2

**Accepted for the exact unchanged continuous dry zero-spin model and its frozen native/Wasm physical-time CLI/ABI/schedule qualification.** This is the reasoned E5 decision of the actual separate reviewer run `/root/burgers_scientific_review`, resumed after REV-burgers-scientific-v1; the transcription/integration author was `/root`. This is not a fresh-context review or an invented platform identity. All nine checklist v1 items pass, with no unresolved blocking finding in this bounded scope. The [record](../../../catalogue/agent-reviews/burgers-agent-v2.json) binds model SHA-256 `1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c`.

The current agent-review policy permits coordinator approval integration without human scientific signature or another user sign-off. This new record reconciles actual prior work, adds missing checklist checks and preserves the original review and explicit-user approval. It does not retroactively rewrite their wording or claim that E6–E8 are complete. The forthcoming main-laboratory timed browser interface, release workflow, package and live site are **excluded** and require separate delivery qualification/review. No standalone page is proposed or qualified here.

## source_provenance

Pass. I previously read the three original primary-source HTML pages, their continuous and discrete equations, property notes, signs and Kelvin initialization function. They are now rechecked against the durably retained private originals: Burgers, Maxwell and Burgers–Mohr, all Itasca 9.0.184, updated 11 December 2025. All exact hashes match the receipts. Readable source supports the restricted continuous deviatoric law with elastic volume; the original Burgers historical publication and full vendor-host transport/coupling are not asserted. The three institutional persistent URLs and equation locators are in the source receipts; public receipts suffice for private copyrighted source identification. See [prior technical reading](../burgers-scientific-v1/README.md), [source audit](../burgers-scientific-v1/source-audit.json), and [new source checks](check-results.json).

## equation_fidelity

Pass. Burgers–Mohr Eqs. (5)–(7), (10), with plastic rates zero, give `k_dot=(S-2Gk*k)/(2etaK)` and `sigma_dot=K tr(D) I+2Gm(dev(D)-k_dot-S/(2etaM))`. The Burgers initialization code and scalar series law corroborate that specialization; Maxwell Eqs. (4)–(6) corroborate factors and volume. Both persistent evolution equations, stress observable, five positive material constants and deviatoric projection were reviewed. There is no plastic branch, cutoff, hidden reset or handwritten production kernel. `dev(ek)` and the `1e-12` trace tolerance are explicit numerical choices. The printed mean-force/trace-index ambiguities are disclosed and resolved using the unambiguous tensor partitions, rather than silently modifying a variant. The vendor centered discrete update remains a different algorithm outside this approval. Exact installed model bytes match the prior reviewed and integration-frozen definition.

## conventions_dimensions

Pass. Pa moduli, Pa s dynamic viscosities and dimensionless Kelvin strain produce Pa/s and 1/s derivatives. Both mechanical signs reverse together from the source compression-negative convention, preserving work. Mandel `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]` preserves the tensor contraction; no engineering shear is substituted. The model declares Cauchy total stress, dry uncoupled conditions, infinitesimal strain, fixed spatial components, zero spin, physical time and explicit stage/loading inputs. Dry total/effective equivalence is a restricted scope choice. Fresh loading/generation validates the exact nested record using the current interpreter/compiler. An independent orthogonal Cartesian basis transformation checks covariance of the interpreted rates, including all shear channels. This passive basis check does not establish finite-rotation objectivity.

## initialization_domain

Pass. Five explicitly supplied positive finite constants and twelve persistent scalar slots (six stress and six Kelvin components) are inventoried. Kelvin trace must satisfy the declared absolute tolerance; state cannot be omitted or implicitly synthesized. Arbitrary deviatoric history is allowed; `k=S/(2Gk)` suppresses only initial Kelvin rate and does not suppress Maxwell creep. Initial schedule strain is an incremental reference, not a reconstructed stress-free strain. Machine bounds are declaration bounds, not a material-validity/stability envelope. Zero/infinite viscosities, disabled branches, variable parameters, thermal effects and specimen calibration are excluded. Saved rejection checks cover missing state, inadmissible trace and zero viscosity. The qualified numeric envelope consists of the literal frozen synthetic states/parameters/requests/settings, not every accepted machine input.

## integration_transactions

Pass. Physical seconds and piecewise rate/control histories are mandatory; strain holds relax deviatoric stress and stress holds creep, while hydrostatic behavior is elastic. Loading/reversal/hold segment discontinuities are split, with no invented infinite-rate impulse or reset. Both stage derivatives use current stress/history. Direct advances use explicit midpoint/step doubling and schedules use backward Euler/step doubling, distinct from the source centered update. Source-derived eigenvalues explain stable/stiff limits; no arbitrary-parameter step guarantee follows. The frozen saved calls substantiate full state/time rollback after internal work, committed-sample schedule rollback, subsequent recovery and complete-history restart within the original analytical budgets. Wasm recovery is in one persistent instance; native requests are separate processes. No arbitrary failure-point proof, bit-identical changed-partition restart or broad browser lifecycle is claimed. Returned instantaneous rates remain outside independent accuracy qualification.

## independent_numerical_evidence

Pass. The actual prior review independently derived energy/dissipation and stable eigenvalues and checked 100 exact rational Cartesian energy/sign/stability cases. Its separate 110-digit affine matrix exponential agrees with every one of the frozen closed-form references: 1,584 state/strain scalars at 88 schedule points, maximum scaled discrepancy approximately `2.224e-102`. This calculation was rerun now, rather than treating native/Wasm agreement as a reference. Source packet algebra/interpreter checks replay to 515 cases in the original dependency context. All source, reference and acceptance inputs precede the recorded compiled observations; no gate was loosened.

Separate Kelvin and stress refinement both actually improve, although the original assessor does not enforce them separately: Kelvin endpoint maximum `1.0146007761255987e-6 -> 1.0990417878662014e-7`, stress `4.236536867159884 -> 0.4524055079527898 Pa`. That low finding remains a hardening follow-up, not a hidden failed result. A fresh check of all six loading directions agrees with the analytical instantaneous fixed-state rate tangent `K I⊗I+2Gm Pdev`; it does not qualify an accepted-step/FE tangent. The law is linear and smooth on its strictly positive domain; nonsmooth-yield derivative testing is irrelevant. Exact energy dissipation of the continuous law is not a claim of unconditional discrete energy decay.

## backend_delivery

Pass for the named existing interfaces. The exact integration-v1 closure and receipts qualify serial native then Wasm builds of the common `atlas_burgers_solver`, and saved evidence gives 44 calls/88 analytical points per backend and 6,168 physical parity comparisons. Current saved-only integration replay passes; eight focused Burgers/temporal-language tests pass. Named strain/stress/mixed/reversal/hold schedules and CLI export/replay are supported to their saved coverage. Descriptor and installed model identities bind the exact definition; native and Wasm use the same qualified generated header. No compiled execution or build was performed in this reconciliation.

The checklist-audit correctly identifies missing dedicated current CI execution and public laboratory routing/lifecycle/live qualification. These are outstanding E4/E6–E8 delivery work and are explicitly outside this bounded E5 interface approval. A successful historical site deployment or live static model JSON is not evidence of interactive Burgers delivery. In particular, this record approves none of the coordinator's new main-laboratory interface artifacts until separately handed off and reviewed.

## applicability_claims

Pass. Approval covers the agreed continuous dry uncoupled, positive-finite, small-strain fixed-frame zero-spin material-point formulation and literal qualified synthetic protocols/settings. The source energy identity and stability analysis support that mathematical restriction. Illustration parameters are uncalibrated. Experimental validation is **not assessed**. General parameter robustness, instantaneous output-rate accuracy, exact vendor timesteps, full Burgers family/default semantics, plastic/contact variants, FE/MPM consistent tangents/host transport, pore pressure, temperature and finite rotations are excluded. Stale embedded pre-integration wording is retained only to preserve exact tested/reviewed bytes; it is a disclosed low metadata finding, not an unresolved uncertainty about the reviewed law. A future metadata revision needs its own exact-byte binding.

## reproducibility_rights

Pass. Source receipts, exact model, policy, integration freeze/references/raw results, previous review and release-audit identities are hash bound. Original copyrighted HTML remains in ignored durable local storage and is not copied into this deliverable. The frozen source archive contains project code rather than vendor source; prior audit verifies every source/log archive entry. Local durable retention is not an off-machine backup. Existing publication/data rights and deployment authorization are unaffected by this agent approval.

Two current-checkout replay failures are retained: the original source verifier rejects changed `atlas/dsl.py`, and the original full review verifier transitively reports that rejection. This is legitimate historical dependency enforcement. I did not alter/rebind the historical scripts, drop their checks or call those runs passes. Both commands pass in the retained exact released extraction at `/private/tmp/burgers-checklist-release-audit`, revision `f18db8e75d27cf182f2c03dfcd6534b7f51d5a86`; the new audit independently records the same released-revision passes. The current model loads/generates and its isolated common integration saved-evidence replay passes, but this record makes no claim of newly compiled current-runtime qualification. Reconstruct the historical context from that revision before replaying the original source verifier.

## Checks and handoff

Run the fresh read-only checks and policy validator:

```sh
python3 -B docs/reviews/burgers-checklist-v2/check_review.py
python3 -B docs/reviews/burgers-scientific-v1/independent_check.py
python3 -B docs/ingestion/burgers-itasca900/integration-v1/verify.py
python3 -B -m unittest tests.test_burgers tests.test_time.TemporalLanguageTests -q
python3 -B -m atlas.agent_review catalogue/agent-reviews/burgers-agent-v2.json --for-approval
```

[Replay commands](replay-commands.json) preserve actual command/exit identities. Current failed source/prior-review outputs, successful historical replays, independent-reference output and focused regression log are all retained in this directory. [Preserved historical hashes](preserved-history.json) distinguish original evidence from the new decision. [Manifest](manifest.json) pins the reconciliation outputs. The generated approval candidate is for coordinator integration, not a direct registry mutation by this reviewer.

No old review/approval, model, runtime/schema/compiler, board, shared registry or browser file was edited. No compiled call/build, vendor-code execution, fitting, remote action or experimental validation occurred. Smallest next action: coordinator validates/integrates the accepted exact-scope agent review, then hands over the final main-laboratory interface and complete browser/package evidence for a distinct delivery review. The full model-delivery umbrella remains open.
