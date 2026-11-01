# Mohr–Coulomb full delivery checklist

Copied without omitting any E0–E8 criterion or exit condition from the canonical57-check checklist on2November2026; canonical SHA-2567554a7e57272fab19dad65b686d18c0cd08b05de9a22859f27662d73e3451e69. Relative links are rebased to this directory. The current source review is not a new backend/browser or live qualification.

Initial six administrative/source-retention checks were completed: E0 items2–4 (exact full formulation, intended interfaces and owned umbrella), E1 items2–3 ([original receipt](sources.json) and [verified private retention](retention-v1/private-retention.json)), and E5 item1 ([actual separate review handoff](../../reviews/mohr-coulomb-agent-v1/PLAN.md)). The actual separate accepted nine-item review now additionally completes E0 item1, E1 items1/4 and E5 items2/3: full governing source/equation/version inspection, evidence inventory and actual no-blocker exact scientific verdict. See [canonical review](../../../catalogue/agent-reviews/mohr-coulomb-agent-v1.json) and [coordinator checks](../../admission/mohr-coulomb-agent-v1/CHECKS.json). All five E5 checks now pass for the exact isolated local commit000ab5e7: generated approval installed, prior24entries preserved and normal full projections independently accepted. See [source checkpoint](../../admission/mohr-coulomb-currentpublic-v1/README.md). Fifteen checks are complete; remaining current integration/package/browser/live checks stay open. Shared-workspace registry is unchanged. Prior source/numerical/browser packets are retained; unmarked items do not discard that work.

Source completion and the existing public-profile draft are reconciled in [source-completion-v1](source-completion-v1/README.md); this closes E1 while retaining all later delivery gates.

## E0 — Claim and define the delivery

- [X] Read current board ownership, existing definitions, dossiers, source inventories, reviews, evidence and retained failures for this model family. Check Downloads/private source inventories before requesting papers again.
- [X] Select the exact publication/version and complete formulation; distinguish family, variant, author implementation and Atlas numerical choices. Check for duplicate IDs or already-delivered work.
- [X] Record the intended schema profile, material/use scope, native and browser interfaces, illustrative protocol(s), acceptance gates and exclusions. Track physical-time or nonstandard UI support as actual work, not an inferred capability.
- [X] Claim the umbrella task and create `DELIVERY.md` with lead, owners, whitelist/worktree, dependencies and stage statuses. Confirm the independent reviewing role will use a separate run.

**Exit:** someone can identify the exact model being delivered, its destination, who owns each handoff and what proves completion.

## E1 — Acquire and understand the sources

- [X] Read the full governing source, including appendices, equations, parameter tables and relevant figures. For PDFs use the PDF skill and inspect equation images where extraction is ambiguous. Abstracts/search snippets do not establish equations.
- [X] Save source receipts: title/authors/year/version, DOI and persistent author/institutional URL, access date, private retained file location, SHA-256 and equation/page/table locators. Check that the bytes match the named source.
- [X] Retain readable originals durably in ignored private storage where permitted. Document source/code/data rights; link rather than publish copyrighted originals. Do not execute supplied author binaries or vendor code.
- [X] Reconcile multiple versions and implementation differences. List missing sources, ambiguous branches and proposed interpretations explicitly; resolve in-scope gaps before claiming source completeness.
- [X] Complete the source packet, prior-work links and an equation-to-source inventory. Distinguish source-complete from executable, approved and deployed.
- [X] Draft the [public model profile](../../PUBLIC_MODEL_PROFILES.md) from the inspected source: readable overview, characteristic behaviours, material parameters, starting state, meaningful limits and references. Keep a specialist draft in its owned packet until coordinator integration.

**Exit:** every required equation and convention has readable source support or an explicit unresolved blocker.

## E2 — Define the schema and integration contract

