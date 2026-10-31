# Catalogue keyboard and small-screen pass — 1 November 2026

Bounded part of ROADMAP WEB-06. Closing a freshly loaded model permalink left focus on the page body. `web/app.js` now restores focus to the matching catalogue card, or Search if the card is filtered out. Existing focus inside the catalogue is retained; other pages are not focused by this fallback.

## Checks

Actual in-app Chromium preview below the `/constitutive-atlas/` project path:

- Fresh Drucker–Prager permalink + Escape: dialog closed, hash `#catalogue`, focus on its model card.
- Card + Enter, then Close + Enter: focus returned to its card.
- Search `no-such-model`, open the permalink and Escape: zero visible cards, focus returned to Search.
- Terra Cotta candidate: Test button hidden; keyboard Close worked.
- At 375×667, the long Mašín 2013 title, close control, scrolling body and footer fit. Candidate page width was 375px, with no horizontal document overflow.
- At 667×320, the same detail panel stayed within the viewport (280px dialog height) with a 79px scrolling body and visible footer.
- Temporary viewport override reset after testing.

The initial event-only fallback did not consistently restore direct-link focus. The final version also restores focus synchronously after the close route. Native dialog tabbing was exercised, but this is not a complete keyboard/screen-reader accessibility audit.

`python3 -B -m unittest discover -s tests -p test_web_catalogue.py -v` passed all three wrappers (catalogue/state JavaScript contracts and ES-module syntax). Real browser checks above cover the changed focus behavior.

## Scope and source identity

Previous app SHA-256: `220f827a4600426321291b34467645c35482ddf12b5f7759c9ec7ac69dbb5ba9`. Exact bytes preserved at [source snapshot](../../../catalogue/source-snapshots/220f827a4600426321291b34467645c35482ddf12b5f7759c9ec7ac69dbb5ba9/web/app.js). Current app SHA-256: `5e60667e095f60adc4e28375ade4798f593dfa7c45b53d1830c7bea31aed7515`.

Preview reused the previous complete local package and copied only the edited app into it. This was not a fresh package build or hosted deployment. No C++/Wasm builds, model changes, scientific decisions or raw-data release.

WEB-06 remains open for chart units, import compatibility, stale assets, cancellation/resource limits and broader accessibility/mobile testing. This task ends with the focus fix and these recorded checks.
