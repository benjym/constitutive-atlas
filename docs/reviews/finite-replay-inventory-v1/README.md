# Finite verifier replay inventory

Read-only inventory, 2026-10-31. Repository: `/Users/bmar5496/code/constitutive-atlas`. No builds, compiled execution, scientific reassessment, shared edits or git operations performed. File reads, Python JSON/hash inspection and `checked_receipt` resolution only. The coordinator's concurrent source-replay additions were included at final inspection.

## Decision

Before changing `cpp/include/atlas/tensor.hpp`, preserve four finite Python verifier contexts: Barodesy isotropic, Barodesy wider paths, clay2014 original failed paths, and clay2014 controlled-resolution follow-up. Their original Python tools hash live source paths directly, so adding a source-archive-map does **not** preserve those executions. Small trusted runtime capsules using the existing `atlas.source_replay` runner are the coherent solution; no binaries are required. Capsule size can be reduced by reusing content-addressed source bytes, but each study keeps its original identity, policy and result.

The current tensor hash is `62a7456ed71910033b165df6479b52cd416425614d5aa354f13501228c794a08`. This is a source-identity dependency in these Python audits; Python does not execute that C++ header. Replaying the original Python audit preserves historical numerical assessment and corruption tests, not compatibility of the changed C++ implementation.

## Outstanding closures, in order

All paths below are repo-relative. Commands run from repository root and are **proposed reproductions, not executed in this inventory**. They execute Python reference/audit code over retained data, never compiled artifacts.

### 1. Barodesy2017 isotropic finite paths

Direct breaker: `tools/barodesy2017_integration_study.py:39–40`, `checked_reference()` loops over `PINNED_DEPENDENCIES` and computes `sha(ROOT/path)`. `verify()` invokes it. Metadata retains those pins.

Original tests to preserve:

```sh
python3 -B -m unittest discover -s tests -p 'test_barodesy2017_integration_study.py' -v
python3 -B -m unittest discover -s tests -p 'test_barodesy2017_finite_diagnostics.py' -v
python3 -B -m unittest discover -s tests -p 'test_barodesy2017_integration_evidence.py' -v
```

Smallest coherent closure: those tests; original study tool, `tools/barodesy2017_transport.py`, `tools/barodesy2017_isotropic_reference.py`, `tools/reference_barodesy2017.py`; imported Atlas Python modules and model schema; exact research model/checklist and every literal dependency pin; complete `catalogue/investigations/barodesy2017-integration-v1/` retained JSON/JSONL and registered original receipt bytes. Include the actual public model definitions used by `all_models()` so the public-exclusion test remains meaningful. Include package `__init__.py` files. Do not populate binary paths.

Acceptance: original scalar reference replay, 45 trajectories / 459 chained calls per backend, 466 opaque transport rows per backend, parity and corruption checks, original admission exclusions. `build-receipt.json` binary hashes are compared as historical values; no artifacts need reopening.

Existing `source-archive-map.json` covers old workflow, CMake, ROADMAP and catalogue manifest only. Its `documents` register build-receipt and manifest; no tensor entry. Raw `native.json` and `wasm.json` are not registered there. Calling `checked_receipt` against these unregistered raw documents raises the generic document-change error; this is a missing document registration, **not evidence that their bytes changed**.

### 2. Barodesy2017 wider finite paths

Direct breaker: `tools/barodesy2017_wider_study.py:38–40`, same live-path dependency loop. `verify`, metadata and parity/reference checks reach it.

```sh
python3 -B -m unittest discover -s tests -p 'test_barodesy2017_wider_study.py' -v
python3 -B -m unittest discover -s tests -p 'test_barodesy2017_wider_parity_review.py' -v
python3 -B -m unittest discover -s tests -p 'test_barodesy2017_wider_evidence.py' -v
```

Closure: original tests (parity review imports the synthetic test fixture); study tool; caller-point, wider-path, Cartesian and isotropic reference modules; common Atlas imports/model schema; exact model and all literal source pins; wider caller-reference protocol/reference; complete `catalogue/investigations/barodesy2017-wider-integration-v1/` retained reports, JSONL, preobservation/assessment/manifest. Preserve 48 trajectories / 576 calls and 583 raw rows per backend, all caller-point reference comparisons and original exclusions. There is no source-archive-map in this packet at inspection.

