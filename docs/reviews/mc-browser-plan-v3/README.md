# Bounded MC delivery plan — 1 November 2026

MC has passed the retained [native](../mc-native-qualification-v3/README.md) and [Wasm](../mc-wasm-qualification-v3/README.md) studies. This packet prepares the next delivery step; it contains no package/browser observations and does not install MC.

The proposed delta contains the byte-exact qualified v0.3 model, one updated discovery entry, a public dossier, pending unsigned source review and bounded numerical-evidence record. Scientific admission remains open. The eleven current model definitions and all other discovery entries remain unchanged.

## Next bounded task

Create one private project-path package and execute [P01–B06](protocol.json). Reuse the qualified binaries; do not compile again, extend the solver, acquire more MC sources, repeat the numerical campaign or deploy. Use the fourteen existing requests and existing compatibility corpus. Stop at the first blocking delivery failure, retain its evidence and name the smallest fix. Do not turn a browser failure into a new numerical study without evidence that one is needed.

1. Run `python3 -B docs/reviews/mc-browser-plan-v3/verify.py`. This checks the frozen baseline and validates the proposed records in an isolated future root, without a material call.
2. Export tracked source at the pinned commit in `baseline.json` into a fresh private temporary directory using `git archive`; overlay only the five paths under `proposed/`. Do not copy untracked PDFs, paper work or unrelated work. Do not symlink the repository as a substitute: evidence packaging requires paths inside its source root.
3. Make a separate engine directory containing the qualified `atlas.js`, `atlas.wasm` and exact generated `models.json`. Sources are `/private/tmp/atlas-mc-execution-v3/wasm/build/atlas.js`, the sibling `atlas.wasm`, and `/private/tmp/atlas-mc-execution-v3/wasm/generated/models.json`. Verify hashes and the retained qualification receipt before reuse. Missing artifacts are a blocker, not permission to rebuild silently.
4. Invoke the isolated snapshot's normal `tools/build_web.py --wasm-dir <engine-directory> --output <fresh-output>/constitutive-atlas`. Keep its catalogue guard. The output must include current evidence/source disclosures and approved experiment assets; no private sources. Hash the complete package before serving it.
5. Derive import documents from the retained Wasm journal in `../mc-wasm-qualification-v3/observations.tar.gz`, matching `../mc-current-collector-freeze-v3/contracts.json`. Use production `createLaboratoryDocument` and parser helpers. Save exact document hashes and source journal/archive bindings before execution. This is fixture preparation from observations, not independent constitutive validation.
6. Run the frozen package/browser gates, then publish a local result packet. Only a passing packet permits exact root installation. Deployment still requires a new request.

## Boundaries and exit

This plan is complete when the proposed records validate, the baseline is pinned and the prospective acceptance checklist is recorded. Actual package/browser execution belongs to the next task. No browser pass, scientific approval, experimental comparison or hosted availability is claimed here.

Roadmap reflection: common-schema execution and reproducibility have advanced substantially; eleven local definitions are available and MC is numerically qualified. Delivery is lagging those studies. Finish one end-to-end MC explorer addition before expanding the catalogue or solver. Then return to the existing source/preparation and independent-review backlog, the Wichtmann comparison and paper. Repeated fitting, micro-audits and additional infrastructure are not the default next work.

The machine-readable policy is [protocol.json](protocol.json); [checks.json](checks.json) records proposed-record checks only. [verify.py](verify.py) reproduces those checks. This packet does not assign a human reviewer.
