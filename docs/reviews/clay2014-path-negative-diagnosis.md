# Independent diagnosis of the retained clay2014 finite-path failure

**The original frozen outcome remains FAILED for both native and Wasm.** Both complete reports fail four of144 prescribed physical-endpoint refinement inequalities. This packet diagnoses the immutable observations; it does not modify the original collector, model, reference, numerical policies, reports or raw companions, and does not replace the original failed assessment with a partial success.

The observations are source commit `3acb9dd6e4b8080a71d043ccfc52382d1c47ac36`, frozen assessor SHA256 `4f46dac83551fa1a7c2bba852972fb7a3fc71f219d3c0875b8239e265357a7af`. Each backend retains24 trajectories,288 actual path updates and295 raw rows (descriptor plus path updates plus three probe/recovery pairs). The script pins the exact eight original report/raw/preobservation documents in `KNOWN_INPUT_PINS`; it checks those bytes before and after diagnosis and hashes/parses each report's held bytes. It replays the pinned independent reference freshly and checks source metadata, full descriptor identity, all source pins, preobservation source files, build receipts and log hashes. The raw verifier audits both complete transport companions and their semantic request/response identities. No executable, loader or Wasm was invoked by this reviewer.

## Exact failed inequalities

Every failure occurs on `isotropic-ratios-hydro-reversal`, caller partitions7, in the required middle-error <=`.65*loose-error + 2*(floor+observed reference uncertainty)` condition. The table applies to both backends; exact full-precision operands, allowances and all144 checks are retained in `negative-diagnosis.json`.

| Endpoint | Channel | Loose error | Middle error | Tight error | Allowed middle error |
|---|---|---:|---:|---:|---:|
|1|stress Frobenius,Pa|0.0543673796413|0.0543673796413|0.0136079746240|0.0353405604243|
|1|void ratio|1.01415709164e-9|1.01415709164e-9|2.53478349421e-10|6.60202997744e-10|
|2|void ratio|7.18204273831e-10|9.44733957731e-10|2.50283793690e-10|4.67834110258e-10|
|3|void ratio|8.41908764926e-10|1.06742137351e-9|2.80888534654e-10|5.48242695603e-10|

The stress floor for this case is8.66025403784e-7Pa; its endpoint1 observed reference uncertainty is1.58033196399e-8Pa. Void floor is5e-13, with observed reference uncertainty below1e-15. These frozen allowances are included exactly; the violations are not rounding-scale equality ambiguities. The original assessor stops at the first stress failure. The independent diagnostic evaluates the later inequalities separately and reveals the three additional void failures, without disabling any acceptance condition.

## Separately established checks

Every path caller point meets its originally declared stress, void and exact-volume accuracy budgets. Maximum consumed fractions of the declared stress and void budgets are respectively0.0438804086850 and0.0153663200682 on both backends. All finite/Boolean/type/echo/settings/returned-state source-domain checks pass. All frozen caller-partition contraction and covariance checks also pass. These checks are recorded separately from the failed endpoint-refinement criterion.

Native/Wasm state and generated-parent differences were independently compared at all288 corresponding updates after verifying both backend protocols and both raw bindings. The maximum fixed-scale stress-Frobenius or absolute-void difference is1.233678230526823e-16, below the predeclared5e-11 partial comparison budget. This is a state/parent comparison only. The frozen complete parity assessor correctly cannot grant full acceptance while either report fails the original refinement gate.

Each backend's budget3 call fails after two accepted internal substeps, coverage0.015625, returns its exact committed caller parent and then recovers identically to its own actual third-call control. The domain probe fails after4776 accepted substeps and coverage0.18491649627685547, with the same exact rollback/recovery. Its message is the generic domain/singular/substep-limit message; this packet does not identify a unique internal rejection cause. Exact zero succeeds, preserves all seven caller values and recovers identically. Thus after-progress transactional rollback/recovery is separately demonstrated for this selected state/protocol, while the overall numerical acceptance remains failed.

The native artifact SHA256 is `9468a693877a794c6786f55e42ebeb1384f6913fd52656e00f1d79ed9c67740f`. Wasm loader SHA256 is `0100cc8d8682cef4bda38291361a3bd9bbfd0aaa1ac77de80955ebea42eac92f`, and binary SHA256 is `51d95914a56d33302c3d2a32e950079aa713f7d07a9fc1506970d4bcc63dd588`. The portable default diagnostic binds report artifact identities to retained build receipts and verifies retained build logs/source receipts; it explicitly does **not** reopen unbundled build artifacts. A separate `local-artifact-negative-diagnosis.json` was generated with `--check-artifacts`; all currently available binary, loader, generated-header/catalogue and CMake-cache bytes matched their exact build-receipt hashes. Neither mode rebuilds or executes them.

## Evidence-supported interpretation

For all seven calls of the first hydrostatic segment, loose and middle runs produce identical state values and identical diagnostics, with two accepted half-step fractions each. Tight uses four. The identical accepted numerical schedule explains the first-endpoint error plateau. On the second segment, middle uses four accepted fractions per caller where loose uses two, while retaining the same first-segment error; the later void-error pattern is consistent with changed accumulation/cancellation of earlier and local errors. This is a supported interpretation of the retained schedule, not a general convergence theorem or proof of a unique cause for every error component.

The strict endpoint contraction requirement is genuinely unsatisfied despite the separate accuracy and transaction results. The original FAILED result must remain visible. Any prospective method/contract investigation needs a new, explicitly versioned and predeclared packet; it must not rewrite these original gates or receipts. Source ambiguity of printed Am, publisher reconciliation, wider domain and near-isotropic cancellation support, material AD, finite-spin material-axis evolution, IGS, experiments, calibration and scientific/public admission remain unresolved.

## Reproduction and focused tests

From an installed repository, generate a fresh file with `python3 -B -m tools.diagnose_clay2014_paths --output /private/tmp/clay2014-negative-replay.json`. Add `--check-artifacts` only when the exact local build artifacts are available; absence or mismatch then rejects. The script refuses an existing output. Run `python3 -B -m unittest discover -s tests -p test_clay2014_path_negative_diagnosis.py -v`. The staged overlay uses `PYTHONPATH=/private/tmp/atlas-clay2014-path-native-negative-review-20261031-v1:/Users/bmar5496/code/constitutive-atlas` and the staged test directory.

Six Python test groups pass in9.618seconds. They freshly recompute the complete frozen diagnostic, preserve FAILED despite partial parity, check all four precise failure identities and allowances on both backends, distinguish the independently passing checks, reject changed original input bytes without rehashing/blessing them, and enforce honest artifact-receipt-only scope in the portable replay. Compiled invocation is forbidden by the test fixture. Exact fresh replay reflects the current Python/libm platform; this packet does not assert a cross-platform correctly rounded reference or rigorous error certificate.
