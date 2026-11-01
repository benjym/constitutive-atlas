# Retained delivery development failures

1. Initial package contract assumed one initial sample and strictly increasing times. The existing timed API intentionally emits left/right samples at the initial control event (same time, continuous state/strain, potentially changed rate). Package test rejected the valid default with `Incomplete timed history`. Correct contract requires samples+2, initial left/right event at start, subsequent times increasing; checks both sides without discarding event data. Scientific references/engine/gates unchanged.

2. Initial contract treated every rate as finite. Stress-hold initial right event intentionally reports six unresolved null rates before solving its first interval; contract now allows exactly that event mask, keeping finite rates required everywhere else. Original package check rejected it with `Invalid returned strain_rate`. No engine/reference changes.

3. First ordinary-switch browser probe waited for the word complete in the pre-existing run-status element and timed out. Inspect actual ordinary status and correct the probe rather than change product behavior or weaken numerical checks.

4. A source-evidence synchronization command ran from the release directory and attempted to copy that directory onto itself. shutil rejected it without changing sources. Reran using explicit workspace and release paths; numerical/package acceptance unchanged.
