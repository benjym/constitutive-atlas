# New-model agent assignment

Copy this assignment into the model's working notes or use the dispatch prompt below. The authoritative scientific and delivery gates are [the full E0–E8 checklist](../MODEL_DELIVERY_CHECKLIST.md); this template makes ownership, outputs and continuation explicit. Read [AGENTS.md](../../AGENTS.md) first. Use the current schema and tooling, rather than assuming old command examples still apply.

## Assignment contract

- Umbrella task: `MODEL-<model-id>`
- Exact publication, year, version and formulation:
- Lead agent / run ID:
- Worktree or explicit writable path whitelist:
- Coordinator / shared integration owner:
- Independent reviewer: separate run, assigned before E5
- Destination: general atlas catalogue and main interactive laboratory
- Intended controls, supported scope and exclusions:
- Public profile: source-backed draft/provenance and integration owner; follow [PUBLIC_MODEL_PROFILES.md](../PUBLIC_MODEL_PROFILES.md)
- Existing packets, model definitions, reviews and failures to reuse:
- Remote publication authorization: session reference or pending

The lead owns continuation through every stage. Delegate source reading, capability work or review with explicit child tasks and owned paths; resume the umbrella after each handoff. Only the coordinator edits the shared board. An accepted source packet or completed review does not close the umbrella.

## Start the task

- [ ] Read the live board and relevant model-family dossiers, existing implementation, source inventory and retained failures. Check Downloads/private receipts before requesting sources again.
- [ ] Confirm exact variant, duplicate/lineage relationships and the complete formulation requested. Do not quietly substitute a restricted model.
- [ ] Have the coordinator claim the umbrella and necessary child tasks before work starts; record ownership, dependencies and paths.
- [ ] Copy [DELIVERY_TEMPLATE.md](DELIVERY_TEMPLATE.md) to `docs/ingestion/<model-id>/DELIVERY.md`. Keep scientific content in a separate `README.md` based on [TEMPLATE.md](TEMPLATE.md).
- [ ] Copy the individual E0–E8 checkboxes from the full checklist into the ledger, or link a model-local checklist containing them. Use `[ ]` unstarted, `[-]` working/blocked and `[X]` verified complete. Record a reason and reviewer agreement for genuinely inapplicable checks; never silently omit them.

## Create the model-local checklist

Keep the canonical checklist unchanged. Copy its E0–E8 sections into `docs/ingestion/<model-id>/CHECKLIST.md`, preserving every check and exit condition, and link that file from `DELIVERY.md`. If an existing model already has equivalent detailed checks, reuse and link them instead. The delivery ledger is the stage summary; the model-local checklist records the individual checks.

For each completed item, record the exact input path/hash, reproducible command or inspection, actual result and retained evidence path. For working or blocked items, record the owner, specific blocker, next concrete action and observable resumption condition. An inapplicable item needs a written reason accepted in the independent review; never silently omit it. Closing a stage requires its exit condition and linked evidence, not just changing the summary checkbox.

## Work through the gates

Use this table to choose the next concrete deliverable. The detailed checkboxes and exit conditions remain in the full checklist; this table does not replace them.

| Gate | Produce | Evidence needed before closing |
| --- | --- | --- |
| E0 — Scope | Assignment, ownership, exact variant, ledger and child tasks | Clear destination, limits, dependencies and acceptance criteria |
| E1 — Sources | Readable-source inventory, receipts, equation locators and version reconciliation | Every required equation/convention traceable; rights and unresolved gaps explicit |
| E2 — Contract | v0.3 source/schema crosswalk and complete integration contract | State, units, signs, stress/frame/tensor conventions, initialization, time/controls, events, transactions and capabilities specified; reference plan frozen |
| E3 — Definition | Declarative candidate, dossier and independent reference checks | Exact candidate validates and generates; source-derived checks pass independently of backend agreement |
| E4 — Numerical delivery | Isolated native then Wasm builds, raw results and assessments | Frozen reference, failure/recovery, restart, parity, public preset and relevant regression gates pass for exact artifacts |
| E5 — Approval | Actual separate-agent checklist, resolved findings and generated approval entry | All nine review decisions and exact model/evidence binding accepted; no human scientific sign-off required |
| E6 — Atlas | Normal catalogue generation, registry/discovery entries, dossier, public profile, examples and database export | Profile coverage and source/parameter identity checks pass; model, source links, approval and evidence survive generation/export; existing models retained |
| E7 — Website | Standard package, public profile/card and main-laboratory routing, controls, plots and actual browser evidence | Readable profile, example/parameter guidance, related/laboratory links and narrow-screen layout work; real preset run, changed inputs, reset/recovery/replay, current asset identities and technical source/review links work |
| E8 — Release | Scoped release commit, authorized push, CI/deployment and live verification receipts | Exact deployed revision passes required jobs; live assets match tested package and live model run works |

