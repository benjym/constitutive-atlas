# SANISAND v0.3 research candidate and prospective backend freeze

Completed 1 November 2026. This packet completes the candidate/preflight task,
not numerical qualification or scientific admission. It uses the existing generic
DSL/compiler and recorded-path API. Existing model records and the public catalogue
are unchanged.

## Identity and source

[model.json](model.json) is the distinctly named project variant
`research-sanisand-2004-fixed-memory-be-v03`, based on
[Dafalias & Manzari (2004)](https://doi.org/10.1061/%28ASCE%290733-9399%282004%29130%3A6%28622%29).
The [independent reference derivation](../../references/sanisand-project-monotonic-v1/DERIVATION.md)
and its source-reading receipt preserve equation/page/table locators and the private
paper hash. See the [source-closure ledger](../../ingestion/sanisand-2004/production-closure-v1/README.md)
for unresolved source decisions. No copyrighted source is bundled here.

[bridge.json](bridge.json) records exact equality of parameters, derived terms,
domain, residual equations and numerical state layout with the legacy research
record. The explicit v0.3 contract declares small-strain spatial Mandel tensors,
compression-positive effective Cauchy stress, a strain-path incremental residual,
and explicit initialization. Persistent fields are stress, void ratio, backstress,
fabric and loading-process anchor (25 values). The 26th value, gamma, is the
temporary rescaled multiplier Delta_lambda times endpoint hardening coefficient;
it is not accumulated plastic strain. The fixed anchor has no reversal-reset rule.
There is no physical clock or finite-rotation update in this variant.

One conservative initial guard requires positive hardening-image projection when
hardening distance is zero and a normalized direction exists. The elastic cone
centre is exempt. This is a project support restriction, not an added source
equation or proof of equivalence at excluded states. The first attempted `==`
syntax was rejected by the DSL; [the failure](initial-validation-failure.json)
and original attempt are retained. The accepted `<=0` test selects zero under
the existing nonnegative-distance domain. No shared parser change was made.

## Frozen study

[prospective-freeze.json](prospective-freeze.json) binds the candidate, source pins,
[policy](policy.json), [literal requests](trajectory-requests.json.gz),
[wire summary](wire-summary.json), bridge and [negative/transaction probes](negative-probes.json)
before any candidate integration or compiled observation.

There are 27 manufactured paths (three pressures, three void ratios and
compression/extension/general shear), each at 256/512/1024 plastic caller intervals:
81 requests and 48,465 material intervals per backend. Every candidate carries its
own full history. The exact-reference first-yield coordinate is supplied as an
initial caller partition; this qualifies entry-aligned plastic continuation,
not a generic event locator or arbitrary unsplit-entry accuracy.

Reference inputs use intended decimals; candidate inputs use explicit nearest
binary64 values. The wire reconstructor checks every endpoint from Decimal85
Cartesian-to-Mandel construction. No interpolated reference state or subsequent
history injection is allowed. The maximum input strain rounding is about 1.735e-18;
no rigorous propagated response bound is asserted.

The frozen fine-path gate is 1% scaled state error (stress divided by initial
pressure; other persistent components by one), with a 0.8 refinement ratio above
the 1e-5 floor. Entry, yield, trace, control, zero-anchor and native/Wasm parity
have separate gates. These are research qualification thresholds, not a release
accuracy or calibration claim. All requests must succeed. Rejection, recovery,
rollback, immutable-parent trial/retry and full-state restart probes are specified;
late internal-substep rollback is not established by a tiny-budget failure alone.
The backend driver and assessor must be frozen and corruption-tested before
backend execution. No full-update tangent is qualified here.

## Delivered checks and reproduction

[preflight.json](preflight.json) records normal schema/dimensional validation,
exact mathematical bridge, 81 request-layout checks, 81 successful explicit
initializations covering 27 distinct states, and ten expected initializer
rejections. Malformed API layout and forced nonlinear failure remain backend checks.
Normal generation succeeded twice with identical output hashes; see
[generation-reproduction.json](generation-reproduction.json). No material integration
or compiled build was performed.

From the repository root:

```sh
python3 docs/reviews/sanisand-v03-research-freeze-v1/verify.py
python3 docs/reviews/sanisand-v03-research-freeze-v1/prepare.py /private/tmp/atlas-sanisand-v03-fresh
```

`verify.py` checks saved packet/source/reference hashes and reconstructs all wire
inputs, then repeats initialization preflight. `prepare.py` requires a new exclusive
directory, copies the pinned normal sources, installs only the new candidate as a
root model and runs the normal generator. It never builds or integrates. Compare
its generated hashes with the saved receipt. Historical-source changes require
exact-byte archive resolution, not silently refreshing pins.

## Next bounded task

Create a separately named qualification packet: freeze the standard-API driver,
independent saved-output assessor and corruption tests; build native then Wasm,
one explicit `atlas_solver` target at a time with `--parallel 1`; execute these
unchanged inputs/gates, retain full diagnostics and report every failure. Public
mixed-catalogue compatibility, browser installation, experimental comparison,
canonical reversal, source signatures and scientific admission remain separate.
Stop this preparation task here. No push or deployment.
