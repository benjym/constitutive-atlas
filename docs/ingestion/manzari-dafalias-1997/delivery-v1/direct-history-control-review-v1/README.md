Accepted source-only app selection fix. Exact inverse of added capture and replaced selection assignment reproduces the saved baseline byte-for-byte. Eligibility predicates, messages and all numeric request/model code are unchanged. Six manufactured state cases confirm supported selection preservation, disabled-cycle fallback0 and empty-value recovery. Actual browser evidence remains coordinator-owned/pending.

The initial review gate wording "first enabled fallback" was overbroad; the proposed change preserves the existing literal0 fallback. Unsupported all-disabled protocols remain blocked by existing eligibility handling; no supported fallback is invented for them.

No compiled calls, browser operation, temporary process or resource was created. Saved baseline and candidate belong to coordinator and remain retained.
