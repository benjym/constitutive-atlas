# Pressure-domain event qualification remains open

MODEL-lade-duncan-1975 is blocked at E2/E4. Source acquisition is complete. This report requests a separately owned generic integration/domain-event investigation; it does not authorize a shared runtime edit, introduce a pressure floor or approve the isolated candidate.

The exact candidate is [model.json](model.json), SHA256 `e1a21278ac9ce65debd5bf81b181462509e57d7928cc8b8366c75cd6110c4e63`. The source is the complete1975 paper, source hash `bdebd928dbe9e4bac47c0a0328ed0bab79ab3e440a25390f1d646e9ed3749fc5`, Eqs2/6/16–19 and Table1. The local Eq19 endpoint backward-Euler policy is a declared numerical realization, not an author-supplied integration algorithm.

For the paper's Table1 `nu=0`, hydrostatic elastic unloading has `f=27<ft` and `dp/dε=Kur*pa*(p/pa)^n`, where ε is strain in each normal direction. Starting at `p0=60000Pa`, the positive-pressure solution reaches zero at

`εcrit=−(p0/pa)^(1−n)/((1−n)*Kur)`.

This is approximately −0.0019576232 (dense) or −0.0041485166 (loose). The source equations supply no positive-pressure continuation through that event. An endpoint-positive backward-Euler root does not establish that the differential path stays in its domain.

The prospectively identified [domain study](hydro-domain-policy.json), [checker](check_hydro_domain.py) and [saved results](hydro-domain-results.json) use both Table1 sets, total per-axis strains0.5 and1.25times εcrit, with1/4/16/64 uniform external increments. All eight cross-event paths return success with positive pressure after the source's finite zero-pressure boundary. Before-event pressure errors decrease with refinement, but a coarse endpoint can be far from the source solution. No post-observation accuracy tolerance has been invented for those diagnostic cases.

Separately, the original finite per-axis strain−2 lifecycle request was incorrectly labeled schema-invalid: finite strain itself is not an invalid input. Its native loose response accepts64substeps and ends near5.7e−11Pa; Wasm rejects and returns the parent. This is the sole failure of the [original56request parity campaign](wasm-results.json). The original lifecycle and Wasm studies remain FAIL. A separate corrected lifecycle campaign passes38checks; that establishes bounded transaction/covariance behavior and does not clear the domain failure.

The smallest next task is to reproduce this one-dimensional elastic source example in a generic integration test, distinguish endpoint residual convergence from path accuracy and domain fidelity, and specify an auditable event/error-control contract before implementing shared changes. Study positive-pressure approach, finite zero-pressure stopping, failed-parent rollback, recovery, and native/Wasm agreement. General3D qualification must also cover the least-principal-pressure boundary, not rely on a hydrostatic special-case patch. Preserve the existing studies and test any changed engine or numerical realization under new pinned identities with unchanged original triaxial bounds.

The coordinator must assign shared runtime ownership before implementation because this ingestion owns only isolated candidate snapshots. E5 acceptance, normal atlas integration, actual browser qualification and publication remain dependent on resolving this blocker. Experimental validation remains unassessed.
