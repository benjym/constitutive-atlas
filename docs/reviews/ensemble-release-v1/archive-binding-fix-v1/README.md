# Exact historical source redirect

Current-main CI41297711154 Linux ran1433tests and failed only the retained
Tresca mixed-catalogue gate. The preceding fixture correction changed
`tests/test_laboratory_view.mjs`; its pre-change bytes were already preserved at
`catalogue/source-snapshots/e2b3d1527edb321012993eeb8778e1399ca27789979e0eacd9561de993809553/tests/test_laboratory_view.mjs`.
The original Tresca source-pins receipt still requires exactly that hash, but its
sidecar did not redirect this path to the existing immutable snapshot.

Add only that original-path/hash/archive-path tuple. All pinned historical
receipt/report bytes, numerical source, reference values, assertions and thresholds
are unchanged. Hash checks prove every document in the sidecar remains unchanged.
The saved Tresca gate, browser fixtures, ensemble packaging and catalogue checks
now pass13tests. The original sidecar and failed Linux log are retained here.
No compiled artifact execution was used for the saved Tresca check.
