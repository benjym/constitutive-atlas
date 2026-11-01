# Exact VW96 policy recovery — 2 November 2026

The accepted VW96 review pins an older `AGENTS.md`. Its exact bytes were recovered with `git show` from the review's recorded source commit and independently matched to the retained clay approval release checkout. `RECOVERY.json` records both origins, length and SHA-256. The exact policy is now retained in its canonical content-addressed archive.

An additive `proposed-source-archive-map.json` adds only the existing review's exact document pin and the policy archive entry. All previous document pins and entries are unchanged. The official approval validator passes against an isolated copy with that proposed map; corrupt-policy and changed-review probes both reject, and restored inputs pass again. The model, accepted review, registry and source/runtime files remain unchanged.

**Not installed:** the shared map has live release consumers pinning its current bytes. Integrating this proposal requires the current integration owner's coordinated source-preservation handoff. No archive-map mutation or new historical-consumer failure is introduced here. The production VW96 integrity exception remains open until that integration is qualified. `map-before.json` preserves the proposal's exact map preimage; check its hash before use.

This is source recovery and a tested integration proposal, not new scientific acceptance, model delivery, numerical/backend/browser qualification or publication. No compiled execution occurred.
