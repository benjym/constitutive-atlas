# Fully rough interface main-laboratory handoff

WEB-interface2016-controlled-path-v1; implementation specialist `/root/hill_interface`; 2026-11-02. Assigned new files: `web/interface2016-laboratory.mjs`, `tools/build_interface2016_web.py`, `tools/test_interface2016_package.mjs` and this directory. No shared router/profile/catalogue/runtime files, builds, compiled material calls, browser sessions, remote actions, approval decisions or commits were performed.

The controller exports `setupInterface2016Laboratory({chart,cancelOrdinary})` and follows the existing main-laboratory controller router. The parent registers it and supplies the ordinary chart function. It reads the actual approved definition, descriptor and source-owned example. Model ID is `hvwe2016-reconciled-fixed-local`; exact state names are `sigma_normal`, `sigma_plane`, `tau_x`, `tau_z`, `e`. The state-name correction from source notation avoids DSL-reserved suffixes. Controls are `normal_strain`, `gamma_x` and `gamma_z`, all dimensionless. They are normal compression strain and two source shear angles. Each shear stretching is half its angle derivative. These controls do not prescribe finite slip, CNL/CNS or contact conditions.

The controller shows separate normal, in-plane normal, both shear-traction and void-ratio plots, the complete state and all observables at every point, complete parameters and starting state, start/end controls, path coordinate and progress. It preserves the complete immutable request on replay. Parameter/input changes or model deselection terminate the superseded worker and clear stale results. Worker replies must echo the current exact request and identity. Saved imports require the same model/engine/review identity and frozen settings, then replay against the saved result. Reset restarts the packaged example. No equations are integrated in the controller.

The package namespace is `material-point-interface2016/`, containing unchanged copies of `path-engine.mjs` and `path-worker.mjs`, a copy of the controller and `engine-path/` assets. The generic worker retains its own relative `./engine-path/` bridge. Existing NorSand assets remain separate. Root `path-engine.mjs` and controller bytes are checked against the namespaced copies. The ordinary root controller route is `index.html#laboratory?model=hvwe2016-reconciled-fixed-local`. No standalone model page is created.

The guarded builder finds the model's single registry approval and validates its accepted review, exact definition and supporting receipts. It regenerates all three controlled-path generated files, compares their exact bytes to the supplied build, validates the current complete compiled source closure and verifies actual engine module/Wasm hashes against the independently reviewed build receipt. Qualification must bind concrete cases and results; a distinct agent must accept that same binding. All public example/receipt/qualification/review/package-case files require scientific-review pins. `BUILD_RECEIPT_CONTRACT.json` gives the precise parent handoff schema. Final definition SHA is taken from the accepted review/registry, never guessed.

The builder emits model, catalogue, example, source receipt, approval, review, qualified engine, reviewed build evidence and source-facing `review.html`. It writes a strict package manifest for the entire namespace plus root copies. Raw copyrighted papers and vendor binaries are omitted. Its review page states fixed local axes, zero spin, dry total stress, the source-reconciled identity and missing finite-slip/contact/finite-rotation mechanisms.

The Node package checker is authored for parent execution only. It checks the strict file set and every hash before engine loading, verifies accepted bindings, then compares all five state components and all six Mandel stress components against reused independently frozen package cases. Existing parent acceptance tolerances are 0.2 Pa and 2e-6 void ratio. It checks the actual default at 40 output intervals against the same independent endpoint, exact replay, effect of the second shear angle, failed inadmissible-density rollback and same-instance recovery. No runtime or numerical success is claimed before the parent executes it.

## Checks actually performed

```sh
node --check web/interface2016-laboratory.mjs
node --check tools/test_interface2016_package.mjs
node docs/ingestion/hypoplastic-interface-2016/interface-v1/test_contract.mjs
```

Python builder AST parsing also passes. The pure contract test reports 37 checks, zero compiled calls and zero browser calls in `contract-results.json`. It rejects incomplete state/control fields, finite-slip control aliases, malformed progress/settings, descriptor mismatch, request extras and altered replay identity/settings/request echoes. It confirms immutable cloned inputs. One synthetic-fixture aliasing failure and its correction are retained in `RETAINED_FAILURES.md`; no production gate was relaxed.

The source worker supplied final candidate SHA `8ab12775390be5f5aa8f7db7a37da0990d444a343d037bd35fa36e3b5bdbc7ce`, `implementation-v1/example.json` and eleven independent package cases. The actual descriptor, forty-interval default request and every source package request pass pure structural validation. Source case settings supplied as named objects are converted to the canonical six-entry execution vector without changing values.

Parent next actions: freeze those source files and E4/E5 evidence in the agreed schema; integrate controller/profile/ordinary atlas/build flags; run guarded bundle/package checker in the coherent qualified tree; qualify the actual desktop/mobile browser; finish the authorized release. Public profile prose and actual default qualification remain coordinator/source-worker work.
