# Frozen source evolution v1 - archive and replay proposal

Task: ARCH-frozen-source-evolution. Owner: review_sanisand. Date: 2026-10-31.
Scope: actual resolver/test inventory, a standard-library-only source-capsule prototype, and isolated replay of the retained preliminary/fixed generic transport audit. No shared sources, frozen reports, tests or model definitions were edited. No compiled execution, builds, git operations or admission changes.

## Decision

Preserve immutable original documents and source bytes, then **materialize a coherent source closure at original repository-relative paths and run its original verifier in a new isolated Python process**. Keep current-code regression tests separate. Do not teach old reports to accept the current source hash, monkeypatch an already-imported verifier's ROOT, or treat current-code numerical agreement as historical reproduction.

Use the existing `catalogue/source-snapshots/<original-sha>/<original-path>` store and document-bound `source-archive-map.json` for durable source identity. Add an explicit per-study replay manifest describing the coherent execution closure and an exportable source capsule. Git commits remain useful locators, but a public source export containing the capsule/replay closure must work without `.git` or local history. The prototype's JSON/base64 format makes the small demonstration self-contained; production may export deterministic tar plus a pinned manifest or reuse the content-addressed objects. The integrity and closure contracts must remain the same.

## What exists, and what is missing

`atlas/evidence.py:52-112` already implements `checked_receipt(root,document,original_path,expected)`. It verifies the source path/hash pair exists in the original receipt, binds the original receipt's exact bytes through a sibling archive map, and selects a content-addressed snapshot. Missing/corrupt mapped snapshots cannot fall back to live code. `verify_manifest_files` at115-124 verifies flat string-valued file/dependency maps. `tests/test_evidence_archives.py` covers changed documents, wrong pairings, duplicate mappings, missing/corrupt snapshots, escaping paths and sibling document registration. `tests/test_clay2014_path_archive.py` protects a concrete CMake migration. These are integrity mechanisms and should be reused.

They do not change imports, stage expression evaluation, module globals captured with `from atlas.model import ROOT`, or a verifier's direct `sha(ROOT/path)` reads. A receipt can be historically intact while executing it against current Python math silently changes outputs. Conversely, a faithful new common implementation can make a historical direct-pin check fail before any old evidence is reassessed. The replay closure is the missing execution mechanism.

`observed-source-inventory.json` pins16 selected inspected verifier/test/provenance files and lists27 literal references to seven common source paths. It is a bounded actual inventory, not a claimed exhaustive dependency scanner. Dynamic source-pins and branch imports are explicitly outside its automatic discovery.

## Exact affected entrypoints and migration split

