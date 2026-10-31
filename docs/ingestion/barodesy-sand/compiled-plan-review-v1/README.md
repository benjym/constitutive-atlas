# Sand barodesy2015 prospective compiled mapping review

Task `AUDIT-barodesy2015-prospective`; owner `review_igs97`; 2026-10-31. This bounded automated review found **no blocking source-v2/corpus mapping mismatch** in the exact pinned inputs. It authorizes no model admission and does not predict compiled success. No compiled executable, Wasm, build or collection was run by this reviewer. Historical source/audit bytes are unchanged.

## Inputs and scope

The selected formulation remains Kolymbas2015 [Introduction to barodesy](https://doi.org/10.1680/geot.14.P.151), fixed-frame/nonzero-stress research selection. The separately identified2019 calibration fixture, source trace typo, zero-stress/frame limits and operational numerical interior remain as documented in [source v2](../rate-study-v2/README.md). This review checks its mapping to the frozen [prospective study](../../../../catalogue/investigations/barodesy2015-rates-v1/README.md), not a new source transcription or scientific review.

`reviewed-inputs.json` pins the three assigned prospective files, prospective README, all72 protocol dependencies and the examined source files. The receipt retains the literal original protocol hash. Future source changes require new review or an explicit archive; passing this packet against changed bytes is not an equivalent review.

## Findings

| Check | Exact locator | Result |
| --- | --- | --- |
| Expected rates | prospective `prepare.py:28–32`; source `reference.py:72–77,93–159`; source `check.py:20–40` | All38 valid IDs and seven-channel oracle120 values map exactly. A complete fresh80/120-digit replay, failure diagnostics, ancestor and frozen-input checks pass. Exact rational volume is independently recalculated for every valid request by this audit. |
| Stress and void budgets | prospective `prepare.py:34–39`; source `protocol.json:14–24`; source `check.py:64–84` | Each of six stress components gets2e-12 times max(natural scale, reference norm). Exact zero-loading budgets are zero. Void is exact zero when reference zero, otherwise4ULP. Parity gets twice these budgets; it does not replace either backend’s independent gate. |
| Literal parameter layout | prospective `prepare.py:29–30`; source `protocol.json:55–63`; `atlas/compiler.py:44,65–67` | Seven slots in order c1,c2,c3,c4,c5,ec0,emin. Every finite literal roundtrips to its named source binary64 value. No default substitution or parameter-count coercion. |
| Literal state/loading layout | source model state list; `atlas/compiler.py:36–43,70–78`; `tests/research_rate_driver.cpp:23–29` | Seven states sigma6/e; six loading components. Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. All38 valid and16 numeric invalid requests preserve actual input components. |
| Numeric rejections and recovery | prospective `prepare.py:41–46`; source `protocol.json:37–54,65–75` | All16 selected invalids appear once, immediately followed by the exact original oblique control request, expected vector and budgets.70 calls plus descriptor equals71 rows/backend. |
| Excluded types | source `protocol.json:31–36,65–69` | boolean-loading, nonfinite-text, extra-parameter and missing-parameter remain Python-only. No malformed CSV test or compiled type rejection is claimed. |
| Dependency coverage | prospective `prepare.py:49–55`; prospective freeze files map | All72 protocol pins and three prospective-freeze pins match. Mandatory source/reference, common compiler/schema/tensor/expm, generic rate driver, isolated CMake and collector/parity files are covered. Artifact/toolchain/generated-byte identities remain future build receipts. |
| Persistent transport intent | `tools/research_rate_observations.py:106–107`; `tests/research_rate_driver.cpp:35–43` | Source uses one native stream with descriptor and all70 calls; CABI target supports repeated calls. Actual persistence/recovery remains an execution evidence gate. |

The cancellation request `[500,1e-130,-500,0,0,0]` is retained with a nonzero exact-rational void target. Literal binary64 summation in a compiled backend may fail this already frozen criterion. Such failure must be retained; this review neither removes the case nor changes any criterion. Rounded-critical-density remains an operational numerical rejection, not a new physical-source restriction.

## Reproduction and negative checks

From this directory, with the reviewed repository available:

```sh
python3 -B audit.py --repo /path/to/constitutive-atlas
ATLAS_REVIEW_REPO=/path/to/constitutive-atlas PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v test_audit
```

Eight test groups pass. Mutations reject swapped parameter slots, swapped shear-state channels, forged expected rates/budgets/parity budgets, Boolean aliases to zero references, missing rejection/recovery rows, a different recovery request and absent/corrupted compiler pins. `evidence.json` retains the positive independent audit. `checks.json` retains test commands/counts. These tests exercise the review verifier, not compiled transport.

The audit independently reconstructs the mapping from source inputs/policy/reference rather than calling `prepare.prepare()`. It invokes only the source Python reference checker for full fresh replay; it does not reuse Atlas constitutive evaluation to establish the source reference. Existing source-v2 derivation/independence qualifications remain in force.

## Limits and next action

No blocker was found within the specified prospective mapping scope. The generic collector’s full raw/parser/evidence implementation is separately reviewed by its assigned lane; this review checks corpus intent and source dependency coverage only. Source numerical classification near boundaries, toolchain identity, actual descriptor/hash matching, raw-before-assessment capture, both backend numerical gates, same-instance recovery and evidence-backed parity must still be demonstrated by the coordinating study. Finite integration, material AD, experiments and scientific/public admission remain open.

The smallest next action is the already frozen71-row/backend study using separately pinned build artifacts, retaining every original observation and any negative outcome. No budget or equation changes are proposed.
