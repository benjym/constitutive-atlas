# Maxwell — approved continuous material-point model

**Approval: approved by explicit user instruction, 1 November 2026**, for the bounded scope below. The [canonical approval registry](../../catalogue/approved-models.json) and [admission record](../admission/maxwell-approved-v1/approval.json) bind approval to exact definition SHA-256 `dc378ac0eb6956f7d0028b1fa5927d2906bf05e14ab45b116bc447c25e6b885f`.

The model implements continuous Maxwell shear relaxation and elastic volume change for a dry, uncoupled material point. It uses infinitesimal strain, a fixed Cartesian frame with zero spin, compression-positive Mandel components and total Cauchy stress. The physical-time law is

`sigma_dot = K trace(D) I + 2 G dev(D) - (G/eta) dev(sigma)`.

The [run guide](../../examples/maxwell/README.md) provides native build/run commands and four timed examples: creep, relaxation, oedometer creep and load/hold/reverse. Existing native and Wasm common-engine qualifications cover the [frozen requests and settings](../ingestion/maxwell-itasca900/integration-v1/reference-cases.json). The declared parameter bounds extend beyond that qualified envelope.

Approval follows the [separate-agent technical review](../reviews/maxwell-scientific-agent-v1/README.md), whose algebra and saved evidence were independently replayed by the parent. It is a user-authorized project admission with an AI technical review, not an invented human scientific signature. Experimental validation is unassessed. The exact executable definition retains its historical `draft` label so source/equation/build hashes and qualification remain intact; the separate registry records current project approval and its authority.

The approved scope excludes arbitrary tolerances, unconditional numerical dissipation, full-domain numerical accuracy, experimental prediction, FE/MPM use, finite rotations, saturated coupling, the vendor's central-difference algorithm and complete vendor/original-book equivalence. The loose-tolerance energy-growth witness and schedule rollback coverage limit remain in the review. This approval does not add a browser timed-control UI or publish a release.

Four exact original manual pages are now retained in ignored persistent private workspace storage. The [additive retention receipt](../admission/maxwell-approved-v1/source-retention.json) closes MW-14 without rewriting the review or original source receipts. Copyrighted files are not redistributed.
