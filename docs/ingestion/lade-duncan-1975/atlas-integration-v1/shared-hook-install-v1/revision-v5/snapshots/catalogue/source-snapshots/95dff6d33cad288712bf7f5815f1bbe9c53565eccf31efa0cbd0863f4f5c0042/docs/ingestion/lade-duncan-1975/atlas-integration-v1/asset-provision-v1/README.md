# Qualified implicit-path asset provisioner — source implementation

CI-lade-qualified-assets-v1; implementation by /root/lade_interface_review. This new implementation requires separate source review. No compiled/material/browser calls or builds were made, and no actual archive, INDEX, qualification or accepted decision was created by this task.

After qualification, independent source review and exact E5 integration:

```sh
python3 -B tools/provision_implicit_path_assets.py
python3 -B tools/provision_implicit_path_assets.py --output PATH_TO_NEW_BUILD_DIRECTORY
```

Default destination is build-implicit-path-wasm. Existing paths and symlinks are rejected. Five verified asset bytes are written only into a temporary sibling build stage. The existing tools.build_implicit_path_laboratory.bundle guard must succeed on that stage before a final destination check and rename. It checks model/source/runtime/artifact/qualification/separate-review/interface bindings without running material code. A guard failure cleans the temporary stage and leaves the intended destination absent. Restoring these assets is not a new qualification or an actual browser pass.

The only accepted future index path is docs/ingestion/lade-duncan-1975/atlas-integration-v1/asset-provision-v1/INDEX.json; its archive path must be docs/ingestion/lade-duncan-1975/atlas-integration-v1/asset-provision-v1/compiled-assets-v1.tar.gz. The coordinator supplies these actual files after the scientific handoff. The provisioner never writes them.

INDEX has exactly these fields:

```text
status: "passed"
model: "lade-duncan-1975-midpoint-elastic-eq19-gap-v4"
archive: { path: the fixed root-relative archive path above, sha256: actual archive SHA-256 }
files: {
  "lade-domain.mjs": actual member SHA-256,
  "lade-domain.wasm": actual member SHA-256,
  "generated/models.json": actual member SHA-256,
  "implicit-path-qualification.json": actual member SHA-256,
  "build-review.json": actual member SHA-256
}
```

All hashes must be lowercase 64-character hex strings. The fixed canonical E5 record is catalogue/agent-reviews/lade-duncan-1975-midpoint-elastic-eq19-gap-v4-agent-v1.json. It must be currently accepted by validate_review(for_approval=True), bind the exact model identity, explicitly list INDEX and archive in artifacts, and generate the sole approved registry entry for this model. No missing/pending E5 or fabricated local qualification can authorize restoration. The standard validator necessarily reads artifact bytes to check E5 hashes, including the archive. The provisioner itself does not directly load or parse the archive until that validation, exact registry comparison and explicit index/archive pins have passed; it then independently hashes the live index/archive bytes.

The gzip tar must contain exactly five ordinary regular files, named exactly as files above. Do not include generated/ directory entries, symlinks, hardlinks, sparse files, PAX override metadata, duplicate members or extra members. No filesystem extraction API is used. Each member is limited to 16 MiB, and both compressed and decompressed archive envelopes are bounded at 81 MiB. Duplicate JSON keys are rejected. Concatenated tar data is scanned rather than silently ignored at the first zero end marker.

Pure reproduction:

```sh
python3 -B docs/ingestion/lade-duncan-1975/atlas-integration-v1/asset-provision-v1/test_provision.py
```

All 22 tests pass. They use synthetic nonexecutable byte strings, gzip/tar construction and mocked E5/package guards. Coverage includes regular success; duplicate/extra/absolute/traversal/missing members; symbolic/hard links; declared oversize; member hash mismatch; extra hash fields; concatenated tar; decompression bound; existing directory and dangling symlink refusal; missing E5; exact explicit pins; registry mismatch; wrong archive path; staging before package guard; and cleanup on rejected guard. Synthetic approvals and successful mocked stages stay inside temporary test directories and are removed; they are not scientific records or actual restored engine artifacts.

source-pins.json binds the reviewed shared dependencies read by this implementation. SOURCE_FREEZE.json binds this new tool, test, report and documentation, excluding its own self-hash. Existing accepted 24 interface pins and public-CI source freeze remain unchanged. Smallest next action: separate source review of these exact files, then coordinator creation of the actual qualified archive/index and E5 binding before authorized real restoration/package checks.
