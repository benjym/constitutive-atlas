# Qualified implicit-path asset provisioner — source implementation

CI-lade-qualified-assets-v1; implementation by /root/lade_interface_review. This new implementation requires separate source review. No compiled/material/browser calls or builds were made, and no actual archive, INDEX, qualification or accepted decision was created by this task.

After qualification, independent source review and exact E5 integration:

```sh
python3 -B tools/provision_implicit_path_assets.py
python3 -B tools/provision_implicit_path_assets.py --output PATH_TO_NEW_BUILD_DIRECTORY
```

Default destination is build-implicit-path-wasm. Existing paths and symlinks are rejected. Five verified asset bytes are written only into a temporary sibling build stage. The existing tools.build_implicit_path_laboratory.bundle guard must succeed on that stage before an exclusive destination mkdir reservation. Verified files are then installed with directory-relative O_EXCL/O_NOFOLLOW writes into the owned reservation. This supports macOS/Linux POSIX directory file descriptors and is not an atomic whole-directory publication. It cannot replace a directory that appears before reservation. It checks model/source/runtime/artifact/qualification/separate-review/interface bindings without running material code. A guard failure cleans the temporary stage and leaves the intended destination absent. Installation failure cleans only matching-inode files created by this helper and empty owned directories; externally added/replaced files are retained. A crash may leave a partial reserved directory that a later invocation refuses to replace. Restoring these assets is not a new qualification or an actual browser pass.

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

The gzip tar must contain exactly five ordinary regular files, named exactly as files above. Do not include generated/ directory entries, symlinks, hardlinks, sparse files, PAX override metadata, duplicate members or extra members. No filesystem extraction API is used. Each member is limited to 16 MiB, and both compressed and decompressed archive envelopes are bounded at 81 MiB. Duplicate JSON keys are rejected. Every physical header is inspected as strict USTAR before a single-header TarInfo checksum/name parse. GNU extended-name/link metadata, PAX and other extension records are rejected before semantic iteration could consume them. After the first zero end marker only bounded zero padding is accepted; concatenated tar data is rejected.

Pure reproduction:

```sh
python3 -B docs/ingestion/lade-duncan-1975/atlas-integration-v1/asset-provision-v1/test_provision.py
```

All 27 tests pass. They use synthetic nonexecutable byte strings, gzip/tar construction and mocked E5/package guards. Coverage includes regular success; duplicate/extra/absolute/traversal/missing members; symbolic/hard links; declared oversize; member hash mismatch; extra hash fields; concatenated tar; decompression bound; existing directory and dangling symlink refusal; missing E5; exact explicit pins; registry mismatch; wrong archive path; staging before package guard; cleanup on rejected guard; both synthetic and the exact independent-review GNU longname witness; concurrent empty-directory reservation refusal; and partial cleanup preserving externally added/replaced content. Synthetic approvals and successful mocked stages stay inside temporary test directories and are removed; they are not scientific records or actual restored engine artifacts.

The initial source-pins.json and SOURCE_FREEZE.json remain unchanged. Their exact original tool/test/report/documentation bytes are retained under superseded-v1/ and indexed by preservation-v1.json. POLICY-v2.json and SOURCE_FREEZE-v2.json bind the corrected current source, tests, source witnesses, result and documentation; sourcefreeze excludes its own self-hash. Existing accepted 24 interface pins and public-CI source freeze remain unchanged. Smallest next action: separate source review of these exact files, then coordinator creation of the actual qualified archive/index and E5 binding before authorized real restoration/package checks.

The independent initial review found that tarfile semantic iteration hid a GNU longname physical header, and that check-then-rename could replace a newly appeared empty destination. These are preserved findings, not observed real-asset failures. The corrected code rejects the original reviewer witness and uses an honest exclusive reservation transaction without claiming atomic directory publication. A new independent exact-source review remains required before actual provisioning.
