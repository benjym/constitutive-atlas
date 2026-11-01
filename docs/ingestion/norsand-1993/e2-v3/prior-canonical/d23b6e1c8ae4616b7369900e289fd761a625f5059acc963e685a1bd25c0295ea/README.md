# norsand-1993 — ingestion packet

Task ING-norsand-1993 / MODEL-norsand-1993; lead `/root`, 2026-11-01. Follow the [E0–E8 delivery ledger](DELIVERY.md). Full source packet: [supplied original and contract](supplied-original-v2/README.md).

## Identity and sources

M.G.Jefferies1993, *Nor-Sand: a simple critical state model for sand*, Géotechnique43(1),91–103, [DOI10.1680/geot.1993.43.1.91](https://doi.org/10.1680/geot.1993.43.1.91). The user supplied all13original pages. [Receipt](supplied-original-v2/source-receipt.json) binds1,100,155private bytes to SHA256fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9. Lead and separate reviewer inspected every page including equations5–12, Table1 and notation. Copyrighted source/text/renders remain ignored/private. Earlier [access failures](delivery-v1/) and [bounded gap review](delivery-v1/independent-review/README.md) remain historical evidence, superseded only as to current acquisition status.

## Existing work and gaps

The [source report](supplied-original-v2/README.md) now replaces provisional text-only ingredient lists with image-verified equations, exact branch exponents and current-image-state ordering. Historical source audits and the paper tree are unchanged. The [independent original-source review](supplied-original-v2/independent-review/README.md) accepts the exact source/contract packet; this is not E5 model approval.

## Equations and schema crosswalk

See the complete [equation inventory, units, state, initialization, domains and parameter examples](supplied-original-v2/README.md), and non-executable [v0.3 crosswalk](supplied-original-v2/crosswalk.json). Original rigid-plastic, rate-independent, associated axial effective-stress scope is preserved; later elasticity, fabric/cyclic rules and general3D closure are excluded. The original requires mixed triaxial controls; current v0.3 arbitrary full-strain inputs cannot simply be relabeled to supply that interface. [Capability handoff](supplied-original-v2/CAPABILITIES.md) records the minimal source-derived witness and generic alternatives.

## Temporal integration and transactions

Source p98 specifies forward differences with consistency but no complete finite algorithm. The packet explicitly separates source incremental equations from reconstructed void-ratio kinematics and prospective finite-step/control/rollback/restart choices. E2 is blocked on NS-HOST-01 (supported mixed-control/path-coordinate contract) and NS-NUM-01 (finite kinematic/discretization/transaction policy). No physical-time dependence, elastic predictor, ignored strain components or unsupported unloading branch is introduced.

## Independent checks

Frozen [algebra policy](supplied-original-v2/algebra-policy.json) and [results](supplied-original-v2/algebra-results.json):425checks at each70/110Decimal digits,850total, covering yield inversion, normality, image/limiting-state identities, N=0 limits, pressure-reference conversion, work conjugacy, local constant-cell derivative and invalid domains. Separate reviewer reproduced all850 and supplied independent finite-difference/source algebra checks. No production candidate, material trajectory, native/Wasm or browser was run.

Reproduce from repository root:

```sh
python3 -B docs/ingestion/norsand-1993/supplied-original-v2/check_packet.py
python3 -B docs/ingestion/norsand-1993/supplied-original-v2/independent-review/check_source_algebra.py
```

The packet checker verifies8public hashes,2retained schema/contract hashes, exact private source and13pages, and exact algebra replay. Review binds12inputs/5reviewer outputs; parent verified all17before integration.

## Handoff

E1 source acquisition/read/transcription review complete. E2 remains open with [separate generic capability handoff](supplied-original-v2/CAPABILITIES.md), before candidate/reference/backend tasks. Required next work is an independently reviewed generic control/finite-kinematic contract and distinct shared implementation ownership; source ingestion does not authorize shared schema/compiler migration edits. The lead retains the full MODEL assignment.

Source complete: yes, to original monotonic drained axial formulation. Executable scope: none yet. Independent numerical qualification: source algebra only. E5 model approval, atlas inclusion, packaged browser and live deployment: absent. Experimental validation: not assessed. No release authorization inferred.