| Current entrypoint/resolver | Actual dependency behavior | Minimal migration |
| --- | --- | --- |
| `tests/test_ingestion_packets.py::test_generic_rate_review_remains_bound_to_installed_fix` | Runs old witnesses against current `tools/research_rate_observations.py`, then compares the full JSON including exact source hash to old final result. Any legitimate new auditor version changes that result. | Preserve that original replay in a frozen closure; add a separate current-version behavioral regression asserting the five defects remain fixed. Do not replace the retained hash or old result. |
| `docs/ingestion/barodesy-sand/rate-study-v2/check.py::checked_reference` | Direct `sha(ROOT/name)` on `provenance.json.ancestor_files`; fresh reference replay, then `interpret` imported from current atlas. `test_rate_study.py` invokes current production draft rates. | Capture original verifier, reference/support modules, exact ancestors, model/corpus and original atlas/schema closure. Run original tests in materialized tree. A new trace implementation gets a new current-runtime study, retaining cancellation negatives. |
| `docs/ingestion/hypoplastic-clay-2005/rate-study-v2/check_study.py::assess(repo)` and `test_v2.py` | Adds repo to sys.path, imports production loader/DSL, reports `runtime_pins` from explicit repo paths. A subprocess avoids prior cached module identities. | Bind repo argument to capsule root, preserve exact local corpus/ancestors and runtime; current-model regression may use new runtime, but cannot overwrite original checks/runtime_pins. |
| `tools/research_rate_observations.py::checked_protocol/audit`, `research_rate_parity.py::assess` | Direct `protocol.files` versus ROOT; collector path/hash compared to current tool; wrapper reads exact raw companions. | Replay old original tool+protocol+model+build/observation/raw bundles in closure. New duplicate/layout fix is an additive version/study, not an in-place reassessment presented as old tool. |
| `tools/barodesy2017_integration_study.py`, `barodesy2017_wider_study.py`, `clay2014_path_study.py` | Literal `PINNED_DEPENDENCIES` checked directly against ROOT, including compiler/DSL/tensor/solver, followed by oracle and frozen policy/reference checks. | Preserve their exact tool, reference generators/data, policies and pinned runtime/source closure; use old verifier in replay tree. New engine results remain separate evidence. |
| `tools/clay2014_rate_study.py` / additive `clay2014_rate_assessment.py` | Metadata computes current source pins; supplementary assessor binds original raw bytes. | Archive both collector and additive assessor if both are part of the authorized evidence path; retain original failed CLI report as well as later additive assessment. |
| `tools/gis2024_integration_study.py` | Literal oracle dependency pins, current model/reference paths and dynamic source receipts. | Explicit study-specific closure; do not infer the three literal pins are sufficient runtime/source closure. |
| `atlas.evidence.verify_manifest_files`, `tools/build_evidence.py`, archive tests | Historical hash integrity via existing resolver. Ingestion manifests instead use local nested `{sha256,bytes}` entries or lists. `validate_record` reads its schema from module ROOT even when an alternate record root is passed. | Keep format-specific adapters; do not feed every ingestion manifest through flat-map verifier. Run historical schema validation with archived `atlas`/schemas root rather than patching only its call argument. Web export needs integrity, not an expensive scientific replay. |

Only these actual paths were examined in detail. Before editing shared `tensor.hpp`, enumerate all receipts mentioning its old hash, including dynamically generated metadata and raw build/source receipts. Existing archive maps are a starting point, not proof that every executable replay closure exists.

## Proposed production contract

A new additive replay manifest should bind:

1. Study/replay identity and exact original receipt documents, including negative reports and their original bytes/hashes. The registry, not a command-line caller's replacement pin, is authority for expected hashes.
2. A coherent mapping `original repository-relative path -> original SHA-256 + byte count + archived object path`. Resolve existing historical pins with `checked_receipt` against their original document. Verify all inputs before export, after extraction and after replay. Do not silently use current bytes when a historic object is missing.
3. Explicit trusted Python entrypoint and literal arguments, expected process termination, replay scope, all required data/artifact companions and a frozen assessment policy. "Expected exit1 reproduced" must remain a negative outcome, not be renamed numerical passed.
4. Compiler/DSL/model/structure/schema and transitive local Python imports; independent reference code/data and exact corpus; protocol/receipt/source maps; generated model JSON/header and build settings if the verifier hashes them; original raw response/transport/descriptor and all additive assessors used. Node source belongs in the closure when hashed, even if historical replay does not instantiate Wasm.
5. Interpreter/stdlib and, for compiled reconstruction, toolchain/compiler/libm/Emscripten/flags/platform provenance. Source replay without those reproduces integrity and observed results on a recorded current environment, not bit-identical historical binaries or a completed compiler rebuild.

Two different hashes for one logical import path cannot both be active in one Python tree. Make separate coherent capsules or include the original archive-map layout when its verifier intentionally resolves an older referenced source. Do not choose "latest" or merge conflicting histories heuristically. Dynamic imports and branch-dependent data access require manual closure review plus an isolated replay, not AST scanning alone.

Replay uses a fresh temporary tree, preserved relative paths, cwd at that root and a fresh Python `-I -S -B` process. A tiny bootstrap inserts only that root before stdlib paths and invokes the original script. Remove `PYTHON*`/`ATLAS_*` overrides that would redirect imports/repo discovery; supply explicit `{root}` arguments where the old CLI provides `--repo`. Do not reserialize reports or rewrite old absolute artifact-path strings. Portable archival assessment and optional artifact reopening are different modes, retaining original scope. If private PDFs are optional in an original portable check, keep the recorded source receipt while omitting the PDF; missing mandatory private input blocks that replay scope honestly.

