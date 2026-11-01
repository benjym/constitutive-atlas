# Additive saved-replay portability correction

1 November 2026. The original committed `manifest.json` mistakenly listed the ignored `__pycache__/assess.cpython-314.pyc` cache created while importing the assessor. A clean checkout does not contain that incidental interpreter file. The original manifest, prospective freeze, sources, expected rows, observations and numerical outcomes remain unchanged.

`portable-manifest-v1.json` binds the original manifest and retains every source/policy/observation hash while excluding exactly that one cache from file-availability checks. This changes no numerical acceptance rule. `python3 -B catalogue/investigations/declared-loading-boundary-v2/verify_portable.py` checks those identities and reconstructs the exact frozen assessment without requiring caches. Cache-absent replay was verified before this supplement was committed. The original pre-build freeze never included this cache; its file identities still verify unchanged.
