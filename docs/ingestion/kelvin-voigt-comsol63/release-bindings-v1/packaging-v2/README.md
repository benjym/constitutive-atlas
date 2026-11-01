# Portable release-binding audit packaging v2

Publish only the five files in this directory, as enumerated in ARCHIVE.json. Do not publish the loose parent v1 audit files or proposal trees. The complete exact handed-off v1 audit — all 33 original manifest members plus the original manifest itself — is retained byte-for-byte inside audit-v1.tar.gz. The v1 manifest's relative paths are logical paths **inside that archive**, validated there by audit_archive.py; they are not new live-root receipt paths.

This packaging resolves a namespace collision discovered before installation: repository archive-coverage tests recursively discover any loose source-archive-map.json and treat it as an active map in its current directory. Proposal copies therefore belong inside an immutable archive, where their original namespace is preserved. No handed-off v1 bytes, decisions, original failures, source hashes or expected gates were changed or deleted. Local loose copies remain available but are explicitly excluded from publication.

Validate the archive and every original receipt/proposal identity without extraction:

```sh
python3 -B docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1/packaging-v2/audit_archive.py check
python3 -B docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1/packaging-v2/audit_archive.py show-plan
python3 -B docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1/packaging-v2/audit_archive.py show-own-plan
```

For coordinator installation after independent review, export only the 14 baseline and two own-interface proposed maps to a **new temporary directory outside the repository**:

```sh
python3 -B docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1/packaging-v2/audit_archive.py export-proposals --output /private/tmp/atlas-kelvin-reviewed-binding-proposals-v2
```

The output retains scope-v2-planned-sidecars/ and own-interface-planned-sidecars/ prefixes. Installation remains the coordinator's separately reviewed action: verify exact baseline hashes, create the 18 baseline prior-byte snapshots and one prior interface snapshot, then install the 16 intended live sidecars and source delta. This wrapper does not install files into the repository or confer scientific approval. A read-only full reproduction capsule can instead be exported with export-v1 and a new temporary --output directory, then the original archived README commands can be followed there. The archive reader refuses duplicate, unlisted, non-file or unsafe members, mismatched hashes and existing export destinations.

Scope-v2 evidence retains its passing simulation of 14,360 original active pairs. The earlier broad proposals and first failed virtual check remain inside the same exact v1 archive. The original interface runtime-test absolute private/tmp pin remains explicitly nonportable; this packaging does not retarget or rewrite it.
