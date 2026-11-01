# Ramberg CI arithmetic investigation

The retained Linux CI failed exact request regeneration despite the fsum patch. Both unchanged macOS Python3.12 and3.14 pass. The first mismatch is case22 `n2.5-uniaxial`, increments[0][0:3]: frozen [0.004999999999999998,-0.0016666666666666661,-0.0016666666666666661] versus Linux [0.004999999999999999,-0.0016666666666666666,-0.0016666666666666666]. A100-digit Decimal power probe independently reproduces all18 differences reported by the upstream recursive Linux diagnostic. The cause is libm pow for z^(3/2), with z=0x1.fffffffffffffp-1. Explicit z*sqrt(z) reproduces the historical operation result without loading expected values.

Concurrent upstream revision339e6dc6505a53a20790ae6a5f781f232924f812 provides the smaller separately reviewed correction: test-only portable_preparation replaces exponent1.5 with z*sqrt(z), and retains complete exact make_requests equality. Parent adopted that exact upstream test. This packet confirms the exact committed test independently: all9 focused tests PASS on local macOS3.12 and3.14. Upstream actual Linuxamd64 Python3.12 nine-test PASS log,18-field diagnostic,pow diagnostics,and independent review are copied byte-for-byte for bounded provenance. Local Docker socket access was unavailable; this packet does not claim a separately executed local Linux container.

`portable_generation.py` and `test_proposal.py` retain an earlier diagnostic prototype using a generic AST arithmetic namespace. It is superseded by the smaller upstream helper and is not an integration proposal. Its six diagnostic tests pass on both local Python versions, including complete83-case equality,100-digit independent other-power evaluation,and mutation sensitivity for parameters,loading,reference states,and controls. No tolerance, frozen request, oracle, physical gate, model, tool, canonical review or original test was changed by this investigation.

Reproduce bounded upstream confirmation:

```sh
python3 -B docs/ingestion/kelvin-voigt-comsol63/ci-repair-v1/ramberg-investigation/confirm_upstream.py
/opt/homebrew/bin/python3.12 -B docs/ingestion/kelvin-voigt-comsol63/ci-repair-v1/ramberg-investigation/confirm_upstream.py
```

The canonical request SHA remains859518b4f1896f2c431992a8cbd98b5f79d1ff9ca7de1f7971b9858960d61aa3, already bound by catalogue/agent-reviews/ramberg-osgood-agent-v1.json. Full terminal CI is still a coordinator delivery requirement.
