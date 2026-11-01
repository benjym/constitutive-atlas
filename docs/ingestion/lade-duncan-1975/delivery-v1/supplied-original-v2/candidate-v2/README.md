# Lade–Duncan1975 isolated gap-history candidate v2

This is a source-mapped research candidate, not an approved/public model. Source acquisition and transcription work are complete enough to execute bounded studies. Full delivery is blocked by pressure-domain fidelity and an original native/Wasm parity failure; see [CAPABILITY_GAP.md](CAPABILITY_GAP.md).

The [model](model.json) has SHA256 `e1a21278ac9ce65debd5bf81b181462509e57d7928cc8b8366c75cd6110c4e63`. It retains the source law and numerical choices of the [failed v1 candidate](../candidate-v1/README.md), replacing direct numerical storage of physical history H with a signed gap carrier q. Physical `H=max(ft,f(S)+max(q,0))`; for nonzero strain the residual enforces `q=max(Hprev−f(S),0)`, while exact-zero strain preserves the raw incoming carrier. Negative q is an explicitly declared alias for zero physical gap. This avoids v1's curved-invariant trial/re-entry deadlock without relaxing the physical history invariant or original reference/error bounds. q is a numerical encoding, not an experimental observable.

The [frozen policy](POLICY.json) discloses small-strain fixed-frame mechanical embedding, zero-pore-pressure restriction, current minimum principal pressure, cluster-average generalized Jacobian at repeated minima, local Eq19 endpoint backward Euler and pre-failure scope. No shared compiler/schema/runtime source was changed for this candidate. Native and Wasm snapshots use the same pinned common engine and generated candidate; [build receipt](build-receipt.json) records serial commands, toolchains, exact artifacts and the failed compiler-cache attempt followed by a successful local-cache build.

| Study | Result | Evidence |
| --- | --- | --- |
| Source algebra |15assertions PASS | [source checks](../algebra-results.json), [independent original-source review](../independent-review/) |
| Candidate validation/generation | PASS | [receipt](validation-generation.json) |
| Interpreter endpoint/hold checks |12PASS | [checker](check_candidate.py), [results](interpreter-results.json) |
| Independent triaxial reference |8convergence cases PASS | [prospective policy](triaxial-policy.json), [source-driven quadrature](triaxial_reference.py), [reference results](triaxial-reference-results.json) |
| Native triaxial refinement |24requests PASS; all finest bounds and plastic stress refinement pass | [checker](check_native_triaxial.py), [results](native-triaxial-results.json) |
| Original native lifecycle | FAIL,4of32checks | [original policy](lifecycle-policy.json), [checker](check_native_lifecycle.py), [retained results](native-lifecycle-results.json), [diagnosis](lifecycle-diagnostic-v2.json), [independent review](lifecycle-review/) |
| Corrected native lifecycle |38checks PASS | [separate policy](lifecycle-corrected-policy.json), [checker](check_native_lifecycle_corrected.py), [results](native-lifecycle-corrected-results.json) |
| Original Wasm parity | FAIL,1of56requests; all24triaxial requests pass | [prospective policy](wasm-policy.json), [checker](check_wasm.mjs), [retained results](wasm-results.json) |
| Corrected lifecycle Wasm parity |38requests PASS | [separate policy](wasm-corrected-policy.json), [checker](check_wasm_corrected.mjs), [results](wasm-corrected-results.json) |
| Hydrostatic source-domain event | FAIL,all8cross-event paths accepted | [prospective diagnostic](hydro-domain-policy.json), [checker](check_hydro_domain.py), [results](hydro-domain-results.json) |

The largest finest native triaxial errors are approximately2.65e−5relative axial stress,2.36e−7absolute radial strain and2.41e−4relative plastic work with a1Pa floor. Bounds were0.005,0.0001and0.02respectively, unchanged from v1. Those bounded successes do not override the domain and parity failures.

The original lifecycle checker omitted the Mandel-to-physical-shear divisor when decoding H for rotated states. The corrected campaign keeps the original covariance tolerances, tests true invalid requests and forces solver exhaustion with a valid parent and explicit one-iteration/no-subdivision settings. It verifies exact full-state rollback, successful ordinary-settings recovery, restart/replay, holds, near-tie and unload/reload probes. It does not label the large finite unloading input invalid, change the failed original report or assert source-domain fidelity.

Reproduce the isolated studies from the repository root using the linked Python/Node checkers after recreating the pinned native/Wasm snapshots and artifacts listed in the build receipt. The [exact28file build-source archive](build-source-archive.json) and [snapshot](build-source-snapshot/) preserve the common engine/generated candidate plus separate native/Wasm CMake files; rebuild instructions are in that archive receipt. Raw large triaxial and Wasm responses stay under ignored `.local/lade-duncan-candidate-v2/`; public reports bind them by exact paths and SHA256. Copyrighted source PDFs remain private. There is no E5 approval, public model registration, packaged website or live delivery.

The first [integrity checkpoint](checkpoint-integrity.json) retained one historical supporting-solver hash failure after a concurrent shared-file change. Both exact reviewed revisions were recovered and archived without changing the original review receipts or executed snapshots. [Receipt-aware verification](check_integrity.py) now [passes](checkpoint-integrity-resolved.json). That integrity repair does not alter the numerical failures.
