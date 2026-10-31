# Catalogue formulation and preparation summary

1 November 2026. **WEB-formulation-summary-v1** exposes the packaged definition in each catalogue detail view, before its source list. It does not create a second metadata database or change a model's scientific status.

For available definitions the panel shows canonical status and description, declared equation/time/kinematic/frame/tensor/sign/stress conventions, and expandable equation/advance inputs. Parameter defaults and ranges are labelled as examples rather than calibration. Initial values distinguish persistent material history from temporary solver fields using the existing shared state-role consumer. Mandel component ordering is shown only when explicitly declared. Legacy records retain an explicit missing-contract message; their mechanics are not inferred or migrated. Candidates without a browser definition receive no inherited defaults or state.

## Checks and scope

- Six new browser contracts cover physical time versus strain-path declarations, undeclared fields, legacy conventions, preparation/default provenance, temporary state, candidate availability, safe text rendering and all nine current root definitions. A Python discovery wrapper runs these in the normal test suite.
- Eighteen Python test methods pass, including the new wrapper, three existing catalogue checks and fourteen archive checks. [Log](tests.log) is retained. No full-project test pass is claimed.
- `tools/build_web.py` packaged nine models and628public experiment records using the existing Release Wasm artifact. Final packaged app/module bytes match the edited source. Static package validation passes beneath `/constitutive-atlas/`.
- The local browser visibly shows the v0.3 Barodesy2017 mechanics and default/state labels, the legacy elasticity missing-contract message, and Terra Cotta's candidate-only message with no test action or inherited parameter/state examples. A screenshot is recorded by local path/hash in [verification](verification.json).

No compiler or model definition changed; there was no native/Wasm build or deployment. The application retains its ordinary startup simulation with the reused Wasm artifact; this work adds no numerical study. The website's broader mobile/accessibility, per-formulation review, preparation and benchmark gates remain open, along with independent scientific review.

## Reproduction

```sh
python3 -B -m unittest tests.test_formulation_view tests.test_web_catalogue tests.test_evidence_archives -v
python3 -B tools/build_web.py --wasm-dir /path/to/verified/wasm-build --output /private/tmp/atlas-summary-preview/constitutive-atlas
```

The packaging command verifies the generated catalogue against the current definitions before copying the existing artifact. It performs no build. Historical UI/packager source bytes and the previous DP archive map were copied before editing; adjacent archive maps retain their original receipt identities. Unrelated manuscript work is untouched.
