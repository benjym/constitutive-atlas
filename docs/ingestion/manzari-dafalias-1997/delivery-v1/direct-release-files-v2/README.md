# Direct release files v2

`release-paths.txt` is the explicit 111-path candidate commit list, relative to `/private/tmp/atlas-md1997-current-main-integration-v1/source`. It preserves all 110 v1 paths and adds only `tools/test_interface2016_compatible_package.mjs`. `release-file-hashes.json` records the current selected bytes, including the updated `tools/build_web.py` dispatch. CI runner and both workflow files remain included.

Source-only checks confirm all 37 scientific-review artifact hashes; new compatibility source inventory dependencies; the five Decimal oracle files; the numerical runner; compatibility helper; and the new Interface checker. The checker reads three fixed compatibility records already selected, uses Node builtins, and imports packaged modules generated from existing tracked source and selected engine assets. Direct build_web local imports and those module source paths exist, with no changed or untracked dependency omitted by this finite check. No additional concrete missing source/data path was found.

`exclude-paths.txt` preserves the same 211 exclusions: unused prospective authority/platform/capture routes and unconsumed transport data. No files are deleted. Root board, paper, and these planning packets are not part of the candidate release list.

Reproduce the finite source check with `python3 docs/ingestion/manzari-dafalias-1997/delivery-v1/direct-release-files-v2/classify.py` from the shared checkout. The two Git name snapshots came only from `git diff --name-only` and `git ls-files --others --exclude-standard` in the candidate. No Git index mutation, compiled execution, package build, archive, or temporary tree was created. Actual package/CI success remains the coordinator's check. v1 is unchanged.
