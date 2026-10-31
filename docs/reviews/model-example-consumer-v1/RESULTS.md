# Complete model-example consumer — verified locally

The laboratory now loads the selected definition's default parameters and complete declared initial state together, including confinement and axial/radial stress ratio. A visible **Load model example** action restores those values while retaining the current protocol, history, target, increment count and numerical settings. The visible notice identifies illustrative inputs and their preparation/calibration limits. Model source links and manual fields remain available. Import bypasses example loading and restores the complete saved specification.

The generic helper rejects unsupported axisymmetry/shear, out-of-range confinement/ratio and incomplete/nonfinite state/default parameters without dropping stress components. This checks the consumer representation; it does not establish material-domain admissibility or mixed-control solvability. All seven root definitions retain their100kPa spherical example; the separately tested clay candidate declares10kPa. No model-specific branch was introduced.

## Prospective policy and results

[Acceptance](acceptance.json) and [after-input/engine manifest](after-manifest.json) were recorded before browser-flow observations. [Before snapshots](before-manifest.json) preserve historical app/HTML/state-helper/test bytes; original integration receipts and the clay2013 failed100kPa study are unchanged.

Seven Node helper checks pass, including the separate10kPa example, tensor history/temporary slots, copy isolation and invalid support. The three Python browser-contract wrappers pass. All seven actual browser default exports succeed with101points each, matching each definition's full initial state and parameter defaults (parameter display conversion within1e-14relative-to-max(1,default), as declared in the collection script before those observations). No native or Wasm rebuild was needed; the exact previously verified seven-model production engine was reused and its hashes are pinned.

The custom elasticity run uses125kPa radial stress,1.2axial/radial ratio,E40MPa, oedometer,.2%strain,20increments and rate tolerance2e-6. Loading its model example restores100kPa spherical stress/E30MPa while preserving every loading/settings value. Import of the saved custom export reproduces its complete specification exactly. Reset restores the complete model and form defaults. The four raw exports and seven-model exports are retained here. [Console](console.txt) reports zero messages/errors/warnings. Real screenshots were visually inspected: action/notice and response plots remain legible; source links remain present.

The first collection helper had a syntax error before any calls; its source and explanation are retained. No model equations, initialization validators, solver settings, schema, catalogue count, experimental files or scientific status changed. The original failed clay default remains failed. A separately frozen candidate study is still required before a new local draft installation. No push or deployment.

Reproduce evidence verification with `python3 docs/reviews/model-example-consumer-v1/verify.py`. The verifier checks retained source/engine identities and recorded browser exports, not a fresh interactive browser session.
