# Independent review of J2 approval archive repair

REV-j2-approval-archive-fix-v1, reviewer `/root/j2_scientific_review`, 2026-11-01. **Accept the archive-resolution repair.** It restores validation of the existing bounded J2 approval without changing scientific judgments, accepted model bytes or numerical acceptance gates. This is a source/unit/saved-evidence review, not a new scientific approval or full-delivery certification.

The validator delegates historical artifact resolution to the existing `checked_receipt` only when the review is explicitly registered in its sibling archive map. That resolver checks the immutable review document hash, original path/hash receipt, unique canonical snapshot location, repository containment and exact archived bytes. A mapped corrupt/missing archive cannot fall back to an unchanged live file. Unregistered reviews continue requiring exact live artifacts. The separate current-model ID/hash check remains direct and never uses the archive resolver. Checklist completeness, separate author/reviewer runs, blocking findings and accepted-status conditions are unchanged.

Independent checks confirm:

- All 22 original model, checklist, scientific-review v1/v2 and approval-packet files are byte-identical to commit `06f5214d2e18f4806a0a779204b6371fb38bafa6`; the J2 registry object is unchanged.
- Five explicit archive edges and their document pins verify. Of 62 historical v2 input receipts, 61 resolve exactly. The sole remaining gap is the known historical WIP `IMPLEMENTATION_PLAN.md` hash `e4d9fbaac223f2b7c37ee83dbb18e2f1131bc3f7a1dc55502cf7a4037c288b84`. It is contextual ownership/board evidence, not a governing equation, numerical reference or build input. This retention gap is nonblocking for restoring the existing scientific approval, and must not be described as complete historical context retention.
- Twenty-six focused unit tests pass. Independent synthetic probes confirm legitimate historical resolution and rejection of corrupt/missing archives even with exact live bytes restored, a symlink escape, a changed registered review and an archived-model attempt to bypass the current model requirement.
- Original v1/v2 scientific saved-data replays and the original approval checker pass. V1 still recommends no admission; v2 remains the separately accepted exact corrected definition. No backend, compiled artifact, vendor code, browser or remote action was executed.

One archive-map construction defect was found during source inspection: the new v2 sidecar initially duplicated the old validator receipt, which would make that embedded input receipt ambiguous. The coordinator removed the redundant additive entry; all five edges now resolve. Historical evidence files were not rewritten. The observation and correction are retained in the parent audit's `archive-map-construction-failure.json` and this review's findings.

Nonblocking code concern AR-LOW-001: a malformed `documents` list containing the registered review path raises an uncaught `AttributeError` rather than the advertised `ValidationError`. The isolated probe confirms that it fails closed; it cannot authorize a stale artifact, model or review. Optional improvement: validate that `documents` is a mapping before membership/lookup, or normalize this error. This does not block the integrity repair.

The E0–E8 checklist does not turn bounded research approval into public delivery. Existing evidence supports the selected variant/source/definition/isolated execution and E5 approval scope. E2/E4 have bounded research-profile evidence, while their complete public-delivery contract, exposed controls and regression obligations remain unfinished. Saved normal-generation evidence excludes J2 from the public catalogue (E6 incomplete); no packaged-browser J2 qualification establishes E7; the saved Actions record is nonterminal and supplies no verified J2 live deployment (E8 incomplete). These are delivery gaps, not reasons to rewrite or broaden the original scientific acceptance. Parent owns the delivery ledger and subsequent work.

Reproduce from repository root:

```sh
python3 -B -m unittest tests.test_agent_review tests.test_agent_review_archives tests.test_evidence_archives -v
python3 -B docs/reviews/j2-delivery-audit-v1/independent-review/check_review.py
python3 -B docs/reviews/j2-scientific-v1/check_review.py
python3 -B docs/reviews/j2-scientific-v2/check_review.py
python3 -B docs/admission/j2-approved-v2/check.py
```

`results.json` binds original identities and archive resolutions; manifests bind reviewed inputs and emitted evidence. The repair is accepted with the low concern and contextual retention gap disclosed. No historical identity or scientific gate changes are requested.
