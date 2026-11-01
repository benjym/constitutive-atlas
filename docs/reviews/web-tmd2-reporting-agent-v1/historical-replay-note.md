# Historical scientific-checker replay after the website update

The final current-live-path replay of the original scientific-review and coordinator-status checkers failed at one old input: docs/reviews/tmd2-web-snapshot-v1/source-archive-map.json. The website change added historical redirects to that live map; its original exact bytes were preserved before installation. The two failures remain in retained-live-path-failures.json and their stderr files. They are not relabeled as current-root passes.

The separate historical-replay.json selects 165 explicitly hash-bound public files into an ignored minimal evidence view. Exactly one input comes from its content-addressed archive: that old map. No original source/checker/expected hash/gate is edited, no private arrays are copied, and no general interpreter/import redirection is introduced. The original scientific public/private checkers and coordinator-status checker run unchanged in this view. All three pass; both scientific results match their original recorded JSON exactly. The private run reads the original seven local files and emits only the already recorded aggregates.

This establishes replay of the accepted historical evidence, not current-source numerical qualification or permanent availability of private dependencies. The site exports only the immutable decision and original review text; it does not claim a fresh model or new experimental validation.

Verify the retained result without execution:

    python3 -B docs/reviews/web-tmd2-reporting-agent-v1/check_historical_replay.py

The original replay_historical_review.py creates one fresh identified view and refuses to overwrite it. Re-execution needs a separately named output and evidence record; it is not necessary for the pure check above. The new website source/package/browser checker remains a separate current check.
