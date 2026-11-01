# Prospective binding addendum

The36power probes run through the newly built ordinary `atlas_solver --mode evaluate` entry point with the exact saved common inputs. `check_probes.mjs` compares each entire response to the saved baselineWasm response with exact equality; no standalone unbound math executable is used. Their exact requests/results and checker are bound before compilation.

Assume the process default round-to-nearest/ties-even environment, as in existing engine tests. `WANT_ROUNDING=1` supports arithmetic paths but does not set or prove a rounding mode. No alternate rounding-mode, signalling-NaN or general portable math API claim is made. The candidate remains diagnostic only.

`commands.json` fixes the configure/build flags and single target; serial slot must be freshly claimed before execution. No other compiler math flags, FMA, fast-math, LTO, model or tolerance changes are permitted. Inspect actual compile commands and object, not only CMake cache.
