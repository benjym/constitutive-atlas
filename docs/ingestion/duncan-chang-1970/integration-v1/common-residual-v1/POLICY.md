# Common-input residual diagnostic

Freeze identical model/parameter/current/previous/strain inputs before any calls. Use all first12saved cyclic endpoints, each native/Wasm previous and strain increment, and native/Wasm endpoint or previous-state guesses. At points9/10 add fixed signed perturbations to each current/previous/strain component. These are reconstructed probes, not observed Newton trials.

Record every raw response from baseline native, contraction-off native and baseline Wasm evaluate APIs. Report domain rejection agreement and all exact residual differences; do not skip invalid cases or convert a negative diagnostic to a release pass. No shared source, build, tolerance, input or scientific gate change. The original browser-wire gate remains failed.
