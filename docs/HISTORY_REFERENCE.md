# Experimental Python history reference

The [history and transaction design](HISTORY_TRANSACTIONS.md) now has a separate Python reference for typed, ordered history updates. It is an arithmetic transaction engine, not a constitutive integrator or a PM4Sand implementation. It does not change the existing model parser, parent-reset semantics, native/Wasm APIs or 32-component capacity.

[Program schema](../schemas/history-program.schema.json), [snapshot schema](../schemas/history-snapshot.schema.json), [reference implementation](../atlas/history.py) and [synthetic program](../fixtures/history/ordered-copy.json) are versioned separately from executable models. The [PM4Sand proposal](../proposals/pm4sand3d-history-contract.json) stays non-loadable and source-blocked. Its constitutive equations, host/subzone reduction, solver and scientific review are separate gates.

## Values, expressions and phases

A program declares all retained fields and all caller inputs. Supported values are finite scalars and six-component symmetric Mandel tensors with checked SI dimensions. Storage classes are `state`, `preparation`, `lag`, `mode` and `context`. A mode has an explicit finite enumeration. Retention does not imply that a field is a nonlinear solver unknown. The reference limits a layout to 32 scalar components and a program to 64 phases; it supplies no general array, fourth-order tensor or host workspace representation.

Each ordered phase declares a named base snapshot, explicit symbol bindings, simultaneous writes and optional checks. Bindings select a declared input or a field in an earlier immutable snapshot. The existing restricted tensor DSL checks expression dimensions and shape; arbitrary attribute access and code execution are unavailable. Only explicit aliases and the identity tensor `I` are visible while evaluating writes and guards. A same-phase write cannot affect another write's right-hand side. An ordered dependency must bind the earlier phase's output explicitly.

An optional first `prepare` phase may update preparation records and history provisionally. All later bases and snapshot bindings must descend from its output, even when its guard is inactive. This prevents a post-reset old-history read from accidentally selecting the incoming history. The incoming snapshot remains the rollback target. Preparation-only initialization is outside this `advance` operation: at least one advance phase is required.

An optional scalar dimensionless phase guard executes the writes only when strictly negative. Zero and positive values skip them. Inactive right-hand sides are not evaluated. A skipped phase still produces a named copy of its base. Phase checks are Boolean expressions over all fields of the resulting snapshot plus `I`; they run even for a skipped phase. Checks do not see input aliases. Numeric intermediates must remain finite, including operands hidden inside comparisons. `select` evaluates only its selected branch.

## Transaction and restart contract

```python
from atlas.history import validate_program, make_snapshot, advance

validate_program(program)
parent = make_snapshot(program, declared_values)
trial = advance(program, parent, explicit_inputs)
if trial['ok']:
    parent = trial['snapshot']  # caller chooses whether to publish this candidate
```

`advance` is pure with respect to the caller's parent. Repeated outer candidates start from the same snapshot; one successful candidate is not automatically made the parent of the next. A returned successful snapshot is a candidate for caller publication, not a global commit side effect.

Snapshot identity includes the canonical program hash, generation and preparation epoch. Every retained field is mandatory and restartable, including lag, mode and context. Success advances generation once. Preparation epoch advances once only when the prepare phase executes. Events identify executed phases and are returned only after all phases succeed. JSON roundtripping a complete snapshot reproduces subsequent results.

Malformed programs, inputs or parent snapshots raise `ValidationError` before a trial. Arithmetic, guard, assignment-domain and phase-check failures during a trial return `ok=false`, the unchanged incoming snapshot and no events. Attempt diagnostics identify processed work and the failing phase. A failure after provisional preparation cannot consume a reset command, change the mode, overwrite lag or advance the clock/epoch. The caller can retry a corrected candidate with the original command.

The program hash identifies the selected declarations and algorithm. It is not a signature authenticating an imported physical history. The caller remains responsible for selecting the correct parent lineage; this reference does not consult a durable commit ledger or verify arbitrary historical epoch claims against one.

## Verification and remaining gates

```sh
python -m unittest tests.test_history -v
```

The arithmetic fixture has simultaneous state copies, a provisional preparation swap, ordered lag updates, a finite user mode, a dimensional clock and tensor stress. Tests use hand-computed outcomes and cover preparation/advance success, exact full-parent rollback after later failure, strict guard signs, inactive invalid right-hand sides, non-finite intermediate values, lazy branches, repeated candidates, restart roundtrips, invalid phase dependencies, units, shapes, fields, input values and resource bounds. They establish this Python contract's behavior; they do not establish a constitutive law or time integration method.

HIST-G2/G3 advance for this bounded reference. Legacy adapters and their migration tests, coupled nonlinear controls, accepted internal subdivisions, complete-step subzone reductions, external command APIs, durable lineage negotiation, native/Wasm code generation and runtime parity remain open. PM4Sand's source blockers must be resolved independently before its update phases can execute. HCA's cycle-count and higher-order polarization requirements are not supplied by this scalar/symmetric-tensor envelope.
