# Source-linked database download

The normal website builder now adds `atlas.sqlite` and `atlas-database.json` after copying matching generated model metadata and the discovery catalogue. The catalogue offers relative download links suitable for GitHub Pages project paths. The SQLite export reuses `atlas.research.export_database`, including its canonical independent-agent approval validation.

## Public content and identity

The package contains public model definitions, source URL/locator/role records, publications, screening and exact approval/review JSON. The fixed nine-table boundary excludes raw measurement tables. PDFs, original measurement arrays and compiled engines are not bundled. Ordinary-engine membership, approval scope and experimental validation remain separate; a discovery record is not an executable model.

The manifest identifies database SHA-256/size, public counts, ordinary-engine IDs and captured package/source hashes. Packaged model definitions must exactly equal the current ordinary definitions, and the packaged discovery catalogue must equal the current discovery record. Exported definitions, executable membership, source links, approval and review objects are checked before publication. Both catalogue comparisons use the same captured bytes as their hashes; source/package drift rejects publication.

Both files are prepared in temporary storage. Preflight/export validation errors retain previous downloads. On an ordinary manifest replacement failure, the previous database is restored (or the new database removed when none existed). This is exception recovery, not a crash-atomic two-file transaction; a process crash or storage failure during restoration requires rebuilding the output directory before publication. Site deployment should publish the completed directory.

## Reproduce without compiling

From the repository root, generate metadata with `python3 -B -m atlas.cli generate /private/tmp/atlas-db-generated`, copy its `models.json` and `catalogue/manifest.json` as `catalogue.json` into a destination directory, then run:

```sh
python3 -B tools/build_database.py --output /private/tmp/atlas-db-site
python3 -B -m unittest tests.test_database_package
```

The normal `tools/build_web.py` invokes the same packager. See `integration-delta.json` and `proposed-source/` for the exact additive builder hook and catalogue links; concurrent shared-file edits are excluded from that projection. `before.json` binds pre-edit working bytes retained in source snapshots. The production module/tests before the review fixes are preserved in `before-fixes/`; original independent findings remain in `independent-review/initial-findings.json`.

Example queries:

```sql
SELECT id, executable FROM models;
SELECT model_id, url, locator, role FROM sources;
SELECT id, record_json FROM model_approvals;
```

## Qualification scope

`package-results.json` records an actual standalone export using normal generated metadata from the current shared working tree. Counts are an observation, not a release baseline. `test-results.json` records the focused approval/archive/export/packaging suite, including real HTTP downloads under a project path and injected drift/publication failures. No native/Wasm build or compiled material call was made. Full-site build, actual application-browser qualification, clean release, CI and live deployment remain separately owned and are not established by this packet.
