# Normalized drained observation replay

The experimental `prepare-replay` command connects normalized drained experiments to the common ordered control solver. It preserves every source observation, including reversals and duplicates, without sorting, trimming, interpolation or fitting. It advances NUM-04/BENCH-03 plumbing; a successful replay does not establish applicability or experimental validation.

From the repository root, using an existing solver binary:

```sh
python -m atlas.cli prepare-replay \
  tests/fixtures/experiments/synthetic-drained-elastic.json \
  protocols/drained-elastic-replay.json --output /tmp/elastic-replay.json
python -m atlas.cli replay /tmp/elastic-replay.json \
  --solver build/atlas_solver --output /tmp/elastic-response.json
```

The first command writes a directly replayable/browser-importable request and `/tmp/elastic-replay.json.provenance.json`. The second runs the existing binary; neither command builds it. The synthetic fixture follows independently derived linear isotropic elasticity with variable radial stress, nonzero initial deviator, reversal and a duplicate observation. It contains no experimental measurements.

## Mapping and admission

The [configuration schema](../schemas/drained-replay.schema.json) requires explicit declarations of fixed-frame axisymmetry about x, compression-positive normalized effective stress, signed `q = sigma_xx - sigma_rr`, and the first observation as axial-strain reference. These are caller assertions requiring a source URL and locator. Structural validation cannot establish their physical truth. Only normalized `drained-triaxial` experiments with 2–5001 observations are admitted. Arbitrary measurement-series records, undrained tests and physical-time models are rejected. Observed elapsed time, if present, is not used.

At observation i, the axial target is `initial_strain_xx + eps_a[i] - eps_a[0]`. Both radial effective stress targets are `p[i] - q[i]/3`; shear strain targets are zero. The initial radial strains must agree, and initial shear strain must be zero. All six controls act in the fixed orthonormal Mandel frame. The coordinate is the original zero-based row index, with no implication of elapsed seconds. Internal solver subdivision remains distinct from these caller observations.

This replays **measured radial effective stress**, which can vary between observations. It does not classify the apparatus as radial-stress-controlled. Measured q contributes to that constraint, so later q agreement must disclose this dependence rather than being presented as independent validation. Volumetric/radial strains remain comparison outputs; they are not imposed by this mapping.

Initial stress comes from the first observed p/q. Contradictory normalized initial effective stress is rejected. Every parameter and every remaining state field must be supplied by name, including transient fields. Nothing silently uses model defaults or infers consolidation/reversal history. Named arrays follow the model's declared state/parameter order. Model domain and initial-history admission remain the engine's responsibility. A supplied conventional void-ratio state `e` that differs from normalized `initial.void_ratio` requires `initial_void_ratio_override_note`; the provenance retains both values and the explanation. This permits explicitly labelled sensitivity studies without overwriting observations. Other history/preparation assumptions require the configuration's initialization note.

The provenance sidecar stores canonical JSON hashes of experiment/configuration/model/request, exact input-file byte hashes, source provenance, explicit declarations, strain origin and row mapping. Preserve it alongside the request and response. It records conversion lineage, not a licence grant or reviewed model/data pairing. Changing model or request after conversion requires regeneration; the native engine does not consume or verify this sidecar.

## Evidence and remaining gates

The Python tests check the independent elastic stress/volume/density solution at all six observations, duplicate-state identity, reversed named tensor-history ordering, explicit initialization overrides, closed contracts, unsupported inputs and CLI provenance/input protection. CI runs the native case with `ATLAS_RECORDED_SOLVER`. No solver or constitutive equation changed in this work. The [retained pipeline manifest](../catalogue/investigations/normalized-drained-replay-v1/manifest.json) pins synthetic results, implementation/input hashes and the passing 59-test run.

A local exploratory KFS-TMD1 run retained all 421 observations and completed using illustrative elastic parameters and source initial void ratio. This is pipeline evidence only: no fitted/material-matched baseline, source-control review or experimental accuracy claim follows. Its sampled request and full response remain outside the repository because original archive redistribution is unresolved. See [data reuse](DATA_REUSE.md). A replay request contains derived source measurements and is subject to the same publication gate; conversion does not make a permission-held dataset publishable.

Next gates are reviewed channel/control semantics and preparation metadata, applicable source-backed model/parameter pairs, comparison on ordered measured paths with disclosed input dependencies, numerical refinement and reproducible experimental benchmark manifests. Physical-time and undrained mappings need separate contracts. Browser execution uses the existing recorded-run importer; this milestone does not include fresh interactive browser QA.
