# FINAL-DISPLAY-1 source correction

Source fix accepted. Current app introduces refreshCatalogueStatus(entry,spec), invokes it both during showCatalogueModel and the open-dialog update after loadEvidenceIndex resolves. The asynchronous continuation resolves the currently selected catalogue entry and model, so an older selection is not restored. Helper changes text only; it neither rebuilds detail body nor moves focus. Existing evidence-section update preserves scroll. This addresses the stale draft badge on a direct catalogue deep link.

The before/after diff also replaces the generic formulation section for material_laboratory entries with a dedicated-lab explanation. This is separate concurrent integration work, outside the narrow OCC helper fix; parent informed to preserve ownership/portable qualification. It does not affect OCC, which has the common executable laboratory.

This is source acceptance only. New package manifest and completed final builder must bind changed app bytes. Actual delayed-evidence browser observation and full portable CI remain pending. Original final-review-v1 and browser failures remain unchanged. Zero reviewer compiled calls. Exact before/current hashes recorded in final-display-fix-source-v2.json.
