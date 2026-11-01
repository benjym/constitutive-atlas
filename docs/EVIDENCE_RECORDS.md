# Evidence and review records

Evidence supports a named claim about a particular definition. A green build or a valid record does not promote a model automatically.

Current model approval follows [independent agent checklist v1](AGENT_REVIEW_POLICY.md), [agent-review.schema.json](../schemas/agent-review.schema.json) and `python3 -B -m atlas.agent_review RECORD --for-approval`. A completed separate-agent review is sufficient; human scientific signatures and further user sign-off are not prerequisites. The older v0.1 source-review envelopes described below remain historical evidence, not an additional approval gate.

Numerical envelopes in `catalogue/evidence/` follow [evidence.schema.json](../schemas/evidence.schema.json). Each has a stable ID, creation time, source commit, exact model-file SHA-256, automated executor/method, scope, limitations, outcome, reproduction command, hashed report artifacts and hashed relevant source files. The schema forces automated records to declare `independent_review: false`. This does not rule out useful analytical or external-reference checks; it prevents confusing their execution with independent scientific review.

Review records in `catalogue/reviews/` follow [review.schema.json](../schemas/review.schema.json). A pending record names the dossier, model revision, supporting evidence IDs and open questions. A completed record requires a reviewer identity, review date and an explicit independence declaration. Acceptance cannot retain unresolved questions. These legacy fields record an actual review supplied by a reviewer; schema validation cannot authenticate identity or establish that the review happened. Do not manufacture a signature or assign a maintainer without agreement.

Validate a record with:

```sh
python3 -m atlas.cli evidence catalogue/evidence/linear-elastic-analytical-v1.json
python3 -m atlas.cli evidence catalogue/evidence/linear-elastic-analytical-v1.json --current
python3 -m atlas.cli evidence catalogue/reviews/linear-elastic-source-v1.json --current
```

The first command checks the structural envelope and immutable artifact hashes. `--current` additionally checks the current model definition and recorded source-file hashes. An older valid record can therefore remain historical evidence while being incompatible with current sources. Paths must remain within the repository, and repeated artifact paths are rejected. These are integrity checks, not a re-execution of the numerical comparisons or a scientific endorsement of the outcome field. The named numerical checker owns its report assertions.

The elasticity checker can emit an envelope with `--record PATH`; commit its checker/model/source files first so that `source_commit` identifies them. It refuses an uncommitted change to the recorded source files, verifies the solver's embedded elasticity definition against the local definition, and hashes the executable used. A binary hash is reproducibility evidence, not a build attestation. Record clean-checkout build/test provenance separately when closing BASE-01. Other ongoing website or paper edits in a shared checkout are not included in this scoped check.

Changing an artifact requires a new evidence revision rather than quietly repairing an existing hash. To reproduce a historical report, check out its source commit and run its command. Platform/compiler differences can change the binary hash and floating-point last digits; compare declared numerical tolerances and model/source identity rather than requiring identical binary bytes across platforms.

The legacy records leave review pending. They do not close REV-01 or the five-model milestone; a new accepted independent-agent checklist can now close the review requirement without a human signature.

The [plasticity investigation](PLASTICITY_VERIFICATION.md) retains failing comparisons as evidence with `outcome: failed`. Its scalar-root and continuum references use method `analytical-and-scalar-reduction`. A nonzero investigative checker result is not hidden by the green software checks.

The [base sand hypoplasticity dossier](models/hypoplastic-sand-vw96.md) uses method `independent-cartesian-rates-and-rk4`: direct Cartesian source-equation rates and separately refined RK4 paths. The failed initial reference-convergence attempt is retained alongside the expanded passing evidence; neither substitutes for original-paper assessment or independent agent checklist review.

The [IGS draft investigation](models/hypoplastic-sand-igs97.md) retains a failed 303-case report: 295 instantaneous/covariance/rollback checks and four histories pass; four history checks fail reference convergence, and an integrated analytical history solution independently confirms a native small-cycle discrepancy. The associated source review remains pending. Passing software regression checks cover the instantaneous cases and do not establish correct cyclic history integration.

The [IGS v2 correction](models/hypoplastic-sand-igs97.md#endpoint-defect-correction-and-v2-evidence) adds passing evidence for the same 303 cases with unchanged tolerances, after endpoint-defect control and analytical collinear history elimination in the RK4 reference. Full-state noncollinear refinement is retained. Failed v1 artifacts and pending source review remain separate from this numerical result.
