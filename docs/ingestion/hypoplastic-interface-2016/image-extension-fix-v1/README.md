# Correct JPEG evidence filenames

The first release (5f3ac8ca) failed the existing recursive source-packet suffix safeguard on macOS. Fifteen browser captures had `.png` names although their bytes are JPEG. This repair does not change that safeguard or scientific, runtime, UI or numerical acceptance inputs.

`inventory.json` pins the original release files. `repair.py` verifies every input, writes and checks canonical archives and same-byte `.jpg` names before removing any old path. Original browser manifests remain byte-identical. `RELOCATION.json` explicitly maps their original relative entries to the durable archives and current names; `verification.json` checks every original member of both manifests. Re-run `python3 -B docs/ingestion/hypoplastic-interface-2016/image-extension-fix-v1/repair.py --install` to check the installed closure idempotently. It never executes a model or changes a manifest pin.

Original Git revision, manifests, failed CI log and hash-named archived bytes retain historical identity. This relocation is evidence maintenance only; E8 remains open until every gate for the successor revision and its actual live delivery pass.
