# Linear-elastic private source retention v1

The three readable OGS files used by the existing source packet are retained at `.local/private-sources/linear-elastic/` beneath the repository root. That directory is git-ignored. [Receipts](receipts.json) record exact paths, upstream URLs/version, original byte counts/hashes and retention date. Original source receipts, models and historical evidence are unchanged. No upstream code was built or executed and no source bytes are published in this packet.

Run from the repository root:

```sh
python3 -B docs/ingestion/linear-elastic/retention-v1/verify.py
```

The checker requires the privately retained files; a fresh public clone will need to retrieve the linked exact revision and verify its hashes. Retention closes source accessibility on this machine, not numerical qualification or scientific approval. Source acquisition date and retention date are distinct fields even though both are 2026-11-01.
