# Landing-page simplification — 2 November 2026

Removed the hero eyebrow, four numbered tile labels, decorative arrows,
Discover prompt, footer eyebrow styling and entire From equations to experiments
introduction. Cover, title/subtitle, main action and four linked panels remain.
The old explore-atlas anchor now points to the panels. Removed unused styles
and kept panel text bottom-aligned.

Actual Playwright-v2 passes content-removal assertions, four destinations,
ensemble/brand navigation and desktop/390px mobile layout. Desktop screenshot
visually inspected. Browser-v1 encountered the unchanged document because a
same-fragment goto did not reload; retained failure, added explicit reload and
passed. No runtime changes/builds or deployment.

Visual follow-up: initial cleanup left partial CSS descendant selectors, disabling
the desktop grid. Corrected the dangling selectors; browser-v3 explicitly
asserts desktop display:grid and passes. Final desktop-v3 screenshot visually
inspected; prior results/screenshots/receipt remain.
