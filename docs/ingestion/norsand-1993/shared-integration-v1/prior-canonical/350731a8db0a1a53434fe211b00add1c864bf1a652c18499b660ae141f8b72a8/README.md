# norsand-1993 — ingestion packet

Task ING-norsand-1993 / MODEL-norsand-1993; lead `/root`, 2026-11-01. Follow the [E0–E8 delivery ledger](DELIVERY.md). Full source packet: [supplied original and contract](supplied-original-v2/README.md).

## Identity and sources

M.G.Jefferies1993, *Nor-Sand: a simple critical state model for sand*, Géotechnique43(1),91–103, [DOI10.1680/geot.1993.43.1.91](https://doi.org/10.1680/geot.1993.43.1.91). The user supplied all13original pages. [Receipt](supplied-original-v2/source-receipt.json) binds1,100,155private bytes to SHA256fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9. Lead and separate reviewer inspected every page including equations5–12, Table1 and notation. Copyrighted source/text/renders remain ignored/private. Earlier [access failures](delivery-v1/) and [bounded gap review](delivery-v1/independent-review/README.md) remain historical evidence, superseded only as to current acquisition status.

## Existing work and gaps

The [source report](supplied-original-v2/README.md) now replaces provisional text-only ingredient lists with image-verified equations, exact branch exponents and current-image-state ordering. Historical source audits and the paper tree are unchanged. The [independent original-source review](supplied-original-v2/independent-review/README.md) accepts the exact source/contract packet; this is not E5 model approval.

## Equations and schema crosswalk

See the complete [equation inventory, units, state, initialization, domains and parameter examples](supplied-original-v2/README.md), and non-executable [v0.3 crosswalk](supplied-original-v2/crosswalk.json). Original rigid-plastic, rate-independent, associated axial effective-stress scope is preserved; later elasticity, fabric/cyclic rules and general3D closure are excluded. The original requires mixed triaxial controls; current v0.3 arbitrary full-strain inputs cannot simply be relabeled to supply that interface. [Capability handoff](supplied-original-v2/CAPABILITIES.md) records the minimal source-derived witness and generic alternatives.

## Temporal integration and transactions

Source p98 specifies forward differences with consistency but no complete finite algorithm. The packet explicitly separates source incremental equations from reconstructed void-ratio kinematics and prospective finite-step/control/rollback/restart choices. The new [controlled-path capability](e2-v3/README.md) now supplies a reviewed staged contract/interpreter/C++ runtime proposal; all9long-path independent reference and interpreter cases pass. E2 remains open pending shared profile integration (NS-HOST-01); staged native/Wasm58requests/backend already pass with exact agreement. No physical-time dependence, elastic predictor, ignored strain components or unsupported unloading branch is introduced.

## Independent checks

Frozen [algebra policy](supplied-original-v2/algebra-policy.json) and [results](supplied-original-v2/algebra-results.json):425checks at each70/110Decimal digits,850total, covering yield inversion, normality, image/limiting-state identities, N=0 limits, pressure-reference conversion, work conjugacy, local constant-cell derivative and invalid domains. Separate reviewer reproduced all850 and supplied independent finite-difference/source algebra checks. That source-packet study ran no production candidate. A later separate [staged interpreter study](e2-v3/interpreter-qualification-v1.json) passes9active-path cases against independent original-equation references. No native/Wasm or browser was run.

Reproduce from repository root:

```sh
python3 -B docs/ingestion/norsand-1993/supplied-original-v2/check_packet.py
python3 -B docs/ingestion/norsand-1993/supplied-original-v2/independent-review/check_source_algebra.py
```

The packet checker verifies8public hashes,2retained schema/contract hashes, exact private source and13pages, and exact algebra replay. Review binds12inputs/5reviewer outputs; parent verified all17before integration.

## Handoff

E1 source complete. E2/E3 now have a declarative candidate, generic staged profile/runtime, independent static/source/reference review,29generic checks and9passing original-equation interpreter cases; all13public model generations remain byte-identical. See [current capability evidence and58frozen backend requests](e2-v3/README.md). The separate native/Wasm capability target passes58requests per backend with exact agreement; shared-profile integration/durable CI, E5approval, atlas/browser and live delivery remain open. [Delivery ledger](DELIVERY.md) tracks the full assignment; this staged capability is not completed model delivery.
