# Evidence API provenance follow-up

Ready overlay: `overlay/`. It contains only merged archive sidecars, exact original source snapshots, and the expanded source-migration inventory. It does not contain `atlas/evidence.py`, `tests/test_evidence_archives.py`, or any runtime/test replacement. Preserve the parent's restored evidence APIs and new inventory replay regression.

The initial packet incorrectly treated the existing evidence module as new. The parent restored its original `sha256` and `validate_record` APIs and appended the archive resolver. This verification compares both original function ASTs to the current installed definitions: they are identical. Four original evidence/oracle test modules import successfully.

The audit covers all 18 currently modified tracked paths, including the unrelated data-license audit solely for receipt discovery (no change proposed). It finds 190 matching historical references, plus the previously retained macOS receipt, giving 191 inventory references across 28 packet directories. All 191 resolve using staged maps and exact archived bytes in a data-only verification root without live source files. All 46 raw document bindings verify. Historical receipt documents and their expected hashes are unchanged.

This follow-up adds 11 merged sidecars and 14 shared snapshots. It includes the original `atlas/evidence.py` (18804fd49c7ee2cfcb9875e566d21e9b3b922209ab70f2ac945ff9082b43850d), `tests/test_evidence.py` (d980d8b86daae07df3b4fc546c2dcb21e27d389438924294c5f2da54a5659968), and `tests/test_capacity.py` (b479f073565b949ef07d24dc43fdeb18902765683e8e54cb9e6ab785062b08cf), plus exact historical ROADMAP, architecture, catalogue and SANISAND test bytes required by old receipts. The inventory now also lists all four extra document bindings supplied in the preceding coverage packet. Existing entries and bindings are preserved.

Verification: 8 non-native original evidence API groups and all 11 installed archive groups pass, including the parent's new complete inventory replay test. The one native evidence test is explicitly excluded. No native/Wasm calls, builds, repository writes, or git mutations were made; read-only historical git inspection recovered exact original bytes. `verification.json` records the result. Reproduce with:

```sh
PYTHONPATH=/Users/bmar5496/code/constitutive-atlas python3 /private/tmp/atlas-evidence-api-provenance-20261031-v1/verify_additions.py
```

Earlier targeted test-loop edits preserved their numerical comparisons, and the SANISAND follow-up retains full semantic regeneration comparison while separating immutable identity checks. The current overlay replaces no code or test files, avoiding another established-API overwrite. The old snapshots prove historical provenance; they do not establish numerical validity or compatibility of the new expm runtime. New-runtime evidence remains a separate gate.
