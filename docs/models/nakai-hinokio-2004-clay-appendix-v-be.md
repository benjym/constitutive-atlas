# Nakai–Hinokio 2004 clay / Appendix V

Approved by explicit user acceptance on 1 November 2026 for the bounded scope in [the approval record](../admission/nh2004-approved-v1/approval.json). The exact qualified v0.3 definition retains its historical draft metadata. User approval, automated scientific assessment and experimental validation are recorded separately.

Run from the repository root:

```sh
python3 tools/run_nh2004.py --protocol drained --output /private/tmp/nh2004.json
```

The common solver provides the selected one-a clay formulation with Appendix V and a named project endpoint backward-Euler discretization. The default state (98 kPa, rho=0, e=.83) is reference-consistent. At the same isotropic pressure rho=.03 requires e=.80. Arbitrary independently supplied density, pressure and void ratio are synthetic states unless reference compatibility is established; the runner does not enforce it.

[Independent review](../reviews/nh2004-scientific-v1/README.md) supports the bounded differential transcription and retained short-path qualification. Sustained softening/peak crossing and broad cyclic accuracy remain open; finite updates introduce reference-invariant drift. Source-matched specimen preparation and experimental reproduction remain pending. No external scientific signature is claimed.

[Source and execution packet](../ingestion/matsuoka-nakai/working-v1/README.md) retains exact source decisions, frozen gates, native/Wasm evidence and failures. Historical statements about pending approval are superseded by this dossier and the registry. The PDF remains private. Browser integration is a separate qualification scope.
