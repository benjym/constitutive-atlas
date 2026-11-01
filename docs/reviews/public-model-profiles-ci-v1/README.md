# Public model profiles — CI repair

Failed revision: `b31c0a94ea04b7282e0780112940a362e8f9d315`. [Original failed run](https://github.com/benjym/constitutive-atlas/actions/runs/41351326129).

The native jobs stopped in `test_j2_main_routing.mjs`: its DOM mock lacked `remove()` after profile-link cleanup was added. Both extracted coordinator contexts now include the real public-summary helper and profile lookup. The original routing assertions and controller membership checks remain intact.

Both Wasm jobs stopped in Maxwell provisioning because the evolving delivery checklist no longer matched its reviewed hash. The exact pre-profile checklist from commit `8cab145b` matches the pinned SHA-256 `b370c525b8650492c8b0fb49e1107a765009b5be8f16818675196541eb128289`. Its bytes are retained in the content-addressed source snapshots. The existing agent-review archive map and a Maxwell approval sidecar select this original for pinned receipts. Current checklist instructions remain in place. No review, approval, model, numerical gate or accepted scope was rewritten. The prior J2 fixture bytes cited by the historical Hill routing records are retained separately.

Local checks on this repair:

- 33 focused Node tests pass, including 175 J2 routing assertions and the ordinary/special deep-link checks.
- 12 Maxwell package tests, 5 provisioning tests, 5 agent-review archive tests and 9 archive receipt corruption tests pass.
- Actual `tools/provision_maxwell_assets.py` succeeds against the retained, hash-qualified engine; no new compilation or binary execution.
- Maxwell and NorSand exact reviews validate; canonical Maxwell approval and every supporting-file receipt validate.
- Public profile coverage remains 46/46.

These are local repair checks, not a claim that the subsequent complete remote workflow or deployment has passed. The original failed log is retained privately at `.local/private-evidence/public-model-profiles-ci-v1/failed-ci.log.gz`; its uncompressed SHA-256 is `91e4fb817d13844b85833655ad5a05754e50a493f0151f28e608eca34afc0f53`.
