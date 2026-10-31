# Provisional KFS development evidence page — v1

The Methods page now links to a separate interactive development summary. It
exposes the existing locked base-VW96 pressure/density comparison and the
conditional evaluation-initialization sensitivity, without mixing them with the
published TMD2+IGS reconstruction or promoting scientific status.

The selector switches saved scalar scores between file and original-table
initialization assumptions. A disclosure shows response shifts at three
resolutions and the frozen refinement result. Previously exposed tests,
inherited fixed constants, unresolved source disagreement and unpropagated TMD13
calibration-state uncertainty remain visible. Links retain primary publication
and exact research-packet provenance; the archived model hash is displayed.

`tools/build_development.py` verifies pinned evidence, reconstructs refinement
flags and exports an explicit scalar field allowlist. It never reads experiment
files or private native outputs. No measured/predicted curves, state vectors,
raw commands, private paths or manuscript material enter the export. The
[exact public projection](public-summary.json) is retained alongside
[verification](verification.json). The JSON includes source-evidence hashes.

## Checks

- Four new Python tests cover source hashes, scalar allowlisting, rebound-hash
  score/gate corruption and the six new JavaScript contracts.
- The JavaScript contracts check both scenario values/contrasts, missing or
  duplicated scores, nonfinite values, unsafe links, missing limits, incomplete
  refinement and unsupported promotion/identity.
- With existing TMD2 packaging and archive checks,22Python methods pass;
  [log](tests.log). No full-project suite pass is claimed.
- Static packaging reuses the previously verified Release Wasm artifact. Nine
  default laboratory paths of101points pass the existing packaged-software
  smoke test. This executes existing Wasm; it does not build an engine or create
  a new scientific study.628public experiment records are packaged normally.
- Actual browser inspection verifies both score states, contrast updates,
  refinement expansion, visible limits/source links and Methods navigation.
  All local development-page links resolve under the Pages project prefix.

Historical index/packager bytes and the previous TMD2 archive map were preserved
before editing. Three explicit historical receipts resolve to their original
bytes through the new sidecars. Scientific packets and their bounds are unchanged.
The first static-check invocation used an unsupported positional CLI argument;
the corrected invocation passes. This command error is retained in verification.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_web_development.py -v
PYTHONDONTWRITEBYTECODE=1 python3 tools/build_web.py --wasm-dir /path/to/existing/verified-wasm --output /private/tmp/kfs-web-preview/constitutive-atlas
node tools/test_web_package.mjs --directory /private/tmp/kfs-web-preview/constitutive-atlas --output /private/tmp/kfs-web-package-check.json
python3 -m http.server 8945 --bind 127.0.0.1 --directory /private/tmp/kfs-web-preview
```

Open `/constitutive-atlas/development.html` on that local server. The original
local preview uses port8945 under `/private/tmp/atlas-web-kfs-development-v1/`.
A screenshot is retained privately by path/hash. The page performs no model
calculation; ordinary main-app startup still uses its existing engine.

No new fit, source-model migration, native/Wasm build, measurement publication,
deployment or scientific admission occurs. Broader website accessibility/mobile
review, TMD13 propagation and independent scientific review remain open.
