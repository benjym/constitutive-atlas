# Independent explicit laboratory controls source review

Scope: additive binary64-bit cumulative-control API/CLI and shared axisymmetric loop. Source-only review, no candidate calls, Atlas imports, builds, browser tests or numerical admission. The coordinator owns implementation, freeze and execution. Reviewed files and exact SHA-256 pins are in `source-results.json`; copied bytes are under `reviewed-source/`.

The reviewed final source has no remaining material source blocker for this bounded foundation study. This is not a proof of compiled behavior or of all model/control paths.

## Findings and resolution

1. **CLI embedded NUL accepted a valid prefix** in the original proposal. Binary file bytes were handed through `c_str()` to `std::string(csv)`, silently dropping a suffix after NUL. The independent grammar witness in `source-results-initial.json` preserves this discrepancy. Final main.cpp explicitly rejects embedded NUL before the C ABI call. C API inputs are naturally NUL-terminated strings, so its contract cannot inspect bytes beyond the terminator.
2. **Explicit regression initially checked only points**, leaving model/settings/loading metadata and numeric controls unchecked. Final harness compares the remaining explicit envelope to the corresponding old settings-API envelope after removing the documented differing fields, and checks numeric control bit echoes.
3. **Catalogue iteration could silently test fewer than nine models.** Final harness asserts the nine frozen IDs, prior catalogue agreement, and exact 90 legacy,90 replay,40 analytic-point counts.
4. **Boundary/domain coverage gaps.** Final harness adds a valid5001-point zero sequence, unknown-model/invalid-initial-domain rejection and a native binary-file NUL negative. Existing invalid5002 and minimum2 controls checks remain.
5. **Recovery claim needed scoping.** Native CLI launches a new process per call, establishing retained prefix and fresh-process repeatability; only the shared Wasm instance tests same-instance failure-state recovery. Final reporting distinguishes these.

The source changed during the first attempted snapshot; the hash mismatch rejected that snapshot. `snapshot-race.json` records this procedural event and `source-results-initial.json` retains original pins. The final copied source passed a new hash-checked snapshot. No candidate observations occurred in this review.

6. **Analytic response shape hardening, recommended before freeze.** The reviewed harness uses strain.forEach and could vacuously accept an empty strain vector. Add exact point count and strain/state widths6/7 for independent elastic responses. This is a prospective assessor completeness issue, not an identified implementation bug. Any parent correction must be separately pinned; the copied reviewed harness remains immutable.

## Source reasoning

The finite parser checks canonical16 lowercase hex digits, token/total length and exponent bits before copying into a binary64 value. It retains finite subnormals and both zero signs; maximum wire length5001*16+5000=85016. Binary64 requirements are explicit at compile time. The wrapper validates size before accessing front, initial numeric zero, every finite value and amplitude, then uses bounded n−1 steps and cycles0. The source-selected amplitude retains the existing protocol caps and does not manufacture a waveform.

Literal reversal of the optional-control selection and wrapper extraction reproduces the original complete solver header exactly. Thus the old controller algebra/order is retained in source, including protocol3's incremental accepted-parent q control. Both APIs use the same control-minus-previous-control expression. Explicit initial signed zero is stored in the initial point, and raw supplied controls are echoed as authoritative hex. The optional controls pointer is used synchronously while its local owner is alive. The new C function has the existing EMSCRIPTEN_KEEPALIVE export annotation.

The independent elastic expressions agree with the intended protocol constraints: G12MPa,lambda12MPa; radial strain0,−nu*axial,−axial/2,−axial/2,axial for protocols0..4; protocol3 axial=q/(3G). The project void-ratio bookkeeping telescopes to1.7exp(−trace strain)−1. Prospective analytic tolerances remain unchanged. Common-input physical parity is a separately declared finite numerical gate, not a universal constitutive bit-identity promise. This policy revision was source-only/pre-observation, and does not replace historical failed MC parity gates.

## Reproduce

`python3 check_source.py reviewed-source`

Expected33 passing source/grammar/reversal checks. This checker models the public wire grammar independently and checks source invariants; it never runs C++ or imports Atlas. It is not a parser implementation oracle. Exact compiled parsing, exceptions, exports and controller behavior remain for the parent's separately frozen native/Wasm study.

Smallest next action: coordinator freeze these reviewed implementation and harness bytes plus original artifacts/dependencies, then run the declared serial native/Wasm gates. Retain any failures; do not infer MC/browser/producer/import compatibility or scientific admission from foundation software results.

## Final pre-freeze closure

The coordinator added exact analytic point count and strain/state widths6/7. `final-closure/check.mjs` and `final-closure.json` pin this final harness separately; prior reviewed bytes/pins remain unchanged. The new durable native unittest file is also source-reviewed/copied in final-closure: four tests cover independent elasticity, malformed whole files, signed-zero/subnormal transport and failure-prefix retention, with explicit skip when ATLAS_SOLVER is absent. It was parsed as Python source but not imported/executed. Six closure source assertions pass. Main/solver bytes remain identical to the reviewed source. No material bounded source-review blocker remains.
