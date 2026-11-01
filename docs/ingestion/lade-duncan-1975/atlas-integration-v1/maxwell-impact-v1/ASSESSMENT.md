# Maxwell source-closure impact assessment

DIAG-lade-maxwell-closure-impact-v1; source/hash assessment by /root/lade_interface_review, 2026-11-02. This is a diagnostic recommendation, not a new accepted Maxwell qualification or permission to edit existing decisions. Only maxwell-impact-v1/ was written. No compiler, build, native/Wasm/material binary, browser or remote action was invoked.

Current Maxwell has no closure drift. All 149 paths and SHA-256 values produced by the current production source_manifest() equal atlas-ci-v2/observations/inputs.json exactly, including the separately versioned implicit-path profile. The current digest is af8a045962d73bef332222ae3b91139a53cd05078b9987444780635ef29bd493, matching both retained qualification and independent build review. The three-member compiled archive, copied qualification and copied review match all three current provisioner constants and provenance member hashes. There is no existing closure mismatch to repair.

The prospective change replaces only cpp/profiles/implicit-path-v1/include/atlas/solver.hpp:

- Current SHA-256: 098e1b926e3eb99545567111415f54d35c08f52e7afbaa796fa23a551fe4a6c0.
- Proposed fused copy: e2e517d9cb5a90383779d4d26eed66284b774d3646d1f74149541589f6ac1026; the proposed bytes are pinned to fused-linear-v1/proposed-native-source/include/atlas/solver.hpp.
- The diff contains two changed physical lines implementing three arithmetic substitutions: matrix elimination a−f·pivot → std::fma(−f,pivot,a), right-hand-side elimination b−f·pivot_rhs → std::fma(−f,pivot_rhs,b), and back-substitution sum−a·x → std::fma(−a,x,sum). Pivoting, thresholds, division, iteration and return behavior are unchanged by this diff.
- Replacing only this file changes the broad Maxwell source manifest to c99402ffe0d84bbb1f61c6521d9d6a240cae0e698fc6432d536d65daeb3456b7. No other current or prospective manifest entry changes. This arithmetic change matters for the implicit profile's numerical qualification, which remains outside this assessment.

## Actual dependency boundary

cmake/maxwell/CMakeLists.txt builds cpp/main.cpp, includes cpp/include plus its generated directory, and links the scalar-function archive established by cmake/AtlasScalarFunctions.cmake. It does not add cpp/profiles/implicit-path-v1 to sources, include paths or link inputs. Shared cpp/include/atlas/solver.hpp remains unchanged; that is the solver reached through main.cpp → schedule.hpp → time.hpp → solver.hpp, and recorded.hpp → linearize.hpp → solver.hpp. Repeated atlas/ header names in the versioned directory do not override the explicit include paths.

The saved native and Wasm actual compile databases each have 13 commands: twelve scalar C translation units and cpp/main.cpp. They equal their retained build-audit command lists. Each backend retains 13 dependency files; all 26 files were read, hashed and copied as metadata under saved-build-metadata/. None refers to cpp/profiles/. Every source dependency under the retained consumer-source root has current root-relative bytes identical to the retained bytes. The saved generated catalogue hash on both backends matches the qualification's catalogue_file_sha256; generated header/catalogue hashes are in dependency-verification.json. Thus this is supported by actual saved compiler dependencies, not only a CMake reading or a statement that Maxwell is a different model.

Compiler scans do not introduce an implicit connection. The Maxwell command is python -B -m atlas.compiler OUTPUT models/research/maxwell. Its CLI explicitly glob-scans only that named directory's *.json, then passes those paths to generate. generate uses all_models() only when explicit model_paths are absent; all_models itself scans top-level models/*.json without recursion. Schema validation reads the chosen schema file. Compiler output includes tensor/checked helpers according to emitted expressions, and its catalogue hash derives from canonical selected models; it never reads or scans cpp/profiles. CMake glob-scans atlas/*.py, schemas/*.json and models/research/maxwell/*.json as generation dependencies, not the unrelated profile. The future profile edit therefore cannot alter normal Maxwell generation under the inspected command.

