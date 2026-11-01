# Barodesy sand 2015 — current delivery qualification

The exact existing `models/barodesy-sand.json` (SHA-256
`3a61b5373404d6973a2957bd0fa21692e10b49e974cdf87eff047d5531851239`)
implements the complete Kolymbas2015 interior Eq31 law, with explicitly
disclosed fixed-spatial zero-spin small-strain scope. The seven parameters
use the separately attributed2019 illustrative calibration. The original
source packet and all historical definitions, receipts and failures remain
unchanged. The originals are retained privately by `source-retention.json`.

The ten independent diagonal references cover all five laboratory controls,
monotonic loading and reversal, including the ordinary1%/100step drained
default. They use the original tension-positive scalar exponential and RK4,
with independently solved mixed-control endpoint conditions. The oblique
full-tensor reference uses Cartesian symmetric eigendecomposition and RK4,
independently of the production matrix-exponential polynomial and adaptive
midpoint solver. Reference refinement was independently reviewed before
compiled numerical observations. `policy.json`, `prospective-freeze.json`
and `transport-freeze.json` retain the prospective inputs and gates.

These are **discrete straight-strain increments with endpoint stress control**.
They do not establish equivalence to the continuous stagewise drained-rate
closure discussed on source p59. Fixed spatial components assume zero spin;
finite rotations, FE tangents, arbitrary parameter/density support, matched
specimen preparation and experimental validation are outside this delivery.
Zero-loading continuation and conservative positive-definite nonzero-stress
support are explicit project choices. No clipping or artificial stress seed
is introduced. Physical time and viscous effects are absent.

## Current results

The serial Release common `atlas_solver` builds use isolated source revision
`b529a0efc3415b2bc567178a68174575c220cadc`; all156 prospectively frozen
source inputs were rechecked after building. Native and Wasm generated
catalogues match byte for byte. Each backend passes668 primary calls and
four additional transaction calls. All45817 compared physical output
channels match exactly across backends.

The largest default-settings stress error over the ten histories is1.07118Pa
against the prospective5Pa limit; tighter settings reduce it to0.090165Pa.
Maximum void error is1.59469e-8, below2e-7. All70 original instantaneous
rate requests retain their exact inputs and independent budgets, including
the historical trace-cancellation witness. Oblique loading/reversal,
zero continuation, all ten midpoint restarts and rejected-increment recovery
pass. The transaction supplement demonstrates complete parent preservation
after four accepted internal substeps are discarded; nonzero before/after
recovery states are bit-identical. Wasm uses a persistent instance; native
CLI calls are separate processes.

`native-results-v1/` and `wasm-results-v1/` preserve raw journals before
assessment, with exact requests and source-independent reference values.
`transaction-supplement-v1/` retains its separately prospective policy and
all four raw responses per backend. `parity.json` records the comparisons;
the build receipts identify exact artifacts and toolchains.

The first Wasm link attempt failed on the system cache lock. Its log remains;
the same target with the existing writable private cache passes without
source or gate changes. The original preview saved-only assessor passes.
The original instantaneous-rate replay command rejects the changed current
compiler source identity; `retained-rate-replay.log` preserves that diagnostic.
It is not represented as a historical replay pass. The new current70-case
qualification directly retains the original independent inputs and budgets.

## Reproduction

Regenerate the independent references using Python with NumPy:

```sh
python3 -B docs/ingestion/barodesy-sand/delivery-v1/reference.py
```

The reference generator writes the two reference files; run it in a scratch
copy when verifying immutable review receipts. NumPy is used only for the
oblique independent spectral reference; compiled qualification itself uses
Python's standard library and the saved references.

Coordinator-owned execution against the matching common-engine build uses:

```sh
python3 -B docs/ingestion/barodesy-sand/delivery-v1/qualify.py native BUILD/atlas_solver FRESH_OUTPUT
python3 -B docs/ingestion/barodesy-sand/delivery-v1/qualify.py wasm BUILD/atlas.js FRESH_OUTPUT
```

These commands execute compiled material calls and do not build. Use the
exact source/model hashes and one explicit build target with `--parallel 1`.
Approval, main-atlas integration, packaged-browser and authorized live
delivery are separate ledger stages; this numerical pass alone closes none
of those later gates.
