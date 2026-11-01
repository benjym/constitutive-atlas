# Bingham COMSOL 6.3 delivery packet

Exact formulation: `bingham-comsol63-mises-perfect-zero-spin-ode`, COMSOL6.3 associative von Mises perfect Bingham elastoviscoplastic solid plus isotropic linear elasticity. Small strain, dry total stress, fixed frame/zero spin; physical time,13persistent state components. No hardening, temperature, finite rotation or experimental validation claim.

The immutable [source packet](source-v1/README.md) contains the full governing equations, equation-to-source/schema crosswalk, explicit initialization/integration contract, receipts and rights, independent analytical reduction, gaps and numerical choices. Private copyrighted originals remain outside the public repository. The [dossier](../../models/bingham-comsol63.md) summarizes applicability.

[DELIVERY.md](DELIVERY.md) and [CHECKLIST.md](CHECKLIST.md) track the full E0–E8 assignment. Sources, contract and Python/transcription checks are complete. Prospective execution review accepted freeze-v3 after retained assessor findings R1–R3 were corrected. Native/Wasm qualification, final scientific approval, atlas packaging/browser and live delivery remain pending. Source packet completion is distinct from those later gates.

Reproducible evidence: source-v1/analytical-check.json; execution-v1/PLAN.md, cases.json, reference-convergence.json and freeze-v3.json; tests/test_bingham_candidate.py; independent-review-v1/REPORT-v1.md and REPORT-v2.md. Frozen references/settings precede any compiled observations. Public main-atlas controls will be relaxation, stress-hold creep and all-six strain rates with complete state and replay.
