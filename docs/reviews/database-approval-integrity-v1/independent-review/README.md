# Independent review of SQLite approval integrity

**Accept the bounded exporter interface and exact intended archive-map delta.**
Reviewer `/root/kfs_development_review`, separate agent run, 1 November 2026.
No model/source scientific re-review, new approval, material call, build, fit,
staging or commit was performed by this reviewer.

Reviewed `atlas/research.py` SHA256:
`279f5564d9484514f9d66db9b8a5fa4482dc534a6c9d4954b0e10001ad7b2c0a`.
Reviewed test SHA256:
`aad4d04913a806e48cbb33160d7e7e5d9e78d83a92a35ba11df3b2d6933d43a1`.
See [manifest](manifest.json), [decision](decision.json) and
[independent results](check-results.json).

## Semantics and evidence

The exporter now invokes the existing canonical `approval_entry` for agent
approvals and compares every generated field before inserting their review row.
This reuses complete checklist coverage, independence, artifact hashes, current
model binding, accepted status and absence of blockers. A matching review hash
or the word accepted alone cannot authorize broader registry scope, removed
limitations, different authority, experimental validation or substituted evidence.
Canonical fields are compared while additional non-authoritative project
metadata remains permitted. This is integrity validation of a real recorded
review, not proof that a scientific reviewer actually did their work.

The discriminator checks either independent-agent authority or an agent review
kind. It rejects missing/inconsistent review metadata rather than using that
inconsistency to bypass validation. Genuine existing explicit-user-authority
records retain their separate treatment. Ordinary executable membership, exact
model definitions, source links and legacy model status are preserved.

I independently ran nine tests: seven new integrity groups plus the two existing
approved-export tests. They cover forged registry fields, self-review, missing or
failed checklist items, blockers, unbound/corrupt evidence, stale review hashes,
exact JSON/source/membership preservation, allowed project metadata, repeated
export and rollback of an existing valid database. The rollback test compares
logical SQLite contents, not physical file-byte identity. Validation occurs
inside the data transaction, so failure rolls back deleted/inserted rows. DDL
creation is not claimed to be reversible for a new invalid-export destination.

Three additional direct synthetic probes confirm that changing review kind,
removing it or removing the review object cannot export an independent-agent
authority approval with forged broader scope. They now all raise ValidationError.
A real current-working-tree export independently retains thirteen approval
objects exactly, nine exact agent review records, four distinct user-authority
records and thirteen ordinary executable definitions. Its second export has
identical logical contents. Those counts describe the reviewed shared checkout,
not a clean staged release or new scientific admission.

The coordinator's separate 44-test log and broader export/FK counts are retained
as supporting evidence; my independent run is the nine tests and four additional
review groups recorded here. I did not claim to rerun all 44 tests.

## Concrete findings resolved

My initial probe found a bypass in the first proposed patch: changing or removing
`review.kind`, or removing `review`, skipped the canonical check while still
exporting independent-agent authority and forged scope. All three exports
succeeded with zero agent-review rows; [original observations](initial-bypass-probes.json)
are retained. The final authority-or-kind discriminator and its regression test
close that observed bypass. No blocking exporter finding remains.

The first real working export also failed on the separately owned Original Cam
Clay review's historical schema binding. That was an integrity failure correctly
exposed by the stricter exporter, not evidence to relax its validation. The
[initial per-approval audit](initial-working-approval-audit.json) preserves the
failure; eight other agent approvals matched exactly. The coordinator recorded
and restored its existing exact historical contract/schema receipt bindings in
`concurrent-review-archive.json`. My subsequent current-tree export passes.
Those concurrent registry/archive objects are not included in this review's
approval of the intended staging delta.

## Exact archives and ownership

The old exporter bytes remain at source snapshot `2668e732...`. The checklist
archive `3436962d...` is exact; I also checked its bytes against
`git show 9e7cab5e:docs/MODEL_DELIVERY_CHECKLIST.md`. The prior dirty source map
snapshot `f34be117...` is exact, and every pre-existing dirty document binding and
entry remains in the working map. Only the two unchanged DP/Burgers review
bindings plus one exact old-checklist entry belong to this task's map change.
Neither review decision nor expected artifact hash was altered.

I compared `proposed-archive-map.json` independently against the committed map
at `f8252c16`. Parsed contents are exactly that base plus those two document
bindings and one entry, with no other working delta. Proposed map SHA256 is
`0cc80b0eac2860cd3236f94b6cbdb35d16969f94ed7bf18b1b54d8089ab28c15`;
[scope proof](proposed-map-review.json) records the exact base and additions.
Acceptance applies to that proposed projection, not wholesale staging of the
mixed working source map. The coordinator must still check the actual index.

No current canonical agent-review artifact directly binds `atlas/research.py`.
Existing retained Newton source trees already preserve their own old copies.
Historical power-creep delivery checks directly assert old live source hashes;
this intentional interface change can therefore make their live-currentness
check fail. Preserve their freezes and original reports. A sidecar cannot make
a direct live-file assertion pass, and no mass archival migration or historical
check weakening is justified by this task.

## Reproduce

From the repository root:

```sh
PYTHONPATH=. python3 -B docs/reviews/database-approval-integrity-v1/independent-review/check.py --output /private/tmp/db-approval-independent-replay.json
```

The checker pins reviewed exporter/test hashes, runs the nine tests, repeats
independent discriminator probes, verifies archive preservation and observes an
idempotent temporary SQLite export. It does not alter the production registry
or database. Its current-tree export needs concurrent valid registry/source-map
state; it is deliberately distinct from the exact proposed staging projection.

Smallest next action: stage only the reviewed source/tests, owned archives/packet
and exact proposed map delta, then verify index ownership. No scientific
promotion, deployment or remote push is authorized by this interface review.
