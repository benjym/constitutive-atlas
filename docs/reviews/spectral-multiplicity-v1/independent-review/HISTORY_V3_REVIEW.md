# Independent review of successful-history expectation correction

Reviewer: `/root/spectral_multiplicity_review`,2026-11-01. Decision: **accept a distinctly frozen revised v3 study**, retaining v2 as failed. This is a test-expectation correction, not a production fix or numerical tolerance change.

I checked the generated history source already frozen before the failed observation. The synthetic program has one unconditional advance phase: `fires=true`. The expression gate chooses the written tensor (`I` when gate0), while the event append is outside that expression and executes whenever the phase fires. Thus successful recovery has exact event sequence `[0]`, identity state, generation8 and epoch3. Failed-write rollback still requires no events and unchanged incoming state/counters.

My initial request that successful recovery assert an empty event sequence was incorrect. The v2 failure exposed that mistaken interpretation; the historical prospective review and failed v2 result remain intact. Changing only successful recovery's expected sequence to exact `[0]` restores correspondence to the preexisting frozen semantics and retains stronger exact event coverage. No scalar numerical result, unresolved-gap policy, tolerance, reference or production behavior is changed. Final review must bind the distinct v3 driver/manifest and retained v2 failures.