- [ ] Map the full law to v0.3: parameters/units/ranges, inputs, complete persistent and temporary state, equations, observables, domain and solution constraints, branches and source locators.
- [ ] Declare equation form, time dependence, kinematics, frame/objective rate, tensor/shear basis, signs, stress measure/binding/scope. Do not use legacy top-level `integration` or infer missing conventions.
- [ ] Define initialization/preparation, required internal variables, initial checks, zero/hold behavior, loading reversals and events. Distinguish source initial state from an illustrative preset or inferred closure.
- [ ] Specify time versus path fraction, control histories and interpolation, discretization/lagging, trial/commit/rollback, substeps, discontinuities, restart/checkpoint state and tangent/AD behavior at nonsmooth points.
- [ ] Compare actual requirements against the current DSL, state capacity, controls, Python/native/Wasm APIs and browser UI. Create a small source-derived capability example for each genuine gap; implement it generically under separate ownership before depending on it.
- [ ] Freeze the verification plan before compiled observations: independent reference provenance, cases and parameter/state range, expected successes/rejections, comparisons/tolerances, refinement and rollback/recovery criteria. Include tests of the proposed public default or named preset and unaffected-model regressions.

**Exit:** the complete requested law fits an explicit supported contract, or the exact blocking capability is assigned. The reference and acceptance plan are recorded before qualification.

## E3 — Transcribe and establish independent checks

- [ ] Write the declarative model in the candidate worktree with its intended final ID/metadata. Use the common engine; no handwritten production kernel for this law. Keep research variants separate from public model counts.
- [ ] Write the dossier and source/schema crosswalk, including every project numerical choice, applicability limit and unresolved issue.
- [ ] Validate the individual definition structurally and semantically; generate code through the normal compiler. Check units, branch/domain limits and initialization failures. A root-wide validation command does not validate nested research files automatically.
- [ ] Implement source-derived algebraic, analytical or independently constructed reference checks. Avoid copying production expressions into an oracle and calling it independent. Backend parity alone is not equation verification.
- [ ] Run Python/interpreter checks relevant to the profile and record commands, exact inputs, results, failures and reference convergence. Resolve reference defects explicitly rather than tuning the solver to them.

Useful existing entry points, from the repository root:

```sh
python3 -B -c "from atlas.model import load; load('models/research/MODEL.json')"
python3 -B -m atlas.cli validate
python3 -B -m atlas.cli generate /tmp/atlas-delivery-catalogue
```

Replace the example definition path with the actual candidate. The latter two commands cover the top-level public catalogue; use `atlas.compiler.generate(destination, [candidate_path])` for an isolated research candidate.

**Exit:** the exact candidate validates/generates and independently checks the source law within the frozen scope. Compilation alone is insufficient.

## E4 — Qualify native, Wasm and the exposed controls

- [ ] Obtain the coordinator's execution handoff; pin source/model/compiler/toolchain identities and build in isolated directories. Use the actual target for this profile; a timed or history model may need a different common-engine entry point from `atlas_solver`.
- [ ] Build native first, serially, and verify embedded metadata against the exact candidate bytes. Save build commands, toolchain, stdout/stderr and executable identity.
- [ ] Run the frozen independent-reference cases, admissible/domain-boundary and invalid-input tests, derivative/covariance checks where applicable, and useful finite paths. Include loading/unloading/reversal, holds and time changes when required by the source.
- [ ] Check failed-increment rollback, subsequent recovery and restart/replay against the stated contract. Preserve parent state on failure; compare all physical state, not only a plotted stress channel. Distinguish exact replay from tolerance-based continuation.
- [ ] Build Wasm only after the native stage is understood. Run the same relevant requests, references and native/Wasm comparisons through the intended API. Check failure/recovery and units/scopes as well as successful values.
- [ ] Verify public defaults or registered named examples are useful and successful within disclosed support. Preserve genuine unsupported-default failures as limitations; do not silently turn an unexpected failure into an approved exception.
- [ ] Run appropriate existing-model regressions using the current explicit fixture/profile policies. Add durable model regression coverage to CI. Changes to generic runtime capabilities need their own regression checks.

Serial build pattern (choose an isolated directory and the correct assigned target):

```sh
cmake -S . -B .local/delivery-native -DCMAKE_BUILD_TYPE=Release
cmake --build .local/delivery-native --target atlas_solver --parallel 1
emcmake cmake -S . -B .local/delivery-wasm -DCMAKE_BUILD_TYPE=Release
cmake --build .local/delivery-wasm --target atlas_solver --parallel 1
```

These are the ordinary strain-path target examples, not a claim that every timed/research target is covered. Do not run an unrestricted all-target build or copy older `--parallel 2` instructions. Follow the current workflow and model-specific target contract for broader regression/research builds.

**Exit:** source-derived numerical gates and the claimed native/Wasm interfaces pass with exact candidate identity and retained limitations/failures.

