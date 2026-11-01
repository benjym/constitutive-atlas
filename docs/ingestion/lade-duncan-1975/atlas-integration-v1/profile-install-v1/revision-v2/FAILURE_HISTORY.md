# Retained development failures

1. The initial revision script refused production drift: Barodesy root-registration independent-review/source-archive-map.json had appeared since v1. Inspection found two Barodesy maps equal to prior candidates and a Duncan–Chang map with additional independently preserved web/Maxwell bindings. The fresh closure now merges these mappings and preserves their current exact bytes.
2. The first supplementary overlay omitted unchanged production sidecars that compute_current.py correctly used. This caused the original Barodesy inputs.json pin to the old Duncan–Chang sidecar (74fb4015…) to resolve to the current map rather than its canonical snapshot. The supplementary overlay now copies unchanged production sidecars as inputs; no receipt or expected hash changed. The 218 combined checks then passed.

These were proposal/harness failures. No production file was written and no compiled artifact was executed.
