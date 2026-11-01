# Published-base reverse binding audit v1

Task AUDIT-md1997-release-bindings-v1, specialist `/root/md1997_source`, 2026-11-02. Read-only published base **d1c3a19409adaa32791c105429a4167e5bac9d9d**. No working-tree bytes were used as source evidence, no shared files/maps were edited, no archives installed, and no compiled artifacts or builds executed. This is prospective preservation evidence, not permission to mutate every candidate map.

`audit.py` reads `git ls-tree -rlz` and selected committed blobs via `git cat-file --batch`. It inventories all 27,812 tracked blobs, scans 16,547 text blobs and parses 8,273 JSON documents. Canonical source-snapshots, nested source/receipt copies and repeated docs/catalogue contexts are excluded explicitly. 181 blobs over 2MB are omitted (including numerical raw arrays and some inventories), with every skipped path/reason recorded in `audit.json`. JSONL and other text receive path+hash co-occurrence matching only. There is no scan of the untracked workspace or private sources, no broad snapshot copy and no claim of complete unbounded dependency discovery.

## Findings

Nine intended paths have exact current-base structural path/SHA pins; current README.md, ROADMAP.md and docs/STATUS.md have none within this bounded scan. Their exact base hashes are still recorded, but preserving them is not required merely because older revisions have historical pins. The board IMPLEMENTATION_PLAN.md DOES have an exact current pin in the orthotropic integration-v3 PLAN.

| Base path | SHA-256 | Direct matching documents |
|---|---|---:|
| catalogue/manifest.json | 1115629127619e5562a84156fcaac5b0de2645ef00c3b732dc29f0d0658ff8d7 | 2 |
| catalogue/approved-models.json | 40f7f438c00d684e22c1b7949679ecf121ebc46fa8e4049d8e87365f3de08694 | 2 |
| catalogue/laboratory-package-policy.json | f0e242cfd9592ab3bf94ab1af16517a347a4bfcdded6fde24d84c73656297094 | 20 |
| catalogue/laboratory-profile-policy.json | 1c1d67d4dad525db721e47f17a1593292bb69e13d53a360ddf6e2be33bbc6e6e | 19 |
| tests/test_solver.cpp | 3407c01bfdb6ca511a26a41bf43384fca8b3ed254d484b84d616a0a44aebf71c | 10 |
| tests/test_recorded.cpp | f38f45ff4190f3a585aeecc2e6670b4f02c3b4ad035d8015c6e0076dadc4d9f9 | 10 |
| tools/check_native_fixture_contracts.py | 2ec42239c58d823d7d0575f57918b07451186fc4f46ef44aacf4d9338fa34609 | 18 |
| .github/workflows/verify.yml | 8bd698676f10974336bbd9093b171a95226715f931d487f65478c9f996a39db9 | 2 |
| IMPLEMENTATION_PLAN.md | d95b3ecd3820be4ce5a8e62325c308ad1386635a751e7b05efbd702640d850c8 | 1 |

Manifest, approval registry and workflow are pinned in `docs/ingestion/orthotropic-ogs/integration-v3/PLAN.json` and `integration-review-v3/prospective-source-check.json`; board is pinned in that PLAN. These are prospective/context identities, not automatically active runtime receipts. Preserve original bytes and do not rewrite their expected hashes. Any subsequent orthotropic study needs its own current integration identity.

Policy/native-fixture pins are concentrated in Duncan integration/release receipts, common-scalar source freezes, Lade actual-package/live-release freezes and shared-hook preservation checks. Exact document paths, JSON locators, hashes and sidecar states are in `archive-plan.json` and `audit.json`. The older-target-pin list (1,513 matches) is separate: older expected bytes must remain older bytes, not be rebound to this published base. Existing legacy archives/maps should be left untouched unless the exact old-byte resolver needs an extension.

## Canonical preservation and reverse closure

For an actually changed, hash-bound original path P with old SHA H, the only canonical archive location accepted by `atlas.evidence.checked_receipt` is `catalogue/source-snapshots/H/P`. Capture exact bytes with `git show d1c3a19409adaa32791c105429a4167e5bac9d9d:P`, check SHA=H before installing, and retain original receipt document bytes. No archives were copied by this audit.

`archive-plan.json` contains 30 unique old-byte source targets across direct files and prospective existing-map reverse closure; four canonical archives already exist and were hash-verified against the expected bytes. The remaining 26 do not exist in this base. These counts are a conservative candidate closure, not a minimum approved mutation set. Each entry names the exact Git source, old SHA, byte length and canonical path.

The structural walk found 176 direct/reverse binding occurrences and 24 candidate sidecar locations. The 36 prospective paths include 12 seed paths (even unchanged/unbound prose) and 24 existing/new sidecars. Three candidate sidecars do not exist in the base. Each candidate map groups exact immutable documents→document SHA plus original_path/SHA/archived_path entries. If extending an existing map, its OLD bytes may themselves be pinned by another receipt: archive that prior map canonically and resolve the parent receipt's sidecar first. Do not recompute the historical parent receipt hash or replace its expected sidecar hash. Sidecar metadata references are marked separately and are not recursively treated as ordinary receipt documents.

Do NOT install this entire candidate set blindly:

- `catalogue/laboratory-profile-policy.json` is an authoritative LIVE consumer of the supported policy. Its current supported_policy hash must bind the NEW prospective current-model policy; a root `catalogue/source-archive-map.json` would not change that raw policy validation. Preserve the old profile-policy bytes for historical readers instead. The root candidate map is an intentional structural false positive, not a requested edit.
- Generic `checked_receipt` resolves only a path/hash actually present in an unchanged JSON document. Its sibling map must have version immutable-source-archive-map-0.1, exact `documents[document_path]` SHA, and one unambiguous original_path/SHA→canonical archived_path entry. A changed/missing archive must fail; no fallback to live bytes is permitted.
- Agent-review validation and review export support explicitly bound checked_receipt contexts. Custom proof scripts, package freezes and context records may read hashes directly or resolve against their own original source root. Adding a sibling sidecar does not make a raw-hash consumer use it. Inspect each relevant checker before choosing a preservation installation or new study.
- Existing copied/isolated contexts were deliberately excluded. They must not be recursively republished or edited to mirror live additions. This audit does not certify every custom historical checker; a fresh current-base drift/resolver preflight remains the coordinator's next step.

## Reproduction and next action

Run from repository root, writing only a new audit output path:

```sh
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/release-bindings-v1/audit.py --output /private/tmp/md1997-release-audit-replay
```

The script regenerates structural `audit.json`; `archive-plan.json` is the supplied derived, consumer-classification plan and includes verified existing archive hashes. `static-checks.json` records source-Git hash checks; `manifest.json` pins all submitted packet files. No numerical or browser check is implied.

After E5, coordinator should recheck actual current bytes against this exact-base inventory, choose only files truly needing edits, preserve those exact originals and required reverse sidecars under a separately reviewed install identity, then freeze a fresh complete current ordinary+dedicated-profile release policy before observing integration. Additive MD model/dossier/review files need no old-byte archive. No app/compiler/schema/runtime change is planned or justified by this audit. Native-test/catalogue count updates and workflow additions must preserve unrelated current model/profile gates. Remote publication remains a separate authorization step.
