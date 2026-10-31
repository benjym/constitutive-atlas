# Reproducible caller loading design v1

Recommended first step: additive exact-bit literal-control API in FOUNDATION_REVIEW.md. Keep the legacy API, browser/import behavior, caller bits and failed gates unchanged. DESIGN.md compares the optional future versioned deterministic producer, proves its conditional bound and defines prospective gates. No production implementation/build/candidate evaluation was performed.

Independent fixtures:1080phasecases,9720controls at140/180digits. Ten exact-rational bound certificates and159584 reference/rounding/phase checks pass; original comparator parsing failure retained. Reproduce with python3 -B reference.py PRECISION OUTPUT, check_proof.py and check_reference.py. Initial source/policy freeze precedes both reference runs. Exact bits are oracle fixtures for a specified arithmetic contract, not observed C++ outputs.

Parent owns implementation/source audit/serial builds and new regression identity; deterministic producer and default/export/import adoption are deferred.
