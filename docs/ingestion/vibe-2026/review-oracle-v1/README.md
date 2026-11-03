# Independent review of synthetic controlled-time oracle correction

Reviewer: `/root/vibe_oracle_review`, a separate run that authored neither the production fixture/runtime nor the original/corrected reference or backend runners. Owned output is this directory only. The coordinator requested a source-only correction review before any rerun.

The original six-test native run failed one group. Its raw output remains a failure. The fixture defines `e_dot = -(1+e)*trace(strain_rate)` in compression-positive Mandel coordinates. Integration gives `e_end = (1+e_start) exp(-Δεxx-Δεyy-Δεzz)-1`. Mandel shear components have zero trace. The original reference generator incorrectly included all six components. For the mixed increment the correct trace is 0.0009; its six-component sum is 0.0014. The recorded native result 0.7983807287813467 is consistent with the former, while the old expectation 0.7974817631770881 fails its original bound.

The earlier review-v3 reproduced the generator's bytes; this did not independently establish that the generator used the correct tensor trace. That historical report and every original reference/failure remain unchanged. This review independently derives the trace solution and checks each of the six basis cases, all mixed partitions and all 18 retained cases.

Final exact-byte decision and inputs are recorded separately after the author's immutable correction freeze. This is eligibility for a new coordinator-run study. It is not an E4 backend pass, model E5 approval, browser qualification or publication.

No build, compiler, native module load, Wasm evaluation, browser, remote action or compiled material execution is performed by this review. `audit.py` uses only Python's standard library and saved JSON observations. No temporary resources or preview processes are created; this directory is retained evidence.
