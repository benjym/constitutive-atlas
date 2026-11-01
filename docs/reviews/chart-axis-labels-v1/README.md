# Generic chart axis readability — isolated candidate

This candidate addresses Maxwell browser finding BROWSER-V2-P1 with the common chart renderer. Shared application files are unchanged; installation awaits the active shared-package handoff, exact-byte source preservation and independent review.

The existing text selectors style only ordinary chart-panel/source charts. Maxwell uses the same renderer inside an experiment-card and inherits 14px text. The retained actual mobile fixture reproduces 13 labels extending beyond the SVG coordinate viewport. The candidate gives every common-renderer SVG an atlas-chart class, shared 11px typography and symmetric label margins. Long numeric labels use three-significant-digit scientific notation. Exact zero remains zero; tiny nonzero values keep their signs rather than being suppressed by the old absolute 1e-10 cutoff.

The actual prior/candidate renderer is extracted byte-for-byte from each saved app source. Four unchanged qualified Maxwell exports supply stress, accumulated strain and rate values. Additional clearly synthetic tiny-value, exponent-range, ordinary-path and empty fixtures test presentation boundaries; they are not scientific qualification. No model or solver executes.

The saved browser observations cover sixteen charts per viewport, four saved histories, source-value equality and every polyline coordinate. Desktop1280px and mobile390px candidate labels all remain inside the480-unit SVG viewport; neither page overflows horizontally. Five actual screenshots include negative rates and exponent labels, visually inspected by the coordinator. The signed formatter test spans1,206 values over exponents-300 through300 and reproduces the old tiny-value loss. The candidate retains all underlying plotted points and axis domains, with only presentation coordinates changing.

Run from the repository root:

    python3 -B docs/reviews/chart-axis-labels-v1/check_saved.py

This is isolated renderer/stylesheet qualification, not an installed whole-application, fresh engine, model, release or live-site approval. Initial automatic favicon404 is retained. The Playwright CLI attempt failed on npm DNS; the available browser connector supplied actual browser observations. No supplied author code, compiler, new trajectory or remote action ran.

Next: separate agent review of exact candidate/evidence, then coordinate rebasing and source/receipt preservation with the current shared package owner before installing and testing the actual main laboratory.
