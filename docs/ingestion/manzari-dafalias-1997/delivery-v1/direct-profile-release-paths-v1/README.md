# Concrete repository release paths

Copied the exact three restored, independently source-proven compatibility engines to the candidate `web/engines/current17-compatible/{norsand,maxwell,interface2016}/`. All29 files/2,833,685 bytes equal their staged inputs. No engine was built or executed. Original qualification/review and compatibility marker bytes remain exact.

Only `tools/build_web.py` defaults and the existing `.github/workflows/pages.yml` three explicit arguments changed. Both changes reverse byte-for-byte by replacing the three paths back. All other defaults, commands, gates and workflow settings remain unchanged. The helper/builders/bindings/decisions were not edited. `asset-map.json` records every copied file hash/size; before/proposed/diffs record both text changes. These are proposed release changes awaiting independent review, not new scientific/browser/CI approval.

The CI owner must apply the same three substitutions to both existing packaging commands in qualification.yml (currently lines486 and703). This task did not edit that file:

- controlled-path: docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/norsand/engine → web/engines/current17-compatible/norsand
- Maxwell: docs/ingestion/vibe-2026/maxwell-refresh-v1/execution-v1/engine → web/engines/current17-compatible/maxwell
- Interface: docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine → web/engines/current17-compatible/interface2016

The fixed helper data prerequisites (v1 bindings, proof manifest, genuine source review and genuine implementation acceptance) must also be included in the eventual release source; no new decisions are authored or copied here. Raw historical absolute paths inside receipts remain provenance, while operational assets now have repository-relative paths. No /tmp/private archive is needed by packaging after those exact files and accepted code/data are retained.

Checks: exact source/destination file-map equality,29 hashes/sizes; reverse equality for both text changes; Python syntax. No failures, previews, large archives or background resources. New candidate engine directories are retained for immediate coordinator package/release use; coordinator owns later cleanup of superseded temporary copies.
