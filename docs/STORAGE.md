# Local artifacts and repository size

Keep executable definitions, source code, schemas, small reference cases and
evidence manifests in version control. Preserve historical receipts and the
exact bytes they identify. Large private sources, datasets, generated websites,
build products and local experiments belong in ignored local storage, not copied
into each new source packet. Existing tracked evidence remains authoritative;
this cleanup does not rewrite Git history or remove its artifacts.

For new investigations, record source/data SHA-256 hashes and reference an
existing immutable artifact when possible. A fresh website qualification still
needs the exact tested package and its manifest, but not independently allocated
copies of every unchanged experiment dataset. Runtime caches are mutable: use a
shared, toolchain-version-specific cache when building serially rather than
freezing caches into evidence. Keep inputs, independent results and the tested
package identity distinct from reproducible intermediate build products.

## Consolidating existing frozen copies

`tools/artifact_store.py` implements a local content-addressed store at
`.local/artifact-store/sha256/`. It finds byte-identical large artifacts and replaces
eligible paths with read-only hard links to a verified canonical object. Ordinary
readers still see regular files at their original paths, with unchanged contents,
lengths and SHA-256 hashes. No custom evidence loader or symlink resolution is
needed. The store and materializations must remain on the same filesystem.

The default scan excludes Git-tracked files, symlinks, existing multiply-linked
files, executables, source-code extensions, artifacts smaller than 64 KiB and
files modified or metadata-changed within two hours. Only explicitly selected
directories are scanned. Select frozen snapshots, not a running build, active
experiment, live server output or mutable cache. Read permissions remain separate
between groups, so private 0600 data does not become publicly readable.

Planning hashes candidate bytes and records original metadata. Apply verifies the
whole plan before mutation, then rechecks each file before atomic replacement.
The receipt records original paths, original modes/timestamps, object bindings and
partial progress if an ordinary error interrupts application. Verify checks every
materialization's object link, read-only permissions and content hash. If a file
changes after planning, prepare a new plan; do not bypass the guard.
Future scans also match newly copied artifacts against existing objects, even
when only one new copy is present. Existing materializations are skipped.

```sh
mkdir -p .local/storage-maintenance/my-cleanup
python3 tools/artifact_store.py plan --scan .local/private-evidence --output .local/storage-maintenance/my-cleanup/plan.json
python3 tools/artifact_store.py apply .local/storage-maintenance/my-cleanup/plan.json --receipt .local/storage-maintenance/my-cleanup/receipt.json
python3 tools/artifact_store.py verify .local/storage-maintenance/my-cleanup/receipt.json
```

This is consolidation, not deletion of unique evidence. Do not remove the object
store while linked evidence exists: links retain the bytes but lose their
canonical registry. A normal byte-copy backup remains valid; backup systems that
preserve hard links retain the space savings. Exporting a site into a standalone
deployment package may materialize normal independent files.

## Editing or rebuilding an archived path

Shared artifacts are immutable. Never use `chmod` or write in place on an object
or one of its links: changing one inode would affect every linked receipt. Detach
the specific path into a private writable copy before making a new revision:

```sh
python3 tools/artifact_store.py detach .local/private-evidence/example/site/experiments/example.json
```

Detaching preserves its bytes, permissions apart from adding owner-write access,
and timestamps, but creates a separate inode. On APFS it uses copy-on-write when
available. The other evidence paths and canonical object remain unchanged.
Detaching intentionally ends that path's binding to its old cleanup receipt;
subsequent scientific changes still require their normal new evidence identity.
For a revised full package, make a fresh writable build rather than overwrite an
archived package.

## What the size measurements mean

`du -sh .` counts allocated files once per hard-linked inode within the traversal.
Separate `du` calls on individual snapshots count the shared files again, so those
figures cannot be summed. APFS clones, volume snapshots and concurrent activity
can make the change in volume free space differ from a `du` reduction.

The local cleanup does not shrink a fresh Git clone: tracked evidence and history
are unchanged. Moving those artifacts to an external archive would additionally
require a durable authorized destination, retrieval/integrity tooling and explicit
migration of consumers. A local ignored object store is not a replacement for a
published scientific archive or an independent backup.

## Applied cleanup — 2 November 2026

The local run consolidated 2,106 untracked archived files into 351 canonical
objects. Every original path, content length and SHA-256 binding was verified.
The before/after `du` measurement fell from 12.424 GiB to 10.775 GiB, a measured
1.649 GiB reduction during concurrent repository activity. The plan contained
2.068 GiB of identical-content duplicate allocations. Do not attribute unrelated
changes in whole-volume free space to this cleanup.

The exact plan, per-path receipt, original file metadata and before/after report
are retained locally under `.local/storage-maintenance/2026-11-02-v1/`. No tracked
evidence bytes, source snapshots, unique research data, paper results, live build
outputs or Git history were removed. Nine focused tool tests pass, including
private-permission preservation, changed-plan rejection, corruption detection,
future-object reuse and independent editing after detach.
