# Current runtime closure prospective review

Reviewer `/root/md1997_review`, actual independent reviewing run, 2026-11-02. Owned only this new review directory. No source/model/reference/harness authorship; no builds or compiled/backend calls. Source-only compiler generation and mocked Python transport are used here.

## Runtime closure and candidate

Source receipt `source-freeze-v2.json` SHA2563122d681c32357cea15d9171ebfacca9ad793c749014166dac1a5aa5bea62a98 binds576files in `/private/tmp/atlas-md1997-delivery-v1/source-v2`. All576file hashes pass, and the full ordinary/source directory file inventory matches the receipt.574base files were compared byte-for-byte with git object contents at d1c3a19409adaa32791c105429a4167e5bac9d9d. Only the two declared additions are excluded from base-byte comparison: unchanged MD1997 candidate28ea763d… and exact Ramberg candidatec949cb14…, verified against respectively the model delivery file and current root definition.

The ordinary set is16models, preserving14ordinary committed definitions and adding exactly those two candidates. Ordinary-regression-policy-v2 SHA25632c703545a611d82c2680c9f1345b5678cefefe996004302457f0582a17b5ec0 covers all16unique ordinary definitions. Every definition hash, parameter insertion order/default vector and flattened complete initial state matches the source definition. All13prior policy case objects remain exactly equal, including the historical GIS failure signature. The three added default cases are Duncan–Chang, OCC and Ramberg. Default request controls/settings remain prospective; MD source-accuracy gates are separate.

I regenerated models.json/models.hpp with the frozen source Python compiler into a temporary review-owned directory. Both outputs are byte-identical to generated-current-closure-v2. Catalogue JSON file SHA256f38da28fd2857e03e1def0c2ed70dc2a5b999984ef087360b324c933a2da3a99 matches policy; embedded catalogue SHA256bedc53e3186a253e9f1e1545a7e46a5fc8fd9f76dce4f5b9721edc21347e9e7c is distinct and recorded. Every generated model object matches its source definition exactly. This is source-only generation, not compilation or backend qualification.

`check_closure.py`/closure-checks.json provide reproducible verification. One initial reviewer path error is retained; correcting repository-root lookup changed no gates.

## Interface compatibility

Read the frozen current cpp/main.cpp and CMakeLists against unchanged native/Wasm transports. Required generic exports atlas_integrate_with_settings, atlas_linearize_with_settings, atlas_run_controls_scope_with_settings and atlas_run_scope_with_settings have matching argument signatures/order. Current native CLI supports run/run-controls/integrate/linearize, integration settings, exact hex control file and stress-scope response contract. Full state/strain/control points, control bits,14x6update tangent, accepted_fixed/selected_fixed contract and partition diagnostics remain available. CMake ordinary target remains atlas_solver, with modularized ESM/ccall for Wasm. No source-level interface incompatibility found. Actual exported functions and embedded candidate identity still require compiled receipts/execution.

This576file runtime closure is not a full website/package receipt: tools/web/catalogue integration and dedicated application profiles still require separately frozen E6/E7 work. It cannot itself prove current application or live delivery. Earlier871closure and its13model policy remain historical and must not certify the new16model application.

## Ordinary runner review and mocked failures

ordinary-regression-v2 only checked GIS failure message/point count. Mock points=[{}] passed as its retained committed point. New ordinary-regression-v3 requires complete exact initial state, zero strain/control and finite state for that historical failure. Its unchanged16case policy retains the original exception rather than adding one. Twelve mocked tests preserve the v2 false accept and verify v3's ideal pass plus9corruption rejections. Missing/wrong success points/state/control, transport error, missingGISpoint/wrongmessage/corruptparent/corruptstrain fail. These are fictitious Python responses with no executable invoked; complete synthetic backend reports are not retained as material evidence.

## Raw-response retention finding

Original execution-v1 parsed nonfinite JSON extensions with json.loads, then its allow_nan=False record writer raised outside the catch before logging raw stdout. A mocked NaN response confirms raw loss. Prospective execution-v2 changed only parsing to reject parse_constant tokens within the catch, preserving NaN and +/-Infinity raw responses. A further mocked valid-JSON overflow numeral1e999 still parses to inf and loses the raw response in record serialization. `check_transport_v2.py`/transport-v2-checks.json retain this result alongside finite1e100 behavior. This remains an evidence-preservation blocker for execution-v2; it does not change material requests or numerical gates. Validating parsed response finite-JSON serializability within the existing try/catch can close it under a new prospective transport identity.

The previously accepted material source gates/parity-v4 numerical policy remain intact. Final current-closure execution acceptance awaits that last transport preservation fix and binding the ordinary runner to it. E5 scientific approval and E4 backend results remain pending actual independently checked native/Wasm observations.
