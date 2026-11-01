# Prospective refinement v2

Native v1 retained five failed accuracy gates: global direct-midpoint errors
of about0.066–0.084Pa exceeded0.06Pa, and two implicit-schedule errors
of about18.4–19.6Pa exceeded15Pa. Local temporal estimates do not bound
global error. Do not relax any gate or alter constitutive/reference equations.

Only rtol/atol tighten by100: direct ODE1e-10/1e-13 and schedules1e-9/1e-12.
All27physical requests, expected statuses, references, budgets and limits stay.
Reuse the exact qualified-source native binary; no rebuild is justified.
Wasm starts only if the new native study passes all27gates. Before Wasm, freeze
this study, wrapper, original source closure and failed v1 report. Native/Wasm
physical parity and same-instance failure/recovery/replay remain required.

The original prospective v1 freeze/report/raw results remain unchanged.
This revised study does not supersede or relabel the original failed outcome.
