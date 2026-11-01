# Native observation CLI binding correction v2

FIX-kelvin-native-observe-harness-v2. Original v1 source, case references, raw results, assessment failure and policies remain unchanged. The retained v1 native calls reject algebraic observation with `option unsupported by timed mode: --current`. The common timed CLI requires `--initial`; the C/Wasm ABI arguments already use the correct current-state position.

This is a CLI spelling correction only. study.py differs from v1 in exactly two token replacements: observe-case native argv and native direct-endpoint observation command. The independently derived reference.py, original PLAN.md and Wasm collector are byte-identical. Regenerated cases differ only in the six observe-case native argv `--current` tokens becoming `--initial`. All 43 case identities, C ABI names/types/arguments, parameters, initial states, histories, outputs, source/model hashes, gates and solver settings are unchanged. The copied PLAN.md and study.py's old standalone prepare metadata retain their historical wording; use prepare_binding.py for the distinct v2 freeze rather than study.py prepare.

Before corrected compiled observations, prepare_binding.py verifies those exact differences and freezes v1 raw/cases/source, v2 inputs and the recovery script. recover_native.py inspect performs no compiled calls. Recovery reuses all original integrate-time/schedule call stdout, stderr and returncodes, including failure and replay records. It recollects only the six failed observe cases (twice each) and 22 direct endpoint observations (once each), 34 algebraic calls total. New rows and complete provenance are written under execution-v2 and never overwrite v1. The original trajectory results are not rerun, replaced or represented as fresh v2 integrations.

Parent-only commands, after prospective review and explicit exact qualified solver hash:

```sh
python3 -B docs/ingestion/kelvin-voigt-comsol63/execution-v2/recover_native.py inspect
python3 -B docs/ingestion/kelvin-voigt-comsol63/execution-v2/recover_native.py recover --solver /absolute/qualified/atlas_kelvin_voigt_solver --solver-sha256 EXACT_QUALIFIED_SOLVER_SHA256
python3 -B docs/ingestion/kelvin-voigt-comsol63/execution-v2/study.py assess --backend native
```

The unchanged assessor checks every state/stress trajectory, all six observations, replay, failure/recovery and reference gates. Failed corrected observations remain raw failures; no acceptance bound is relaxed. Wasm collection may target execution-v2/cases.json and execution-v2/wasm-raw.json with the unchanged collector; all C ABI calls are identical to v1. Parent owns all compiled execution and numerical interpretation. This preparation worker executes no compiled artifacts.
