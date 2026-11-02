# Package v6 — minimal option-recognition correction

Prospective source-only successor to accepted package-v5. Actual v5 freeze failed before writing source-freeze.json or launching package: its asset loop interpreted a positional asset directory ending `burgers-wasm-dir` as an option, then treated the next `--hill-wasm-dir` flag as a directory. Parent terminal receipt: session70683, tool chunk9eac7b, exit1, freeze_inputs.py line116. Parent reported full tracked source-byte verification had completed before this loop. The exact v5 code/failure remain unchanged; this is not a passing freeze claim.

The sole freezer change requires both `arg.startswith('--')` and `arg.endswith('-wasm-dir')`. Normal builder argv changes only output site-v5 to site-v6. Wrapper and lifecycle helper remain byte-identical. Exact all-tree policy, source/asset/dataset/witness/membership guards and all scientific/runtime gates are unchanged.

`test_option_recognition.py` evaluates the exact AST predicate against flags and positional directory names, and all 14 actual plan asset options. It verifies source delta, same wrapper/lifecycle, same ordered parents/cwd and output-only argv difference. No actual source or assets were hashed, no freeze/package/child launched. First manufactured fixture incorrectly expected `--wasm-dir` not to match the suffix; the predicate correctly recognized it (tool2b8e4a exit1). Corrected fixture passes and the original failed expectation is retained here.

After independent exact review, coordinator-only commands:

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/package-v6/freeze_inputs.py --revision 4e60096f3ab4535c53fd48ee92acb094b5682f4d
python3 -B docs/ingestion/hypoplastic-interface-2016/package-v6/run_package.py --revision 4e60096f3ab4535c53fd48ee92acb094b5682f4d --preflight-only
python3 -B docs/ingestion/hypoplastic-interface-2016/package-v6/run_package.py --revision 4e60096f3ab4535c53fd48ee92acb094b5682f4d
```
