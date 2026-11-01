# Generic predictor change: published release bindings audit v1

AUDIT-implicit-predictor-bindings-v1, `/root/md1997_source`, 2026-11-02. Read-only **d1c3a19409adaa32791c105429a4167e5bac9d9d** audit. Own only this new directory. No existing capability-authored files were rewritten, no root/runtime/map/archive installation occurred, and no build or compiled artifact was executed. Capability acceptance and current release qualification remain separate pending work.

## Exact original and canonical archive

Published `cpp/include/atlas/solver.hpp`: Git blob 723f6925c9aaa0fa00f4f944448629ead9cc5cb1, 20,921 bytes, SHA-256 **b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e**. The existing preserved `../original/solver.hpp` matches these committed bytes. It was read only; this audit did not duplicate or modify it.

Before any authorized root edit, exact canonical old-byte target:

`catalogue/source-snapshots/b094c0f08d1f9ca71af5279c7946259e222c491b0bd97c3c70dbda392bbbe46e/cpp/include/atlas/solver.hpp`

This canonical archive is absent in the published base. Extract with `git show d1c3a19409adaa32791c105429a4167e5bac9d9d:cpp/include/atlas/solver.hpp`, verify the SHA above, then install only under a separately reviewed preservation task. The proposed new standalone fixture/CMake paths are additive and need no old-byte archive; do not edit global CMake or include their synthetic model in the public catalogue as a convenience.

## Reverse pins and sidecar candidates

`audit.py` reuses the unchanged prior bounded Git-blob audit, pins its dependency hash in `consumer-inputs.json`, and sets just the root solver as the seed target. The full 27,812 tracked tree inventory produces 16,547 selected text reads and 8,273 parsed JSON docs. Excluded canonical/nested source snapshots, receipt copies, repeated docs/catalogue contexts and 181 blobs over 2 MB are enumerated in audit.json. JSONL and scripts receive only literal path+hash co-occurrence scanning. No untracked/private scan or massive snapshot copy was performed. These limits preclude claiming every historical custom checker is covered.

Results: 25 direct exact-current-byte receipt documents, 100 direct/reverse structural occurrences, 20 unique candidate canonical old-byte targets (root solver plus 19 existing sidecar versions), 25 candidate sidecar locations, 6 of them not present in the base. Four canonical archives in the candidate closure already exist and were hash-verified; 16 are absent. There are 164 older solver path/hash matches, reported separately and NOT repinned to b094. Older solver revisions are different historical identities.

`archive-plan.json` lists each exact Git source/byte length/SHA/canonical archive and groups proposed document hashes plus entries by sidecar. It is a conservative CANDIDATE closure, not an instruction to mutate all 25 maps. `audit.json` includes JSON locators, entry/document-pin state and separate metadata-only matches. No direct current-base receipt already resolves b094 through its sibling map and canonical archive.

Direct published-current consumers are concentrated in:

- Duncan integration-v2 independent audit/final-bindings; release-v1/v2 source/freezes/allowlists/preflight and saved qualified-NorSand records.
- Lade live-release staged freezes, saved qualified-NorSand records, Maxwell impact/rebind closure and checked pins, and shared-hook preservation checks.
- Maxwell atlas-ci-v2 saved inputs; orthotropic integration-v3 PLAN; common-scalar actual-root/source/install/provenance/profile/dependent-review records.

Full exact paths are retained in the plan; copied nested contexts were deliberately excluded. New maps appear as candidates for Duncan saved qualified-NorSand, Lade saved qualified-NorSand/Maxwell-rebind and independent checked pins, NorSand layout-fix staged context, and orthotropic PLAN. Those are preserved historical or prospective context documents, not implicit authorization to replace present-day qualification.

A changed sidecar can itself be pinned. Preserve its OLD bytes canonically, extend the parent receipt's sibling map for that exact old sidecar SHA, and keep the immutable parent document bytes/hash unchanged. The recursive candidate graph records these dependencies. `checked_receipt` requires the original document actually contain the exact path/hash pair, an exact documents pin and unambiguous canonical archive entry; corrupt/missing archives never fall back to live source. Existing sidecar documents/entries must remain intact when extending a map.

## Dedicated profiles: current runtime versus historical receipts

This published build_web calls EIGHT dedicated packagers, including orthotropic. Do not use the earlier seven-profile integration map as this release's complete surface. Hashes of the inspected exact published packagers, CMake/runtime consumers and registry are in consumer-inputs.json.