## E5 — Independent agent review and approval

- [X] Hand the exact candidate, readable source receipts, dossier, prospective gates and complete saved results to a separate agent run. Record actual implementation/reviewer run IDs and independence basis. Do not ask the implementation agent to certify its own transcription.
- [X] The reviewer checks all nine items in [checklist v1](../../AGENT_REVIEW_POLICY.md) and supplies reasons, hashed evidence, scope, limitations and blocking findings using [the review template](../../AGENT_REVIEW_TEMPLATE.json).
- [X] Resolve blocking findings; rerun only affected qualification and regression checks when justified. Obtain a new or updated reviewer decision bound to the final model bytes and artifacts. Preserve superseded failures and decisions.
- [X] Store the accepted record under `catalogue/agent-reviews/`, validate it and generate the approval entry. Coordinator integration requires no human scientific sign-off or further user approval.
- [X] Confirm approval refers to the exact intended formulation and supported interfaces/parameter/protocol scope. Keep experimental validation separately assessed; no experimental match is required merely to illustrate an otherwise verified law.

```sh
python3 -B -m atlas.agent_review catalogue/agent-reviews/MODEL-agent-v1.json --for-approval
python3 -B -m atlas.agent_review catalogue/agent-reviews/MODEL-agent-v1.json --approval-output /tmp/MODEL-approval.json
```

**Exit:** an accepted independent agent checklist supports a current, exact-definition approval entry, with no unresolved in-scope blockers.

## E6 — Integrate into the atlas

- [ ] Coordinator installs the exact qualified model bytes and reviewed approval entry, dossier, examples and relevant evidence. Use `models/` only for profiles supported by the normal public engine; otherwise implement/qualify the required generic engine and browser routing. A separate research executable is not public atlas delivery.
- [ ] Update the discovery/catalogue entry and lineage/source links, approval registry, evidence/publication mappings and protocol/example registries as required by their actual consumers. Do not manufacture a legacy human-review acceptance to make an exporter happy.
- [ ] Integrate the public profile in `web/model-profile-data.mjs` under the exact catalogue ID. Explain the implemented variant and a supported example, link related family/variant entries, and retain local content provenance. Run `node tools/check_model_profiles.mjs`; missing public content blocks website delivery.
- [ ] Preserve approval/evidence hashes. If integration changes model metadata, IDs, equations, numerical settings or dependencies covered by the review, rebind the review and rerun affected gates before using the old approval claim.
- [ ] Regenerate the full public catalogue and verify engine metadata equals the definitions packaged with it. Ensure all prior models remain present and retain their qualified behavior.
- [ ] Extend complete-coverage/default/profile policies deliberately for the new model and freeze expected outcomes before observing the new release gate. Keep prior policy/evidence identities and declared failures; do not skip the new model to obtain a green package.
- [ ] Update current status/roadmap counts and model summaries from actual records. Count full formulations and restricted variants accurately. Export the database when part of the release; verify the exact model/source/approval identity survives export.

**Exit:** the ordinary atlas generation path includes the model, its public profile and its actual approval/evidence. No private adapter or hand-edited generated catalogue is required.

## E7 — Make the packaged website work

- [ ] Use fresh matching Wasm/generated metadata and the standard web builder. Packaging must reject stale model/engine combinations. Include only permitted public assets; keep private sources and unapproved original measurement arrays out.
- [ ] Ensure the model is selectable and reachable by its shareable URL; source/DOI links, equations, assumptions, author/variant attribution, initialization, parameter units and limitations are visible.
- [ ] Keep the public profile prominent and the accepted agent review, exact approved scope and retained checks accessible inside closed technical details. If the current exporter/UI only understands older review records, add and qualify generic support for agent-review/approval data; a registry entry alone does not make the website expose it accurately.
- [ ] In the actual packaged browser, inspect the catalogue summary, full public profile and laboratory/profile links. Confirm readable parameter meanings and units, correct initial-state guidance, a supported example and related-model links; check long names/tables on a narrow screen. Do not lead with agent/curation notes or imply that a literature-only entry is runnable.
- [ ] Provide the actual controls required by this model. Physical-time laws need honest time/rate/hold controls and labels; unsupported controls must be unavailable with a useful explanation. A static catalogue card or timed CLI alone is not the requested interactive delivery.
- [ ] In an actual browser, run the public default/named preset; inspect meaningful plots, units, all required state and absence of worker/console/network failures. Exercise parameter/initial-state changes, supported protocols, reset and latest-request behavior.
- [ ] Test export/import/replay and invalid input followed by recovery through the real exposed interface. Record fetched engine/catalogue identities so a stale browser cache cannot supply the evidence.
- [ ] Exercise compatible measurement overlays and their toggle when data rights and model applicability permit. Otherwise show why comparison is unavailable; do not imply calibration, density matching or experimental validation from a plotted overlay.
- [ ] Run relevant package, scope/parity, examples and browser checks. Save exact package manifest, requests/responses and UI evidence. Include at least one successful end-to-end request for this model; no silent unsupported-model filtering.

