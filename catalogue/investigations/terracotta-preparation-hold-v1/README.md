# Terra Cotta end-to-end preparation/hold study v1

**Reference and prospective request stage complete; compiled execution pending.** The [independent reference packet](../../../docs/ingestion/terracotta-2024/preparation-hold-reference-v1/README.md) retains the failed original source quadrature study and a separately frozen passing refinement. Its v2 full-path reference regenerates byte for byte in the coordinator's clean temporary copy, and all957 numerical assertions plus zero-temperature inversion rejection pass. The transport/freeze audit passes ten checks, including five corruption probes. Neither implementation imports Atlas or author code.

The new schedules prepare for10s and then hold total stress for20s, with compression, extension and isotropic paths at tolerances1e-4,1e-6,1e-8. `requests.json` contains all nine explicit requests, validated against the current schedule schema/temporal contract. `assemble.py` maps source parameter names K/G/M/p1 explicitly to unchanged model names Kmod/Gmod/Mcrit/pOne. New source-reference work targets v0.3; the historical research definition remains unmodified v0.2, with no migration or new executable-model claim.

Unlike the earlier prepared-creep study, each backend will run a single schedule starting before preparation. It must carry its own computed preparation state and accumulated strain into the hold and capture its own incoming-rate total stresses. The independent reference likewise carries each refinement's own endpoint. No backend receives a replacement reference endpoint or fixed numerical hold target.

`policy.json` fixes the intended scope and inherited fine component limits before compiled observation. `assess.py` checks complete ordered23point responses, exact state/strain continuity, incoming stress capture, one physical clock, masked boundary rates and separate preparation/hold errors. Six contract tests pass using explicitly synthetic reference-shaped responses; these test request construction and rejection of reset clocks, replaced state, changed captured stress and missing runs. They are **not solver observations**.

`request-freeze.json` binds the prospective request/policy/assessor stage to exact independent reference and model bytes; `coordinator-validation.json` retains checks. A **complete compiled-source freeze remains pending**. No numerical result for this study identity is claimed yet.

The direct author journal PDF request returned HTTP403, publisher PDF browsing returned a cache miss and the publisher landing route returned403 on this follow-up. No journal PDF bytes, page-image checks or source closure are claimed. This study uses the existing pinned author-image Figure1 law and unchanged research definition; source strictness and author mixed-control discrepancies remain open.

Next: freeze the full model/compiler/C++/collector source closure and generated declarations, build isolated native then Wasm with one target/worker, collect every raw outcome, and assess both phases against the unchanged policies. No tolerance relaxation, scientific admission or public deployment follows from this input stage.

```sh
python3 -B -m unittest tests.test_terracotta_preparation_hold -v
```
