# Agreed export and assessment boundary

Dispatch-plan author `/root/md1997_review` and oracle author `/root/md1997_reference` agreed this conceptual interface through direct team messages on2026-11-02. This document is the proposed dispatch contract; it does not freeze or accept the oracle author's still-preparing phase1 implementation. Its final exact schema, corpus and assessor require separate hash-bound independent review before C++ export implementation/actual observations. A material schema change requires an additive reviewed plan identity.

Successful new-mode output has identity `md1997-decimal-ad-export-v1`, selector `md1997-decimal-fd-reference-v1`, status `exported-unassessed`, models16. Its closed top-level fields are identity, selector, status, models, bindings, base, endpoints, ad_hex, cpp_checks. No plain-text success label is emitted. cpp_checks contains literal true rank13, rotation and other_models. Those flags summarize source-reviewed completed assertions; they cannot replace actual assertion execution.

Bindings name request_sha256, reference_sha256, evaluator_sha256, policy_sha256, base_source_freeze_sha256, model_sha256 and build_binding_sha256. The base is the complete request layout/state_hex/previous_hex/loading_hex/parameters_hex/scales_hex. Endpoints are the56 exact ordered request records, each with literal-true domain and branch flags; all individual metadata keys/array order come verbatim from the pre-frozen request schema, not an independently invented alternate representation. ad_hex is14 residual rows by14 scaled coordinate columns; all196 entries are finite binary64 hex strings. Use exact request hex formatting and signed zero identity for transported metadata. Actual native endpoint arithmetic must be independently compared to those source-only expected values.

Proposed assessor invocation, owned by the oracle author:

```
python3 -B assess_saved.py --requests REQUESTS --reference REFERENCE --process PROCESS --build-binding BUILD_BINDING --build-binding-sha256 PINNED_EXPECTED_HASH --output FRESH_REPORT
```

The build-binding path and expected hash are supplied by the independently reviewed collector freeze, never accepted merely because output names its own binding. The binding records actual augmented source freeze, fixture, generated catalogue, executable path/hash, model and working_directory; wrapper evidence additionally binds the full actual build receipt, source/tools and pre/post checks. A synthetic binding is explicitly synthetic-test-only and cannot qualify an actual call. All assessor/policy/corpus/schema hashes are externally pinned too; mutable self-consistent files are insufficient.

Two process identities are agreed:

- `md1997-decimal-direct-process-v1`: directly observed native argv/cwd/selectors/executable hash, integer exit0, separate exact raw stdout and stderr path/hash bindings. The collector requires empty successful stderr. Each actual direct call has a unique callID and receipt; its C++ export is assessed separately.
- `md1997-decimal-ctest-child-v1`: atlas_numerical child name/registered command/directory, CTest-reported child status, complete fresh raw LastTest.log path/hash, exact combined Output-region path/hash, parent CTest argv/cwd/exit0 and raw separate stdout/stderr, effective selectors and executable hash. No child integer exit or separate child stderr field is invented. Its complete CTest wrapper receipt additionally requires exact selected suite argv, full registration/coverage/order, source/tool/artifact checks and one-to-one parent/section/output/assessment binding.

Raw bindings contain path and SHA256; existence, exact bytes and independent pinned input identity are checked. The collector retains resolved-path and full environment evidence even where the narrower assessor process schema exposes only the closed selector map. The plan's new export binding environment variable is not silently added to that selector map. Both transport types carry a purpose distinguishing actual and synthetic-test-only evidence; an actual dispatcher rejects a synthetic assessment.

The assessor report must bind exact request/reference/process/build-binding/raw-output hashes, purpose, channel scope,588 comparison results/count and all failures. Dispatcher separately pins its assessor source/policy and receipt hashes, requires passed literally true,588 comparisons and no failures, and verifies that exact report belongs to the current call and current frozen corpus. No missing report, truthy string, report from a second invocation or wrapper's bare export success qualifies. No overall positive CI result precedes that assessment of the actual CTest envelope.

The final oracle schema must specify every nested field/type/order, CTest framing and permitted trailing transport newlines, all finite-hex rules, Decimal context and report format. The dispatcher adapter is stricter where it has fuller actual build/CTest/source evidence; a narrow assessor pass never waives these composition gates. Any missing enforcement is a future implementation blocker, not permission to weaken this design.
