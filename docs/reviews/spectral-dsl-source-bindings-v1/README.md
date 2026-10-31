# Spectral DSL source preservation v1

Before evolving the DSL, compiler, history compiler or model validator, preserve their exact source identities and the previous archive maps. This is evidence identity maintenance, not numerical verification or model admission.

The reviewed worker audit is retained byte-for-byte in `audit/`, including its 30-file manifest, extraction probes, full inventory, consumer index, historical availability search and pre-append map bytes. `preserve.py` records the coordinator's one-shot staging action; its absolute staging inputs are intentional and it must not be rerun over this completed output. `archive-checks.json` records every resolved document/source pair and changed sidecar. The after-archive scanner output is retained separately.

All 37 current source bindings in 23 original documents now resolve to exact content-addressed snapshots. All 304 other original pair resolutions are unchanged; 11 historical unresolved pairs remain explicit. Original documents are unchanged, and all existing map pins/entries are preserved. Twenty-two sidecars were created or extended, with 21 new source/map snapshots. New sidecars also register 76 unchanged sibling JSON documents so their introduction does not invalidate sibling receipt consumers. The supplementary audit's prose counted six new locations; its actionable plan contains six document rows in five unique new locations, and 22 unique maps overall.

The sole historical root-relative secondary gap is a packet-local path whose exact bytes exist in the original packet. Copying the audit inventory makes the scanner enumerate a second descriptive occurrence of that same path; neither occurrence is a new byte loss. Do not treat source identity resolution as complete package replay or scientific verification. No builds or compiled observations occurred.

Reproduce extraction without modifying the frozen inventory:

```sh
python3 -B docs/reviews/spectral-dsl-source-bindings-v1/audit/scan.py /path/to/constitutive-atlas --output /tmp/spectral-bindings-new-inventory.json
```

Future code evolution may change the live-source identity classifications. Verify the original document-bound pairs against the preserved archive paths rather than replacing their expected hashes with current source hashes.
