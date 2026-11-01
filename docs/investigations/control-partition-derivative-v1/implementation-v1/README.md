# Protocol 1 control derivative: implementation handoff v1

`CAP-control-partition-derivative-v1`, coordinator-authorized isolated implementation. No C++ compiler, native/Wasm build or compiled fixture/material call was executed by this worker. This packet is ready for separate prospective review, not an accepted capability or evidence that the old MD1997 failure is resolved.

Owned runtime: `/private/tmp/atlas-control-partition-v1/source/cpp/include/atlas/solver.hpp`, new `cmake/control-partition-derivative/CMakeLists.txt` and new `tests/fixtures/control-partition-derivative/{main.cpp,rate.json,residual.json}`. `source-freeze.json` binds the resulting582-file source closure, including all577 untouched existing files and the four additions. `original/solver.hpp` preserves exact old SHA `7a3aacf4c283ca4ba32e0e0dc996142c6543bf9193685ab7281ac3435b2cbbc5`. `proposed/` contains exact proposed bytes for review; it is not an installed shared runtime. `parent-inputs.json` pins original design/policy/addendum/receipt bytes.

## Change and bounds

`solver.patch` and `exact-edits.json` contain precisely three edits: a generic accepted-partition comparator and callback-based derivative helper; protocol1's derivative call using that helper; and completion of the two actual accepted half-increment records for rate success. The rate numerical update, existing fractions and counters do not change. **Rate successful diagnostics intentionally gain accepted_increments**; new receipts/regressions must record that difference without overwriting old reports. No schema, generated scientific model, shared root runtime, C++ API serializer or public setting changes.

The helper probes nominal h0/2^k for k0..10, bounded11evaluator calls. It requires exact ordered positive fractions with unit coverage within1e-12, matching retry identity and all finite six-component accepted increments, with actual-affine consistency at8epsilon local scale and8denorm_min floor. Unchanged total components require exactly unchanged accepted increments. It uses the nominal selected h in the denominator, preserving the prior convention; actual rounded input totals are audited and every nonzero direction channel must change representably. Unrepresentable perturbation fails without evaluating that probe.

Two **consecutive** comparable finite slopes must converge within1e-3max(abs(dh),abs(dhalf),1Pa/strain); the smaller-h slope is used. Failed/mismatched/nonfinite/wrong-length/empty probe responses clear the previous candidate. Empty base fails before observer invocation. No positive-slope assumption is introduced. The original nearzero derivative guard,30outeriterations, physical checks, settings, strict-descent line search and caller rollback are unchanged. Production evaluator captures the same const parent/parameters/settings and invokes only existing generic integrate. Helper audit is local and is never spliced into accepted material state, counters, settings or budgets. The standalone fixture exposes full audit; public CLI/API serialization is unchanged.

Protocol3's production block and **all bytes from its marker through end of solver.hpp are identical** to the original. Its derivative vulnerability remains a documented gap. The fixture's protocol3-direction callback is structural helper evidence only.

## Frozen prospective fixture

`cases.json` defines25ordered groups and exact input vectors, expected decisions, evaluator counts, selected h and numerical gates. The native and Wasm standalone fixture returns the same JSON shape through `atlas_control_partition_fixture()`; it uses synthetic callbacks for metadata discontinuities and generated declarative residual/rate elasticity for production control tests. It contains no handwritten production constitutive kernel.

Groups include wrong-partition jump followed by recovery at h/2,h/4; exact-boundary/exhaustion and stable negative/zero slopes; failed/nonfinite/overflow/wrong-length/empty callback responses and reset; unrepresentable perturbation and empty base without observer/evaluator calls; recovery after exhaustion from the immutable parent; non-dyadic affine tensors with negative/zero/shear channels and malformed metadata; and generated rate/residual constant-lateral-stress elasticity with invalid-domain rejection/full-parent rollback/recovery.

Analytic elasticity: E30MPa,nu.25, axial.001, lateral-.00025, directional slope48MPa, final stress[130000,100000,100000,0,0,0]Pa and e=.69915. Both generated laws use fixed e_initial=.7. Complete stress tolerance1e-6Pa, e1e-12, lateral1e-12. Synthetic slope78MPa is checked at1e-6Pa/strain; decisions/counts/h are exact. The zero-slope helper may converge but protocol1's unchanged nearzero guard still rejects it. Both backend repetitions must be byte-identical within backend, and all state/audit fields are compared under the frozen paired policy. Synthetic NaN metadata is preserved as explicit JSON null with rejection flags, never accepted as a finite slope/state.

