# norsand-1993 — ingestion packet

Task ING-norsand-1993 / MODEL-norsand-1993; lead `/root`, 2026-11-01. Follow the [E0–E8 delivery ledger](DELIVERY.md). Full source packet: [supplied original and contract](supplied-original-v2/README.md).

## Identity and sources

M.G.Jefferies1993, *Nor-Sand: a simple critical state model for sand*, Géotechnique43(1),91–103, [DOI10.1680/geot.1993.43.1.91](https://doi.org/10.1680/geot.1993.43.1.91). The user supplied all13original pages. [Receipt](supplied-original-v2/source-receipt.json) binds1,100,155private bytes to SHA256fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9. Lead and separate reviewer inspected every page including equations5–12, Table1 and notation. Copyrighted source/text/renders remain ignored/private. Earlier [access failures](delivery-v1/) and [bounded gap review](delivery-v1/independent-review/README.md) remain historical evidence, superseded only as to current acquisition status.

## Existing work and gaps

The [source report](supplied-original-v2/README.md) now replaces provisional text-only ingredient lists with image-verified equations, exact branch exponents and current-image-state ordering. Historical source audits and the paper tree are unchanged. The [independent original-source review](supplied-original-v2/independent-review/README.md) accepts the exact source/contract packet; this is not E5 model approval.

## Equations and schema crosswalk

See the complete [equation inventory, units, state, initialization, domains and parameter examples](supplied-original-v2/README.md), and non-executable [v0.3 crosswalk](supplied-original-v2/crosswalk.json). Original rigid-plastic, rate-independent, associated axial effective-stress scope is preserved; later elasticity, fabric/cyclic rules and general3D closure are excluded. The original requires mixed triaxial controls; current v0.3 arbitrary full-strain inputs cannot simply be relabeled to supply that interface. [Capability handoff](supplied-original-v2/CAPABILITIES.md) records the minimal source-derived witness and generic alternatives.

## Temporal integration and transactions

Source p98 specifies forward differences with consistency but no complete finite algorithm. The packet explicitly separates source incremental equations from reconstructed void-ratio kinematics and prospective finite-step/control/rollback/restart choices. The new [controlled-path capability](e2-v3/README.md) now supplies a reviewed staged contract/interpreter/C++ runtime proposal; all9long-path independent reference and interpreter cases pass. E2 is complete after separately reviewed shared profile integration; staged native/Wasm58requests/backend already pass with exact agreement. No physical-time dependence, elastic predictor, ignored strain components or unsupported unloading branch is introduced.

## Independent checks

Frozen [algebra policy](supplied-original-v2/algebra-policy.json) and [results](supplied-original-v2/algebra-results.json):425checks at each70/110Decimal digits,850total, covering yield inversion, normality, image/limiting-state identities, N=0 limits, pressure-reference conversion, work conjugacy, local constant-cell derivative and invalid domains. Separate reviewer reproduced all850 and supplied independent finite-difference/source algebra checks. That source-packet study ran no production candidate. A later separate [staged interpreter study](e2-v3/interpreter-qualification-v1.json) passes9active-path cases against independent original-equation references. That interpreter study does not itself establish compiled/browser qualification. Later separate58request/native and58request/Wasm studies pass; actual main-browser qualification is pending.

Reproduce from repository root:

```sh
python3 -B docs/ingestion/norsand-1993/supplied-original-v2/check_packet.py
python3 -B docs/ingestion/norsand-1993/supplied-original-v2/independent-review/check_source_algebra.py
```

The packet checker verifies8public hashes,2retained schema/contract hashes, exact private source and13pages, and exact algebra replay. Review binds12inputs/5reviewer outputs; parent verified all17before integration.

## Handoff

E1 source complete. E2/E3 now have a declarative candidate, generic staged profile/runtime, independent static/source/reference review,29generic checks and9passing original-equation interpreter cases; all13public model generations remain byte-identical. See [current capability evidence and58frozen backend requests](e2-v3/README.md). The separate native/Wasm capability target passes58requests per backend with exact agreement; shared-profile integration/durable CI, E5approval, atlas/browser and live delivery remain open. [Delivery ledger](DELIVERY.md) tracks the full assignment; this staged capability is not completed model delivery.

## Shared profile installation

[Shared integration](shared-integration-v1/README.md) is independently accepted: exact generic profile/schema/runtime and normal generator routing installed;25Python tests PASS(3opt-in native skips);13public generations and3controlled-path generated files unchanged. The exact draft candidate lives at `models/research/norsand/norsand-jefferies-1993-active-axial.json`, with named example `catalogue/path-examples/norsand-1993-loose-constant-cell.json`. E2/E3complete. Fresh durable target/CI qualification is queued behind the active serial owner; E5 approval and main-atlas/browser/live delivery remain pending. [Generic browser bridge](browser-v1/PLAN.md) is staged for independent prospective review and existing-artifact qualification, without a standalone-page completion claim.


## Current full-delivery status —2026-11-01

The exact original active drained axial variant has completed E0–E5 independent scientific approval and bounded local E6/E7 main-atlas/browser qualification. [Delivery ledger](DELIVERY.md), [local audit](atlas-v1/delivery-check-v1.json), [public download](atlas-v1/downloads/norsand-1993-qualified.zip). The19file download exactly replays the41point browser export offline; raw copyrighted PDF is excluded. E8 remains open: no remote authorization/deployment and separately owned shared release findings remain. Earlier staged/gap descriptions above are retained historical packet states.
