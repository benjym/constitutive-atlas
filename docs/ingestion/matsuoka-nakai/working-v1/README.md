# Working NH2004 full-extension clay research model

The selected Nakai–Hinokio2004 subloading tij clay formulation now runs through the unchanged Atlas common solver, including stress-path-dependent associated/isotropic plastic flow, AppendixV isotropic-only flow, unloading/reloading and softening. It is a separate explicit v0.3 draft, `nakai-hinokio-2004-clay-appendix-v-be`.

Run the actual common laboratory driver from the repository root:

```sh
python3 tools/run_nh2004.py --protocol drained --output /private/tmp/nh2004-drained.json
```

The runner builds only its isolated native target, serially with `--parallel 1`, on first use or when model/runtime source changes. Default drained run:1% axial strain,100increments,101full-state points. Options include `--protocol undrained`, `isotropic`, `oedometric`, or `stress-controlled` (default5000Pa), `--cycles`, `--rho`, `--pressure`, `--void-ratio`, and `--initial` for an explicit16component state. `--solver` can reuse an explicitly selected compiled engine. Default cache is the platform temporary directory under `constitutive-atlas-nh2004`; builds use the current source, which must be separately qualified after changes.

The installed research definition is [the model JSON](../../../../models/research/nh2004/nakai-hinokio-2004-clay-appendix-v-be.json). Its bytes equal [the qualified definition](model.json). It is intentionally a research catalogue, with no change to existing public definitions, web catalogue or scientific admission.

## Source and numerical choices

[Source decisions](SOURCE_DECISIONS.md) resolve the earlier selection gates: full one-a clay, AppendixV selected, Table1 projection and repeated Eqs18/A10 used instead of the inconsistent A8 intermediate, unique positive algebraic stress transformation, total-plastic-volume density compatibility. The [original source packet](../README.md), PDF receipt and original failed oracle/verifier observations remain byte-for-byte unchanged.

The finite update is a named **endpoint backward-Euler project discretization**. Six extra symmetric algebraic auxiliary components represent the source inverse-square-root tensor without restricting repeated principal stresses or adding a handwritten material kernel. All16state components have explicit v0.3 semantics/init declarations. Zero-spin infinitesimal strain only; Table2 clay parameters; the two-a Toyoura sand variant is not this identity. The source's physical model is rate independent. No physical clock or autonomous creep is added.

Backward Euler is first order. Internal substeps enforce nonlinear solvability; caller-grid refinement establishes finite-path accuracy. The beta1.5 flow has a nonclassical derivative at isotropy, so the zero-branch Newton derivative is an algorithmic choice and no general material tangent is claimed. The retained initial auxiliary-consistency tolerance is1e-8; rho initial roundoff tolerance is−1e-10. Those are numerical checks, not physical extensions.

## Qualified results

[Prospective plan](PLAN.md) and [delivery supplement](DELIVERY_PLAN.md) froze reference policies before the corresponding compiled observations; [freeze receipts](prospective-freeze.json) and [delivery receipt](delivery-freeze.json) retain exact hashes.

- Standalone independent Cartesian/principal-value reference with NumPy, no Atlas imports: all five branches and one rotated non-diagonal residual fixture agree;240regular differential samples checked. [Fixtures](residual-fixtures.json), [reference code](reference.py).
- Native material study: **1,383calls pass**, including six finite strain paths at32/64/128caller increments, non-diagonal shear/tensor loading, finite hydro,32continuous unload/reload steps, exact repeated trials, invalid/inconsistent-state rejection, budget failure with full rollback and same-process recovery. Every accepted state includes all16components. Finest scaled endpoint errors range from1.06e−5 to1.07e−3; they decrease with refinement and meet the frozen3e−3stress/3e−4scalar limits. Independent RK4 references use256/512/1024subdivisions; separate hydro analytical limits pass. [Summary log](qualification.log), saved details in `qualification.json.gz`.
- Actual shared laboratory driver: **five protocols pass**, each with101points at the frozen targets. Finite/SPD, fixed lateral stress, zero volume, final deviator stress and independent void-balance checks pass. [Report](laboratory-report.json), full responses in `laboratory-responses.json.gz`.
- Actual Wasm C ABI: **1,383native/Wasm pairs and22,128state components pass**, with unchanged request inputs and exact failure rollback. All six independent source-residual fixtures also pass. [Report](wasm-report.json), [parity log](wasm-parity.log). Backend agreement is separate from independent source checks.
- Existing language/state-contract regression suite:23tests,20pass and3optional native-fixture skips. [Log](software-tests.log). Normal `atlas.model.load` validates the full v0.3 structure and semantic/dimensional contracts; the earlier crosswalk's partial schema verifier is not being used as model validation.
- The reusable runner was exercised both against the study binary and with its own fresh isolated build; default drained run succeeds with101points. [Runner log](runner.log).

## Reproduction and evidence

```sh
python3 docs/ingestion/matsuoka-nakai/working-v1/verify.py
python3 docs/ingestion/matsuoka-nakai/verify_packet.py --source
```

The first command verifies saved results, the installed record, reference fixtures and hashes without running compiled code. The second also checks the original private PDF when present. `runtime-source.tar.gz` archives the compiler/runtime/schema/model source closure for the retained builds; it includes no third-party PDF or experimental arrays. The source and binary receipts distinguish current-source runner reproduction from the qualified historical build. Compressed JSON/JSONL evidence preserves exact uncompressed bytes/hashes. Do not overwrite these retained reports with a changed-source run.

To prepare a distinct isolated study with the pinned current source:

```sh
python3 docs/ingestion/matsuoka-nakai/working-v1/prepare.py /private/tmp/atlas-nh2004-reproduce
cmake -S /private/tmp/atlas-nh2004-reproduce -B /private/tmp/atlas-nh2004-reproduce/build -DCMAKE_BUILD_TYPE=Debug
cmake --build /private/tmp/atlas-nh2004-reproduce/build --target nh2004_solver --parallel 1
```

The prepared target also supports Emscripten. A private writable `EM_CACHE` is required if the system cache is read-only. The first Wasm link failed on a read-only Homebrew cache; that log is retained. Copying the existing cache into the private build directory and retrying succeeded, with no equation, tolerance or compiler/runtime source change. `transport.cpp` wraps the existing C ABI in a persistent line transport only; it contains no constitutive equations.

Other retained setup failures: the first model draft used unsupported Python conditional syntax instead of DSL `select`; the first interpreter harness supplied flat state instead of a name mapping, then NumPy scalars instead of native Python floats. These were authoring/harness corrections before material qualification; the frozen model equations and acceptance policy were not changed after the successful native observations. See [history](history.json).

Source inventory and working software are delivered. Scientific review, source-matched experimental reproduction, full finite-rotation scope and general tangents remain open. The shared website was not modified or deployed.
