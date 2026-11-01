# Actual paired fixture review

Decision: **ACCEPTED for the bounded native/Wasm control derivative fixture pair only.** Reviewer compiled calls and builds: zero. No blocking finding in this scope. This does not approve the generic capability across production regressions or MD/E5.

The frozen 582-file runtime, original implementation manifest and audit-v2 supplement, native receipt, actual Wasm module and payload, generated two-model catalogue/header, retained raw reports, process transcript and serial Release build records all match their recorded identities. One saved Node worker creates one engine and calls the fixture twice. Both calls contain the same ordered 25 groups. The two Wasm raw outputs repeat exactly.

Recomputing saved evidence gives all **7,469 original paired checks and 2,590 supplemental audit checks passing**, with the same check multisets as the coordinator records. A separate 23-check review validates the bindings and full parsed objects. Every native/Wasm parsed fixture value is exactly equal, including helper decisions, receipts, states, analytic controls, invalid-parent rollback and subsequent recovery already examined in the native actual review.

Raw cross-backend output bytes differ: native length 69,506, Wasm length 69,505, solely the native terminal newline. Both repeats satisfy native_stdout == wasm_stdout + newline. The original receipt honestly records full_fixture_byte_parity=false; the two additive notes accurately distinguish this from zero parsed-value differences. No policy or receipt rewrite is needed.

Exact Wasm module SHA-256: `0b39463f53ce79917e6a33b1e23d5b1484150b6d1a96f4306b059529fa222ae3`; payload: `642db15f38450fb434cb397af8646a5f5499f74b4724da2217d3b1893f5e0409`; raw report: `48433af82dc5afe5266ce0853f2d446de4ef2bcb694da6e6aec03daa47fb6e47`.

Reproduce with `python3 check_saved.py` from this directory only after selecting fresh output filenames: the mandatory original checker preserves existing output files. No artifact is executed by this review script. Initial reviewer assertions wrongly expected the worker rows to already contain collector-added parsed responses, then expected deterministic order from a checker traversing sets. Those reviewer-only failures and the first successful checker output are retained; corrected checks compare raw fields and full check multisets. They did not expose evidence failures or change any acceptance gate.

Remaining next action: coordinator-owned production regressions on the exact runtime, including original coarse MD failures, separately rebound resolution study, ordinary defaults and affected profiles/transaction diagnostics. Original MD source-accuracy failures remain failures; fixture parity supplies no scientific admission.
