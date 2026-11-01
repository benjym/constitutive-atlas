# Actual native FD failure localization

Reviewed logging-only source overlay. Configure and one serial atlas_numerical_tests target build passed; the original unchanged positive-mode invocation exited 1 as expected. First failure: row0/column8, AD -235.38608480040432, FD -235.37722881883383, h 5.0000000000000002e-11. Full exact residual operands/state/scales in 2/stderr. No tolerance or acceptance changed; this is failure localization, not numerical qualification.

Orchestration verifies all source/tool/input pins before and after every command. Complete source/build/raw execution archive has every member checked against archive-receipt.json. Original positive study remains FAIL.
