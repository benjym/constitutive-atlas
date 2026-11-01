# Qualification inputs prepared, execution pending

The first preparation is retained as `freeze.json`. A complete cross-check then found that the retained controlled-path and Kelvin module/Wasm pairs also differed from the qualified Kelvin v7 package. No compiled result was observed and no gate changed.

`freeze-v2.json` supersedes those execution inputs. Every engine now has its own private snapshot. All eleven module/Wasm/catalogue sets are byte-identical to the qualified full package; copied supporting generated source and qualification receipts remain hash-pinned. The normal current catalogue generation matches the retained ordinary catalogue exactly. The public-profile source checker passes all 47 catalogue entries.

This is preparation, not current package or browser qualification. Run the recorded unchanged complete builder only after a fresh execution-slot handoff and a passing preflight. Its own exact-source and qualification guards remain mandatory. Keep any failure; do not edit the model, references, tolerances or admission requirements to make packaging pass.