### 3. Clay2014 original finite paths: preserve the negative

Direct breaker: `tools/clay2014_path_study.py:48`, live-path `PINNED_DEPENDENCIES` checks before fresh reference replay. `tools/diagnose_clay2014_paths.py` reaches the same checker, pins original reports/journals and reconstructs the original failure.

```sh
python3 -B -m unittest discover -s tests -p 'test_clay2014_path_study.py' -v
python3 -B -m unittest discover -s tests -p 'test_clay2014_path_raw_parity.py' -v
python3 -B -m unittest discover -s tests -p 'test_clay2014_path_negative_diagnosis.py' -v
```

Closure: those tests (raw-parity test imports/loads the synthetic test file), original study and diagnosis tools, `tools/clay2014_path_reference.py`, `tools/reference_clay2014_cartesian.py`; common Atlas imports/schema, research definition and all source pins; path-reference and path-design packets; full original `clay2014-paths-v1` reports/journals, source-freeze/preobservations, original negative assessments and negative-diagnosis receipts. No `--check-artifacts` operation. Local-artifact checks are outside portable scope.

Acceptance must retain original `failed` outcome and `global refinement unresolved at physical endpoint: stress`, including per-physical-endpoint refinement gates, while retaining passed backend parity/transport facts. Do not replace it with the later controlled study. No source-archive-map exists here; source-migration-inventory records earlier rates/CMake migration, not tensor protection for this finite study.

### 4. Clay2014 controlled-resolution follow-up

Direct breaker: `tools/clay2014_controlled_study.py:30–34`, `frozen_inputs()` directly hashes every `collection-freeze.json.files` entry, including current tensor. It imports the original path transport module; that import alone is not the immediate breaker, but the freeze loop is.

```sh
python3 -B -m unittest discover -s tests -p 'test_clay2014_controlled_study.py' -v
python3 -B -m unittest discover -s tests -p 'test_clay2014_controlled_evidence.py' -v
```

Closure: original two tests; controlled study/reference; original path study and Cartesian/path references; common Atlas imports/schema; all collection-freeze files; full `clay2014-controlled-resolution-v1/` protocol/reference freezes, reports/journals/assessments/parity/execution receipt/manifest; original failed paths manifest needed by explicit negative-preservation assertion. Preserve passed controlled outcome, 315 compared points per backend, all endpoint/refinement checks, zero retained parity difference and `original_failed_study_replaced=false`. No archive map exists here. Keep its closure distinct from the failed original study even if archived bytes are shared.

## Combined capsule option

One compressed source-only capsule can coherently cover the four finite families: select the eleven original test modules listed above and run them as four explicitly labelled groups in one isolated tree. Keep per-family expected outcomes, counts and source bindings; do not collapse the failed original clay study into a single overall numerical pass. The original four study directories total approximately 26 MB of retained data; compression/content reuse can avoid repeating base64 JSONL without changing decoded bytes. Bind all referenced map documents and only their exact archived snapshot targets, plus dependencies and imported package/schema files. The registry must bind original manifests and every source entry their `files`/`dependencies` declare, not only raw data.

`all_models()` is exactly `sorted((ROOT/'models').glob('*.json'))`, followed by model loading (`atlas/model.py:230`). It does **not** fetch other model manifests. Preserve these five public definition files for its exclusion assertion: `models/drucker-prager.json`, `models/hypoplastic-sand-igs97.json`, `models/hypoplastic-sand-vw96.json`, `models/linear-elastic.json`, `models/modified-cam-clay.json`. No unrelated research directories need discovery. Additional models are loaded only at explicit research paths already listed above.

## Source closure mechanics

Common imported Python dependency chain for the first four families: `atlas/model.py`, `dsl.py`, `scalar_math.py`, `structure.py`, `symmetric_expm.py` and package initializers. Tests using evidence helpers additionally require `atlas/evidence.py` and its imports. Model loading requires the original schema. Literal pins include C++/compiler/metadata files that are hashed but not executed; include their exact bytes too. Merely copying imported modules omits these required hash-only dependencies.

