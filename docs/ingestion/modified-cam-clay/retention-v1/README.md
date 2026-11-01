# MCC private primary-source retention v1

The exact Silbermann–Nagel2023 PDF is retained at ignored `.local/private-sources/modified-cam-clay/ModifiedCamClay_report.pdf`. [Receipts](receipts.json) preserve the original acquisition identity, commit-pinned link, SHA-256, length and local retention location. Original receipts and PDF bytes are unchanged. The public repository contains links/receipts only; copyright permission to redistribute the PDF is not inferred.

The separate mutable Itasca reading remains unhashed and is explicitly not claimed as retained original bytes.

Reproduce from the repository root:

```sh
python3 -B docs/reviews/mcc-agent-v1/check_review.py --repo "$PWD" --private-source "$PWD/.local/private-sources/modified-cam-clay/ModifiedCamClay_report.pdf" --output /private/tmp/mcc-retained-source-check.json
```

The reviewer-authored checker verifies the original PDF hash before independent algebra and saved-report checks. A fresh public clone must acquire the exact linked original and verify its hash. Private source retention does not qualify current binaries, migration, browser or live delivery.
