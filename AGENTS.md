# Agent instructions — Constitutive Atlas

## Start here

For a full new-model assignment, follow [MODEL_DELIVERY_CHECKLIST.md](docs/MODEL_DELIVERY_CHECKLIST.md) from E0–E8 and maintain `docs/ingestion/<model-id>/DELIVERY.md` using [the delivery ledger](docs/ingestion/DELIVERY_TEMPLATE.md). The lead carries the model through source ingestion, implementation, independent agent approval, atlas integration, actual browser qualification and verified live delivery. A source packet is a specialist deliverable, not completion of the full model task.

Every catalogue entry also needs a reader-facing profile under [PUBLIC_MODEL_PROFILES.md](docs/PUBLIC_MODEL_PROFILES.md). Explain behaviour, parameters, starting state, supported examples and meaningful limits; keep curation/check details behind the technical disclosure. Source-only workers supply the draft and provenance inside their owned packet; the coordinator integrates it into `web/model-profile-data.mjs` and verifies it at E6–E8. A runnable model without its public profile is not complete website delivery.

Read [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the live model-ingestion board, [ROADMAP.md](ROADMAP.md) for research milestones, [docs/RESEARCH_CHARTER.md](docs/RESEARCH_CHARTER.md) for admission rules and [docs/STATUS.md](docs/STATUS.md) for existing evidence. Read the named model's dossiers, source audits and research packets before doing work. The historical JSON research queue is background evidence; do not edit it to track live ownership.

The user authorizes parallel model ingestion. Work on different model packets concurrently. The coordinating parent agent is the integration owner; do not assign work to Benjy or François without their agreement.

## Schema target for new work

Use [model-v0.3.schema.json](schemas/model-v0.3.schema.json) and [FORMULATION_CONTRACT.md](docs/FORMULATION_CONTRACT.md) for all new model records and ingestion crosswalks. Declare `schema_version: "0.3"` and the complete explicit `formulation`; do not use the legacy top-level `integration` field or infer convention defaults. Map the source-supported equation form, time dependence, kinematics, frame/objective rate, tensor/sign conventions and stress binding/scope. If a source needs an unsupported profile, record the capability gap rather than force it into a supported one or guess missing conventions.

Another agent owns migration of existing records. Do not migrate existing model JSON, rewrite hash-pinned evidence, or modify the shared schema/compiler as part of ingestion. Historical packets and receipts retain their original identities; new crosswalks target v0.3. Read the current schema and contract before starting because this version is being integrated concurrently.

## Agent review and model approval

Follow [AGENT_REVIEW_POLICY.md](docs/AGENT_REVIEW_POLICY.md). A separate agent run reviews the exact model/source/numerical evidence against checklist v1. An accepted, hash-bound checklist permits coordinator integration into the approval registry without human scientific review, signatures or another user approval. Do not self-review, invent reviewer decisions, waive blocking findings or infer experimental validation from approval. Existing pending records are historical; create a new agent-review record rather than rewriting them. The coordinator may dispatch an explicitly scoped independent review to a separate agent when this approval step is needed.

## Claiming and coordination

1. Ask the coordinator to claim one unstarted task. The coordinator alone edits the shared board: set `[ ]` to `[-]`, record owner, date, scope and output directory **before dispatch**. Re-read the board before starting. A queued owner starts after handing off prior work; do not run two unrelated assignments simultaneously in one worker.
2. For a source-only specialist task, own only the assigned `docs/ingestion/<model-id>/` directory. For a full-delivery lead, the coordinator assigns a dedicated worktree or explicit wider path whitelist and dependent integration/build/review tasks; do not silently inherit shared-file ownership. Agents sharing this checkout must not stage, commit, reset, stash, clean, or overwrite one another's files. A separate worktree may be used when the coordinator provides it.
3. Do not edit shared schema/compiler/C++/CMake/web/catalogue manifests or historical evidence. Describe a missing generic capability in the packet with a minimal source-derived example; the coordinator creates a separate implementation task. Do not introduce a model-specific handwritten kernel.
4. Keep the coordinator informed of progress and exact blockers. If source access is blocked, produce a useful bounded gap report and work on all independent sections. Never invent missing equations. Do not reclaim an apparently idle task without coordination.
5. Submit exact files and checks to the coordinator. Only the coordinator marks `[X]` after reviewing and integrating the agreed deliverable. Preserve partial results and failed checks; a gap report may complete an explicitly scoped acquisition task but never a source-complete ingestion task.

## Worker status and handoff

A worker reports the task ID, understood scope and owned output path when starting. Send the coordinator a short update at a meaningful milestone, when scope changes, or when blocked. A final handoff lists exact files, reproducible checks, retained failures, blockers and the smallest next action. A submitted packet remains `[-]` until the coordinator reviews and integrates it; completion of an agent run alone does not change the checkbox.

Dependencies belong on the task row. Keep source acquisition, transcription, executable integration, independent agent approval and website/release work as separately scoped child tasks under a `MODEL-<id>` full-delivery umbrella. The lead resumes after each handoff; the umbrella remains open until live delivery is verified (or honestly recorded blocked/ready to publish). Unrelated model ingestion can continue while a shared capability is pending.

## Ingestion deliverable

Copy [the packet template](docs/ingestion/TEMPLATE.md) to `docs/ingestion/<model-id>/README.md`. Deliver:

- Exact formulation, publication/version identity and persistent hyperlinks (prefer DOI and author/institutional source). Distinguish model families, later revisions, implementations and numerical choices.
- A source-backed public-profile draft following [the public content contract](docs/PUBLIC_MODEL_PROFILES.md), with local provenance, readable references and a supported example where the model is runnable. A literature-only profile must not promise laboratory availability or invent missing equations/parameters.
- Source receipt: title/authors/year/version, URL, local private path if available, SHA-256, access date and equation/page/table locators. Check user-provided Downloads and existing source inventories first. Verify title/equations against readable source; do not infer equations from abstracts or search snippets.
- Complete available equations and a source-to-schema crosswalk: parameter units/ranges, state layout, signs, tensor/shear conventions, loading inputs, constraints, initialization/preparation, branches/domain limits and history/reset events.
- Explicit integration contract: rate versus incremental law; strain-path parameter versus physical time; required time/loading history; trial/commit/rollback semantics; ordering and lagged values; zero-load/hold behavior; discontinuities/events; tangent and solver requirements. Record unsupported or unspecified behavior.
- A small independent algebraic/analytical check where justified, plus reproducible commands/results. A blocked source acquisition need not invent a numerical test. Shared interpreter/native/Wasm agreement is not independent equation verification.
- Gaps, ambiguities, rights/access restrictions, schema capability requests and the smallest next implementation/reference study. State source completeness, executable status, numerical verification and scientific admission separately.

Keep raw copyrighted PDFs and vendor code private unless redistribution is clearly authorized. Link and hash sources instead. Never execute supplied Fortran, DLLs or other author binaries. Browsing/source reading and isolated Python analysis can run in parallel; use the applicable PDF skill when inspecting PDFs.

## Builds, evidence and repository safety

Native and Wasm builds are owned by the coordinator and run **serially, one explicit target, `--parallel 1`** because of prior Cortex interruptions. Workers do not build or execute compiled artifacts without an explicit coordinator handoff. Do not bypass endpoint protection.

Freeze references and acceptance policies before observing compiled results. Preserve original reports, failures, receipts, source hashes and archives. Never relax a gate after observing failure to obtain a pass. New diagnostics and revised studies have distinct identities. Do not rewrite hash-pinned documents or model definitions casually; coordinate exact-byte archival first.

Preserve unrelated work, especially the existing `paper/` tree and untracked numerical evidence. Only commit explicitly owned paths, through the coordinator. Local commits only: **do not push, deploy or trigger remote CI** without a new explicit instruction. Follow current filesystem permissions; an assigned path is not a sandbox override.

## Suggested full-delivery lead prompt

> Read AGENTS.md and docs/MODEL_DELIVERY_CHECKLIST.md. Lead MODEL-<model-id> through E0–E8 for the exact assigned formulation. Maintain docs/ingestion/<model-id>/DELIVERY.md, arrange separate-agent checklist review and coordinator-owned shared/build handoffs, and continue from source packet to working atlas/browser integration and verified live delivery when authorized. Use only the assigned worktree/whitelist, preserve failures and report evidence-backed stage status. Packet completion alone does not finish this assignment.

## Suggested source-only specialist prompt

> Read AGENTS.md and IMPLEMENTATION_PLAN.md. You own ING-<model-id>, only docs/ingestion/<model-id>/. Read existing evidence first. Produce the bounded source/schema/integration packet using docs/ingestion/TEMPLATE.md; do not edit shared code, build, commit, or change admission status. Report exact output files, checks and blockers to the coordinator.
