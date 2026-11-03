# Generic closed-form oracle correction v1

Owned scope: NEW docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/ only,
worker /root/vibe_capability,2026-11-04. No runtime, candidate, fixture, original
corpus/generator/test or original execution evidence was edited. No build, module
load, material call, browser, commit or remote operation ran in this correction.
Actual serial slot remains parent-owned and held; separate reviewer acceptance is
required before any rerun.

The original actual native generic run failed the corpus gate: mixed e was
.7983807287813467 versus old expected .7974817631770881. The original log,
receipt, failed raw test and25-file artifact receipt remain at their exact original
root execution-v1 paths, pinned in original-failure-bindings.json. Five other
reported groups passed. This packet does not rewrite that failed result as a pass.

## Cause and independent correction

The synthetic fixture declares e_dot=-(1+e)*trace(strain_rate). Integrating gives
`e_end=(1+e0)*exp(-trace(strain_end-strain_start))-1`. In a Mandel symmetric tensor,
trace is the sum of the THREE diagonal/normal components. The three shear entries
are off diagonal and contribute zero to trace. The old independent generator
mistakenly summed all six components.

The mixed strain vector [.001,-.0003,.0002,.0004,-.0005,.0006] has exact trace .0009;
the incorrect six-component sum is .0014. Its old reference is therefore
1.8*exp(-.0014)-1; the corrected exact result is1.8*exp(-.0009)-1. Their difference
exceeds the unchanged scalar bound. Pure shear basis3,4,5 must leave e=.8; normal
basis0,1,2 each has e=1.8*exp(-.0007)-1. Fraction exact trace and Decimal80 closed
forms establish these witnesses without importing the interpreter/runtime.

The new generator reads the hash-pinned immutable18-case v1 corpus, preserves its
inputs/settings/bounds and all other expected values, and recomputes only e using
that analytic identity. V2 changes precisely six expected e entries (three mixed
partitions and three shear bases) and the corpus identity. The complete structural
round-trip audit restores those six values/identity and requires exact equality to
v1. All other twelve e values are exact unchanged, as are all other state fields.
`proof-results.json` records every delta and the original analytic counterexample.
No tolerance or execution setting changed. This is an independently reviewable
oracle defect correction after an original failed execution, not a gate waiver.

## Exact corpus-only runner projections

The original native and Wasm runner bytes are SHA-pinned in runner-delta-proof.json.
Prepared source snapshots and unified diffs change ONLY the corpus path. Native
has two references to the same logical corpus location (raw receipt and reader);
Wasm has one shared variable. Reversing the literal replacement must recover the
original source bytes exactly. Gate equations, ABI calls, settings and assertions
are unchanged. Wrapper/loader scaffolding is separately bound by the manifest.

Native run_native_v2.py compiles the source projection with its original filename,
sets original __file__, and preserves root fixture locations and unittest discovery.
Wasm run_wasm_v2.mjs evaluates the source projection through SourceTextModule with
the original identifier/import.meta.url, preserving every unmodified fixture URL.
Static imports are restricted to node built-ins and linked via complete namespace
exports; dynamic import forwards to the native loader. The Wasm wrapper requires
Node's --experimental-vm-modules flag only for explicit future execution. These
wrappers do not replace constitutive equations or implement a new kernel.

Both wrappers default to inspect mode, which verifies original/snapshot/corpus
hashes and corpus-only byte deltas, then exits without importing NativeEngine,
evaluating the target JS module or touching any compiled artifact.

Pure source reproduction (safe before serial handoff):

```
python3 -B docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/prepare_runners.py
python3 -B docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/run_native_v2.py --inspect
node docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/run_wasm_v2.mjs --inspect
```

Future opt-in execution ONLY after exact independent source approval and explicit
parent slot handoff, with new output identities and the original native env inputs:

```
python3 -B docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/run_native_v2.py --execute -v
node --experimental-vm-modules docs/ingestion/vibe-2026/controlled-time-oracle-correction-v1/run_wasm_v2.mjs --execute MODULE CATALOGUE NEW_OUTPUT SOURCE_MANIFEST
```

Native requires the existing explicit ATLAS_CONTROLLED_TIME_MODULE,
ATLAS_CONTROLLED_TIME_CATALOGUE, ATLAS_CONTROLLED_TIME_SOURCE_MANIFEST and
ATLAS_CONTROLLED_TIME_RAW_OUTPUT. Use the correction manifest as source-manifest
input to retain the new study identity. The original runners retain corpus-v2 bytes
in their existing raw receipts. Neither future command was run by this worker.

Pure Decimal/Fraction proofs, projection inspect checks, Python AST and JS syntax
checks pass. One initial syntax-only check used CommonJS stdin mode and rejected
ESM import syntax; it executed no module. The corrected syntax command is
`node --input-type=module --check < wasm-runner-v2.source.txt`. This invocation
failure is retained in syntax-attempts.json. No numerical/backend failure was
observed or waived by these source checks.

No process/server/worktree/download or disposable build was created. Source and
proof files remain durably in the owned packet; parent execution artifacts and
original sources remain untouched. Independent review, actual corrected native
and Wasm execution, model E4/E5 and browser/live delivery are separate open gates.
