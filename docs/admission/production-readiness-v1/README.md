# Production admission: first reviewed collection

This is the operational closure package for the agreed sequence: review elasticity,
Drucker–Prager and Modified Cam Clay first; prepare barodesy clay 2017 for the next
draft-to-reviewed decision; retain Terra Cotta and SANISAND as distinct follow-ups.
It does not change model status or supply independent scientific review.

## First decision

The proposed first release is a **bounded material-point library and laboratory**:
infinitesimal strain, fixed spatial frame/zero spin, compression-positive Mandel
effective stress, explicit caller-supplied persistent state, and the named verified
paths. It is not a general finite-element material qualification. A host requiring
complete-update tangents, objective finite rotations, poromechanics or physical
preparation must obtain separate evidence for those features.

The three legacy definitions remain byte-identical. Their complete v0.3 crosswalks
explain semantics without migrating the roots owned by another workstream.
Schema migration is a separately identified definition/build change and must be
verified under its own identity; it cannot inherit an old report by renaming it.

## Review order and actual decisions

| Order | Package | Required reviewer judgments | Existing numerical evidence |
| --- | --- | --- | --- |
| 1 | [Elasticity](linear-elastic.md) | Constant-parameter source specialization, Mandel/sign map, effective-stress host interpretation, void bookkeeping and bounded parameter/control scope. | 29 native analytical cases; exact rational stiffness and current Python residual checks are separate. |
| 2 | [Drucker–Prager](drucker-prager.md) | Perfect-plastic uncapped specialization, source scaling, ideal-cone apex, corrected `0 <= Md <= M`, expected tensile-apex failure and rollback scope. | 83-case native guard study plus a separate saved 83-case Wasm replay; retain failed v1 and historical 73-case v2. |
| 3 | [Modified Cam Clay](modified-cam-clay.md) | Printed source conflicts, endpoint stiffness, multiplier normalization, exponential log-hardening/volume, actual-partition replay and initialization limits. | 57 native scalar/tensor cases and refinement; retain the failed unpartitioned v1 comparison. |
| 4 | [Barodesy clay 2017 closure](../../ingestion/barodesy-clay-2017/production-closure-v1/README.md) | Named body-law source selection and zero-spin scope, current-preview versus historical research evidence, preparation and operating limits. | Current preview and separately identified derivative/finite-path studies; do not combine their identities. |

The first three decision sheets identify the exact current definition and pending
review, evidence to inspect, recommended bounded scope and the question to answer.
They do not require another broad numerical campaign before a reviewer can start.
Any reviewer-requested numerical work must name a specific uncovered claim and
freeze a distinct prospective study before execution.

## Admission procedure

1. Run `python3 -B docs/admission/production-readiness-v1/check.py`. This checks
   package/source hashes, exact model/review/evidence bindings and records open
   gates. A successful packet check means the material is intact, not admitted.
2. Agree an independent reviewer; no maintainer is assigned by this package.
   The reviewer copies `decisions-template.json` to a new, separately named review
   output, records identity/independence/date and answers every question with
   evidence locators and rationale. The template and prior pending reviews stay
   unchanged. An AI technical assessment is not an independent scientific signature.
3. For each disagreement, either resolve it in a new source/model/study revision,
   or narrow the supported claim explicitly. Preserve original failures and do not
   loosen observed numerical gates. An omitted experimental claim is not evidence
   of experimental validation.
4. After acceptance, add a canonical exact-definition review using the existing
   review schema, with no unresolved questions inside the accepted scope. Keep
   excluded capabilities in the dossier/release limitations. Pending records and
   all previous reports remain historical records.
5. Freeze the release source/toolchain, exact definitions and declared state/control
   contracts. Run the accepted regression matrix on a traceable serial native build
   and Wasm build, then package/browser checks. Record complete outcomes and resolve
   failures before a reviewed release; current CI alone does not supply scientific
   acceptance or a reusable source-to-binary attestation.
6. Publish a release manifest binding the signed reviews, model hashes, build and
   numerical reports, supported controls/initialization and limitations. Only then
   update model/catalogue wording for that scope. Deployment needs a separate explicit
   instruction under the repository rules.

Experimental prediction is a separate model/material/protocol claim. It needs a
source-supported parameter set and specimen preparation, usable data rights, a
published baseline and a prospectively frozen calibration/evaluation policy. The
library release must not present default examples or matched plot overlays as that
claim. The assembled KFS scientific handoff remains separately unsigned.

## Next additions

- [Terra Cotta](../../ingestion/terracotta-2024/production-closure-v1/README.md): the
  complete carried preparation/hold v1 and passing refinement-v2 already exist.
  Preserve both. Resolve journal/author-code source questions and restricted timed
  integration decisions; do not regenerate the completed reference or claim full 3D.
- [SANISAND-2004](../../ingestion/sanisand-2004/production-closure-v1/README.md): the
  2004 original is available; the exact 1986 loading-process dependency is missing.
  Complete variant, singular initialization, yield-entry and reversal decisions
  before a canonical full model. Existing capacity/tensor/history primitives are
  evidence to reuse, not reasons to launch another generic engine project.

## Verification and current outcome

`work-packages.json` freezes the selected inputs and proposed tasks.
`decisions-template.json` is unsigned. `check.py --require-admitted` deliberately
returns a nonzero status while review/release gates remain open. `test_check.py`
exercises stale identities, damaged evidence and accidental promotion attempts.
The generated `verification.json` records the actual local checks. No compiled
artifact, author code, fit, model promotion or deployment is executed by this package.

The original DP `verify.py` was attempted and rejected the changed live catalogue
manifest before assessment. Its full failure is retained in
`dp-original-live-replay-failure.txt`. The new `replay_dp.py` restores all 460
original source inputs in a temporary context, selecting nine changed dependencies
from exact archived bytes (two recovered from matching Git blobs). It executes the
unchanged saved-JSON assessor and reproduces the original 83-case report byte for
byte. No engine, numerical gate or historical report is changed. Reproduce with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B docs/admission/production-readiness-v1/replay_dp.py
```

`dp-replay-bindings.json` records the original freeze and exact historical sources.
The wrapper supplies the saved-replay argument explicitly; it never loads Wasm or
executes a native binary. This repairs evidence accessibility, not current-build
qualification or scientific acceptance.
