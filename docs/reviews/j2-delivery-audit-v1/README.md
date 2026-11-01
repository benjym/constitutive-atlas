# J2 retrospective delivery audit v1

The bounded scientific/model delivery remains valid, but the full E0–E8 loop is incomplete. The [delivery ledger](../../ingestion/j2-linear-hardening/DELIVERY.md) records each gate. The original commit/push did not put J2 into the normal atlas or live browser.

## Findings and repair

1. **Approval integrity regression — repaired.** Adding the new checklist link changed the live agent-review policy, invalidating the old exact artifact pin. The original failure is retained in `approval-before-fix.log` and `before-fix.json`. The validator now uses the existing strict immutable receipt resolver only for explicitly registered historical review documents. Exact old policy/helper bytes and additive archive maps preserve historical identities. Unregistered reviews retain current-artifact checks. The current model hash remains mandatory; archived models cannot authorize changed current definitions.
2. **Full delivery gaps — open.** Normal generation and discovery omit J2, and normal compiled CI target lists omit its standalone solver. Python J2 tests are included by unittest discovery. Browser/package interfaces and their regressions have not been qualified. Live metadata excludes J2. These remain E2/E4/E6–E8 work, without broadening the approved isolated scope.
3. **Historical contextual input — unresolved.** The original reviewer pinned one unsaved WIP `IMPLEMENTATION_PLAN.md` snapshot. Its expected hash is preserved in `historical-input-gaps.json`; no inferred replacement is accepted. All other historical scientific inputs resolve. This is an explicit reproducibility limitation, not a new scientific result.

Original model, review, approval and scientific reports remain unchanged. The independent reviewer checks 22 original files against commit `06f5214d` and the identical J2 approval-registry object. No compiled artifact, vendor code or numerical model was executed/changed in this audit; no new push or deployment occurred.

## Verification

From repository root:

```sh
python3 -B -m unittest tests.test_agent_review tests.test_agent_review_archives tests.test_evidence_archives tests.test_j2 -q
python3 -B docs/reviews/j2-scientific-v1/check_review.py
python3 -B docs/reviews/j2-scientific-v2/check_review.py
python3 -B docs/admission/j2-approved-v2/check.py
python3 -B docs/reviews/j2-delivery-audit-v1/independent-review/check_review.py
```

`tests.log`: 33 focused tests pass. `approval-check.json`: nine accepted checklist decisions, four private source receipts and five admission-corruption rejection checks pass. Both original scientific replays pass (v1 retains its rejected reverse-root finding; v2 remains accepted). Independent-review output records archival mutation probes and original-byte preservation. Its first attempt detected a duplicate additive archive receipt; the parent removed the duplicate and retained that failure in `archive-map-construction-failure.json` and independent-review attempt files.

`generation-check.json` records normal versus isolated source generation, without a build. `live-catalogue-check.json` records successful HTTP metadata observations and exact returned hashes. `actions-run.json` records the exact original push's nonterminal Actions status; `actions-refresh-failure.json` retains a later network failure. CI success and deployment are unverified, not assumed.

The audit/fix/review child tasks may close after independent review. MODEL-j2-linear-hardening remains open. The next concrete task is a prospectively frozen normal-atlas interface and regression study.

Nonblocking reviewer finding AR-LOW-001: a malformed archive-map `documents` list can raise raw `AttributeError` rather than `ValidationError`. The request fails closed; no model/hash bypass was found. Error normalization remains optional follow-up.
