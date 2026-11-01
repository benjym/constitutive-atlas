# Additive current frontend package v2 review

Separate reviewer run `/root/occ_delivery_gate_review`, 2026-11-01. Own scope is this new additive report and bindings. Earlier accepted reviews/manifests are preserved. No product, canonical ledger, compiled/native/Wasm execution or browser action was performed by this reviewer.

**Verdict: accept the exact v2 frontend/package with its explicitly frozen engine for the observed local browser scope; do not claim exact-current production-runtime closure.** The latter has a material concurrent source mismatch described below. This distinction does not invalidate the actual frozen-package browser runs, but blocks treating them as verification of a build from every current checkout production byte. CI, scientific approval, release and live deployment remain separate.

## Exact package and browser observations

Manifest SHA-256 `d426db46720e5da743382c6e5402a6d9304a595f0f51d25e7c1ed843e32956eb` binds887 files in `site-v2`. Independent rehashing found every file matches, the exact file set matches, all42 retained public source files match the checkout, and all8,032 captured inputs match the v2 freeze. The standard builder returned0 with empty `changed_inputs`. The supported-package-v2 report passes its thirteen-model policy plus GIS named example. These are bounded supported-input claims; the earlier strict GIS ordinary-default step1 failure remains unwaived.

The v1→v2 package has the same file set and exactly seven changed files: `app.js`, three engine identity files and three corresponding package manifests. Engine identity changes are exclusively `release_revision`, from `5ae90008d44575ef4b92b2b9e6e34fe1ca1f47b3` to `302f2adc06d39b634e1865899e24ff088cc32f72`; engine modules/Wasm, models, scientific review and approval bytes remain identical. Package manifests consequently rebind those identity bytes. The sole frontend source change replaces a general formulation section with a `Physical-time formulation` heading and dedicated-laboratory explanation for a timed route, leaving the ordinary formulation path unchanged.

The retained actual Playwright v4 process on loopback18774 returned0. This reviewer independently checked all15 fetched hashes against the v2 manifest, nine successful101-point exports containing all7 OCC state components, exact default/import replay except elapsed time, final quick-request target `.004`, and all five protocol exports. Error/bad-response arrays are empty. The existing browser-v4 verification records source-consistent initialization/reference changes and no source drift during that browser run. The new current-route-v2 process also returned0: it visibly found the changed physical-time heading on the power-creep catalogue entry, navigated to `power-creep.html`, returned to OCC and recovered the successful ordinary run/approved badge without page or HTTP errors. That route receipt does not itself test a power-creep numerical run; previous dedicated engine qualification remains separately bound.

## Material current-production mismatch

The stronger assertion that production source is unchanged is **false relative to the current checkout**. An initial reviewer hash assertion failed on this comparison; the explicit mismatch is retained in `current-package-v2-checks.json`, rather than suppressed. Three current files differ from prospective-v1 and the frozen source used for the packaged common engine:

- `cpp/include/atlas/solver.hpp` adds a non-dyadic one-third/two-thirds retry after a failed residual update, records accepted/discarded increment tensors and exposes partition diagnostics.
- `cpp/include/atlas/linearize.hpp` replays actual accepted increment tensors for that retry rather than only fraction-scaled increments.
- `cpp/main.cpp` emits the new partition diagnostics in several response paths.

These are substantive runtime/response changes, not merely archive-map or frontend edits. The packaged common module/Wasm remains identical to v1 and matches its preserved frozen source snapshot; it therefore does not execute these newer current changes. The v2 broad input freeze accurately records current file hashes but is not proof that those current C++ bytes produced the older engine. The standard builder's matching-model-catalogue guard does not establish that compiler/runtime source identity.

Smallest next action: the coordinating owner must explicitly segregate these concurrent runtime changes from the frozen delivery scope, or separately qualify and package the newly changed runtime before claiming exact-current production delivery. Such qualification must include affected retries/tangents/diagnostics and ordinary-model regression/parity; this reviewer neither directs an unapproved build nor declares the changes defective. Existing frozen-engine parity evidence remains valid for its original bytes. A separately reported clean Python/CI campaign is not assessed or inferred here and cannot silently rebind these engine bytes.

`current-package-v2-checks.json` records successful package/browser assertions alongside `exact_current_production_closure_passed: false`. `current-package-v2-bindings.json` binds the reviewed new and old manifests, browser exports, code and differing current/frozen runtime files. `current-package-v2-manifest.json` binds only this additive review. No earlier accepted record is rewritten or repinned.
