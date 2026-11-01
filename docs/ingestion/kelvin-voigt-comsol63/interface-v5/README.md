# Coherent replay-tampering fixture v5

The parent retained normal package attempt2 failure in ../package-v1/build-attempt2.log: the checker altered saved state[3] by.01 while leaving its duplicate strain[3] unchanged. The valid transport guard rejected this inconsistent document before the intended exact-replay rejection assertion.

This narrowly scoped correction also alters the duplicate saved strain[3] by.01. The existing100Pa stress alteration and unchanged exact-replay rejection assertion remain in place. The test now presents a coherent but numerically corrupted saved output to import, permitting the intended fresh-result comparison to reject it. No production file, input control, numerical policy or acceptance gate changed.

Exact previous checker bytes are preserved under prior/tools/test_kelvin_voigt_package.mjs and bound in freeze.json; earlier failures and freezes remain unchanged. `node --check tools/test_kelvin_voigt_package.mjs` passes. No compiled execution, package build, browser action or Git mutation occurred; coordinator rerun and separate review remain required.