## Integration details that must not fall between owners

- [ ] Resolve missing generic DSL/compiler/solver capabilities under a separate assigned task, with a minimal source-derived example and relevant regressions. Do not add a handwritten production model kernel.
- [ ] Freeze reference cases, tolerances, expected failures, refinement, parameter/control scope and acceptance policy before compiled observations. Keep raw results and failed attempts.
- [ ] Arrange the coordinator's explicit build/execution handoff. Native first; one explicit build target per command, `--parallel 1`; serialize native/Wasm work and respect Cortex interruptions.
- [ ] Supply at least one useful source-supported preset through the actual public interface, including required preparation and physical-time history. Qualify complete state and relevant controlled quantities, not only one plotted channel.
- [ ] Obtain the real independent agent review; validate its record and integrate the generated exact-definition approval. An integrity checker cannot create or substitute for that review.
- [ ] Update the actual consumers: discovery manifest, approval registry, publications/evidence mappings, examples/protocols, normal builder, engine routing, database export and required CI coverage as applicable. Check current code paths rather than adding unused metadata.
- [ ] Keep persistent DOI/author/institutional source hyperlinks in the definition and visible website. Show exact variant, units, initialization, assumptions, applicability and approved scope.
- [ ] Deliver a [public profile](../PUBLIC_MODEL_PROFILES.md) explaining behaviour, parameters, initial state, supported exploration and material limits. The coordinator installs `web/model-profile-data.mjs`; run `node tools/check_model_profiles.mjs`. Inspect it in the packaged and live catalogue, with checks/curation records in closed technical details. A source-only worker hands off the packet-local draft and provenance.
- [ ] Add model-appropriate controls to the main laboratory and meaningful plots/state output. A standalone page, catalogue card or dedicated CLI alone does not finish website delivery.
- [ ] Verify packaging rejects mismatched model/engine assets. Exercise the real browser worker, current fetched assets, model switching/latest-request behavior, invalid input then recovery, export/import/replay and reset.
- [ ] Evaluate measurement overlay compatibility and redistribution rights. Where permitted, test the toggle; otherwise explain its absence. Keep illustrative execution, calibrated comparison and experimental validation as separate claims.
- [ ] Reconcile status/roadmap counts only from actual stage evidence. Reopen affected gates when reviewed model, runtime or interface identities change.

## Evidence and handoff format

For each closed checkbox, record the exact input identity, command/checker, actual outcome and retained output path. A summary saying “tests pass” is insufficient. Use hashes or the applicable committed revision and artifact manifest. Keep copyrighted sources in permitted private storage and publish their receipts/links.

At every handoff or blocker, update the ledger with:

```text
Task / phase:
Exact model path, SHA-256 and claimed scope:
Owned files changed:
Checks run, actual results and evidence paths:
Retained failures / untested claims:
Independent review decision and exact inputs, if available:
Next concrete action / owner:
Blocker and condition that permits resumption:
```

Prefer the smallest next action that closes a named gate. Reuse valid evidence; start another study only for an identified uncovered claim. A source gap stays a source gap, a capability gap gets an assigned implementation task, and an authorization-only release stop is “ready to publish.” Continue independent useful work while a dependency is pending. Do not weaken a failed gate to obtain completion.

## Finish the assignment

- [ ] E0–E7 have evidence-backed completion and all blocking review findings are resolved.
- [ ] Review the exact scoped diff and exclude private material and other workers' changes.
- [ ] Use existing session authorization for remote actions within its scope. If absent, prepare the tested release completely and ask only for the remaining push/deployment action.
- [ ] Verify every required CI job and Pages deployment for the actual release revision, then run the model on the live main atlas and check its source/review links and asset identities.
- [ ] Complete E8 receipts and have the coordinator close the umbrella. Report source completeness, executable scope, approval, browser/live delivery and experimental validation separately.

## Copyable dispatch prompt

> Read AGENTS.md, docs/MODEL_DELIVERY_CHECKLIST.md and docs/ingestion/AGENT_ASSIGNMENT_TEMPLATE.md. Lead MODEL-<model-id> for <exact publication/version/formulation> through ingestion, declarative implementation, independent numerical qualification, separate-agent approval, general atlas/main-laboratory integration and verified live delivery when authorized. Your worktree/whitelist is <paths>; the coordinator is <owner>. Reuse <existing evidence>. Maintain docs/ingestion/<model-id>/DELIVERY.md with detailed E0–E8 checkboxes and evidence. Arrange explicitly scoped capability, build and independent-review handoffs; continue after each. Preserve failures, source rights and other workers' files. Do not stop at a source packet, approval record or local preview. Report the smallest concrete next action whenever blocked, and distinguish ready-to-publish from live.
