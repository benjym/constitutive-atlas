# Independent agent approval policy v1

The user's 1 November 2026 instruction replaces human scientific sign-off with a separate agent review against a reasonable checklist. Current authority is `docs/AGENT_REVIEW_POLICY.md`; the charter, roadmap, status, agent/reviewer instructions and queued baseline/barodesy review tasks now use that pathway.

New `schemas/agent-review.schema.json`, `atlas/agent_review.py` and the pending template enforce nine named checklist items, separate reviewer/author run IDs, exact current model ID/hash, reasons, hashed evidence references and no unresolved blocking findings. Core items must pass; compiled backend delivery can be excluded with a reason when outside the approved scope. The command generates an approval-registry entry after an accepted review; it requires no human signature or extra user sign-off and never rewrites model metadata. Deployment and experimental validation remain separate. No model was automatically approved by this policy change.

All existing review records, explicit approvals, failures and private sources remain intact. The old v0.1 human-oriented review envelope remains a historical format; new approval uses the agent-review format. Original policy documents and transitive map identities are preserved under content-addressed snapshots. Legacy nonstandard review maps were left intact; their original document/source pins are separately recorded in the archive plans.

Validation: 25 focused tests pass, including checklist/independence/hash/finding negative cases, archive and CI contract tests, and every existing committed evidence/review envelope. Pending template conforms to its schema and CLI help executes. No native/Wasm build, material simulation, automatic model promotion, push or deployment belongs to this policy task.

The initial archive planner encountered a legacy nonstandard map and stopped before modifying sources. The revised plan preserves that format and its exact references separately. This planning failure and adjustment are retained here; no expected result or acceptance threshold changed.
