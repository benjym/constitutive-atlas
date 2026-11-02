# Prospective package v5 — exact full-tree source closure

This distinct implementation adapts accepted package-v4 to independently accepted full-tree resource policy `source-closure-v5-review/decision.json` (`8c8e353d68edd57b3c38cfc8c34d3f17d1093a13546fd401ed8e7df5ccd76d6e`). No actual source freeze or package was run by the author. Only temporary-file manufactured checks ran; no child processes were launched.

The exact metadata identity remains external and hash-bound: `../source-closure-v5/full-tree-resource-identity.json`, SHA256 `f7627a0638674d476b73f97045e68c8be4078d2bbef261ef2809450dbed026d5`. All 40,318 tracked logical paths / 3,605,081,558 bytes of commit `4e60096f3ab4535c53fd48ee92acb094b5682f4d` are verified. No recursive JSON discovery or capacity ceiling is used in this new context; old v4 code, its 750 MiB ceiling and actual prelaunch failure remain unchanged.

Regular files use `O_NOFOLLOW`, descriptor/path identity checks, exact byte count, mode and simultaneous Git blob SHA1/SHA256 in 1 MiB blocks. Ancestor symlinks are rejected. The sole known negative-fixture link uses readlink payload verification only. Both case-alias paths are independently verified. The wrapper rechecks the complete source set pre/post; it never calls ordinary `sha()` on the source symlink. Copied-root membership/empty-directory/mode checks, asset sets, dataset/ignored witness and deleted-path checks are preserved. Their regular copied-file hashing also streams. `owned_process.py` is byte-identical to v4.

Normal full-builder argv is unchanged except distinct output `site-v5`. The existing release-v3 source and external qualified asset roots are used in place. There is no source copy or provisioning in this helper. Parent remains responsible for normal Perzyna source-only asset provisioning and slot authorization. No scientific, model, reference, runtime or supported-package gate changed.

Retained manufactured failure: first setup created empty copied roots absent from its fake Git tree; the inherited empty-directory guard correctly rejected it (tool `08917c`, exit1). Setup was corrected to create only its tracked root. The 24-check first passing result is retained. The final 24-check result additionally exercises the `O_NOFOLLOW` implementation; both are temporary-file/source checks only. Lifecycle code was not rerun and no real signal fixture launched.

After separate exact implementation review, parent-only commands:

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/package-v5/freeze_inputs.py --revision 4e60096f3ab4535c53fd48ee92acb094b5682f4d
python3 -B docs/ingestion/hypoplastic-interface-2016/package-v5/run_package.py --revision 4e60096f3ab4535c53fd48ee92acb094b5682f4d --preflight-only
python3 -B docs/ingestion/hypoplastic-interface-2016/package-v5/run_package.py --revision 4e60096f3ab4535c53fd48ee92acb094b5682f4d
```

Each verification streams the full closed tree, plus unchanged additional copied-root/assets guards. Parent owns scheduling; no throughput claim or deduplication reduces these reads. Failures/output/logs are retained and retry needs a distinct packet. Browser and publication checks remain separately required.
