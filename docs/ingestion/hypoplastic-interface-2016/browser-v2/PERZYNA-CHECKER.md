# Prospective Perzyna download checker

Frozen before any new composed-browser observations. This adapter reads files only; it does not instantiate the engine or establish that supplied files were downloaded through a browser. A separate reviewer must assess this checker. No new browser acceptance is claimed.

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/browser-v2/check_perzyna_exports.py \
  --package <actual-qualified-composed-package> \
  --source-root /private/tmp/atlas-interface2016-delivery-v1/release-v3 \
  --revision 4e60096f3ab4535c53fd48ee92acb094b5682f4d \
  --relaxation <fresh-relaxation-download.json> \
  --creep <fresh-creep-download.json> --rate <fresh-rate-download.json> \
  --reset <fresh-reset-download.json> --replay <fresh-replay-download.json> \
  --output <new-offline-report.json>
```

The default source root is the tree containing this script; specify the composed tree when invoking the script from the shared checkout that lacks Perzyna files. Policy/reference SHA256 guards remain mandatory. The default revision is the exact composed source above; an explicit expected revision supports later independently qualified releases without discarding the release check. Output is create-only.

The checker binds the complete stable accepted package identity, source/engine/review/approval/component hashes and expected release_revision. It rehashes all identity-listed engine/assets/components, requires complete request/controls/provenance, strict finite vector lengths, all six output times and side/segment events, full13state/6stress values and metadata, and exact parsed default/reset/replay. It compares342 frozen values using the unchanged bound max(3e-7 for state or3Pa for stress,2e-5×absolute reference). Solver/reference hashes and settings remain unchanged. Duplicate keys, unsafe integers, nonfinite numeric tokens, booleans in numeric vectors and unexpected fields are rejected.

The public-rate reference driver's pre-event initial_strain_rate differs from the original UI: the UI sends six zeros before the segment-right rate applies. The adapter binds zero initial rates and the exact original UI CSV strings, while retaining the frozen state/stress references and every numerical threshold. This transport distinction was found prospectively against retained historical exports, not used to reinterpret a new failure. It is retained in perzyna-checker-transport-finding.json. The initial missing-source-root guard failure is also retained.

Reproduce bounded checker validation with `python3 -B docs/ingestion/hypoplastic-interface-2016/browser-v2/test_perzyna_checker.py`. Three committed historical exports are read through local Git. They pass342 numerical components at their historical revision and reject the new expected revision unchanged. A memory-only copy with just its provenance revision changed tests the prospective transport baseline; it is explicitly synthetic, never saved as a new browser download.192 injected identity, shape, request, metadata, bound, replay and nonfinite faults are rejected. No new model/module/browser/package/compiler/remote call occurs. This proof does not exercise actual new package bytes or new downloads, which do not exist yet.

Do not overwrite prior exports, receipts or proof after freeze; changes require a distinct prospective checker version. The Interface0.2Pa/2e-6 checker and old Perzyna evidence remain untouched.
