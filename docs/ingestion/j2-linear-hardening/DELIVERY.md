# J2 linear isotropic hardening — completed delivery ledger

MODEL-j2-linear-hardening is complete for its bounded approved formulation and main-laboratory scope. Delivered revision `8e060a425015d65ffe087243204d17b8dba62ab8` passed [every required CI/Pages job](https://github.com/benjym/constitutive-atlas/actions/runs/41299887463); 20 live/upload asset comparisons and the actual live full-state preset pass. [Open J2 in the main laboratory](https://benjym.github.io/constitutive-atlas/index.html#laboratory?model=j2-linear-isotropic-hardening-be).

| Phase | Verified evidence |
| --- | --- |
| E0 | Coordinator-owned scoped tasks and preserved unrelated work; prior explicit commit/push authorization continued through closeout. |
| E1 | [Source packet](README.md) and private source receipts for the complete selected OpenSees specialization. |
| E2 | Explicit v0.3 source/schema/integration crosswalk, conventions, transaction/reset/history semantics and frozen independent references. |
| E3 | Corrected v2 transcription; rejected original v1 and reverse-root failure preserved in [correction](CORRECTION-v2.md). |
| E4 | Isolated native/Wasm qualification: 115 main cases, 27 history increments and 16 default supplement cases; original independent/parity/tangent/rollback gates. Normal copied package: 327 calls / 1,264 state / 192 tangent comparisons and current all-green CI. |
| E5 | [Separate scientific review](../../reviews/j2-scientific-v2/README.md) and [exact bounded approval](../../admission/j2-approved-v2/approval.json), unchanged. |
| E6 | Normal atlas catalogue/Explore/source/review/approval integration and dedicated material-point engine mounted in main index.html. Current concurrent source-linked database packaging remains intact. |
| E7 | [Independent main-interface qualification](delivery-v2/README.md), actual custom/full-state/import/export/failure/retry checks, four-profile routing and late-work checks; original scientific approval does not approve arbitrary browser inputs. |
| E8 | [Exact release receipt](delivery-v2/live-release-v1/README.md): five required jobs pass, Pages deployment succeeds, 20 assets match actual tested upload, actual live export: 32 state comparisons and empty error/warning log. |

Definition: `models/research/j2/j2-linear-isotropic-hardening-be.json`, SHA256 `a28068cbb8cfc660e49eb648d6ce7fcbf993ea50b45e8eb0d325c6b75f4ffc3b`. Accepted review: `949eefe828ae1e8a6b6830517a8f97087af60134d6402a2de313464f80256d33`; approval: `7e2838bf5a9ca4f14a47836d0502227417d09454b714dce8ae26f5148416b43d`. Runtime catalogue identity: `2ce7ce9c486598a15c04c65600478bfb1fba227d442538d4aa3fc99076d15084`.

Scope: mathematical backward-Euler associative J2, nonnegative linear isotropic hardening, sigInf=sig0 and eta=0; dry total Cauchy stress, infinitesimal strain, fixed frame/zero spin, compression-positive Mandel components. Complete eight-slot state and all six prescribed strain increments. No physical-time/stress-controlled/pore/finite-rotation, broad-parameter or experimental validation claim.

Historical [delivery-v1](delivery-v1/README.md) qualifies the retired standalone snapshot only; it is absent from the current upload. [Delivery-v2](delivery-v2/README.md) is the user-selected replacement. The original failed release f8252c16, two VM-fixture failures, exact prior test bytes, archival corrections and independent fixture acceptance remain in [ci-fixture-fix-v1](delivery-v2/ci-fixture-fix-v1/README.md). The exact prior mutable ledger is retained in [prior-DELIVERY.md](delivery-v2/live-release-v1/prior-DELIVERY.md). The second release 75d36e7a failed the Linux historical Tresca receipt gate and was later cancelled; its original result, complete 19-receipt audit, eight additive redirects and independent acceptance remain in [ci-archive-fix-v2](delivery-v2/ci-archive-fix-v2/PLAN.md). No failure, source receipt or original scientific decision was overwritten.
