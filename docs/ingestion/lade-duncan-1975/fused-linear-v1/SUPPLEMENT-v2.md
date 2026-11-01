# Bounded first-target driver correction before execution

Use check_legacy_exact_bounded.py for the FIRST exact native baseline gate.
It supersedes the unfired original driver's generic timeout handler: retain
TimeoutExpired partial stdout/stderr and hashes, elapsed time and explicit
failure. No retry; complete response still must match every original field,
and elapsed must be strictly less than120seconds. All other CONTRACT and
SUPPLEMENT gates, order, source, policies and budgets remain unchanged.
