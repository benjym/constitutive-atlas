# Prospective stage outcome contract addendum

Coordinator clarification received after initial review freeze e35e66e891e29436d15a8c2974882e1d0e18a0bf94580ee496a6a0206ff5aedc; its exact manifest bytes are preserved in initial-freeze-manifest.json. Original REVIEW.md/decision/witness bytes remain unchanged.

All65 planned stages expect process exit status0. The new corrected receipt identity must require exit_status==0 before post passed can be literal true, while still retaining exact stdout/stderr hashes and nonzero status on failure. V2 currently sets passed=true after recording any supplied integer exit status. Its documentation explicitly described this as identity-only success, so this addendum preserves that historical meaning rather than inventing a numerical observation. The coordinator now requires a distinct prospective stage-success contract in v3. A nonzero stage must stop the study; saved raw failure evidence must never be omitted.

Batch this correction with B1 and B2: nonassert unoptimized guards in entry and verify; PYTHONOPTIMIZE=0 allstages and tool policy; strict matching pre identity/phase/profile/stage/packet/source/tool/plan, command and literal true. No numerical requests, model, source tolerance or assessment gate changes are authorized.
