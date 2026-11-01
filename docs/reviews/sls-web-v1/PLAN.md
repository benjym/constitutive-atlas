# WEB-sls-comsol63-v1 acceptance freeze

Frozen 2026-11-01 before observing the packaged runtime/browser. Owner: /root/sls_browser_delivery. Scope: new SLS page, isolated engine-sls package, package tests and actual browser functional qualification. No compiler/build/scientific approval changes.

Use exact approved model eccfeb372810afd81a5e9cddf5d8ac33e2cb5df6921fc88e14e9175c73e50906 and handed-off qualified module. Builder must validate approved registry membership, independent checklist and every artifact hash, current generated catalogue equality, model and binary identities. No source originals included.

Default: K=20e6 Pa,Ginf=8e6 Pa,G1=12e6 Pa,tau=2s; eps=[.002,.001,-.001,.0005,-.0004,.0003], q=[5000,-2000,-3000,1000,-500,250]Pa; 8 physical seconds,4 intervals. Relaxation: all strains held; creep: all stresses held. All six observable stress channels and twelve state channels inspectable. Comparisons use existing frozen execution-v1 cases/references: strains atol 3e-8, branch stress/observable stress atol 1 Pa, matching existing bounded schedule study; no parameter envelope qualification inferred.

Package Node gate executes actual copied Wasm relaxation and creep, checks every point/all12 state +6 stress against frozen independent references; exact catalogue/model/module/Wasm/review bindings; relative assets. Negative identity mutation rejected by builder. No handwritten constitutive kernel in production page.

Real browser gates: default completes; switch creep completes; explicit parameter and all-state edits reflected in request; reset restores preset; export full request/result/provenance; import/replay validates exact identity, finite arrays and dimensions and compares full result; invalid duration/state/import followed by recovery; superseded requests cannot publish. Inspect status, plots, full state table, source/review/approval links, runtime hashes, console/network; capture desktop and narrow screenshots. Browser changes to parameters/state are functional checks only, not new scientific approval. Invalid imports must clear stale export and invalidate pending work. No compatible calibration/source experimental overlays available; visible explanation required.

Retain original failing observations, distinguish harness defects from application failures, fix and rerun with separate result identities. Qualification is isolated local package; shared normal package/release/live verification belongs to parent. Artifacts stored within this review directory; Playwright scratch uses output/playwright in private package working directory.
