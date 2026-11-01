# Native CI dispatch compatibility plan v2

PLAN-md1997-native-ci-dispatch-v2 is source-only. This supplement prepares exact14 historical, exact15 published and prospective16 MD routing; it does not implement the dispatcher or execute binaries. Published base37d70660e3561c342bb114716c233a3d06651bcb is authoritative. The dirty shared checkout's14 helper is preserved. The accepted numerical plan and separate review are input hash-bound in inputs.json.

The smallest future implementation whitelist is:

- NEW tools/check_native_fixture_dispatch.py: exact catalogue/source/helper classification, strict contracts, bounded CTest suite selection and complete transport receipts.
- NEW tools/check_md1997_native_fixture_contract.py: exact16 legacy explicit-v5 failure plus unknown/incompatible numerical selector checks.
- NEW tests/test_native_fixture_dispatch.py: mocked catalogue/process/environment/dispatch corruption tests.
- tests/test_solver.cpp: only accepted numerical-plan selector, admissible MD FD/rotation fixture changes and early selector/layout guards.
- .github/workflows/verify.yml and tests/test_ci_profiles.py: dispatch commands and corresponding coverage assertions, preserving every other published gate.

Existing tools/check_native_fixture_contracts.py, tests/test_native_fixture_contracts.py, tests/test_recorded.cpp, CMake, runtime/compiler/schema, model files and package/admission policies are outside that whitelist. No generated production outputs are proposed. The historical14 route requires its exact archived policy/helper context; current15 uses the unchanged published helper. For16 the new envelope validates all16 before passing only the exact15 projection to the unchanged recorded-failure analytical check. No scientific approval or package16 policy is manufactured.

Proposed interfaces, not existing commands:

```
python -B tools/check_native_fixture_dispatch.py check --catalogue build/generated/models.json --source-root . --build build --output "$RUNNER_TEMP/native-ci-dispatch/contracts.json"
python -B tools/check_native_fixture_dispatch.py ctest --catalogue build/generated/models.json --source-root . --build build --suite macos-main --output "$RUNNER_TEMP/native-ci-dispatch/macos-main.json"
```

The only suites are macos-main (exclude exactly ^atlas_recorded$), linux-main (exclude exactly ^(atlas_python|atlas_recorded)$), and recorded (select exactly ^atlas_recorded$). Each retains --test-dir build --output-on-failure. No caller-supplied arbitrary test filter is permitted. Exact16 main suites set the new numerical selector; recorded and all14/15 suites remove it entirely. All set original native explicit-v5. Default/unknown/legacy calls sanitize both variables first. Unknown catalogue aborts before any process. Check runs four strict calls for14/15;16 retains four plus four distinct MD contracts (eight total), with actual positive CTest acceptance separate. Preserve process order, full argv/selector presence/timeout/returncode/stdout/stderr and source/catalogue/helper/policy/artifact hashes; save partial receipts on every failure, never overwrite prior outputs. Wrapper success is never a replacement for positive CTest success.

workflow-proposal.diff is against exact published37d only, not the checkout. It moves the strict contract step before positive CTest and adds always-run log retention. The original macOS and Linux main/recorded CTest partitions remain exact. The proposal adds neither deployment authority nor remote CI execution.

Reproduce the bounded source-only checks:

```
PYTHONDONTWRITEBYTECODE=1 python3 -B docs/investigations/control-partition-derivative-v1/native-ci-dispatch-plan-v2/check_prospective.py
```

The check imports only frozen pure recorded-failure helpers, never their main functions. Catalogue and subprocess records are mocks. It checks exact projection ordering, inherited OCC analytical signatures, process failures, environment stripping and reversible workflow preservation. These checks do not prove selector implementation or compiled behavior. prepare.py records the earlier exact Git/source inputs and should not be rerun over a frozen packet.

Cross-coordinator integration dependency: latest published15 Ramberg changes must remain in the integration base, then a fresh source/model/hash drift check must bind the16 map and the separately authorized numerical implementation. Parent and separate reviewer must accept this plan before any implementation, isolated build or compiled observation. Actual numerical qualification and E5/E6 admission/package integration remain separate. No remaining tooling blocker was found for this plan; live implementation and runtime evidence are intentionally absent.

The local check additionally requires the retained exact582 source tree at /private/tmp/atlas-control-partition-v1/source (read-only model definitions only); it does not execute that tree. inputs.json binds all published snapshots, the accepted numerical plan/review and the ordinary-v7 policy. Catalogue serialization in prepare.py was reproduced from source JSON without invoking a compiler and matches the already frozen16 generated-file hash. No unavailable model input was inferred. The final manifest includes the intentional .github workflow snapshot explicitly; generated caches and binary extensions are forbidden.
