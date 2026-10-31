# Source-rate replay with separate runtime provenance

The original sand source report contains `sys.version`. The v1 adapter compares
that provenance string with the active interpreter, so Python 3.14.10 cannot
reproduce a report whose metadata names 3.14.7 even if every equation value agrees.

This separately named v2 adapter retains every original capsule source byte and
its old entrypoint, and adds one new entrypoint. It compares every report field
except `python_version` exactly, checks the active report names the actual Python
interpreter, then runs all 11 original test groups unchanged. Original reports,
capsule, registry and output remain unchanged. This is a new numerical replay
identity, not an assertion of identical historical environment or output.

The outer replay result records the actual interpreter. The original interpreter
remains in the original bound source report. No tolerance, numerical reference,
constitutive definition or scientific admission gate changes.

Run `python -B -m atlas.source_replay sand --registry
catalogue/source-replays/source-rates-runtime-v2/registry.json`.
