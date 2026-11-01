# Shared-hook preservation proposal v2 — not applied

Revision v2 retains the original six-source proposal unchanged, with exact copies under prior-v1/ and PRESERVED_V1.json. It adds catalogue/approved-models.json as the seventh pending source. Its old hash is 7abba1ef96a7abf5886712d786fce5cb99e8c6604e5a4c551584654b61010fd0. Future registry and Maxwell-helper bytes remain unspecified. Both live paths are omitted in the temporary overlay to prove historical bindings through archives without inventing replacement hashes.

This revision also preserves the five changed initial Lade provisioner source/proof files using the exact saved_copy bytes in asset-provision-v1/preservation-v1.json. Its unchanged initial SOURCE_FREEZE.json remains live and is not redundantly archived. The original initial review receipt and initial freeze resolve through current checked_receipt using additive document pins and canonical snapshots. Neither original freeze, initial receipt, current tool nor approved registry was edited.

The fresh scan follows the actual reviewed profile installation. It excludes mutable source-archive-map.json files as immutable receipt identities: their documents dictionaries are resolution metadata, and treating the map itself as its own old receipt creates an unsatisfiable self-document hash cycle. Their exact old bytes are preserved canonically and every genuine external immutable consumer is scanned. The coordinator explicitly agreed to this classification. The failed preliminary scan and its nine self-reference failures are retained under development-failures/seven-source-self-map/. No existing map entry or document pin is dropped, repointed or changed; missing peer receipt document pins are added so new archival sidecars also permit current receipts in their parent.

The fixed point has 33 source/map pairs and 103 obligations. Thirty-one sidecars (22 replacements, 9 creations) and 32 new canonical snapshots make 63 exact apply paths in APPLY_WHITELIST.json. One canonical archive already exists. Every replacement requires its stated actual current hash; every new destination requires absence. Seven pending source replacements are listed separately and are not part of the metadata apply list. Recheck guards before any separately reviewed application.

Mandatory checks pass: 103 source/map obligations plus 261 existing recognized archive bindings, and all 530 checks from the original shared-hook/profile/recovery proposal. The supplementary checker also examines 19,483 safe repository-relative existing peer receipt pairs. Across 20,377 checks, 20,317 pass. Sixty unrelated preexisting failures remain explicitly recorded with original baseline and overlay errors; they are not repaired or reported passed. Every previously valid peer binding passes. Where an already-invalid peer references a prospectively changed map/source, its exact current bytes are independently preserved canonically; otherwise its live bytes are unchanged. No gate or expected hash was relaxed to turn these diagnostics into passes.

Source/map/receipt bytes, live input pins, original plans/freezes and failures are retained. The terminal summary of the completed full supplementary run raised a KeyError after CHECK_RESULTS.json and SOURCE_PINS.json had both been written; only that final print key was corrected. The exact pre-correction script is retained. No checked result was altered.

Pure reproduction (approximately several minutes; metadata/source reads only):

```
python3 -B docs/ingestion/lade-duncan-1975/atlas-integration-v1/shared-hook-install-v1/revision-v2/check_overlay.py
```

Do not rerun the full planner into this frozen revision after input drift; create a new revision. SOURCE_PINS.json guards live inputs; SOURCE_FREEZE.json binds owned outputs. No production source, sidecar, approval registry, native/Wasm artifact, qualification or approval was written. Independent source review is the next step before coordinator application. The separate root-authored hooks/workflow review remains separate.