In contrast, tools/build_maxwell_laboratory.py source_manifest deliberately recursively scans all atlas Python, schema JSON and cpp .cpp/.hpp files, plus scalar sources and explicit model/CMake files. It includes the unrelated profile as provenance. That broad guard will correctly reject the old qualification after the proposed edit, even though no actual Maxwell compilation input changed. Preserve this check.

## Honest reuse path

For precisely this one-file future delta, reusing the existing exact Maxwell artifacts and inherited numerical evidence is technically justified, subject to a new independent impact review and new provenance binding. It would not claim a rebuild from the new broad source closure. The qualification should explicitly say the artifacts were produced from the retained original compiled dependency closure and remain unchanged; only an unused separately versioned profile's repository provenance changed.

There is an existing bounded precedent: dependent-independent-review/profile-provenance-bindings-v2.json accepts an additive noncompiled profile provenance delta, and the retained qualification/build review cite build-local-v2/maxwell/profile-provenance-delta.json. That earlier acceptance covers its exact old bytes, not the proposed FMA change; it cannot be repinned silently or treated as a future approval.

Minimal next action after the exact FMA install:

1. Archive the prior installed solver bytes and all affected binding/installer identities. Recompute the actual broad closure and verify it equals this one-file prospective result, with zero additional drift. If anything else changed, classify that separately before proceeding.
2. Ask a separate agent to assess this exact delta, saved native/Wasm command/dependency proof, unchanged generated model/compiler inputs, artifact hashes and original accepted numerical evidence. Produce a new impact-review identity. Do not have this diagnostic implementation manufacture the reviewer's acceptance.
3. If accepted, create new Maxwell qualification/build-review/provenance records in a new packet identity, preserving the old records byte-for-byte. The new source_manifest_sha256 may be the prospective hash; all artifact/model/catalogue/reference hashes and original five gate outcomes remain inherited from their exact unchanged reviewed evidence, with explicit provenance-only explanation. The new reviewer must actually accept that inheritance. The existing guard's exact source hash, five gates and separate reviewer requirements remain mandatory.
4. Update the selective provisioner to the newly reviewed qualification/review packet and constants through the coordinator's separately owned handoff. The compiled archive can retain the identical three members and archive hash. No need to alter or relax build_maxwell_laboratory.py or omit Maxwell's route. Revalidate restored asset/approval/source guards and required package regressions; actual runtime invocations require a separate coordinator authorization/handoff.

A new native/Wasm numerical campaign is not intrinsically required merely to change provenance of this unreachable profile file while serving identical artifacts and identical Maxwell requests. If independent review cannot establish unchanged actual dependencies/generated outputs, or any shared solver/tensor/scalar/main/model/schema/compiler/CMake/toolchain option/link dependency actually changes, the narrow reuse argument no longer applies. Determine impact, rebuild serially where needed and repeat the affected original native references, Wasm references, transactions, backend parity and four public preset/replay gates under unchanged policies; obtain independent exact-artifact review. A new artifact hash cannot inherit old artifact qualification solely because its source equations look similar.

The source closure should not be narrowed ad hoc to avoid the rejection. A future separate design could distinguish a compiled dependency closure from repository provenance, but that requires a reviewed generic policy and packager change. It is larger than the single-file provenance rebind proposed here.

## Reproduction and limitations

Run from repository root:

```sh
python3 -B docs/ingestion/lade-duncan-1975/atlas-integration-v1/maxwell-impact-v1/check_impact.py
```

The script performs Python source/JSON/hash/archive reads only. It compares current and retained closure maps, computes the prospective in-memory replacement hash/diff without editing production source, verifies retained qualification/review/archive constants, and reads actual saved compile databases/dependency metadata. Reports: closure-comparison.json, prospective-profile-solver.diff, archive-verification.json, dependency-verification.json and source-pins.json. Saved build metadata and SOURCE_FREEZE.json make the inspection auditable. Reproduction of external retained dependency paths requires the original /private/tmp consumer build trees; copied metadata remains available if those trees are later removed.

This assessment does not rerun the original numerical assessor, authenticate an unobserved build, approve the future FMA profile, certify generated outputs from an unexecuted new compiler, or qualify a future package/browser. Current compiler and every broad source input are byte-identical to the old bound closure; the only prospective source difference lies outside both observed Maxwell backend dependency closures. Existing accepted 24 interface pins and the new public-CI source freeze remain unchanged.
