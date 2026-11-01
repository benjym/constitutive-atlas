# Full-history import sizing

The first browser check produced a 25 MB full-range default export, exceeding
the old 10 MB upload guard. Increase the UI file-size guard to 100 MB to allow
full-history exports up to the existing 39-run limit (about 65 MB at the observed
default per-run size). Exact request/source/result validation is unchanged.
Retain the initial browser failure and rerun the same checks after this fix.
This is an upload-size adjustment, not a numerical acceptance change.
