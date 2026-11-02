# Perzyna prospective export checker: corrections required

The checker SHA256 `998178fb09477886d769dcff88506e2cf7aa7c4c649b819fae73529b4ebfcc6c`, frozen by manifest `3aed0dcf5814952f7fbccf8e4466ec47abe2ed252fc0749656ec11c339244a21`, requires a distinct correction before qualifying new composed-browser downloads. All six manifest members match their frozen identities. No actual new export was observed or accepted here.

This reviewer did not author the checker or its proof. The review read source, the small frozen reference/policy files and three retained historical exports through bounded local Git reads. It imported only the Python offline-checker definitions; it did not invoke main, package assets, Wasm/JavaScript engines, material trajectories, browser, compiler or remote operations. Historical exports were altered only in memory to test the new release identity; they were never saved as fresh downloads.

## Blocking metadata gap

`validate_run` requires `strain_rate` to be a finite six-vector, with a documented all-null exception at creep's right initial event, but does not bind finite rates to the prescribed schedule or initial event. Exact request/controls validation and the 342 state/stress comparisons do not reject contradictory point metadata.

Independent memory fixtures retain every state/stress/reference value and replace one point's strain_rate with `[1e99]*6`. All three still pass `assess`:

- rate loading point2 at time0.5, whose prescribed vector is fixed by the rate schedule;
- relaxation point2 at time0.5, whose prescribed strain rate is zero;
- creep point0 at the left initial event, whose initial strain rate must be zero.

The relaxation fixture copies the same mutation into reset/replay, preserving their exact parsed equality. Thus reset/replay equality cannot repair this validation gap. See `check-results.json` and `check_sources.py` for exact reproduction.

A successor must explicitly bind initial left-event rates to the source request's zero vector; relaxation and rate-control event/interior rates to their exact prescribed vectors; and the documented unresolved creep right event to its exact supported representation. Add adversarial finite wrong-rate mutations, including event placement, to the frozen proof. No numerical threshold or state/stress oracle change is needed. Preserve this checker and failure witness unchanged.

Solved creep rates at later points lack an independent rate-vector oracle in the selected frozen references. Their finite/shape admission can remain an explicitly bounded limitation unless a separately justified inverse-law check is specified; do not invent a reference from the observed new export.

## Positive findings and remaining gates

The stable package-identity hash includes all identity fields except release_revision, which is explicitly checked against the supplied exact revision. `check_package` rehashes the declared nine engine/approval/review/source receipt assets and all identity-listed components, with safe component basenames. Frozen policy and reference hashes, exact solver settings and unchanged `max(absolute, relative*abs(reference))` thresholds are enforced. All13 state and6 stress components are checked individually at all6 points for all3 modes:342 comparisons. Numeric vectors reject booleans, wrong lengths and nonfinite values; JSON loading rejects duplicate keys, unsafe integer tokens and nonfinite numeric tokens. Result/control/request key sets, times, sides, segments, strain/state binding and diagnostic types are checked. Reset/replay require exact complete parsed equality. Output is create-only.

The retained historical memory baseline independently passes342 comparisons under its synthetic new provenance, demonstrating transport compatibility only. Actual package-asset bytes, new browser-download origin, visible controls, replay actions, concurrency and live delivery remain untested. An offline checker cannot establish freshness merely from matching provenance; actual browser evidence remains separately mandatory.

Reproduce with `python3 -B docs/ingestion/hypoplastic-interface-2016/browser-v2/perzyna-checker-review-v1/check_sources.py`. Smallest next action: independently review a distinct adapter successor with exact prescribed/event rate validation, then apply it to actual new downloads from the qualified composed package.
