# Nakai–Hinokio 2004 subloading tij clay research model

Run from the repository root:

```sh
python3 tools/run_nh2004.py --protocol drained --output /private/tmp/nh2004.json
```

This explicit v0.3 full-extension/Appendix-V clay formulation uses the common solver with a named endpoint backward-Euler discretization. [Source choices, qualification, initialization and limitations](../../../docs/ingestion/matsuoka-nakai/working-v1/README.md). Native/Wasm and independent reference checks pass within their documented scopes. Scientific review and experimental validation remain open. Fixed spatial, zero spin, infinitesimal strain; beta1.5 isotropic flow has no general classical tangent. This directory is separate from the public model catalogue.
