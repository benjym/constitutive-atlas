# Shared website source-context preservation

Shared commit f51113bd simplified site navigation and changed three hash-pinned browser test sources. The retained original working-tree run correctly rejected one missing source redirect in the Tresca mixed saved gate. Exact pre-change files from f51113bd parent are preserved, along with15original sidecars needed for recursive receipt closure.33original path/hash references now resolve; all18snapshot bytes hash exactly. No test/source/model/policy bytes or expected hashes changed. Only original-byte copies and additive archive redirects are integrated.

In isolated committed51a9 snapshot, with only these archive redirects plus the separately reviewed catalogue consumer correction,18saved-only Tresca/evidence tests pass in1.999s; compiled calls are forbidden by the existing saved-only test. The delivery identity/76earlier archive checks also pass unchanged.

The first tracked-JSON inventory used an unsupported literal git ls-tree glob and returnedempty; its zero-edge attempt is retained. Corrected inventory explicitly lists tracked JSON from51a9. Broader working-tree compiler/DSL/history/solver archival belongs to another worker and remains unstaged. Final index is reconstructed from HEAD plus only the33listed edges rather than staging whole shared sidecars.