| Dedicated surface | Published consumer and solver relationship | Required response to root solver change |
|---|---|---|
| Maxwell | `build_maxwell_laboratory.source_manifest()` hashes cmake/maxwell, scalar sources and ALL current atlas/*.py, cpp/*.cpp/*.hpp and schemas. Root solver is in current closure. Qualification binding includes source_manifest_sha256; separate build-review must match. | NEW native/Wasm current-source qualification plus separate exact build review; old qualified receipt will be stale. Historical source archives preserve old approval evidence, but cannot satisfy current source_manifest. |
| NorSand controlled path | `build_controlled_path_web` current-receipt branch requires exact current cpp/include/atlas/*.hpp plus Python/schema/scalar/source set. Fallback also compares root header hashes against retained target-source-freeze-v2 before accepting old artifacts. | Both routes reject changed root solver unless a fresh current source closure/qualified build and independent build review are supplied. Do not bypass by omitting current receipt or redirecting a live closure through an archive. Broad binding may include headers unused by actual path runtime; preserve gate regardless. |
| Lade–Duncan implicit path | Standalone cmake/implicit-path-v1 includes ONLY `cpp/profiles/implicit-path-v1/include`; its `atlas/solver.hpp` is a separate preserved version. Packager runtime_manifest hashes this profile's main+headers, not root solver. Compiler outputs are also exact-pinned. | Root-only patch does not change its versioned runtime digest or generation inputs. Preserve exact qualified profile assets/review/interface and run existing package checks. Do not copy the generic patch into that versioned profile or infer its numerical behavior changed. |
| J2 material point | CMake uses common cpp/main.cpp and root cpp/include. Packager requires exact model/approval/review and matching generated catalogue, then records copied binary hashes. It does NOT prove whole current source closure from catalogue equality. | Rebuild/requalify the actual current engine under its existing material-point policies if representing current runtime. Retaining old qualified binary is historical runtime use, not evidence patch is qualified for J2. |
| Orthotropic material point | Same common main/root includes; dedicated exact model/catalogue/review plus module/Wasm identity, with no Maxwell-like current whole-source receipt gate. | Preserve existing 121-case/backend acceptance and interface/browser gates. Current-runtime rebuild needs actual rerun; unchanged model/catalogue alone cannot certify root solver patch. |
| Burgers | Common main/root includes (time.hpp includes root solver for shared helpers/types); packager validates exact review/approval/catalogue and copied artifacts. | Do not infer a timed-law effect from implicit phase patch, but preserve timed/default/history/rollback/parity package checks for a current rebuild. A historical retained artifact must remain explicitly identified. |
| SLS | Common main/root includes; exact scientific supporting files are checked by raw live-file hashes; catalogue/artifact identity is separate. No direct root-solver pin exists in this published approval supporting_files list. | Preserve exact scientific evidence and dedicated current software qualification; no blanket source rebinding or claim old pass covers changed binary. |
| Power creep | Common timed main/root includes. Supporting files use raw hashes; exact approved model and dedicated generated catalogue checked before packaging; binary hashes recorded. No direct root-solver pin exists in published supporting_files. | Preserve physical-time source scope and package defaults/history/replay gates. Rebuild qualification must match actual new artifact if current runtime claimed; archive maps do not alter raw live hash assertions. |

Root implicit_step is relevant to common incremental residual engines; physical-time branches use their own integration algorithm even though compilation includes shared solver helpers. This distinction explains likely impact and required evidence, not an exemption from the frozen profile gates.

## False positives and preservation boundaries

Structural JSON pairs do not prove a custom checker calls checked_receipt. Saved source-manifest/qualified-build JSON may be historical immutable evidence: preserve its original solver bytes and record scope, but do not change its expected hash or mark it a qualification of a new binary. A newly constructed CURRENT Maxwell/NorSand receipt must bind NEW actual source/artifact hashes and actual observed gates; archiving b094 cannot make an old current-build binding pass against the new source. Prospective orthotropic PLAN is also not a scientific approval of this patch.

Raw-hash assertion consumers (including some scientific supporting-files loops) do not automatically honor a sibling sidecar. Agent-review validation/review export do support explicit original-document checked_receipt contexts. Before installing any candidate map, classify the exact checker and source root. A metadata-only reference inside source-archive-map.json is not itself a normal receipt to recursively redirect to itself. No script here creates archives/maps or repins receipts.

## Reproduction and next action

```sh
python3 -B docs/investigations/implicit-predictor-constraints-v1/release-bindings-v1/audit.py --output /private/tmp/predictor-release-bindings-replay
```

The script emits structural audit.json; supplied archive-plan.json and consumer classification are derived planning evidence. Static checks verify all 20 source blobs, four existing archives, exact prior public solver copy and immutable original capability manifest. There is no compiled acceptance.

After actual independent capability acceptance, parent must fresh-check latest origin/root drift, select the actual minimal preservation installation and review its reverse sidecars, then freeze and execute the complete then-current ordinary+dedicated release closure. Maxwell/NorSand fresh qualification is a concrete prerequisite under the inspected current packagers; retain failures if any. Additive standalone fixture/CMake files do not justify changing schemas/compiler, current model definitions, versioned implicit profile, or unrelated app surfaces. Remote publication needs its separate authorization.
