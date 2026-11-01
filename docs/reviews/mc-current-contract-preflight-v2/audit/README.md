# Current scoped Mohr–Coulomb transport audit v2

Bounded independent AI technical review, using manufactured frames only. Transport checks pass, but document validity fails: the current browser reader accepts 28 malformed documents (14 duplicate envelope names and 14 nested unused `1e999` numbers). This is not model qualification or scientific signoff. No model, backend or compiled artifact was called.

The independent replay reproduces `consumer-results.json` byte for byte, including `passed:false`. Collector exit zero means collection completed; it does not mean readiness passed. The parent's separate failed readiness gate is not independently executed here.

Independent checks cover 12 metadata records, 14 Mohr–Coulomb paths, 834 controls and 820 deltas. The exact helper name, return type, six argument types and parameter/initial/settings/control arguments were checked in 28 manufactured callbacks. The original collector has 56 manufactured callbacks. Twelve metadata entries do not establish twelve numerically qualified or deployed models.

All 70 tested document mutations actually change the document and are rejected. The historical zero-hold wrong-control mutation was a no-op; the retained final mutation selects a different zero/minsub bit and rejects. Both parser weaknesses independently reproduce on all 14 paths. `tools/strict_observation_json.py` rejects the two retained raw witnesses: it checks duplicate decoded names and finite numbers throughout the document. Its integer policy is not identical to the browser's exact-integer check.

The catalogue hash independently recomputes; all 172 source pins match. The candidate differs from the prior MC record only in name, description and status. No constitutive expression, parameter or guard change was found. Existing reference inputs remain pinned. This collector does not exercise the prospective stress/strain/control or backend-parity accuracy budgets, and gives no evidence of numerical accuracy.

Frames are explicitly synthetic: 834 state/strain/control values agree with rounded independent references, while diagnostics are manufactured zeros and unavailable pore pressure is null. Signed q is reconstructed from rounded axial/radial state, rather than necessarily the directly rounded high-precision q. At protocol-0/monotonic point 7 those are 52500.0 and 52500.00000000001 respectively. Two initially overstrong audit provenance checks failed; their code and explanations are retained without changing production code or policy.

A generic document-parser repair is warranted before an execution freeze: reject duplicate decoded names (including nested/escaped aliases) and every nonfinite decoded number, including unused fields, while preserving the intended integer and signed-zero semantics. Freeze new parser tests and rerun the failed transport gate before considering a numerical collection. No future collector, freeze or admission is approved by this audit.

Public handoff files are all files listed in `manifest.json`: README, findings, independent audit/check scripts and results, raw manufactured witnesses, original failed audit checks/explanations, reviewed source snapshots, and their pins. No private paper or compiled artifact is included. Replays: `node audit.mjs`; `python3 -B check.py`. The copied parent collector can be run with an explicit output path from this packet.
