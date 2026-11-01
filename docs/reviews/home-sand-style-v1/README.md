# Sand Atlas inspired home and shared theme — 2 November 2026

User requested a new index page, cover image and styling adapted to
https://sand-atlas.scigem.com/. Inspected the actual site in Playwright:
photographic panels, dark backgrounds, white type/rules, widely tracked labels,
Source Sans typography and outlined actions. Implemented an original cover and
layout rather than copying its content or assets. Reference screenshot retained
at output/playwright/sand-reference.png.

## Changes

- Root, #home and the brand now open the new landing page. Four large links
  open existing testing, catalogue, ensemble and methods routes. Start exploring
  opens testing; Discover scrolls to the introduction. Existing model/section
  deep links continue to resolve. Navigation is available before solver startup.
- New atlas-theme.css supplies the shared horizontal header, Source Sans3 type,
  neutral laboratory surfaces, dark home panels and responsive layouts.
  Existing controls, charts and model definitions are unchanged.
- web/assets/constitutive-cover.webp is a395KB1536x1024 original AI-generated
  illustrative sandstone/mineral-grain image, made using the imagegen skill.
  It is decorative editorial imagery, not an experimental specimen record.
  Original retained privately at
  /Users/bmar5496/.codex/generated_images/01a19913-8e67-77f0-8a62-9100a3586f07/exec-c30c67cc-15be-4e78-9d91-bdeab4bd2b77.png.
- Narrow builder hook copies the new CSS, navigation module and exact cover
  into the standard website package. Existing concurrent builder changes kept.

## Checks

33Node catalogue/package/ensemble checks and9Python checks pass. Actual-source
laboratory routing probe passes256checks/36profile transitions for14ordinary
models and5special profiles. Navigation JS and builder syntax pass; owned
tracked-file whitespace checks pass.

Actual Playwright final-v4 passes root/cover, four cards/brand/active navigation,
Discover/Start actions, linear-elastic deep link with successful response,
browser history,15realWasm full-range ensemble completions, and every route at
390/760/900pixels without overflow or header overlap. Final home screenshots:

- output/playwright/home-sand-style-desktop-final-v4.png (1440x1781)
- output/playwright/home-sand-style-mobile-final-v5.png (390x2304)

Both visually inspected. Laboratory/ensemble screenshots also retained.
Browser script and final transcript are adjacent to this README.

## Retained diagnostics and boundaries

Initial port18870 was occupied by another preview; left it untouched. Its
screenshot is home-sand-style-port-collision.png. Initial browser-v1 geometry
check measured main rather than its padded page; browser-v2 corrected it and
fixed inherited mobile static header positioning. Visual inspection found
cross-page smooth scrolling and stale screenshot height. Final theme uses
instant route transitions and explicit flex header; final mobile screenshot
waits for settled layout. Earlier results/screenshots remain.

First isolated preview reused the old ensemble engine. Current ordinary worker
requires a newer scoped ABI, producing TypeError in that preview despite
working ensemble requests; missing unrelated package assets also returned404.
Final browser-v4 instead reuses the already-qualified matching full package
/private/tmp/atlas-occ-shared-app-v2/site-v2 read-only, overlaid with current
frontend modules and ensemble assets, at
/private/tmp/atlas-home-sand-style-v1/site-v2. Linear-elastic response and the
ensemble both complete there. This is a scoped frontend qualification, not a
fresh current full-site/runtime build. No engine was rebuilt, no scientific
approval changed, and no commit/push/deployment/remoteCI occurred.

Reproduce frontend tests with the existing commands from ensemble-full-range-v1.
Serve the final isolated preview on127.0.0.1:19484 and run
playwright-cli -s=atlas-home run-code --filename docs/reviews/home-sand-style-v1/browser-checks.cjs.
