# Independent Maxwell CI regression prospective review

Accepted the exact revised prospective drivers and command in [prospective-review.json](prospective-review.json), after resolving the retained [initial findings](initial-findings.json). This is source acceptance before coordinator compiled execution, not actual result or workflow acceptance.

Reproduce from repository root with `python3 -B docs/ingestion/maxwell-itasca900/atlas-ci-regression-v1/independent-review/check_saved.py`. The checker verifies exact inputs, executes 21 existing pure Node tests, checks all four source normalizations, then uses JavaScript mock engines and injected Python subprocess timeouts. It never loads Wasm or calls a compiled engine. [checks.log](checks.log) preserves the successful output.

Actual retained-engine observations and narrow archived workflow projection require a later separate final review. Existing scientific and delivery limitations remain in force; the receipt states the original collector partial-pair boundary explicitly.
