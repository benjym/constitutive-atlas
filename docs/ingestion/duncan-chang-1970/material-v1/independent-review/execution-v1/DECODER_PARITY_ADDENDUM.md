# Prebuild decoder/parity addendum review

Reviewer `/root/duncan_complete_review`,2026-11-01. **Accept the bounded prebuild addendum.** No compiled artifact, material update or build was executed. This supplies no material numerical pass or E5 decision.

Independently compared assess-v2.py with frozen assess.py: removing only the raw-response restoration block yields exact byte equality. Scientific gates, tolerances, required successes/failures and replay bit comparisons are unchanged. The added recursive decoder reparses original C API stdout using parse_int=float, correctly preserving integer-spelled negative zero as well as decimal negative zero. A nested synthetic raw-response test reconstructed both as binary648000000000000000; ordinary zero remained0000000000000000. This repairs loss introduced by JSON.stringify in the saved parsed Wasm copy; the preserved raw stdout remains authoritative.

Read parity.py: complete-state numerical comparisons use4e-8 normalized by100000Pa; serialized normalized AD columns use4e-5 absolute difference, with finite-value checks, identities and coverage comparisons. This is within the prospective parity budget and makes no bitwise backend claim. Independent source assessments on each backend remain separately mandatory; the parity script alone does not establish either backend's source acceptance. Negative-zero reparsing is required for same-backend exact replay, whereas cross-backend parity is deliberately numerical.

Rehashed all five entries in prebuild-addendum-v2.json: every hash matches, including original freeze.json and additive input preflight. The114-file original closure and original assessor remain unchanged. Later raw observations and their assessment identities must bind this addendum explicitly.
