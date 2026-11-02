# Fixed current Maxwell / NorSand dependency provisioner

PROVISION-bingham-current-dependencies-v1 owns the new `tools/provision_bingham_dependency_assets.py` and this packet only. It restores the existing twelve exact public dependency files, without building or executing a constitutive model and without creating a qualification or reviewer decision. The original Maxwell/NorSand qualification, independent review and archived asset records remain unchanged.

The fixed retained index is `current-engine-equivalence-v1/qualified-packaging-v1/INDEX.json`, SHA256 `5606f1ab6b50a3c85c5577c10afbecbc083ce6616cdf74aab91e061d1d67ed14`. Its ZIP SHA256 is `2554747b771125373fbdc90f75391ec5a06359b8bf9c6384e79f7e83a494a1f6`. `INPUTS-v2.json` records exact current helper, unchanged guard, index/archive and accepted source-equivalence report identities.

## Approval boundary and restore sequence

The helper requires one actual Bingham registry entry whose canonical `catalogue/agent-reviews/*.json` record passes `validate_review(..., for_approval=True)` and exactly produces that entry through `approval_entry`. The exact model ID and candidate SHA are pinned. Both fixed index and ZIP must appear with their exact hashes in that accepted review's artifacts. A missing/pending/unregistered E5 review fails closed. This worker did not create or infer that scientific approval.

Only twelve literal member names are allowed, with the exact known lengths. The helper rejects duplicates, missing/extra/path-escape members, non-Unix/nonregular entries, symlinks/special files, set-ID modes, encryption, unsupported compression, size mismatches and SHA mismatches. No `extract` or `extractall` is used. It reads bounded bytes and writes fresh private staged directories. Index JSON rejects duplicate keys.

Both output directories must initially be absent, distinct, nonnested, and have no symlink ancestor. After staging, the helper calls the unchanged `tools.build_maxwell_laboratory.bundle` and `tools.build_controlled_path_web.bundle` on the staged directories. Those existing guards validate current source/generated metadata, canonical scientific approval, exact qualification and actual separate build review. The helper then rechecks staged bytes and canonical E5/index/archive identities before checking both output destinations again and installing.

Each directory is installed with an atomic no-replace operation through pinned directory file descriptors: Linux `renameat2` with `RENAME_NOREPLACE`, or macOS `renameatx_np` with `RENAME_EXCL`. Every directory component is opened with `O_NOFOLLOW`; an empty directory created after the second check cannot be overwritten. Unsupported systems/filesystems fail closed, with no plain-rename fallback. Constants and declarations follow the [Linux UAPI header](https://github.com/torvalds/linux/blob/master/include/uapi/linux/fs.h), [Linux rename manual](https://man7.org/linux/man-pages/man2/rename.2.html) and [Apple XNU stdio header](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/stdio.h).

The two directories cannot be installed as one filesystem transaction. If a race prevents the second rename after the first succeeded, the helper raises an explicit error listing the already installed verified directory and retains it. It never deletes or overwrites a destination to manufacture success. Re-running against an existing destination remains refused.

## Commands and checks

Default intended use, only after real E5 review and coordinator release approval:

```sh
python3 tools/provision_bingham_dependency_assets.py
```

Defaults are `build-maxwell-wasm` and `build-controlled-path-public`. Explicit fresh destinations:

```sh
python3 tools/provision_bingham_dependency_assets.py \
  --maxwell-output /absolute/fresh/maxwell \
  --controlled-path-output /absolute/fresh/controlled-path
```

The normal website builder must use its existing `--controlled-path-wasm-dir build-controlled-path-public` option; workflow wiring belongs to the coordinator.

Synthetic-only verification:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/ingestion/bingham-comsol63/current-dependency-provision-v1/test_security.py
```

All thirteen tests pass in `security-attempt3.log`. They exercise synthetic twelve-member fixtures, malformed members/lengths/hashes, duplicate JSON, existing/symlink/nested outputs, mocked actual-review boundaries, both unchanged guard entrypoints, staged-byte and binding tampering, rejection before any install, late destination races, native atomic no-replace behavior on this macOS host, ancestor-link rejection and explicit partial second-install failure. Actual engine files, real bundle guards and constitutive functions were never executed by the worker. Linux operation is source-prepared; it was not executed on this macOS host.

Earlier twelve-test passes and the exact pre-ancestor-hardening helper are retained. `INPUTS.json` pins that initial helper; `INPUTS-v2.json` pins the final helper. All Python sources syntax-parse. No shared workflow, guard, registry, model or historical evidence was edited. Final independent E5 review and coordinator real provision/normal-package checks remain required.