Use an isolated root containing original relative paths; derive `atlas.model.ROOT` from that archived tree. Bind immutable receipt fields to capsule source entries through registry `source_bindings`, and bind tests/adapter/complete reference/report bytes too. Retain original tools unmodified. Pin exact expected output/exit and separately preserve test-count/result assertions. No local git history, binary, Wasm loader execution or current-model substitution should be necessary. An additive trusted wrapper may run several original test modules in one archived interpreter and summarize deterministic counters; it must not bypass their assertions.

## Already handled or identity-only cases

- **Sand prospective mapping audit is now closed:** `tests/test_ingestion_packets.py::test_sand_prospective_mapping_review` now dispatches `catalogue/source-replays/sand-prospective-v1/registry.json`, replay id `sand-prospective`, asserting eight original mutation groups. Original `docs/ingestion/barodesy-sand/compiled-plan-review-v1/audit.py` directly checks protocol.files (including tensor) and runs the original source-v2 reference in a Python subprocess. Original `test_audit.py:8` defaults to a machine-specific ROOT; trusted archived adapter must set `ATLAS_REVIEW_REPO` inside execution and preserve subprocess PYTHONPATH. The installed registry/capsule handles this; do not duplicate or change original audit bytes. Root also reports compiled-negative closure committed as `997f876`; this inventory does not re-audit it.
- **Clay2013 isotropic/nonisotropic and GIS2024 finite manifests:** their source-archive maps already resolve tensor `d964ff6e2e46f81e465533f2b517c3aabef7df42de4ed2b9907cc5e4448c6a1e`. Their current retained numerical tools do not enforce live current tensor hash: clay2013 nonisotropic pins only independent reference scripts; GIS integration pins reference scripts. Existing map + `checked_receipt` suffices for the tensor identity portion. Future Python/DSL changes still warrant original runtime capsules, but tensor-only evolution does not create the direct failure identified above. Avoid blanket `test_clay2013_engine.py`: native tests may execute a present local binary.
- **Clay2014 midpoint diagnostic** (`tools/clay2014_midpoint_diagnostic.py` and test) is independent stdlib-only retained-data analysis, pinning original reports/reference, not tensor. It needs original data preserved, not a tensor runtime capsule.
- **Terra Cotta creep:** verifier imports model/schedule/initialization but does not pin tensor directly. Its custom manifest is not the flat `verify_manifest_files` shape; no generic map claim made here. Artifact-reopen CLI is outside this portable source-only inventory.
- Barodesy runtime/hydro-AD and checked-log1p operator receipts also pin current tensor; they are outside finite-path scope and should not be mistaken for coverage from these four closures.

**When a map alone suffices:** an identity-only check routed through `atlas.evidence.checked_receipt`/`verify_manifest_files` can preserve old tensor bytes by adding the exact old object and a document-bound mapping. Register every actual receipt document that is resolved; mapping another manifest does not implicitly authorize raw reports. This validates identity only. It does not redirect literal `sha(ROOT/path)` loops or preserve the imported Python semantics of numerical re-audits. Those require the original runtime closure, not a weakened live verifier.

## Reproduction without compiled execution

Installed prospective audit replay (Python-only):

```sh
python3 -B -m atlas.source_replay sand-prospective --registry catalogue/source-replays/sand-prospective-v1/registry.json
```

Identity-only receipt example; checks archive resolution, not a numerical reference:

```sh
python3 -B - <<'PY'
from pathlib import Path
import json
from atlas.evidence import checked_receipt
root=Path.cwd()
name='catalogue/investigations/clay2013-integration-v1/manifest.json'
receipt=json.loads((root/name).read_text())
path='cpp/include/atlas/tensor.hpp'
print(checked_receipt(root,name,path,receipt['files'][path]))
PY
```

Before evolving tensor, run existing selected current tests once, freeze four original runtime contexts, replay each in an artifact-free temporary root, then verify deliberate live tensor-byte mismatch leaves original replay working while direct original live checks reject it. That mutation belongs in temporary test fixtures, never in retained receipts or the shared tree. Compare original expected failures and exact source/report bindings; no scientific rerun is claimed.
