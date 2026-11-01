# Isolated Lade–Duncan1975 local-Eq19 backward-Euler candidate v1

This candidate is an explicit numerical realization of the source equations in [the complete original-source packet](../README.md), not a public/approved model or a later1977 formulation. Source choices and limitations are frozen in [POLICY.json](POLICY.json). SHA-256 of [model.json](model.json): `5d02250d99a70bf0dbb0783e098ccb8738544b5e04de876f0d295057036ec8c1`.

## Exact choices and scope

v0.3 incremental_residual, strain_path, small_strain_3d, fixed_spatial, no objective rate, compression-positive Mandel stress/strain. Declared total Cauchy stress is a restricted uncoupled mechanical/zero-pore-pressure embedding; the source supplies no pore-pressure law or total/effective decomposition. No undrained interpretation is authorized. Only dense/loose Table1 example sets are presently checked; parameter slider intervals span their numerical values but do not imply qualification of intermediate combinations.

The minimum-pressure expression uses the exact lazy repeated-minimum composition reviewed independently. It supplies a Clarke cluster-average generalized derivative at ties, not a classical directional derivative or a Newton-convergence guarantee. All coefficients use current endpoint stress. The flow tensor differentiates the potential at fixed κ2, then the completed residual differentiates its coefficient dependencies as usual. State consists of sigma, maximum reached stress level h (bounded below by threshold ft), and accumulated local Eq19 work wp. No plastic strain tensor is needed by these equations. Explicit preparation supplies all persistent state; initial literals are examples only. The candidate stops at f>κ1 and supplies no postfailure extension.

The finite residual consumes the newly reached f excursion above committed h; it has no physical clock. Integration subdivision and event resolution remain necessary. Work uses the local Eq19 interpretation, not a global changing-pressure Wp(f,a) constraint. No stress clipping, artificial eigenvalue separation, coefficient freezing or history reset is present.

## Recorded checks and retained failures

- Original-source algebra:15 assertions pass; independent reviewer additionally confirms work/covariance and contrary-interpretation witnesses.
- Candidate schema/semantic validation and normal compiler generation pass: [validation-generation.json](validation-generation.json). The first declaration attempt compared Pa work with dimensionless zero; that type rejection and exact rejected model are retained in `validation-generation-rejected-dimensions.json` and `model-rejected-dimensions.json`. The corrected comparison uses0·pa.
- [Eight interpreter known-endpoint checks](interpreter-results.json) pass for both Table1 examples: zero, hydrostatic, proportional constant-f loading, and a source-derived plastic endpoint. These do not integrate a path.
- [Independent stress-driven triaxial reference](triaxial_reference.py), with frozen [policy](triaxial-policy.json), converges for eight targets across both examples: [reference results](triaxial-reference-results.json). It uses scalar source compliance quadrature split at ft and stress inversion, independent of the candidate DSL or native solver. This is not digitization or reproduction of the paper's measurements.
- Coordinator built one explicit isolated common-engine target with `--parallel 1`: [build receipt](native-build-receipt.json). Source snapshot pins and build/configure logs are retained. No shared CMake/compiler/runtime/public model files were edited. An initial manually malformed five-component state request was rejected; exact response retained separately.
- The prospective [native refinement study](native-triaxial-results.json) **FAILS**:7/24 requests return success, and the required finest plastic paths fail for both examples. No bound was relaxed. Original complete request/response bytes are retained at their ignored `.local/.../native-requests/` paths and hashes recorded in the public report.
- [New onset diagnostic](native-onset-diagnostic-v1.json), created after the failed study without altering it, finds each finest failed path's last committed h slightly below recomputed f (about7e-15 to5.9e-9). The candidate's strict source-consistency `h>=f` initial check then rejects even a zero increment. A small residual alone therefore does not ensure an admissible reusable committed history state. No numerical tolerance or projection was added to make the frozen gate pass.

Reproduction from repository root:

```
python3 -B docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/candidate-v1/check_candidate.py
python3 -B docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/candidate-v1/triaxial_reference.py
python3 -B docs/ingestion/lade-duncan-1975/delivery-v1/supplied-original-v2/candidate-v1/check_native_triaxial.py
```

The native checker requires the exact pinned isolated binary. Build commands and serial target are in the build receipt; generated/common-engine snapshot source identities in native-source-manifest.json. The shared checkout may evolve independently; do not regenerate and call new bytes the same study.

## Current blocker and smallest next action

E3/E4 remain incomplete: accepted solver output does not consistently satisfy the strict history invariant needed for re-entry. An independent failure review is scoped under failure-review/. Distinguish a missing model solution declaration, generic trial-versus-commit feasibility semantics, and an alternative exact declarative history representation before selecting a fix. Any changed candidate, numerical convention or generic lifecycle support needs a new identity, prospective study and affected regression checks. Retain the current failed model/results. Do not silently relax the invariant, project history, remove the failing example, or relabel the elastic-only successes as full model support.

Wasm/browser/atlas integration and E5 model approval have not been attempted; the source-access blocker is resolved. The independent source audit is not a checklist approval for this candidate. Full MODEL-lade-duncan-1975 stays open.
