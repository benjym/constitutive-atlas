# Final prospective supplement decision v3

Independent reviewer `/root/md1997_review`, 2026-11-02. No author implementation edits, builds, engine loading or compiled calls. Prior v2 findings, checks, manifest and synthetic failure witnesses are preserved byte-for-byte.

**Accepted prospectively for bounded actual native execution, then mandatory final paired qualification. No remaining prospective blocker identified. This does not accept any actual backend result or model E5 item.**

Exact v3 checker SHA256 `5c5221f0f1d804ff6c2e0b2677bf9436cffa1bdf7c4816be1ace9dba1b2de9bc`; policy `e53e3c7af5d6e2e133d8399817d03bfc8d5efce368d1f21590d48022ce18630b`. supplement-manifest-v3.json and every input it binds were verified. Its hash is recorded in v3-checks.json and this review's final manifest. Original frozen author packet remains unchanged.

V3 resolves v2's native-only sequencing gap. Code diff adds optional Wasm positional argument plus explicit --native-only, validates mutually exclusive invocation forms, limits native-only execution to all existing native per-row gates, and records the actual mode. Paired numerical/binding gates are unchanged. The policy clearly says native-only makes no parity claim and requires both the original parity checker and paired v3 against the two actual reports for final qualification. No synthetic or duplicated backend report can substitute for actual evidence.

Reviewer reran all20 synthetic input variants in both modes: 40 expected decisions pass. Valid paired and native-only reports pass. All19 adversarial paired variants reject. Native-only correctly rejects all17 adversarial native variants; it ignores only the two changes confined to Wasm label/wire, which are irrelevant in that mode. Two invalid invocation combinations reject with CLI status2. Original valid pair also passed the retained original parity checker in v2 tests. Full inputs, detailed outputs and test source are retained here.

Proceed under the previously reviewed exact source closure, literal requests and unchanged numerical gates. Coordinator still must preserve actual raw reports, build/toolchain/source/generated-catalogue/artifact receipts, failures and serial target/parallel1 build policy; all unchanged MD, ordinary16 and dedicated-profile/transaction regressions remain required. Independent review of actual evidence remains outstanding. Earlier limitations concerning native process isolation, artifact provenance beyond its local file hash and treating checker exceptions/missing outputs as failed verification still apply.
