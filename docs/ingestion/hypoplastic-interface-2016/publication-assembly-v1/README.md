# Read-only publication assembly plan

The plan uses published Perzyna106a9cf8c327c9c262a97eb86aa04dae3f6cadb8 as the tree base and Interface closeout136636f14ce12b0dd83e65a8c37d3af9a5cc1381 as the second parent, with common base54f409b37deaed0ab82a85cdac9f489bc65e1309. It overlays the exact Interface Git delta, the independently accepted49 composition targets, all107 proposal members and original manifest, all5 independent review files, the actual closeout receipt and unchanged parent-authored assembly script. This README and preparation helper are included as source metadata. Entries identical to the published tree are filtered so the parent's exact-delta assertion remains meaningful.

The plan also contains an explicit lowercase manifest.json alias with the same exact bytes as physical MANIFEST.json. Accepted review source uses the lowercase path; macOS resolves both names, while Linux distinguishes them. Both exact Git destinations are intentional and independently hash-bound. A case-insensitive copy-on-write materialization may retain one physical file after verifying byte equality; the Git tree must retain both names. The accepted review is unchanged.

prepare_plan.py validates proposal/review hashes, every proposed source, all7 ledger documents in the closeout commit, catalogue/approval/profile counts and preservation of published-only paths. It reads only bounded branch deltas and listed source members; it performs no Git mutation or material/package/browser/compiler/remote action. It writes only this owned plan and proof metadata. proof.json records hashes, counts, expected root guards and default read-only preflight; it is a preparation receipt rather than an input that circularly pins its own plan hash.

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/publication-assembly-v1/prepare_plan.py
python3 -B docs/ingestion/hypoplastic-interface-2016/publication-assembly-v1/create_commit.py
```

The second command is the default read-only preflight. This worker does not invoke --execute. The parent owns alternate-index commit creation under refs/heads/delivery/interface2016-release-v3 and all subsequent copy-on-write source freeze/package/browser/release qualification. Source composition approval is not approval of a new package, scientific model or deployment.
