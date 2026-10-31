# Full preparation/hold v1 — retained accuracy failure

Both serial builds completed normally. All nine native and nine Wasm schedules completed their full30s histories, with23points each (414retained points total). Exact carried state/strain, clock, transition masks, response settings and captured stress controls pass. Native/Wasm physical-channel parity passes with maximum scaled difference `1.230021640097334e-11` against the predeclared `1e-7` limit.

**Overall independent-accuracy outcome: failed on both backends.** Five fine-resolution component gates exceed their unchanged limits:

| Path / phase / channel | Native maximum error | Bound |
|---|---:|---:|
| Compression / hold / elastic shear strain | 2.0012004841e-10 | 2e-10 |
| Extension / hold / elastic shear strain | 2.0012004835e-10 | 2e-10 |
| Isotropic / preparation / elastic volumetric strain | 2.1300459591e-9 | 2e-9 |
| Isotropic / preparation / total pressure, Pa | .01171607166 | .01 |
| Isotropic / hold / elastic pressure, Pa | .01119494041 | .01 |

Wasm has the same five component failures within the retained parity bound. `assessment.json` also records the frozen assessor's first overall failure, in addition to the diagnostic enumeration of all five component exceedances; this is not a sixth distinct numerical failure. Every coarse/medium/fine phase metric is retained. No reference, physical input, source guard, solver default, numerical bound or result was changed to obtain a pass.

The complete87file cache-free prospective manifest was frozen before native execution. The unchanged historical v0.2 research definition is compiled using the frozen current compiler and common C++ engine; this is not a new model migration or admission. Native and Wasm builds used one explicit target and `--parallel 1`, with `EMCC_CORES=1`, sequentially. Exact commands/stdout/stderr, configuration snapshots, artifacts hashes and raw journals are under `native/` and `wasm/`.

`verify_study.py` rehashes source inputs and artifact bytes, verifies receipts and serial ordering, reconstructs the frozen Python source closure under isolated Python, regenerates exact model declarations and requests, and reproduces every physical assessment field without compiled execution. Failed-result tracebacks contain the copied source paths, so full assessment bytes differ; only traceback metadata is excluded from that comparison. The original tracebacks remain unchanged. No ROOT rewriting, hash substitution or binary execution occurs in replay.

Next numerical action: a separate, prospectively frozen refinement study adding one tighter tolerance per path. Backward Euler's first-order global error with step-doubling suggests quartering local relative tolerance to2.5e-9 approximately halves leading error. Keep all physical inputs, component limits and100000substep budget unchanged; preserve this failed study and retain any new failure. This is a numerical refinement hypothesis, not a passing result.

Journal-source reconciliation, strictness, author mixed-control equivalence, experimental matching, general3D and public timed-browser admission remain open. No push or deployment.
