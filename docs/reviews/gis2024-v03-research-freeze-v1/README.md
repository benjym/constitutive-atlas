# GIS2024 v0.3 research artifact and prospective qualification freeze

INT-gis2024-v03-research-freeze-v1, 1 November 2026. A distinctly named
[research model](model.json) now declares the complete v0.3 contract. Normal
validation and code generation pass. This is preparation, not backend qualification
or a new public model. No compiled build or material trajectory was run.

## Identity and mathematical bridge

`research-hp-extracted-asbs-gis-2024-v03` selects the HP/extracted-ASBS+GIS pairing
of [Mugele, Stutz & Mašín (2024)](https://doi.org/10.1016/j.compgeo.2024.106480),
[institutional full text](https://publikationen.bibliothek.kit.edu/1000171366/153009465).
Persistent model source hyperlinks and original equation locators are preserved.
The [ingestion packet](../../ingestion/hypoplastic-generalized-igs-2024/README.md)
is the authority for state/sign/source choices and unresolved review gates.
This task adds no new original-paper reading or author-code equivalence claim.

[bridge.json](bridge.json) binds the unchanged legacy record: every parameter,
derived expression, equation, domain predicate, source and numerical state field
matches exactly. Identity/name and explicit contract metadata change. All 14
components are persistent: sigma6,e,h6,Omega. There is no implicit preparation,
multiplier, reset or physical clock. The contract is strain-path rate,
small-strain 3D, zero-spin fixed spatial, compression-positive Mandel, effective
Cauchy stress. Initialization requires every physical field explicitly; existing
initial values are examples only. No existing record is migrated or rewritten.

## Frozen inputs and gates

[trajectory-requests.json.gz](trajectory-requests.json.gz) contains 20 literal
initial-state/parameter/settings/ordered-strain requests: four existing reference
paths, each at three tolerances and two additional seven-part caller runs.
There are 204 base trajectory updates per backend, plus the separately required
probe/recovery and fresh-context restart suffix calls. The 17-digit wire strings reproduce the same
binary64 values as the retained study. Each subsequent call must use its own
backend's preceding returned state. No reference endpoint or hidden history is
injected. Compare all 14 components at each of the three original-segment endpoints;
keep the distinction between caller points and independent reference samples.

[policy.json](policy.json) preserves original endpoint, reference adequacy,
volume, temporal-refinement and caller-partition criteria. Reference uncertainty
allowances are stress1e-4Pa,e1e-12,h1e-13,Omega1e-10; stored fine-grid differences
must be below one quarter of each. Normalized endpoint bounds are .005,.0003,
.00002 for local rate tolerances1e-4,1e-6,1e-8; they are global regression
allowances, not local error certificates. Native/Wasm scaled parity is limited
to1e-7. State scales and all inequalities are explicit in the policy; no failed
case may be removed. Stored references are reused without a new ODE replay here.

[probes.json](probes.json) freezes nine probe fixtures plus recovery and restart
semantics: negative e, invalid Omega endpoints, exterior memory, zero pressure,
malformed state/parameter arrays, a three-substep budget and exact zero increment.
The late-budget fixture **must fail after accepted internal work**; if it does
not, the late-failure gate fails rather than changing its budget after observing
results. Structurally valid failures must return all 14 incoming committed
components exactly. Layout-error envelopes have their own API contract.
After each probe, an identical valid control must reproduce the clean control's
state in the persistent backend. For all20trajectories, restart at the first
original endpoint and compare identical suffixes in continued and fresh contexts,
using the full captured state/parameters/settings. Zero loading preserves state;
it is not a physical-time hold experiment. Full-update tangents are outside
this qualification scope.

These fixtures select bounded interior histories and explicit rejection cases;
they do not establish arbitrary saturated-state integration, finite rotations,
source-matched specimen preparation, experimental validity or complete source
admission. Strict computed-memory norm and suppression-underflow limitations
from the ingestion dossier remain in force.

## Checks and reproduction

[prospective-freeze.json](prospective-freeze.json) pins candidate, bridge,
requests, probes, policy and staging code before generation or compiled execution.
[source-pins.json](source-pins.json) binds 420 normal source/reference files.
[preflight.json](preflight.json) records 20 accepted explicit initializations,
five expected domain rejections and valid literal wire layouts. API, late-failure,
zero and restart behavior remain unexecuted backend requirements.
Normal generation succeeds twice with identical models.hpp/models.json bytes;
[generation-reproduction.json](generation-reproduction.json) retains both results.
No third-party author binary or compiled artifact was executed.

From repository root:

```sh
python3 docs/reviews/gis2024-v03-research-freeze-v1/verify.py
python3 docs/reviews/gis2024-v03-research-freeze-v1/prepare.py /private/tmp/atlas-gis2024-v03-new
```

`verify.py` checks saved evidence and reconstructs requests against retained
reference/legacy input records; it does not integrate or compile. `prepare.py`
requires a new exclusive directory, checks hashes and initialization, copies the
pinned normal sources, installs only this candidate as a top-level model and
uses the normal generator. It never builds. The public root catalogue and legacy
research bytes are unchanged.

## Next bounded task

Freeze the standard-API backend driver and an independent saved-output assessor,
including corruption/coverage/rollback/restart tests, against these unchanged
inputs and criteria **before any compiled observation**. The driver must retain
raw outputs before assessment and check actual model/canonical catalogue identity.
Then build one explicit native atlas_solver target with --parallel1; execute the
frozen matrix/probes and stop qualification on failure. Wasm follows only after
native acceptance, serially. No repeated development fitting or extra trajectory
families belong in this task. Public catalogue compatibility, browser lifecycle,
author-release/source review and scientific admission remain separately gated.