## Source-only checks and retained initial findings

`python3 -B <packet>/check_source.py` verifies original578receipt, exact edits, unchanged protocol3/downstream bytes, all582source hashes, proposed copies, parent receipt hashes,25groups, Python AST syntax and final packet manifest. Python source generation via `python3 -B -m atlas.compiler <packet>/source-check-generated <source>/tests/fixtures/control-partition-derivative` succeeded and produced the retained two-model header/catalogue; this is schema/transcription validation, not C++ compilation. `node --check <packet>/collect_wasm.mjs` checks transport syntax only.

`initial-validation-findings.json` retains the original missing rate metadata, a fixture repeated-call delimiter correction, and the independent source-review layout guard finding. Exact pre-correction source attempts are retained as text. Negative mock checker reports preserve attempted empty coverage, fabricated pass-only rows without inputs/audit, and paired identical empty reports. Their intentional checker exit1 is expected; no mock is actual backend evidence. `static-checks.json` records these source-only observations.

## Coordinator commands after independent prospective review

Use new build/evidence paths, retain exact toolchain/configuration/environment/source/fixture/generated/binary/module/payload hashes and process logs. Every build is serial, one explicit target, --parallel1. Native results must pass before proceeding to Wasm. These commands are a handoff, not actions run by this worker.

```
cmake -S <source>/cmake/control-partition-derivative -B <new-native-build> -DCMAKE_BUILD_TYPE=Release
cmake --build <new-native-build> --target atlas_control_partition_derivative_fixture --parallel 1
python3 -B <packet>/collect.py --solver <new-native-build>/atlas_control_partition_derivative_fixture --output <new-native-evidence>
python3 -B <packet>/check_saved.py <new-native-evidence>/report.json --output <new-native-checks.json>
emcmake cmake -S <source>/cmake/control-partition-derivative -B <new-wasm-build> -DCMAKE_BUILD_TYPE=Release
cmake --build <new-wasm-build> --target atlas_control_partition_derivative_fixture --parallel 1
python3 -B <packet>/collect.py --engine <new-wasm-build>/control-partition-derivative.mjs --output <new-wasm-evidence>
python3 -B <packet>/check_saved.py <new-native-evidence>/report.json <new-wasm-evidence>/report.json --output <new-paired-checks.json>
```

Collectors refuse existing output directories, retain process stdout/stderr/exit status and raw JSON plus saved parsed response for both repeats, and bind artifact/payload/case/source/manifest identities. Checker verifies exact25group order and expected full inputs, rejects missing/fabricated rows, checks current artifact bytes, and performs full paired audit/state comparison; equal incomplete reports cannot pass. Keep artifacts available at recorded paths for read-only checking. Invalid exported JSON and subprocess timeout evidence remain preserved. No existing public ABI is called by the standalone fixture collector.

After synthetic success, the coordinator must obtain separate actual review and run the exact old failed coarse control trace/path, original unchanged128/512 source study, a separately identified new-runtime binding of frozen2048/4096 study, ordinary16model and C++ transaction/rate regressions, and the eight-profile plan under current qualified receipts. Neither this fix nor a synthetic pass waives a source/refinement/FD-partition gate. The old predictor578closure and all old studies/failures remain immutable. If comparable stable probes cannot resolve the exact failure, preserve the result and request a distinct fixed-partition replay/analytic-control capability; do not broaden this patch retrospectively.

## Prospective transport evidence correction

The initial32-file handoff manifest and exact collector/checker/README bytes are retained in pre-transport-audit-v1/. Before any compiled observations, source inspection found that a Node process could emit two rows and later exit nonzero. The final collector therefore binds complete processes.json and its hash into the report; the final checker requires zero transport process exits, expected process/repeat counts, raw process-to-call linkage and saved raw JSON equality. No runtime, source case or numerical tolerance changed. Additional negative checks are retained under transport-correction-mocks/.
