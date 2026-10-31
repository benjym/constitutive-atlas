# Generic rate collection v1 - independent bounded review

Task: AUDIT-generic-rate-collection. Owner: review_sanisand. Date: 2026-10-31.
Scope: source inspection and synthetic Python/ESM-loader witnesses for the additive collector/comparison layer, over unchanged original assessor. No compiled native/Wasm artifact or scientific study was run. No shared code, receipts, model or admission status was changed.

## Reviewed exact inputs

Repository paths below are relative to Constitutive Atlas. Hashes pin the bytes reviewed, not a future edit.

| Input | SHA-256 |
| --- | --- |
| tools/collect_research_rates_wasm.mjs | 69ce09fb1d3ea5fa05c5f75bba6c4f51b532195f7f5ad7f3485a8275b6214d8d |
| tools/research_rate_parity.py | 5d24276ff1a7c281670a378800bd055f9eabd1d872378eab33c97a05487b409c |
| tools/research_rate_observations.py | 691a4dc606d0fb7b7ee0c5bc2816004292676eb50c3a4cd2e09e71634d75312a |
| tests/test_research_rate_collection.py | 48a92bfaf67c38bf60829daf334aa233a2e39102eb68b61182cd85cd9905c640 |

Source authority checked: `atlas/compiler.py` parameter metadata at44, positional binding at65-67, sorted-key catalogue digest at133 and order-preserving descriptor at136; `tests/research_rate_driver.cpp` consumes positional parameter CSV and returns descriptor from that generated model. These reads establish the layout issue below without executing a compiled driver.

## Blocking finding: positional parameter layout not bound

At `research_rate_observations.py:179-181`, descriptors are compared with order-insensitive `same`, then a canonical hash which sorts dictionary keys. The comparison wrapper at `research_rate_parity.py:24-30` delegates to that auditor without adding a layout check. The compiler consumes parameters in dictionary insertion order. Reversing the compiled descriptor's parameter dictionary retains the accepted canonical hash and semantic dict equality, but declares a different positional CSV interpretation.

The ninth independent witness changes only the native raw descriptor's parameter-key order, updates the raw companion hash, and submits both complete raw bundles. The wrapper reports passed. This is not a claim that an observed compiler produced wrong material rates: it shows the evidence gate cannot distinguish two different declared positional layouts. A finite corpus which happens to agree is not a substitute for checking that layout.

Smallest fix: an additive strict descriptor validation in the wrapper (and any authoritative standalone reassessment entry point), checking `list(compiled_model['parameters']) == list(source_model['parameters'])`. Read each descriptor from held raw bytes, rather than a new independently parsed file. State order is already an ordered list and is checked by existing equality. Preserve original assessor bytes/history if that is the milestone's archival contract. Require the mismatch rejected for both backend roles. No compiler, constitutive law or numerical budget change is needed.

## Additional inherited parser limitation

Response JSON parsing at original auditor179 lacks its document-level duplicate-key hook. A raw response containing `"ok":false,"ok":true` is treated as success by last-key-wins parsing and passes the wrapper after its companion hash is rebound. The eighth witness retains this result. Actual generated driver JSON is assembled with unique keys, so this is not a demonstrated generated-output regression or a separate constitutive failure. Nonetheless, stricter raw evidence validation can reject duplicate keys in descriptor/rate JSON before calling the unchanged auditor. Avoid describing current response decoding as duplicate-free strict JSON.

## What the new layer does establish

- Node holds protocol, build receipt, all declared source pins and loader/Wasm artifact bytes; hashes artifacts before import and supplies the held Wasm bytes to the factory. Its final lifetime check runs after all calls. Loader loading still uses the pinned path; this review does not claim an adversarial filesystem sandbox.
- Each CABI function, types, literal four string controls and opaque return string is journaled before any numerical parsing. Constructor/import errors retain an incomplete empty journal; call exceptions retain a null raw plus exception and partial journal. Non-string results are retained then fail. Existing files are not overwritten on a fresh-run check failure.
- Python comparison takes explicit native/Wasm build+observation+raw triples; independently re-audits both and binds assessment identities back to held evidence bytes. It does not accept arbitrary external assessment objects as evidence. The lower-level original `parity` utility alone remains an explicitly pre-audited-object API.
- Overall outcome combines independent numerical gates with parity; two equally wrong backends do not pass. Failed numerical comparison CLI writes JSON then exits1. Matching outputs are not claimed as source or experimental validation.
- Original auditing rejects Boolean numeric aliases, wrong-length or nonfinite output vectors, wrong parser-versus-domain rejection shape and changed literal controls. Finite integer/float JSON spelling differences are harmless. One persistent Node instance services the entire ordered corpus; explicit `recovery_of` cases require identical arguments and identical known-state responses. Corpus authors must actually declare those cases: the collector does not invent recovery coverage.
- Portable reassessment verifies retained receipt/source/raw bindings, not the continued presence or execution of artifact bytes. Node collection does reopen loader/Wasm bytes; the comparison's default build-receipt check does not reopen historic binaries. A successful build receipt is trusted metadata tied to protocol/artifact hashes, not a re-executed build.

Source pin coverage is exactly the protocol's declared file map, plus generic tools held by the wrapper. The generic protocol requires a model pin, but does not prove every possible model/compiler/oracle dependency is pinned. Each real study must freeze its full source/reference/build scope separately. No complete real generic protocol/build receipt was admitted by this audit. The generated descriptor and numerical gates are necessary additional checks, not an attestation of arbitrary external builds.

## Reproducible checks

Existing suite: `python3 -B -m unittest tests.test_research_rate_collection -v` from repo root: eight tests passed. These tests use project-owned synthetic ESM modules and inert bytes labelled synthetic-not-a-wasm-module; they never instantiate compiled Wasm.

Independent packet witnesses:

`python3 -B docs/reviews/generic-rate-collection-v1/witnesses.py --repo /absolute/path/to/constitutive-atlas`

Nine witness groups exactly replay `witness-results.json` at the pinned inputs. The first seven assert accepted/rejected behavior; the last two assert and retain known accepted limitations. `--require-layout-fixed` changes the ninth expectation to rejection for follow-up review of an additive correction; it should fail on the originally reviewed wrapper. Helpers import the pinned existing synthetic fixture class and use temporary files, without mutating retained evidence or live sources.

Coverage includes factory exception/empty partial journal, Boolean output/echo aliases, swapped backend roles, integer/float identity, changed literal controls despite a rebound companion hash, typed parser rejection, conflicting duplicate JSON keys, and reversed compiled parameter layout. The original eight additionally cover call trap, source mutation, non-string/overwrite refusal, pre-import artifact corruption, full raw re-audit, equally wrong backends, and mutation between audits.

## Handoff

Four files: README.md, witnesses.py, witness-results.json, manifest.json. All hashes are local relative file entries. No compiled execution, model integration, source admission or scientific admission. Resolve positional-layout gate before treating this comparison wrapper as authoritative for generic parameter-CSV studies; optional duplicate-key prevalidation should be separately identified. Then freeze exact protocol/source/artifact/acceptance identities before any actual study observations.
