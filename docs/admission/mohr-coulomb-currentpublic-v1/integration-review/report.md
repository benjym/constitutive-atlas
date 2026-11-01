# Mohr-Coulomb metadata integration review

Accepted for the exact isolated candidate on public base `e32f8a86df44298f100394b34e084e313d48b195`. Actual reviewer: `/root/mc_scientific_review`; requester and implementer: parent `/root`. Task `REVIEW-mohr-coulomb-integration-v1`, 2026-11-02. No blocking integration finding remains.

This is an integration decision, not a new scientific signature or re-review. The accepted scientific record remains byte-identical at SHA-256 `5190673eb3991450b598f1d0bb0943e6995f605be8890f69d0dc536d9014d9ce`, installed at `catalogue/agent-reviews/mohr-coulomb-agent-v1.json`. Its exact model remains SHA-256 `6a3a139218fc413f066abe5b851c5c7aed8899ee23efbd7ae2a2e68c7655f0e5`. Every original scientific scope limitation remains unchanged.

## Actual checks

The read-only independent checker inspects the candidate and saved outputs, rather than trusting the parent's projection summary. It imports only source metadata validators and reads saved SQLite in read-only mode. It invokes no exporter, material model, compiler, browser or network service, and writes no candidate files.

- Git HEAD is the specified public base. The tracked delta is exactly `catalogue/approved-models.json`; the untracked additions are exactly the 16 hash-pinned evidence/review files in INSTALL.json. No existing model, runtime, schema, source-map, web, CI or other tracked source changed. The source capsule contains exactly these 17 paths and reopens byte-for-byte against the candidate.
- All 24 previous registry objects remain identical and ordered; one generated Mohr-Coulomb approval is appended. Top-level registry metadata is unchanged. The prior registry bytes match both the clean base and the saved before file. The final registry is SHA-256 `96f86b66ceecaf66180b5b1c7dc9a6d8959bb2d72d66edd03b697de710a39504`.
- Normal JSON serialization re-escapes Unicode in some old lines. This is a disclosed textual change within the one registry file; prior object values and exported rows remain exact. This acceptance does not assert registry byte-prefix preservation.
- The appended object equals the ordinary `approval_entry` result and the parent's saved approval-entry.json exactly. It preserves the actual reviewer identity, scientific record hash, model hash, scope, all limitations, `experimental_validation: not_assessed` and `deployment_authorized: false`.
- All 25 approved definitions and all 21 registered independent-agent review entries validate. For each agent entry the regenerated approval equals the registry object. The 40 previous review/definition artifacts match the clean public base byte-for-byte. The new scientific record's 55 direct artifact hashes and all 13 frozen review-input hashes match; no archive map, older evidence or source binding was rewritten.
- Every row in all nine saved before/after database tables is compared with duplicate-aware multisets. Models remain 48 and sources 202; all publication, relationship, screening and evidence rows remain unchanged. Only model_approvals grows 24 to25 and agent_reviews20 to21, each adding exactly its expected JSON object and losing no row.
- Every old evidence-index section and all20 old agent-review rows are identical. The one new row has the exact current MC definition, accepted scientific record, checklist, scope, limitations and registered approval identity. Every saved metadata file is byte-compared: precisely two new exports (scientific record and exact model-definition copy), two changed exports (registry copy and evidence index), and no removed export. Exported MC record, definition and registry match source bytes exactly.
- Both retained archives reopen safely without extraction: candidate-source.tar.gz has17 exact source files, and projection-outputs.tar.gz has234 exact saved normal public database/evidence files. Their source/output hashes are bound in source-pins.json. No article PDF or compiled payload was added. The retention receipt names the private original, but that original is absent from the candidate and its source capsule.

## Test disposition

I read both terminal logs and TESTS.json. The initial command was `python3 -B -m unittest tests.test_agent_review tests.test_agent_review_export tests.test_database_approval_integrity tests.test_database_package`. It finished with exit1:34 tests,33 passes, one PermissionError at `self.socket.bind(self.server_address)` in the project-path HTTP download-link case. This original failure remains retained.

The exact single blocked case was then retried with loopback permission: `python3 -B -m unittest tests.test_database_package.DatabasePackage.test_download_links_resolve_under_a_project_path_with_matching_bytes`. Its terminal log says Ran1test/OK; the actual parent process receipt records exit0. No source or gate changed between attempts. Thus every one of the34 existing cases is resolved; there was no claimed full-suite exit0 rerun. The checker verifies the receipts against both exact log hashes. I did not rerun these tests or open a socket during this review.

## Pins and reproduction

`source-pins.json` hashes candidate inputs, the unchanged scientific artifacts, relevant metadata validation/export/test sources, the parent's projection script and every saved evidence file, including both preservation capsules and test receipts. `check-results.json` records the actual successful independent check. The parent projection script was inspected and pinned; it temporarily removes/restores candidate additions to generate before/after normal exports. It was not executed by this reviewer.

Reproduce without material execution or candidate mutation:

```sh
python3 -B check_saved.py /private/tmp/atlas-mc-admission-public-v1 /private/tmp/atlas-mc-admission-evidence-v1
```

The checker accepts other absolute candidate/evidence paths, provided the candidate remains an uncommitted exact17-path delta on the named Git base and the saved inputs retain their pinned bytes. After committing the candidate, reproduce in a fresh checkout of the named base with the exact source capsule applied. The parent owns preservation/integration of the candidate and saved output capsules; no external evidence was copied or rewritten by this reviewer.

## Scope and handoff

Acceptance covers only additive source/approval metadata integration and the inspected normal database/evidence projections. It makes no new claim about compiled execution, builds, engine/package/browser/live delivery, current-release qualification or experiments. The original scientific near-apex, parameter, tangent, preparation and physical applicability limitations remain intact. No public original PDF is introduced.

Smallest next action: coordinator verifies this decision and its hashes, then integrates precisely the reviewed17 source paths and retained evidence using the project's existing authorization. A changed candidate, source binding or scientific record needs a new integration check; this decision does not authorize changing an old record, broadening its scientific scope or declaring deployment complete.
