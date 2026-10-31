# Python JSON signed-zero reader correction v2

The original frozen integration test and its failure are retained in the parent study. CPython's default json.loads('-0') returns integer0 and erases the sign, whereas the native serializer's -0 token and authoritative controls_bits preserve it. The Node primary gate already verifies every signed-zero/minsub bit on both backends.

This separately identified correction changes exactly one test-reader expression to json.loads(result.stdout,parse_int=float). It maps integer-form numeric tokens back to binary64, matching their C++ origin and JavaScript parsing. No constitutive/controller/parser implementation, request, analytic formula, bound or old report is changed. The original four-test run remains failed. Freeze the corrected file, JSON-only witness and independent review before reusing the exact same native artifact for the corrected four-test run. No rebuild is needed.
