# Evidence and review records

Evidence supports a named claim about a particular definition. A green build or a valid record does not promote a model automatically.

Numerical envelopes in `catalogue/evidence/` follow [evidence.schema.json](../schemas/evidence.schema.json). Each has a stable ID, creation time, source commit, exact model-file SHA-256, automated executor/method, scope, limitations, outcome, reproduction command, hashed report artifacts and hashed relevant source files. The schema forces automated records to declare `independent_review: false`. This does not rule out useful analytical or external-reference checks; it prevents confusing their execution with independent scientific review.

Review records in `catalogue/reviews/` follow [review.schema.json](../schemas/review.schema.json). A pending record names the dossier, model revision, supporting evidence IDs and open questions. A completed record requires a reviewer identity, review date and an explicit independence declaration. Acceptance cannot retain unresolved questions. These fields record an actual review supplied by a reviewer; schema validation cannot authenticate a person or establish that the review happened. Do not manufacture a signature or assign a maintainer without agreement.

Validate a record with:

```sh
python3 -m atlas.cli evidence catalogue/evidence/linear-elastic-analytical-v1.json
python3 -m atlas.cli evidence catalogue/evidence/linear-elastic-analytical-v1.json --current
python3 -m atlas.cli evidence catalogue/reviews/linear-elastic-source-v1.json --current
```

The first command checks the structural envelope and immutable artifact hashes. `--current` additionally checks the current model definition and recorded source-file hashes. An older valid record can therefore remain historical evidence while being incompatible with current sources. Paths must remain within the repository, and repeated artifact paths are rejected. These are integrity checks, not a re-execution of the numerical comparisons or a scientific endorsement of the outcome field. The named numerical checker owns its report assertions.

The elasticity checker can emit an envelope with `--record PATH`; commit its checker/model/source files first so that `source_commit` identifies them. It refuses an uncommitted change to the recorded source files, verifies the solver's embedded elasticity definition against the local definition, and hashes the executable used. A binary hash is reproducibility evidence, not a build attestation. Record clean-checkout build/test provenance separately when closing BASE-01. Other ongoing website or paper edits in a shared checkout are not included in this scoped check.

Changing an artifact requires a new evidence revision rather than quietly repairing an existing hash. To reproduce a historical report, check out its source commit and run its command. Platform/compiler differences can change the binary hash and floating-point last digits; compare declared numerical tolerances and model/source identity rather than requiring identical binary bytes across platforms.

Current records leave review pending. No independent reviewer has signed the elasticity transcription, and these records do not close REV-01 or the five-model review milestone.
