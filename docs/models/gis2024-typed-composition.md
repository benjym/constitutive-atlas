# Typed14-rate HP+GIS composition wrapper

`tools/inspect_gis2024_coupled.py` now provides `coupled_rates(state,de,parameters)` by composing the corrected typed HP host and existing typed supplied-host GIS evaluator. This is instantaneous composition only: no finite update, state commit, hidden preparation, universal default material parameters or admitted model.

State requires exactly `sigma:Sym`, `e:real`, `h:Sym`, `Omega:real`; `de` is a Sym strain derivative in compression-positive Mandel convention. All18 physical parameters are explicit. The wrapper validates/copies all inputs, calls `tools.inspect_gis2024_hp_host.host`, supplies E,m,C,S,f to `tools.inspect_gis2024_rates.rates`, and computes the source-mapped void-ratio rate `-(1+e)*trace(de)` using the existing finite-intermediate restricted AST interpreter. It returns named tensor rates as Sym, scalar e/Omega rates, a14-component derivative list ordered sigma6,e,h6,Omega and scalar diagnostics. Exact zero de preserves the GIS policy: zero rates and undefined q,k,suppression. Inputs are never mutated.

Production imports contain no oracle/reference module. Conversely, `tools/reference_gis2024_coupled.py` and its independent host reference import no production typed evaluator or Atlas DSL. Scientific source review is still pending; implementation separation is not independent scientific authorship.

`tests/test_gis2024_coupled_composition.py` checks all38 retained independent cases and reevaluates the plain-sequence oracle. Three groups pass: complete rate/diagnostic comparison and input isolation; zero-direction handling; exact parameter/state/type/domain rejection without input changes. Dimensionless memory rates receive separate tight absolute checks rather than sharing the stress-rate tolerance. Across the retained cases the observed maximum absolute differences are:

- sigma rate: `1.862645149230957e-9` Pa per dimensionless coordinate;
- h rate: `2.168404344971009e-19`;
- e rate: zero;
- Omega rate: `6.938893903907228e-18`.

These sampled arithmetic errors are retained in `catalogue/investigations/gis2024-coupled-rates-v1/comparison.json` with per-case values and dependency hashes. They are not integration-error estimates or evidence near singular source domains. The corrected typed host is a required dependency. The independent shared host-reference copy remains identical to the prior host packet.

After installing dependencies at normal repository paths, run:

```sh
python3 -m unittest discover -s tests -p 'test_gis2024_coupled*.py' -v
```

The original seven pure-reference groups and three composition groups all pass in the staged overlay. The isolated flattened research schema now matches these instantaneous outputs through Python, native and Wasm checks; see [engine evidence](gis2024-research-rates.md). The full pairing uses strict computed Mandel norm(h)<=R and rejects nonzero-direction suppression underflow. This wrapper does not perform finite integration.