Existing web build and package entry points:

```sh
python3 -B tools/build_web.py --wasm-dir .local/delivery-wasm --output .local/delivery-site
node tools/test_supported_package.mjs --directory .local/delivery-site --output /tmp/atlas-delivery-package.json
python3 -m http.server 8765 --bind 127.0.0.1 --directory .local/delivery-site
```

Use the current workflow's other parity/profile/browser commands for the actual package. `test_web_package.mjs` is the strict all-default gate; any known unsupported defaults must stay visible, with separately identified supported-input qualification rather than an unexplained waiver. A Python HTTP server is a preview, not proof of deployment.

**Exit:** the exact packaged public application explains the model through its public profile and demonstrates it interactively, with accurate source/review/applicability disclosures and passing interface checks.

## E8 — Publish and verify the live website

- [ ] Prepare a scoped commit containing only reviewed model/integration/delivery changes. Check the staged diff, current source/approval hashes and absence of private or unrelated files. Record source revision and remaining limitations.
- [ ] Confirm push/deployment authorization from the current session. If present, proceed; do not ask again. Otherwise leave the concrete tested release ready and request only the remaining authorization. Do not mark the live-delivery stage complete while it is pending.
- [ ] Push the intended branch and record the exact commit and GitHub Actions run URL. Monitor that run to terminal results; do not substitute an older green run or restart because observation timed out.
- [ ] Require every native, Python, Wasm, package and deployment gate in the current workflow to pass. Investigate failures with retained evidence and requalify changed inputs. A passing browser job does not override a failed native job.
- [ ] Verify the Pages deployment succeeded for that exact revision. Compare live entry/browser/engine/catalogue/model assets with the actual tested upload and check source/review/approval links resolve on the project-path URL.
- [ ] Verify the live public-profile data/rendering assets match the tested upload and the model's catalogue profile, related links and laboratory link display the intended explanation.
- [ ] Open the live model page and execute its illustrative run; confirm the expected model, current fetched identities, meaningful plots and accurate scope. A successful Actions run or a local browser alone does not establish live availability.
- [ ] Fill the delivery ledger with live URL, deployment revision, checks and limitations; update the umbrella task only after the following definition of done is met.

**Definition of done:** the complete named formulation is source-mapped, declarative and numerically qualified for its stated scope; a separate agent has accepted the exact bytes; the atlas includes its public profile and sources/approval/evidence; the packaged and live website explain the model and can actually exercise it; required CI and deployment gates pass for the delivered revision. No human scientific signature is required. Experimental validation and broader unsupported host/kinematic claims remain distinct.

## Handoff and resumption

Every handoff names the umbrella task and phase, exact files/hashes, passed/failed checks, retained failure locations, next owner/action and blocker resolution condition. A blocked source or capability stage stays open; an authorization-only stop is `ready to publish`. The lead resumes from verified evidence, not from an earlier agent's confident summary. Reopen affected later stages after a model/interface identity change; do not rerun unrelated finished campaigns.

Full-delivery dispatch prompt:

> Read AGENTS.md and docs/MODEL_DELIVERY_CHECKLIST.md. Lead MODEL-<id> from existing source work through E0–E8 for the exact assigned variant and website scope. Maintain docs/ingestion/<id>/DELIVERY.md and the coordinator-owned board. Use the assigned worktree/whitelist; arrange specialist capability and separate-agent review handoffs, serial native/Wasm qualification and actual browser checks. Continue after packet handoff to atlas integration and verified live delivery when remote authorization exists. Preserve failures, sources and other workers' files. Report exact evidence and honest blocked/ready/live state; do not equate a packet or approval with delivery.
