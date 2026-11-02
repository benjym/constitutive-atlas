# Additive contract clarification v2

The original CONTRACT.md is preserved exactly. Its sentence that p_ref scales error “only” is too narrow: the unchanged candidate uses p_ref both as the state/error/observable stress scale and to set the numerical pressure-admission margin `trsig > p_ref*1e-8`. With the illustrative p_ref=100000Pa this trace-stress margin is0.001Pa, corresponding to mean pressure above0.000333333Pa. It is not an inherited material constant or a physical pressure cutoff. Changing p_ref can therefore change numerical admission as well as error scaling. No candidate equation, domain guard, parameter value or frozen acceptance tolerance changes in this clarification.

Source labels sigma_n/sigma_p correspond to candidate persistent identifiers sigma_normal/sigma_plane. The latter are necessary because `_n` is a reserved DSL state suffix. All source-to-Mandel equations and physical meanings are unchanged.

The frozen material candidate raw SHA remains8ab12775390be5f5aa8f7db7a37da0990d444a343d037bd35fa36e3b5bdbc7ce. Original policy SHA remainsbd8ee5fc47aff6dfd064ccd04b6be9fb1bf838afd3f695e5b0b74eec0d167928.