Tracked capsule/source-object bytes make a public checkout portable. A deterministic tar implementation must reject traversal, absolute/duplicate members, symlinks/hardlinks and file/directory collisions before extraction; it must verify exact member hashes rather than trust archive metadata. No tar extractor is implemented in this bounded prototype.

This is a trusted-project-code replay mechanism, **not a security sandbox**. It does not permit executing arbitrary vendor/author code or bypassing native build authorization. Python entrypoints can have side effects; the coordinator must approve the declared source-only entrypoint. It does not claim hermetic dependency discovery or all-platform numerical reproduction.

## Prototype and actual retained evidence

`capsule.py` implements explicit pinned export, self-contained blob integrity, safe/fresh materialization, original relative paths, isolated Python replay and archived-input postchecks. It accepts byte overrides for a historical source only when they match the supplied original pin; production overrides must come from document-bound receipt resolution. It does not search Git, infer dependency closure or update pins. Ingested capsules must themselves be bound by an immutable public manifest. The prototype JSON is not a finalized common schema.

`preliminary-capsule.json` and `fixed-capsule.json` contain the actual preliminary assessor SHA `783002f9a5ac2440b497cda4fb20bc3a95cb6064c25a7733bf25ece0b38050c1` and fixed assessor SHA `691a4dc606d0fb7b7ee0c5bc2816004292676eb50c3a4cd2e09e71634d75312a`, respectively, plus the actual retained five-witness script and explicit ten-file atlas/schema/import closure. Source bytes are the project's public Python/JSON, not private papers or author implementations. The preliminary bytes were preserved privately before the correction and are now included exactly in this public prototype capsule; no Git history is needed.

`demo.py` replays both capsules and verifies the original audit input hash, all five witness identities and vulnerability flags. `demo-results.json` retains five historical defects for the preliminary implementation and zero for the fixed implementation, with capsule-file and stdout hashes. It does not pass a compiled report or claim material validation. Running the old audit successfully means the **old negative findings are reproduced**; it does not mean the old assessor is approved.

`test_capsule.py` has seven tests: archive replay survives a poisoned current source; a missing archived import cannot fall back through ambient PYTHONPATH/current repo; expected exit1 stays exit1; corruption/path/hash/size/collision failures reject; original pin mismatch rejects; source mutation during replay rejects; existing materialization destination rejects. These use only synthetic local Python files.

Reproduce from the installed packet directory:

```sh
python3 -B -m unittest discover -s docs/reviews/frozen-source-evolution-v1 -p test_capsule.py -v
python3 -B docs/reviews/frozen-source-evolution-v1/demo.py
```

The demo output exactly matches retained `demo-results.json` on this interpreter. Seven tests pass. Python/stdlib remain external and are recorded by direct `capsule.py` replay reports; no cross-version bit equality is promised. No native/Wasm code, author program, build or Git operation ran.

## Smallest next implementation

Before changing trace or the generic auditor, the coordinator should choose one actual frozen study (the generic transport audit is already prototyped), register a production replay manifest/source closure under `catalogue/source-snapshots` with immutable document bindings, and install a single current test that invokes the trusted archived replay. Separately retain a current-code behavioral test; future numerical work gets a new identity. Then migrate the sand/clay v2 and affected finite-study closures one at a time, exercising unchanged negatives and absent/corrupt archive failures before shared source edits.

Acceptance gates: exported checkout without `.git` replays; current common source is deliberately changed in a temporary clone without altering old replay; old negative observations remain exact negatives; missing/corrupt closure objects fail instead of current fallback; original document/hash changes fail; no model/threshold/policy mutation; current code still receives independent regression coverage. Build/rebuild authorization is separate and serial, owned by the coordinator. No blanket historical-test skip or hash refresh is acceptable.
