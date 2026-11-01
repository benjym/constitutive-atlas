# Require valid database downloads in website packages

The existing standard and supported website package gates now call `validateDatabasePackage` before importing or executing the material engine. Completed uploads must contain `atlas.sqlite` and `atlas-database.json`; the validator checks the fixed database path, MIME, SQLite header, size and SHA-256, exact packaged models/catalogue byte hashes, ordinary-engine membership and metadata-only exclusion flags. It reads only completed package files and needs no source checkout. The ordinary package checks still validate individual definitions, source links, schemas, local assets and Pages project paths.

This is artifact identity checking, not a second SQLite semantic verifier or a tamper-authentication mechanism. The Python packager retains responsibility for integrity/FK checks, exact definition/approval/review content and source provenance. Header-valid synthetic files in Node tests deliberately exercise only this narrower boundary. An attacker able to rewrite every package byte and its manifest is outside this consistency check. No new model or scientific approval is granted.

`test-results.json` binds the 65 passing static Node tests: 24 database tests, 11 standard package tests and 30 supported-policy tests. They reject missing files, corrupt database bytes, wrong header/hash/size/path/version/MIME, stale packaged model/discovery bytes, duplicate/different membership and changed exclusion declarations. Existing source/project-route/default-policy checks still run. No material engine is imported by these tests.

`clean-snapshot-results.json` records successful validation of an actual SQLite export from a clean archive of committed revision c88f307c. Normal code generation and the ordinary database CLI succeeded there without compilation. It contains 18 definitions and twelve ordinary engine models, distinct from the newer shared working-tree observation in the previous packaging packet. Temporary paths are observation receipts, not permanent artifact storage; reproduce by archiving that commit, generating metadata and running `tools/build_database.py`, then invoking the new validator against its output.

`before.json` binds exact pre-edit package tool/test bytes retained in content-addressed source snapshots. Historical Burgers/OCC freezes that name those bytes are preserved; their current-source checks are not silently requalified by this change. New package qualification must use the new gate and fresh assets. Independent review lives under `independent-review/`. Full website packaging, application-browser runs, CI and deployment remain separately owned.

Run from the repository root:

```sh
node --test tests/test_database_download_gate.mjs tests/test_web_package.mjs tests/test_supported_package.mjs
```
