/** Public model profiles. Authoring requirements: docs/PUBLIC_MODEL_PROFILES.md. */
export const modelProfiles = {
  "modified-cam-clay": {
    "summary": "A clay plasticity model that connects compression history with yielding and permanent deformation.",
    "introduction": "Modified Cam Clay describes how a clay changes volume and carries shear stress as it is loaded. A changing yield surface separates elastic response from plastic deformation. Its size records the effect of past plastic compression.",
    "behaviours": [
      [
        "Pressure-dependent stiffness",
        "The elastic stiffness increases with mean effective stress and depends on the current void ratio."
      ],
      [
        "Yielding and compression history",
        "Loading inside the yield surface is elastic. Reaching the surface can cause permanent deformation and change the size of the surface."
      ],
      [
        "Contraction, dilation and critical state",
        "Plastic shearing can reduce or increase volume, depending on the stress state. At critical state, shearing can continue without further plastic volume change."
      ]
    ],
    "exploration": "Choose Drained triaxial and Monotonic ramp. Start with a radial effective stress of 100 kPa, an axial / radial stress ratio of 1, void ratio 0.7 and preconsolidation pressure of 200 kPa. These give an initial overconsolidation ratio (OCR) of 2: the preconsolidation pressure is twice the initial mean effective stress.",
    "comparison": "Compare this with a fresh run using preconsolidation pressure 100 kPa (OCR 1), keeping the other inputs the same. Look at when the stress–strain response changes and how the volume response differs. This isolates the effect of the model’s initial yield-surface size; the two states are illustrative rather than reconstructions of prepared specimens.",
    "parameters": [
      {
        "name": "M",
        "symbol": "M",
        "meaning": "Critical-state slope",
        "help": "Sets the ratio of deviator stress to mean effective stress at critical state (q = M p)."
      },
      {
        "name": "lambda_c",
        "symbol": "λ",
        "meaning": "Virgin compression index",
        "help": "Controls compression during virgin loading in specific volume versus natural log of mean effective stress."
      },
      {
        "name": "kappa",
        "symbol": "κ",
        "meaning": "Swelling index",
        "help": "Controls elastic compression and swelling. It must be smaller than λ."
      },
      {
        "name": "nu",
        "symbol": "ν",
        "meaning": "Elastic Poisson ratio",
        "help": "Sets the balance of shear and bulk stiffness in the elastic response."
      }
    ],
    "stateLabels": {
      "e": "Void ratio e",
      "pc": "Preconsolidation pressure p_c"
    },
    "preparation": "Supply the initial effective stress, void ratio e (pore volume divided by solid volume) and preconsolidation pressure p_c (the size of the yield surface). For isotropic stress, OCR = p_c / p. The initial stress must lie on or inside the yield surface. These inputs are independent entries in Atlas; it does not infer a consistent specimen preparation history from them.",
    "scope": "The Atlas formulation uses three-dimensional small strains and effective stress, with compression positive. It is rate independent: changing the elapsed loading time alone does not produce creep or stress relaxation. Pore-pressure evolution needs a surrounding drainage or fluid formulation; the laboratory reconstructs pore-pressure change for its undrained controls.",
    "limits": "Use this profile to explore the basic critical-state response of clay. This formulation has isotropic hardening and no evolving fabric anisotropy, structure/bond degradation or dedicated cyclic-memory mechanism. It requires positive mean effective stress and does not cover mean tensile stress or finite rotations.",
    "equations": [
      [
        "Yield surface",
        "f = q² + M² p (p − p_c) = 0"
      ],
      [
        "Elastic stiffness",
        "K = (1 + e) p / κ;  G = 3 K (1 − 2ν) / [2 (1 + ν)]"
      ]
    ],
    "references": [
      {
        "label": "Silbermann and Nagel — Modified Cam Clay report (2023)",
        "url": "https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/web/content/docs/benchmarks/small-deformations/ModifiedCamClay/ModifiedCamClay_report.pdf"
      },
      {
        "label": "Itasca — Modified Cam-Clay theory and parameter guidance",
        "url": "https://docs.itascacg.com/itasca930/common/models/camclay/doc/modelcamclay.html"
      }
    ],
    "explorationTitle": "Try changing the compression history",
    "parameterNote": "These dimensionless example values illustrate behaviour. Calibrate them for the material and stress range you want to represent. The compression indices use natural logarithms.",
    "equationIntro": "p is mean effective stress; q measures deviator stress. The elastic region has f ≤ 0. Plastic flow follows the normal to the yield surface (associated flow), and plastic volume change evolves p_c.",
    "equationNote": "Atlas uses endpoint stiffness and exponential updates for volume and preconsolidation pressure. The complete finite-step equations are in the technical details below.",
    "contentSources": [
      "docs/models/modified-cam-clay.md"
    ],
    "title": "Modified Cam Clay"
  },
  "linear-elastic": {
    "summary": "A simple reversible response with constant stiffness and no permanent deformation.",
    "introduction": "Linear isotropic elasticity is a useful baseline: stress changes in direct proportion to strain, and the material has the same stiffness in every direction.",
    "behaviours": [
      [
        "Elastic loading and unloading",
        "Returning along the strain path reverses the stress change."
      ],
      [
        "Volume and shape changes",
        "Two constants determine the resistance to compression and shear."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "There is no yielding, hardening, density-dependent stiffness or plastic volume change. The stored void ratio is bookkeeping and does not affect stress.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation.",
    "parameters": [
      {
        "name": "E",
        "symbol": "E",
        "meaning": "Young modulus",
        "help": "Sets the slope of the elastic axial stress–strain response.",
        "unit": "Pa"
      },
      {
        "name": "nu",
        "symbol": "ν",
        "meaning": "Poisson ratio",
        "help": "Controls the balance of lateral and axial elastic deformation.",
        "unit": "1"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "OpenGeoSys — isotropic linear elasticity",
        "url": "https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/MaterialLib/SolidModels/LinearElasticIsotropic.h"
      }
    ],
    "related": [],
    "contentSources": [
      "models/linear-elastic.json",
      "docs/models/linear-elastic.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Choose Drained triaxial and a small monotonic strain. Compare two Young-modulus values while keeping the initial stress and Poisson ratio fixed. The stress–strain slope changes.",
    "comparison": "Try unloading through a strain cycle to see the reversible response.",
    "equations": [
      [
        "Elastic response",
        "Δσ = K tr(Δε) I + 2 G dev(Δε)"
      ]
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Linear isotropic elasticity"
  },
  "drucker-prager": {
    "summary": "Pressure-dependent yielding with separate controls for frictional strength and plastic volume change.",
    "introduction": "Drucker–Prager uses a smooth conical yield surface. More compressive mean stress raises the shear stress needed to yield; a separate dilation parameter controls the accompanying plastic volume change.",
    "behaviours": [
      [
        "Frictional strength",
        "The shear yield stress depends on confinement."
      ],
      [
        "Nonassociated plastic flow",
        "Strength and dilatancy can be adjusted independently."
      ],
      [
        "Perfect plasticity",
        "The yield surface does not expand with accumulated plastic strain."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "This implementation has constant elasticity, no hardening and no separate tensile cutoff. The yield intercept is defined in p–q space and is not directly a Mohr–Coulomb cohesion.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation.",
    "parameters": [
      {
        "name": "E",
        "symbol": "E",
        "meaning": "Young modulus",
        "help": "Sets the slope of the elastic axial stress–strain response.",
        "unit": "Pa"
      },
      {
        "name": "nu",
        "symbol": "ν",
        "meaning": "Poisson ratio",
        "help": "Controls the balance of lateral and axial elastic deformation.",
        "unit": "1"
      },
      {
        "name": "M",
        "symbol": "M",
        "meaning": "Friction slope",
        "help": "Raises shear yield stress as mean stress increases.",
        "unit": "1"
      },
      {
        "name": "Md",
        "symbol": "M_d",
        "meaning": "Dilatancy slope",
        "help": "Controls plastic volume change; use source-consistent values between zero and the friction slope.",
        "unit": "1"
      },
      {
        "name": "c",
        "symbol": "c",
        "meaning": "Yield intercept",
        "help": "Sets the shear-stress intercept at zero mean stress.",
        "unit": "Pa"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "OpenSees — Drucker–Prager material",
        "url": "https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/DruckerPrager.html"
      }
    ],
    "related": [],
    "contentSources": [
      "models/drucker-prager.json",
      "docs/ingestion/drucker-prager/README.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Choose Drained triaxial. Compare the response at two confining stresses, starting each run from an admissible initial state. Look for the change in shear stress at yielding.",
    "comparison": "Keep the friction slope fixed and vary the dilatancy slope to explore the plastic volume response.",
    "equations": [
      [
        "Yield surface",
        "f = q − M p − c ≤ 0"
      ],
      [
        "Plastic potential",
        "g = q − M_d p"
      ]
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Drucker–Prager, nonassociated perfect plasticity"
  },
  "mohr-coulomb": {
    "summary": "Frictional yielding defined by cohesion and friction angle, with a separate dilation angle.",
    "introduction": "Mohr–Coulomb describes pressure-dependent shear strength using the largest and smallest principal stresses. Its angular yield surface distinguishes loading directions that a smooth cone treats alike.",
    "behaviours": [
      [
        "Confinement-dependent strength",
        "Increasing compressive confinement raises the shear strength."
      ],
      [
        "Plastic dilation",
        "The dilation angle controls plastic volume change independently of the friction angle."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "The Atlas variant has constant cohesion and elastic stiffness, with no hardening, cap or separate tensile cutoff. This realization uses strictly positive cohesion, friction and dilation angles; some nearly repeated-stress states can be rejected.",
    "preparation": "Supply an admissible effective stress. This variant carries stress history without a void-ratio evolution law.",
    "parameters": [
      {
        "name": "E",
        "symbol": "E",
        "meaning": "Young modulus",
        "help": "Sets the slope of the elastic axial stress–strain response.",
        "unit": "Pa"
      },
      {
        "name": "nu",
        "symbol": "ν",
        "meaning": "Poisson ratio",
        "help": "Controls the balance of lateral and axial elastic deformation.",
        "unit": "1"
      },
      {
        "name": "c",
        "symbol": "c",
        "meaning": "Cohesion",
        "help": "Sets the cohesive part of shear strength.",
        "unit": "Pa"
      },
      {
        "name": "phi",
        "symbol": "φ",
        "meaning": "Friction angle",
        "help": "Sets the dependence of strength on normal compression.",
        "unit": "rad"
      },
      {
        "name": "psi",
        "symbol": "ψ",
        "meaning": "Dilation angle",
        "help": "Controls plastic volume expansion during shearing.",
        "unit": "rad"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Sysala and Čermák — implicit Mohr–Coulomb integration",
        "url": "https://arxiv.org/abs/1508.07435v3"
      }
    ],
    "related": [
      "drucker-prager",
      "extended-mohr-coulomb-2013"
    ],
    "contentSources": [
      "models/mohr-coulomb.json"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Choose Drained triaxial and a monotonic ramp. Compare two positive dilation angles while keeping cohesion, friction and initial stress fixed. Look at the volume response after yielding.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Mohr–Coulomb · nonassociated perfect plasticity"
  },
  "hypoplastic-sand-vw96": {
    "summary": "A sand model whose stiffness, strength and volume response depend on pressure and density.",
    "introduction": "The von Wolffersdorff hypoplastic law evolves stress directly from the current stress, void ratio and strain direction. It describes nonlinear behaviour without dividing each increment into a separate elastic and plastic part.",
    "behaviours": [
      [
        "Pressure-dependent stiffness",
        "The same strain change can produce a different stress change at another pressure."
      ],
      [
        "Density-dependent shearing",
        "Dense and loose states can have different strength and contraction or dilation."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "The basic law has no additional small-strain direction-memory variable. Multiple reversals can show limitations in reloading stiffness. Atlas uses a restricted compressive-stress and density domain and does not transport finite rotations.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation.",
    "parameters": [
      {
        "name": "phi",
        "symbol": "φ_c",
        "meaning": "Critical friction angle",
        "help": "Sets the frictional limit at critical state.",
        "unit": "rad"
      },
      {
        "name": "hs",
        "symbol": "h_s",
        "meaning": "Granular hardness",
        "help": "Sets the pressure scale for stiffness and density limits.",
        "unit": "Pa"
      },
      {
        "name": "n",
        "symbol": "n",
        "meaning": "Pressure exponent",
        "help": "Controls how density limits and stiffness change with pressure.",
        "unit": "1"
      },
      {
        "name": "ed0",
        "symbol": "e_d0",
        "meaning": "Dense limiting void ratio",
        "help": "Locates the dense limit at zero pressure.",
        "unit": "1"
      },
      {
        "name": "ec0",
        "symbol": "e_c0",
        "meaning": "Critical void ratio",
        "help": "Locates the critical-state density at zero pressure.",
        "unit": "1"
      },
      {
        "name": "ei0",
        "symbol": "e_i0",
        "meaning": "Loose limiting void ratio",
        "help": "Locates the loose limit at zero pressure.",
        "unit": "1"
      },
      {
        "name": "alpha",
        "symbol": "α",
        "meaning": "Density influence",
        "help": "Controls the influence of density on the nonlinear response.",
        "unit": "1"
      },
      {
        "name": "beta",
        "symbol": "β",
        "meaning": "Density stiffness influence",
        "help": "Controls how relative density changes stiffness.",
        "unit": "1"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "von Wolffersdorff (1996) — hypoplastic relation for granular materials",
        "url": "https://doi.org/10.1002/(SICI)1099-1484(199607)1:3<251::AID-CFM13>3.0.CO;2-3"
      }
    ],
    "related": [
      "hypoplastic-sand-igs97",
      "barodesy-sand"
    ],
    "contentSources": [
      "models/hypoplastic-sand-vw96.json",
      "docs/ingestion/hypoplastic-sand-vw96/README.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Choose Drained triaxial. Compare two admissible initial void ratios at the same stress and material parameters. Follow both the stress–strain curve and the volume change.",
    "parameterNote": "The three limiting void ratios share a zero-pressure reference and must retain their dense–critical–loose ordering. Example coefficients are not a calibration for every sand.",
    "title": "Sand hypoplasticity · von Wolffersdorff (1996)"
  },
  "hypoplastic-sand-igs97": {
    "summary": "Sand hypoplasticity with additional memory of very small strains and changes in loading direction.",
    "introduction": "The Niemunis–Herle intergranular-strain extension adds a tensor describing recent deformation to the von Wolffersdorff sand law. This lets unloading, reversal and continued loading have different stiffness.",
    "behaviours": [
      [
        "Small-strain stiffness",
        "The extra memory changes stiffness over a small deformation scale."
      ],
      [
        "Direction-dependent reloading",
        "Reversing or turning the strain direction changes the response."
      ],
      [
        "Pressure and density effects",
        "The sand host retains its stress- and density-dependent behaviour."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "This is the 1997 extension paired with the selected von Wolffersdorff host. ISA and generalized intergranular strain are different extensions. Holding a stationary strain path does not erase memory.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation. Also specify the full intergranular-strain tensor h. Zero history and a mobilized history describe different starting conditions.",
    "parameters": [
      {
        "name": "phi",
        "symbol": "φ_c",
        "meaning": "Critical friction angle",
        "help": "Sets the frictional limit at critical state.",
        "unit": "rad"
      },
      {
        "name": "hs",
        "symbol": "h_s",
        "meaning": "Granular hardness",
        "help": "Sets the pressure scale for stiffness and density limits.",
        "unit": "Pa"
      },
      {
        "name": "n",
        "symbol": "n",
        "meaning": "Pressure exponent",
        "help": "Controls how density limits and stiffness change with pressure.",
        "unit": "1"
      },
      {
        "name": "ed0",
        "symbol": "e_d0",
        "meaning": "Dense limiting void ratio",
        "help": "Locates the dense limit at zero pressure.",
        "unit": "1"
      },
      {
        "name": "ec0",
        "symbol": "e_c0",
        "meaning": "Critical void ratio",
        "help": "Locates the critical-state density at zero pressure.",
        "unit": "1"
      },
      {
        "name": "ei0",
        "symbol": "e_i0",
        "meaning": "Loose limiting void ratio",
        "help": "Locates the loose limit at zero pressure.",
        "unit": "1"
      },
      {
        "name": "alpha",
        "symbol": "α",
        "meaning": "Density influence",
        "help": "Controls the influence of density on the nonlinear response.",
        "unit": "1"
      },
      {
        "name": "beta",
        "symbol": "β",
        "meaning": "Density stiffness influence",
        "help": "Controls how relative density changes stiffness.",
        "unit": "1"
      },
      {
        "name": "R",
        "symbol": "R",
        "meaning": "Memory radius",
        "help": "Sets the scale of very small strain over which direction memory changes.",
        "unit": "1"
      },
      {
        "name": "mR",
        "symbol": "m_R",
        "meaning": "Reversal stiffness",
        "help": "Sets the stiffness increase after reversing the strain direction.",
        "unit": "1"
      },
      {
        "name": "mT",
        "symbol": "m_T",
        "meaning": "Orthogonal stiffness",
        "help": "Sets the stiffness response when the loading direction turns by a right angle.",
        "unit": "1"
      },
      {
        "name": "beta_r",
        "symbol": "β_r",
        "meaning": "Memory mobilisation",
        "help": "Controls how quickly intergranular strain approaches its limiting magnitude.",
        "unit": "1"
      },
      {
        "name": "chi",
        "symbol": "χ",
        "meaning": "Stiffness transition",
        "help": "Controls the transition between small-strain and continuing-loading stiffness.",
        "unit": "1"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "Niemunis and Herle (1997) — hypoplastic model with intergranular strain",
        "url": "https://doi.org/10.1002/(SICI)1099-1484(199710)2:4<279::AID-CFM29>3.0.CO;2-8"
      }
    ],
    "related": [
      "hypoplastic-sand-vw96",
      "hypoplastic-isa",
      "hypoplastic-generalized-igs-2024"
    ],
    "contentSources": [
      "models/hypoplastic-sand-igs97.json",
      "docs/ingestion/hypoplastic-sand-igs97/README.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Compare a monotonic path with a small strain cycle. Follow unloading and reloading stiffness, keeping the complete initial stress, density and memory fixed.",
    "parameterNote": "The three limiting void ratios share a zero-pressure reference and must retain their dense–critical–loose ordering. Example coefficients are not a calibration for every sand. The additional memory parameters belong to the selected IGS extension.",
    "title": "Sand hypoplasticity with intergranular strain (1997)"
  },
  "hypoplastic-clay-2005": {
    "summary": "A nonlinear clay model connecting stress, density and compression history without a separate yield surface.",
    "introduction": "Mašín’s 2005 hypoplastic clay formulation evolves stress and void ratio directly. It combines a normal compression line with a direct nonlinear stress response.",
    "behaviours": [
      [
        "Compression and swelling",
        "Density relative to the compression line influences loading and unloading."
      ],
      [
        "Shearing and volume change",
        "The current stress and density determine the coupled shear and volume response."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "This is the five-parameter Appendix C base law, without a small-strain-memory extension. Atlas requires a regular compressive-stress domain and uses fixed axes without finite-rotation transport.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation.",
    "parameters": [
      {
        "name": "phi_c",
        "symbol": "φ_c",
        "meaning": "Critical friction angle",
        "help": "Sets the critical-state frictional strength.",
        "unit": "rad"
      },
      {
        "name": "lambda_star",
        "symbol": "λ*",
        "meaning": "Compression slope",
        "help": "Controls the normal compression line in logarithmic volume–pressure space.",
        "unit": "1"
      },
      {
        "name": "kappa_star",
        "symbol": "κ*",
        "meaning": "Unloading slope",
        "help": "Controls the initial unloading stiffness relative to compression.",
        "unit": "1"
      },
      {
        "name": "N",
        "symbol": "N",
        "meaning": "Density intercept",
        "help": "Locates the normal compression line at the specified reference pressure.",
        "unit": "1"
      },
      {
        "name": "r",
        "symbol": "r",
        "meaning": "Stiffness ratio",
        "help": "Sets the initial normal-compression-line bulk-to-shear stiffness ratio.",
        "unit": "1"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "Mašín (2005) — clay hypoplasticity",
        "url": "https://doi.org/10.1002/nag.416"
      }
    ],
    "related": [
      "modified-cam-clay",
      "hypoplastic-clay-2014"
    ],
    "contentSources": [
      "models/hypoplastic-clay-2005.json",
      "docs/ingestion/hypoplastic-clay-2005/README.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Start with Load model example to use this formulation’s own initial state. Choose a small monotonic drained triaxial path and compare admissible void ratios at the same pressure. The two clay formulations have different parameters and initial examples; keep each example with its own formulation.",
    "parameterNote": "The logarithmic compression parameters and density intercept use the formulation’s 1 kPa reference pressure. Keep that convention with the parameter set. Example values are illustrative.",
    "title": "Clay hypoplasticity — Mašín (2005)"
  },
  "hypoplastic-clay-2013": {
    "summary": "A clay hypoplasticity model that explicitly describes the states approached during continued loading.",
    "introduction": "Mašín’s 2013 hypoplastic clay formulation evolves stress and void ratio directly. It explicitly represents the asymptotic states approached during sustained proportional loading.",
    "behaviours": [
      [
        "Compression and swelling",
        "Density relative to the compression line influences loading and unloading."
      ],
      [
        "Shearing and volume change",
        "The current stress and density determine the coupled shear and volume response."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "The asymptotic state boundary is a descriptor of the law, not a yield surface that blocks every outside state. This profile excludes the separate 2014 stiffness-anisotropy extension. Atlas requires a regular compressive-stress domain and uses fixed axes without finite-rotation transport.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation.",
    "parameters": [
      {
        "name": "phi_c",
        "symbol": "φ_c",
        "meaning": "Critical friction angle",
        "help": "Sets the critical-state frictional strength.",
        "unit": "rad"
      },
      {
        "name": "lambda_star",
        "symbol": "λ*",
        "meaning": "Compression slope",
        "help": "Controls the normal compression line in logarithmic volume–pressure space.",
        "unit": "1"
      },
      {
        "name": "kappa_star",
        "symbol": "κ*",
        "meaning": "Unloading slope",
        "help": "Controls the initial unloading stiffness relative to compression.",
        "unit": "1"
      },
      {
        "name": "N",
        "symbol": "N",
        "meaning": "Density intercept",
        "help": "Locates the normal compression line at the specified reference pressure.",
        "unit": "1"
      },
      {
        "name": "nu",
        "symbol": "ν",
        "meaning": "Hypoelastic Poisson parameter",
        "help": "Controls the stiffness balance of the linear part of the hypoplastic response.",
        "unit": "1"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "Mašín (2013) — clay hypoplasticity",
        "url": "https://doi.org/10.1007/s11440-012-0199-y"
      }
    ],
    "related": [
      "modified-cam-clay",
      "hypoplastic-clay-2014"
    ],
    "contentSources": [
      "models/hypoplastic-clay-2013.json",
      "docs/ingestion/hypoplastic-clay-2013/README.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Start with Load model example to use this formulation’s own initial state. Choose a small monotonic drained triaxial path and compare admissible void ratios at the same pressure. The two clay formulations have different parameters and initial examples; keep each example with its own formulation.",
    "parameterNote": "The logarithmic compression parameters and density intercept use the formulation’s 1 kPa reference pressure. Keep that convention with the parameter set. Example values are illustrative.",
    "title": "Clay hypoplasticity with explicit asymptotic states — Mašín (2013)"
  },
  "barodesy-sand": {
    "summary": "A sand model that links stress evolution to the direction of deformation and current density.",
    "introduction": "Barodesy describes the approach to characteristic stress and density states under continued deformation. The sand law uses stress, void ratio and strain direction to determine the stress response.",
    "behaviours": [
      [
        "Direction-sensitive stress evolution",
        "The imposed deformation direction shapes the evolving stress."
      ],
      [
        "Density effects",
        "Density affects contraction, dilation and the approach to critical states."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "Atlas uses the 2015 sand law with a separately attributed 2019 illustrative parameter set. It requires a regular positive-definite stress state and a density margin; it does not include finite rotations.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation.",
    "parameters": [
      {
        "name": "c1",
        "symbol": "c1",
        "meaning": "Direction coefficient",
        "help": "Controls the deformation-direction mapping.",
        "unit": "1"
      },
      {
        "name": "c2",
        "symbol": "c2",
        "meaning": "Direction coefficient",
        "help": "Controls the deformation-direction mapping.",
        "unit": "1"
      },
      {
        "name": "c3",
        "symbol": "c3",
        "meaning": "Stress evolution coefficient",
        "help": "Controls the stress-rate response.",
        "unit": "1"
      },
      {
        "name": "c4",
        "symbol": "c4",
        "meaning": "Stress scale",
        "help": "Sets a pressure scale in the sand law.",
        "unit": "Pa"
      },
      {
        "name": "c5",
        "symbol": "c5",
        "meaning": "Density coefficient",
        "help": "Controls the density-dependent response.",
        "unit": "1"
      },
      {
        "name": "ec0",
        "symbol": "e_c0",
        "meaning": "Critical void-ratio intercept",
        "help": "Sets the critical density reference.",
        "unit": "1"
      },
      {
        "name": "emin",
        "symbol": "e_min",
        "meaning": "Minimum void ratio",
        "help": "Sets the lower density reference.",
        "unit": "1"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "Kolymbas (2015) — barodesy for sand",
        "url": "https://doi.org/10.1680/geot.14.P.151"
      },
      {
        "label": "Kolymbas and Bathaeian (2019) — parameter example",
        "url": "https://doi.org/10.1002/nag.2984"
      }
    ],
    "related": [
      "barodesy-clay-2017",
      "hypoplastic-sand-vw96"
    ],
    "contentSources": [
      "models/barodesy-sand.json",
      "docs/ingestion/barodesy-sand/README.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Choose Drained triaxial and compare two admissible starting void ratios. Watch the stress path and volume response as the strain grows.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Barodesy sand (2015)"
  },
  "barodesy-clay-2017": {
    "summary": "A clay barodesy model built around compression properties and critical-state friction.",
    "introduction": "The Medicus–Fellin clay formulation describes stress and density evolution directly from deformation. Its material inputs connect the critical friction angle with the normal compression and unloading lines.",
    "behaviours": [
      [
        "Compression history through density",
        "The current stress and void ratio influence the response."
      ],
      [
        "Asymptotic behaviour",
        "Continued proportional deformation tends toward characteristic stress–density states."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "Atlas selects the 2017 body equations and their critical-density expression. The formulation is restricted to fixed axes, zero spin and regular positive-definite stress states.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation.",
    "parameters": [
      {
        "name": "phi_c",
        "symbol": "φ_c",
        "meaning": "Critical friction angle",
        "help": "Sets the critical-state frictional strength.",
        "unit": "rad"
      },
      {
        "name": "lambda_star",
        "symbol": "λ*",
        "meaning": "Compression slope",
        "help": "Controls the normal compression line in logarithmic volume–pressure space.",
        "unit": "1"
      },
      {
        "name": "kappa_star",
        "symbol": "κ*",
        "meaning": "Unloading slope",
        "help": "Controls the initial unloading stiffness relative to compression.",
        "unit": "1"
      },
      {
        "name": "N",
        "symbol": "N",
        "meaning": "Density intercept",
        "help": "Locates the normal compression line at the specified reference pressure.",
        "unit": "1"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "Medicus and Fellin (2017) — improved barodesy for clay",
        "url": "https://doi.org/10.1007/s11440-016-0458-4"
      }
    ],
    "related": [
      "barodesy-sand",
      "hypoplastic-clay-2013"
    ],
    "contentSources": [
      "models/barodesy-clay-2017.json",
      "docs/models/barodesy2017-research-rates.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Load the model example and use a small monotonic drained triaxial path. Compare the effect of changing the starting void ratio within the admissible domain.",
    "parameterNote": "The logarithmic compression parameters and density intercept use the formulation’s 1 kPa reference pressure. Keep that convention with the parameter set. Example values are illustrative.",
    "title": "Barodesy clay 2017"
  },
  "original-cam-clay-sw-electronic-log-recovery-v1": {
    "summary": "Original Cam Clay with a logarithmic yield relation and no recoverable shear strain.",
    "introduction": "This formulation follows the selected Schofield–Wroth text. It connects mean effective stress, shear stress and specific volume through the original critical-state framework.",
    "behaviours": [
      [
        "Compression and recovery",
        "Compression and unloading follow different volume–pressure slopes."
      ],
      [
        "Original yield shape",
        "The yield relation has a corner at isotropic stress, unlike Modified Cam Clay’s smooth ellipse."
      ],
      [
        "Shear-rigid elastic response",
        "There is no elastic shear compliance in this selected formulation."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "The strain-controlled realization makes an explicit stress selection where the shear-rigid law is not unique. Stress changes can be abrupt. Cyclic stress control is unsupported; this is distinct from Modified Cam Clay.",
    "preparation": "Supply the complete effective stress and specific volume v = 1 + e. The critical-state intercept and reference pressure belong together; preserve their convention when changing units.",
    "parameters": [
      {
        "name": "M",
        "symbol": "M",
        "meaning": "Critical-state stress ratio",
        "help": "Sets the shear-to-mean-stress ratio at critical state.",
        "unit": "1"
      },
      {
        "name": "lambda_c",
        "symbol": "λ",
        "meaning": "Compression slope",
        "help": "Sets the virgin specific-volume versus natural-log-pressure slope.",
        "unit": "1"
      },
      {
        "name": "kappa",
        "symbol": "κ",
        "meaning": "Recovery slope",
        "help": "Sets the recoverable volume–pressure slope.",
        "unit": "1"
      },
      {
        "name": "Gamma",
        "symbol": "Γ",
        "meaning": "Critical-state intercept",
        "help": "Locates the critical-state specific volume at the reference pressure.",
        "unit": "1"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Schofield and Wroth — Critical State Soil Mechanics, Chapter 6",
        "url": "https://fme.hcmuaf.edu.vn/data/critical_state_soil_mechanics.pdf"
      }
    ],
    "related": [
      "original-cam-clay",
      "modified-cam-clay"
    ],
    "contentSources": [
      "models/original-cam-clay-sw-electronic-log-recovery-v1.json",
      "docs/models/original-cam-clay-sw-electronic-log-recovery-v1.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Choose a monotonic isotropic compression path to explore compression and recovery conventions. Use the supported strain-controlled interface; compare the yield shape conceptually with Modified Cam Clay.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Original Cam Clay · logarithmic-recovery formulation"
  },
  "original-cam-clay": {
    "summary": "The original critical-state clay model connecting compression, yielding and shear deformation.",
    "introduction": "Original Cam Clay provides a framework for relating a clay’s volume and compression history to its stress response. Its yield shape and elastic assumptions differ from Modified Cam Clay.",
    "behaviours": [
      [
        "Critical state",
        "Continued shearing is described through a characteristic stress ratio and volume relation."
      ],
      [
        "Compression history",
        "Normal compression and unloading use separate slopes."
      ]
    ],
    "scope": "This is the family entry. The linked logarithmic-recovery formulation identifies the version available in the laboratory.",
    "limits": "A family name does not specify a particular shear-elastic assumption, tensor extension or finite-step algorithm.",
    "preparation": "Initial stress and specific volume must be consistent with the chosen compression and critical-state conventions.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Schofield and Wroth — Critical State Soil Mechanics",
        "url": "https://fme.hcmuaf.edu.vn/data/critical_state_soil_mechanics.pdf"
      }
    ],
    "related": [
      "original-cam-clay-sw-electronic-log-recovery-v1",
      "modified-cam-clay"
    ],
    "contentSources": [
      "docs/ingestion/original-cam-clay/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Original Cam Clay"
  },
  "duncan-chang-1970-endpoint-average": {
    "summary": "A hyperbolic soil model with confinement-dependent stiffness and a separate unloading stiffness.",
    "introduction": "The Duncan–Chang law was developed around nonlinear soil stress–strain curves. As the stress difference approaches strength, primary-loading stiffness decreases; previous maximum stress difference helps select unloading and reloading behaviour.",
    "behaviours": [
      [
        "Nonlinear primary loading",
        "Tangent stiffness reduces as the stress level approaches failure."
      ],
      [
        "Confinement effects",
        "Stiffness and strength vary with the principal confining stress."
      ],
      [
        "Unloading and reloading",
        "A stored maximum stress difference selects a separate modulus."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "This is the original constant-Poisson three-dimensional incremental closure with Atlas endpoint averaging. It has no independent dilatancy or density-evolution law. A positive postfailure modulus is a numerical continuation, not a postfailure material calibration.",
    "preparation": "Supply initial effective stress and the previous maximum principal stress difference. A stress state alone does not reconstruct earlier loading.",
    "parameters": [
      {
        "name": "pa",
        "symbol": "p_a",
        "meaning": "Atmospheric reference pressure",
        "help": "Provides the pressure reference for the calibrated modulus and strength expressions.",
        "unit": "Pa"
      },
      {
        "name": "K",
        "symbol": "K",
        "meaning": "Primary modulus number",
        "help": "Sets the scale of primary-loading stiffness.",
        "unit": "1"
      },
      {
        "name": "Kur",
        "symbol": "K_ur",
        "meaning": "Unloading modulus number",
        "help": "Sets unloading/reloading stiffness.",
        "unit": "1"
      },
      {
        "name": "n",
        "symbol": "n",
        "meaning": "Stress exponent",
        "help": "Controls the confinement dependence of stiffness.",
        "unit": "1"
      },
      {
        "name": "Rf",
        "symbol": "R_f",
        "meaning": "Failure ratio",
        "help": "Controls curvature toward failure.",
        "unit": "1"
      },
      {
        "name": "c_cohesion",
        "symbol": "c",
        "meaning": "Cohesion",
        "help": "Sets the cohesive contribution to strength.",
        "unit": "Pa"
      },
      {
        "name": "phi",
        "symbol": "φ",
        "meaning": "Friction angle",
        "help": "Sets confinement-dependent strength.",
        "unit": "rad"
      },
      {
        "name": "nu",
        "symbol": "ν",
        "meaning": "Poisson ratio",
        "help": "Controls the balance of lateral and axial elastic deformation.",
        "unit": "1"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Duncan and Chang (1970) — Nonlinear Analysis of Stress and Strain in Soils",
        "url": "https://doi.org/10.1061/JSFEAQ.0001458"
      }
    ],
    "related": [
      "duncan-chang-1970"
    ],
    "contentSources": [
      "models/duncan-chang-1970-endpoint-average.json",
      "docs/models/duncan-chang-1970-endpoint-average.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Choose Drained triaxial. Compare a monotonic ramp with unloading/reloading, keeping initial stress and prior maximum stress difference consistent.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Duncan–Chang (1970) · constant-Poisson formulation"
  },
  "duncan-chang-1970": {
    "summary": "A hyperbolic description of soil loading with pressure-dependent stiffness.",
    "introduction": "Duncan–Chang relates the changing tangent stiffness to stress level and confinement. Its unloading modulus and history rule distinguish it from a reversible nonlinear-elastic curve.",
    "behaviours": [
      [
        "Hyperbolic primary loading",
        "The stress–strain curve becomes less stiff as failure is approached."
      ],
      [
        "Different unloading stiffness",
        "Unloading and reloading depend on prior loading."
      ]
    ],
    "scope": "This is the 1970 model-family entry. The constant-Poisson endpoint-average realization is linked below.",
    "limits": "Later revisions and numerical closures can have different volume responses and history rules.",
    "preparation": "The selected realization needs initial stress and loading history in addition to material coefficients.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Duncan and Chang (1970) — Nonlinear Analysis of Stress and Strain in Soils",
        "url": "https://doi.org/10.1061/JSFEAQ.0001458"
      }
    ],
    "related": [
      "duncan-chang-1970-endpoint-average"
    ],
    "contentSources": [
      "docs/models/duncan-chang-1970-endpoint-average.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Duncan–Chang hyperbolic model (1970)"
  },
  "lade-duncan-1975-midpoint-elastic-eq19-gap-v4": {
    "summary": "A sand elastoplastic model whose strength and plastic flow depend on all three principal stresses.",
    "introduction": "The original Lade–Duncan formulation combines pressure-dependent elasticity with a stress-invariant failure description and plastic-work-dependent evolution. The flow direction is distinct from the failure surface.",
    "behaviours": [
      [
        "Three-principal-stress response",
        "The intermediate principal stress participates in the invariant description."
      ],
      [
        "Plastic volume change",
        "The plastic potential supplies a nonassociated flow direction."
      ],
      [
        "Work-dependent loading",
        "Accumulated plastic work affects the continuing-loading response."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. This realization uses total mechanical stress with zero pore pressure. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "This is the midpoint-elastic, local Eq. 19 realization of the 1975 law. It excludes a pore-fluid law, finite rotations and general postfailure continuation. The source dense/loose examples belong to their complete parameter sets.",
    "preparation": "Supply initial stress, loading memory and accumulated plastic work. The dense and loose presets supply explicit initial histories; changing only one density-related coefficient does not reproduce a different prepared sand.",
    "parameters": [
      {
        "name": "pa",
        "symbol": "p_a",
        "meaning": "Atmospheric reference pressure",
        "help": "Provides the stress normalization for the original source coefficients.",
        "unit": "Pa"
      },
      {
        "name": "k1",
        "symbol": "k₁",
        "meaning": "Failure invariant",
        "help": "Sets the failure level of the stress-invariant function.",
        "unit": "1"
      },
      {
        "name": "ft",
        "symbol": "f_t",
        "meaning": "Reference loading invariant",
        "help": "Sets the reference level in the plastic-work relation.",
        "unit": "1"
      },
      {
        "name": "A",
        "symbol": "A",
        "meaning": "Plastic-potential coefficient",
        "help": "Controls the nonassociated flow direction.",
        "unit": "1"
      },
      {
        "name": "rf",
        "symbol": "r_f",
        "meaning": "Failure ratio",
        "help": "Controls the plastic-work loading relation.",
        "unit": "1"
      },
      {
        "name": "M",
        "symbol": "M",
        "meaning": "Work coefficient",
        "help": "Sets the scale in the plastic-work relation.",
        "unit": "1"
      },
      {
        "name": "l",
        "symbol": "l",
        "meaning": "Work pressure exponent",
        "help": "Controls pressure dependence of the work relation.",
        "unit": "1"
      },
      {
        "name": "Kur",
        "symbol": "K_ur",
        "meaning": "Elastic modulus number",
        "help": "Sets pressure-dependent elastic stiffness.",
        "unit": "1"
      },
      {
        "name": "n",
        "symbol": "n",
        "meaning": "Elastic pressure exponent",
        "help": "Controls confinement dependence of stiffness.",
        "unit": "1"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Lade and Duncan (1975) — Elastoplastic Stress-Strain Theory for Cohesionless Soil",
        "url": "https://doi.org/10.1061/AJGEB6.0000204"
      }
    ],
    "related": [
      "lade-duncan-1975",
      "matsuoka-nakai"
    ],
    "contentSources": [
      "docs/models/lade-duncan-1975-midpoint-elastic-eq19-gap-v4.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Select Dense sand · Table 1 or Loose sand · Table 1 and Triaxial · fixed lateral stress. Compare stress–strain and volumetric response using each complete source parameter set.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Lade–Duncan (1975) · midpoint-elastic formulation"
  },
  "lade-duncan-1975": {
    "summary": "A three-dimensional sand plasticity model using stress invariants and plastic-work history.",
    "introduction": "Lade–Duncan accounts for the combined role of the three principal stresses in the strength and deformation of cohesionless soil.",
    "behaviours": [
      [
        "Intermediate principal stress",
        "The strength description uses the full principal-stress state."
      ],
      [
        "Nonassociated plasticity",
        "Plastic volume change follows a separate plastic potential."
      ]
    ],
    "scope": "This is the 1975 family entry. The linked midpoint-elastic realization provides the laboratory implementation.",
    "limits": "The family entry does not identify later Lade revisions or a universal postfailure law.",
    "preparation": "Use the complete initial state and parameter set of the selected realization.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Lade and Duncan (1975) — original publication",
        "url": "https://doi.org/10.1061/AJGEB6.0000204"
      }
    ],
    "related": [
      "lade-duncan-1975-midpoint-elastic-eq19-gap-v4"
    ],
    "contentSources": [
      "docs/models/lade-duncan-1975-midpoint-elastic-eq19-gap-v4.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Lade–Duncan elastoplastic model (1975)"
  },
  "tresca-associated-perfect-bk2022v1-be": {
    "summary": "Pressure-independent yielding governed by maximum shear stress.",
    "introduction": "The Tresca law yields when the difference between the largest and smallest principal stresses reaches twice the shear strength. Atlas pairs this with constant elastic moduli and associated plastic flow.",
    "behaviours": [
      [
        "Maximum-shear yield",
        "Adding the same pressure to every normal stress does not change the yield measure."
      ],
      [
        "Perfect plasticity",
        "Shear strength remains constant after yielding."
      ],
      [
        "Plastic history",
        "The model stores the full plastic-strain tensor."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. The model uses total stress. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "There is no pore-pressure law, pressure-dependent friction, hardening or viscosity. Yield-surface corners make changes of active flow direction nonsmooth.",
    "preparation": "Supply all total-stress and plastic-strain components. The shear strength is a model input; relating it to an undrained soil strength requires a material interpretation.",
    "parameters": [
      {
        "name": "lame_lambda",
        "symbol": "λ",
        "meaning": "First Lamé modulus",
        "help": "Sets the elastic volume–shape coupling.",
        "unit": "Pa"
      },
      {
        "name": "mu",
        "symbol": "μ",
        "meaning": "Shear modulus",
        "help": "Sets elastic shear stiffness.",
        "unit": "Pa"
      },
      {
        "name": "k",
        "symbol": "k",
        "meaning": "Maximum shear strength",
        "help": "The uniaxial yield stress is 2k.",
        "unit": "Pa"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Boulmezaoud and Khouider (2022) — selected Tresca continuum closure",
        "url": "https://arxiv.org/abs/2207.12719v1"
      }
    ],
    "related": [
      "tresca",
      "j2-linear-isotropic-hardening-be"
    ],
    "contentSources": [
      "models/tresca-associated-perfect-bk2022v1-be.json"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Use a monotonic strain path and compare two shear-strength values at fixed elastic moduli. Look for the change in stress at yielding.",
    "equations": [
      [
        "Yield condition",
        "max(σ_i) − min(σ_i) ≤ 2 k"
      ]
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Tresca · associated perfect plasticity"
  },
  "tresca": {
    "summary": "A maximum-shear-stress yield criterion, often used as a simple pressure-independent plasticity baseline.",
    "introduction": "Tresca compares the largest and smallest principal stresses. The same pressure added in every direction leaves the criterion unchanged.",
    "behaviours": [
      [
        "Pressure-independent strength",
        "Yield depends on stress differences."
      ],
      [
        "Cornered yield surface",
        "Different shear mechanisms meet at corners."
      ]
    ],
    "scope": "This is a criterion-family entry. The linked associated perfect-plastic formulation supplies elasticity, plastic flow and history.",
    "limits": "A yield criterion alone is not a complete stress-update law. It does not specify stiffness, flow or hardening.",
    "preparation": "Choose a full constitutive formulation before assigning material parameters and an initial state.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Boulmezaoud and Khouider (2022) — Tresca constitutive closure",
        "url": "https://arxiv.org/abs/2207.12719v1"
      }
    ],
    "related": [
      "tresca-associated-perfect-bk2022v1-be"
    ],
    "contentSources": [
      "models/tresca-associated-perfect-bk2022v1-be.json"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Tresca criterion"
  },
  "j2-linear-isotropic-hardening-be": {
    "summary": "Pressure-independent plasticity with a yield strength that increases as plastic strain accumulates.",
    "introduction": "J2 plasticity uses the deviatoric stress to determine yielding. In this specialization the yield surface expands uniformly, so accumulated equivalent plastic strain raises the yield stress in every loading direction.",
    "behaviours": [
      [
        "Smooth shear yield",
        "Hydrostatic pressure does not change the yield threshold."
      ],
      [
        "Isotropic hardening",
        "Plastic deformation increases the subsequent yield strength."
      ],
      [
        "Elastic unloading",
        "Unloading within the expanded surface is elastic."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. The model uses dry total stress and all-six-component strain increments. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "There is no pressure-dependent friction, kinematic hardening, softening or rate sensitivity. The laboratory uses prescribed strain increments rather than a general stress-control interface.",
    "preparation": "Supply the full initial stress and nonnegative accumulated equivalent plastic strain. Previous plastic deformation changes the initial yield strength.",
    "parameters": [
      {
        "name": "K",
        "symbol": "K",
        "meaning": "Bulk modulus",
        "help": "Controls elastic volume change.",
        "unit": "Pa"
      },
      {
        "name": "G",
        "symbol": "G",
        "meaning": "Shear modulus",
        "help": "Controls elastic shape change.",
        "unit": "Pa"
      },
      {
        "name": "sigma_y",
        "symbol": "σ_y",
        "meaning": "Initial yield stress",
        "help": "Sets the yield stress before hardening.",
        "unit": "Pa"
      },
      {
        "name": "H",
        "symbol": "H",
        "meaning": "Hardening modulus",
        "help": "Sets the increase in yield stress per unit equivalent plastic strain.",
        "unit": "Pa"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "OpenSees — J2Plasticity mathematical formulation",
        "url": "https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/J2Plasticity.html"
      }
    ],
    "related": [
      "tresca-associated-perfect-bk2022v1-be"
    ],
    "contentSources": [
      "docs/models/j2-linear-isotropic-hardening-be.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Use the laboratory’s prescribed strain-increment example, then compare zero and positive hardening modulus. Inspect stress and equivalent plastic strain through loading and reversal.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "J2 plasticity · linear isotropic hardening"
  },
  "norsand-jefferies-1993-active-axial": {
    "summary": "An original NorSand shearing law linking sand density relative to critical state with dilatancy and hardening.",
    "introduction": "This realization isolates the active drained axial branch of Jefferies’ 1993 model. Its image-state construction describes the relation between current density, stress ratio and continued plastic shearing.",
    "behaviours": [
      [
        "State-dependent shearing",
        "Density relative to critical state influences the shearing response."
      ],
      [
        "Dilatancy and hardening",
        "The current state couples plastic volume change with stress-ratio evolution."
      ]
    ],
    "scope": "The laboratory supports active monotonic drained axial paths in a dimensionless shear-progress coordinate. Effective stress controls can vary along that path.",
    "limits": "This restricted rigid-plastic formulation supplies no elastic loading, unloading, cyclic continuation or general three-dimensional stress update. Later NorSand revisions are separate.",
    "preparation": "Supply the complete stress-ratio and volume/strain history, starting coordinate and stress controls. Keep the initial state with its selected example.",
    "parameters": [
      {
        "name": "M",
        "symbol": "M",
        "meaning": "Critical-state stress ratio",
        "help": "Sets the shear-to-mean-stress ratio at critical state.",
        "unit": "1"
      },
      {
        "name": "N",
        "symbol": "N",
        "meaning": "Dilatancy coefficient",
        "help": "Controls the original 1993 stress–dilatancy relation.",
        "unit": "1"
      },
      {
        "name": "h",
        "symbol": "h",
        "meaning": "Hardening coefficient",
        "help": "Controls the evolution during active plastic shearing.",
        "unit": "1"
      },
      {
        "name": "lam",
        "symbol": "λ",
        "meaning": "Critical-state-line slope",
        "help": "Controls the density reference as pressure changes.",
        "unit": "1"
      },
      {
        "name": "Gamma",
        "symbol": "Γ",
        "meaning": "Critical-state intercept",
        "help": "Locates the critical-state density at the reference pressure.",
        "unit": "1"
      },
      {
        "name": "pref",
        "symbol": "p_ref",
        "meaning": "Critical-state reference pressure",
        "help": "Defines the pressure convention for the critical-state intercept Γ.",
        "unit": "Pa"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Jefferies (1993) — Nor-Sand: a simple critical state model for sand",
        "url": "https://doi.org/10.1680/geot.1993.43.1.91"
      }
    ],
    "related": [
      "norsand-1993"
    ],
    "contentSources": [
      "docs/models/norsand-1993-active-axial-v1.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Start with the provided controlled-path example. Compare the constant-cell-pressure and constant-mean-pressure stress paths using their matching controls. Follow stress ratio and volume change against shear progress.",
    "parameterNote": "The critical-state intercept Γ and reference pressure must use the same convention. This is the original 1993 active axial variant; later NorSand calibrations are separate.",
    "title": "NorSand (1993) · active drained axial formulation"
  },
  "norsand-1993": {
    "summary": "A critical-state sand model built around density relative to the critical-state line.",
    "introduction": "NorSand uses an image-state construction to connect sand state, dilatancy and hardening. The original 1993 formulation is distinct from its later developments.",
    "behaviours": [
      [
        "State parameter",
        "The relevant density depends on pressure through the critical-state line."
      ],
      [
        "Dilatancy and hardening",
        "The state affects plastic shearing and volume change."
      ]
    ],
    "scope": "This is the original 1993 family entry. A restricted active drained axial formulation is available through the related profile.",
    "limits": "The linked axial branch does not supply the full family’s possible elastic, cyclic or three-dimensional extensions.",
    "preparation": "Initial density, stress and internal history must belong to the exact formulation being used.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Jefferies (1993) — original NorSand publication",
        "url": "https://doi.org/10.1680/geot.1993.43.1.91"
      }
    ],
    "related": [
      "norsand-jefferies-1993-active-axial"
    ],
    "contentSources": [
      "docs/models/norsand-1993-active-axial-v1.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "NorSand — Jefferies (1993)"
  },
  "maxwell-itasca900-zero-spin-ode": {
    "summary": "Elastic volume response combined with shear creep and stress relaxation.",
    "introduction": "The Maxwell continuum combines an elastic shear spring with a viscous element in series. It relaxes deviatoric stress under held strain and continues shearing under a held deviatoric stress.",
    "behaviours": [
      [
        "Stress relaxation",
        "Held deviatoric strain allows shear stress to decay."
      ],
      [
        "Steady creep",
        "Held deviatoric stress produces a continuing strain rate."
      ],
      [
        "Elastic volume",
        "The bulk response has no viscous mechanism."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Dry total stress; durations and rates use physical seconds.",
    "limits": "This is a linear deviatoric Maxwell model with elastic bulk response. It excludes bulk creep, yielding, finite rotations and pore-fluid coupling.",
    "preparation": "Supply initial stress, accumulated strain and the loading history. The oedometer preset includes its elastic preparation.",
    "parameters": [
      {
        "name": "Kmod",
        "symbol": "K",
        "meaning": "Bulk modulus",
        "help": "Controls resistance to changes in volume.",
        "unit": "Pa"
      },
      {
        "name": "Gmod",
        "symbol": "G",
        "meaning": "Shear modulus",
        "help": "Controls the instantaneous resistance to changes in shape.",
        "unit": "Pa"
      },
      {
        "name": "eta",
        "symbol": "η",
        "meaning": "Shear viscosity",
        "help": "Together with G, sets the shear relaxation time η/G.",
        "unit": "Pa·s"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Itasca 9.0 — Maxwell viscous model",
        "url": "https://docs.itascacg.com/itasca900/common/models/viscous/doc/modelviscous.html"
      }
    ],
    "related": [
      "sls-comsol63-deviatoric-zero-spin-ode",
      "burgers-itasca900-dry-zero-spin-ode"
    ],
    "contentSources": [
      "docs/models/maxwell-itasca900-zero-spin-ode.md",
      "web/maxwell-laboratory.mjs"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Compare Relaxation · hold strains with Creep · hold stresses. Change viscosity while keeping elastic moduli fixed to see the change in time scale.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Maxwell viscoelasticity"
  },
  "sls-comsol63-deviatoric-zero-spin-ode": {
    "summary": "A viscoelastic solid that relaxes toward a nonzero long-term shear stiffness.",
    "introduction": "The Standard Linear Solid, also called the Zener model, places a relaxing Maxwell shear branch alongside an equilibrium spring. An independent elastic bulk response controls volume change.",
    "behaviours": [
      [
        "Partial stress relaxation",
        "Held strain loses the transient overstress but retains the equilibrium elastic stress."
      ],
      [
        "Delayed creep",
        "Held stress produces a delayed approach toward a finite strain."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Dry total stress with physical time in seconds.",
    "limits": "Atlas uses one ordinary deviatoric relaxation branch. There is no bulk relaxation, plasticity, fractional-time law or finite-rotation transport.",
    "preparation": "Supply total strain and the full deviatoric branch overstress. Zero overstress describes a relaxed branch; a freshly imposed strain has a different branch state.",
    "parameters": [
      {
        "name": "K",
        "symbol": "K",
        "meaning": "Bulk modulus",
        "help": "Controls elastic volume change.",
        "unit": "Pa"
      },
      {
        "name": "Ginf",
        "symbol": "G∞",
        "meaning": "Equilibrium shear modulus",
        "help": "Sets the long-term shear stiffness.",
        "unit": "Pa"
      },
      {
        "name": "G1",
        "symbol": "G₁",
        "meaning": "Branch shear modulus",
        "help": "Sets the additional transient shear stiffness.",
        "unit": "Pa"
      },
      {
        "name": "tau",
        "symbol": "τ",
        "meaning": "Relaxation time",
        "help": "Sets the decay time of the Maxwell branch.",
        "unit": "s"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "COMSOL 6.3 — Standard Linear Solid theory",
        "url": "https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.029.html#3441011"
      }
    ],
    "related": [
      "maxwell-itasca900-zero-spin-ode",
      "burgers-itasca900-dry-zero-spin-ode"
    ],
    "contentSources": [
      "docs/models/sls-comsol63-deviatoric-zero-spin-ode.md",
      "web/sls-laboratory.mjs"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Compare the relaxation and creep modes. Increase the relaxation time with both shear moduli fixed; the transient response lasts longer.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Standard Linear Solid (Zener) · deviatoric response"
  },
  "burgers-itasca900-dry-zero-spin-ode": {
    "summary": "A viscoelastic model combining immediate elasticity, delayed deformation and continuing creep.",
    "introduction": "The Burgers continuum combines Maxwell and Kelvin shear mechanisms. Their separate time scales let it describe a transient creep phase followed by continuing viscous deformation.",
    "behaviours": [
      [
        "Transient and steady creep",
        "Held shear stress produces delayed strain as well as a continuing viscous contribution."
      ],
      [
        "Stress relaxation",
        "Held strain allows deviatoric stress to evolve over time."
      ],
      [
        "Elastic volume",
        "The volume response remains elastic."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Dry total stress; loading duration is measured in physical seconds.",
    "limits": "The formulation is linear viscoelastic in deviatoric response, with no plastic yield surface, bulk viscosity or pore-fluid law.",
    "preparation": "Supply total stress and the Kelvin deviatoric-strain history. Accumulated strain and physical-time history are also needed for a reproducible run.",
    "parameters": [
      {
        "name": "Kmod",
        "symbol": "K",
        "meaning": "Bulk modulus",
        "help": "Controls resistance to changes in volume.",
        "unit": "Pa"
      },
      {
        "name": "Gm",
        "symbol": "G_m",
        "meaning": "Maxwell shear modulus",
        "help": "Sets instantaneous shear elasticity in the Maxwell branch.",
        "unit": "Pa"
      },
      {
        "name": "Gk",
        "symbol": "G_k",
        "meaning": "Kelvin shear modulus",
        "help": "Sets the stiffness of the delayed-recovery branch.",
        "unit": "Pa"
      },
      {
        "name": "etam",
        "symbol": "η_m",
        "meaning": "Maxwell viscosity",
        "help": "Controls continuing shear creep.",
        "unit": "Pa·s"
      },
      {
        "name": "etak",
        "symbol": "η_k",
        "meaning": "Kelvin viscosity",
        "help": "Controls the time scale of delayed strain.",
        "unit": "Pa·s"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Itasca 9.0 — Burgers model",
        "url": "https://docs.itascasoftware.com/itasca900/common/models/burgers/doc/modelburgers.html"
      }
    ],
    "related": [
      "maxwell-itasca900-zero-spin-ode",
      "sls-comsol63-deviatoric-zero-spin-ode"
    ],
    "contentSources": [
      "docs/models/burgers-main-laboratory-v1.md",
      "web/timed-laboratory.mjs"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Compare the creep and relaxation presets. Change the Kelvin viscosity to explore delayed response, then the Maxwell viscosity to explore the continuing creep contribution.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Burgers viscoelasticity"
  },
  "power-creep-itasca900-both-active-ode": {
    "summary": "Stress-dependent creep formed by adding two active power-law mechanisms.",
    "introduction": "The two-component Norton law relates deviatoric creep rate to deviatoric stress through two powers. Their sum can give different stress sensitivity over different stress levels.",
    "behaviours": [
      [
        "Nonlinear creep",
        "Changing the deviatoric stress can change creep rate by much more than the same proportion."
      ],
      [
        "Relaxation under held strain",
        "Viscous shearing can reduce deviatoric stress while strain is held."
      ]
    ],
    "scope": "The dedicated laboratory uses dry total stress, small strains, fixed axes and physical seconds. Volume response is elastic.",
    "limits": "Both creep mechanisms remain active in this variant, with exponents at least one. Threshold switching, pore-fluid coupling and finite rotations are excluded.",
    "preparation": "Supply initial total stress and a complete time/loading history. A fixed strain hold still advances physical time and can relax stress.",
    "parameters": [
      {
        "name": "Kmod",
        "symbol": "K",
        "meaning": "Bulk modulus",
        "help": "Controls resistance to changes in volume.",
        "unit": "Pa"
      },
      {
        "name": "Gmod",
        "symbol": "G",
        "meaning": "Shear modulus",
        "help": "Controls the instantaneous resistance to changes in shape.",
        "unit": "Pa"
      },
      {
        "name": "b1",
        "symbol": "b₁",
        "meaning": "First rate coefficient",
        "help": "Sets the first mechanism’s creep rate at the reference stress.",
        "unit": "1/s"
      },
      {
        "name": "n1",
        "symbol": "n₁",
        "meaning": "First stress exponent",
        "help": "Sets the first mechanism’s stress sensitivity.",
        "unit": "1"
      },
      {
        "name": "b2",
        "symbol": "b₂",
        "meaning": "Second rate coefficient",
        "help": "Sets the second mechanism’s creep rate at the reference stress.",
        "unit": "1/s"
      },
      {
        "name": "n2",
        "symbol": "n₂",
        "meaning": "Second stress exponent",
        "help": "Sets the second mechanism’s stress sensitivity.",
        "unit": "1"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "Itasca 9.0 — two-component power creep",
        "url": "https://docs.itascacg.com/itasca900/common/models/power/doc/modelpower.html"
      }
    ],
    "related": [],
    "contentSources": [
      "docs/models/power-creep-itasca900-both-active-ode.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Open the dedicated physical-time laboratory. Compare a stress hold with a strain hold, then change a stress exponent to explore nonlinear rate sensitivity.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Two-component power creep"
  },
  "sanisand-2004": {
    "summary": "A sand plasticity model that couples critical-state behaviour with evolving fabric effects.",
    "introduction": "The 2004 Dafalias–Manzari model adds fabric-change effects to a critical-state sand plasticity framework. Internal tensors distinguish stress-ratio evolution, loading-process memory and fabric-dependent dilatancy.",
    "behaviours": [
      [
        "Density and pressure effects",
        "A critical-state relation provides the density reference."
      ],
      [
        "Fabric-sensitive reversal",
        "Fabric evolution influences the response after changes of loading direction."
      ]
    ],
    "scope": "This profile describes the original 2004 publication. It is available here for reading; the main laboratory has no public SANISAND run.",
    "limits": "Later SANISAND versions have different history rules and mechanisms. A parameter set or algorithm from a later version cannot identify the 2004 law.",
    "preparation": "A complete setup needs stress, void ratio, surface/backstress variables, fabric and loading-process memory. These histories cannot be inferred from initial stress alone.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Dafalias and Manzari (2004) — sand model accounting for fabric change effects",
        "url": "https://doi.org/10.1061/(ASCE)0733-9399(2004)130:6(622)"
      }
    ],
    "related": [
      "manzari-dafalias-1997",
      "norsand-1993"
    ],
    "contentSources": [
      "docs/ingestion/sanisand-2004/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "SANISAND — Dafalias & Manzari (2004)"
  },
  "manzari-dafalias-1997": {
    "summary": "A critical-state two-surface plasticity model for sand.",
    "introduction": "The 1997 Manzari–Dafalias formulation belongs to the critical-state sand-plasticity family. Its two-surface construction separates the current yield description from an additional surface governing response.",
    "behaviours": [
      [
        "Critical-state framework",
        "Sand density is interpreted relative to a pressure-dependent critical state."
      ],
      [
        "Two-surface plasticity",
        "An additional surface supplies structure beyond a single fixed yield surface."
      ]
    ],
    "scope": "This is the 1997 literature entry; there is no public laboratory implementation.",
    "limits": "The later 2004 fabric-change model is a separate formulation. Exact surface, hardening and calibration conventions must be taken from the selected original source.",
    "preparation": "Use the original publication for the complete parameter and internal-state specification; no Atlas material preset is supplied.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Manzari and Dafalias (1997) — A critical state two-surface plasticity model for sands",
        "url": "https://doi.org/10.1680/geot.1997.47.2.255"
      }
    ],
    "related": [
      "sanisand-2004"
    ],
    "contentSources": [
      "docs/ingestion/manzari-dafalias-1997/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Manzari–Dafalias sand model (1997)"
  },
  "matsuoka-nakai": {
    "summary": "A frictional strength description that includes the intermediate principal stress.",
    "introduction": "The Matsuoka–Nakai framework relates soil strength and deformation to a mobilized-plane construction under three different principal stresses.",
    "behaviours": [
      [
        "Three-principal-stress effects",
        "The intermediate stress participates in the strength description."
      ],
      [
        "Frictional behaviour",
        "The construction links shear and normal stress on mobilized planes."
      ]
    ],
    "scope": "This is a literature-family entry, with no public stress-update implementation.",
    "limits": "A strength criterion by itself does not specify a complete constitutive model. Elasticity, flow and evolution rules depend on the chosen formulation.",
    "preparation": "Consult the exact source formulation before assigning stiffness, history or a loading path.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Matsuoka and Nakai (1974) — stress-deformation and strength under three principal stresses",
        "url": "https://doi.org/10.2208/jscej1969.1974.232_59"
      }
    ],
    "related": [
      "lade-duncan-1975",
      "mohr-coulomb"
    ],
    "contentSources": [
      "catalogue/manifest.json"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Matsuoka–Nakai plasticity"
  },
  "s-clay1": {
    "summary": "An anisotropic elastoplastic model for soft clay.",
    "introduction": "S-CLAY1 represents directional differences in clay response through an anisotropic plasticity framework. It is intended to distinguish a material with a preferred direction from an isotropic clay idealization.",
    "behaviours": [
      [
        "Directional yielding",
        "The response depends on stress direction relative to the material’s anisotropy."
      ],
      [
        "Soft-clay plasticity",
        "Elastic and permanent deformation are represented within one constitutive formulation."
      ]
    ],
    "scope": "This profile identifies Wheeler, Näätänen, Karstunen and Lojander’s 2003 publication. There is no public laboratory run.",
    "limits": "S-CLAY1 and later structured-clay extensions need their own equations and calibration. This entry supplies no interchangeable Modified Cam Clay parameter set.",
    "preparation": "A setup needs the initial anisotropy as well as stress and density. Use the original formulation for its exact state and parameter conventions.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Wheeler et al. (2003) — An anisotropic elastoplastic model for soft clays",
        "url": "https://doi.org/10.1139/t02-119"
      }
    ],
    "related": [
      "modified-cam-clay",
      "hypoplastic-clay-2014"
    ],
    "contentSources": [
      "docs/ingestion/s-clay1/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "S-CLAY1 — Wheeler et al. (2003)"
  },
  "hypoplastic-isa": {
    "summary": "A hypoplastic sand extension for loading-direction memory and cyclic mobility.",
    "introduction": "The selected Fuentes–Wichtmann–Gil–Lascarro formulation combines intergranular-strain anisotropy with additional cyclic-mobility effects for liquefaction analysis.",
    "behaviours": [
      [
        "Small-strain memory",
        "Additional history describes recent loading directions."
      ],
      [
        "Cyclic mobility",
        "The extension introduces a mechanism for changing response during cyclic loading."
      ]
    ],
    "scope": "This is the 2020 journal formulation, first published online in 2019. It is a reading profile without a main-laboratory implementation.",
    "limits": "ISA, the 1997 IGS overlay and 2024 generalized intergranular strain are different formulations. Their history variables and initial states are not interchangeable.",
    "preparation": "A complete setup includes the selected sand host, intergranular histories and cyclic-mobility history in addition to stress and void ratio.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Fuentes et al. (2020) — ISA-Hypoplasticity accounting for cyclic mobility effects",
        "url": "https://doi.org/10.1007/s11440-019-00846-2"
      }
    ],
    "related": [
      "hypoplastic-sand-igs97",
      "hypoplastic-generalized-igs-2024"
    ],
    "contentSources": [
      "docs/ingestion/hypoplastic-isa/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Hypoplasticity + ISA — Fuentes et al."
  },
  "hca-sand-2005": {
    "summary": "A cycle-averaged model for accumulation of sand deformation over many repeated loads.",
    "introduction": "The high-cycle accumulation approach estimates the gradual drift caused by many cycles rather than resolving every small loading excursion. It uses information about strain amplitude, direction and previous cyclic loading.",
    "behaviours": [
      [
        "Long-cycle accumulation",
        "Small changes per cycle can build up into significant permanent deformation."
      ],
      [
        "Amplitude and history effects",
        "The representative cycle and its direction affect the accumulated response."
      ]
    ],
    "scope": "This is the Niemunis–Wichtmann–Triantafyllidis 2005 literature entry. There is no public HCA laboratory run.",
    "limits": "Cycle count is its accumulation coordinate. The model is not an instantaneous stress-rate law and cannot replace explicit cyclic simulation for every loading regime.",
    "preparation": "A setup needs resolved representative cycles, amplitude/polarization information and preloading history, together with stress and density.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Niemunis et al. (2005) — A high-cycle accumulation model for sand",
        "url": "https://doi.org/10.1016/j.compgeo.2005.03.002"
      }
    ],
    "related": [],
    "contentSources": [
      "docs/ingestion/hca-sand-2005/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "High-cycle accumulation — Niemunis et al. (2005)"
  },
  "pm4sand": {
    "summary": "A plane-strain sand plasticity model developed for earthquake loading and liquefaction analysis.",
    "introduction": "PM4Sand uses a stress-ratio-controlled plasticity framework to describe sand behaviour under monotonic and cyclic loading. Its calibration and initialization belong to a particular software-model release.",
    "behaviours": [
      [
        "Cyclic sand response",
        "The formulation addresses changes in shear response over repeated loading."
      ],
      [
        "Liquefaction modelling",
        "State and history variables support effective-stress analyses of liquefaction-related response."
      ]
    ],
    "scope": "This entry identifies PM4Sand2D version 3.3. No public Atlas laboratory implementation is supplied.",
    "limits": "The model is plane strain. PM4Sand3D is a separate formulation, and parameters require release-specific calibration rather than transfer across versions.",
    "preparation": "Use the selected release manual for relative-density calibration, initial effective stress and all cyclic-history initialization.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Boulanger and Ziotopoulou — PM4Sand releases and manuals",
        "url": "https://pm4sand.engr.ucdavis.edu/pm4sand-files"
      }
    ],
    "related": [
      "pm4sand3d-1.0",
      "pm4silt"
    ],
    "contentSources": [
      "docs/models/pm4sand-versions.md",
      "docs/ingestion/pm4sand/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "PM4Sand2D 3.3 — Boulanger & Ziotopoulou"
  },
  "pm4sand3d-1.0": {
    "summary": "A three-dimensional PM4Sand formulation for sand response under general stress paths.",
    "introduction": "PM4Sand3D extends the PM4Sand modelling approach to a three-dimensional setting, with its own constitutive history and integration requirements.",
    "behaviours": [
      [
        "Three-dimensional loading",
        "The formulation can represent stress paths beyond a plane-strain restriction."
      ],
      [
        "Cyclic sand behaviour",
        "The model family targets earthquake-related sand and liquefaction response."
      ]
    ],
    "scope": "This entry identifies Kippen, Boulanger and Ziotopoulou’s PM4Sand3D version 1.0. There is no public Atlas laboratory run.",
    "limits": "A three-dimensional formulation is not obtained by simply adding components to PM4Sand2D. Use the correct 3D release, history layout and calibration.",
    "preparation": "Initial stress, density/calibration and internal cyclic histories must follow the selected 3D manual.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Kippen, Boulanger and Ziotopoulou — PM4Sand3D releases",
        "url": "https://pm4sand.engr.ucdavis.edu/pm4sand3d-files"
      }
    ],
    "related": [
      "pm4sand"
    ],
    "contentSources": [
      "docs/models/pm4sand-versions.md",
      "docs/models/pm4sand3d-1.0-manual.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "PM4Sand3D 1.0 — Kippen, Boulanger & Ziotopoulou"
  },
  "pm4silt": {
    "summary": "A cyclic plasticity model for low-plasticity silts and clays in earthquake analyses.",
    "introduction": "PM4Silt is a separate model from PM4Sand. Its strength-based calibration and cyclic-history mechanisms address fine-grained soil response.",
    "behaviours": [
      [
        "Cyclic fine-grained-soil response",
        "History affects stiffness, plastic deformation and volume tendency during repeated loading."
      ],
      [
        "Strength-based setup",
        "Material calibration is tied to the selected fine-grained-soil formulation."
      ]
    ],
    "scope": "This is PM4Silt version 1 (2018), a plane-strain literature entry with no public Atlas run.",
    "limits": "PM4Sand parameter sets and later PM4Silt releases cannot be substituted for this version. The formulation and host implementation have release-specific initialization rules.",
    "preparation": "Use the version 1 manual for strength, stiffness and cyclic-history initialization, including the initial effective stress.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Boulanger and Ziotopoulou — PM4Silt author site",
        "url": "https://pm4silt.engr.ucdavis.edu/"
      }
    ],
    "related": [
      "pm4sand"
    ],
    "contentSources": [
      "docs/ingestion/pm4silt/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "PM4Silt — Boulanger & Ziotopoulou"
  },
  "extended-mohr-coulomb-2013": {
    "summary": "A hardening extension of Mohr–Coulomb with a separate volume-change rule.",
    "introduction": "Doherty and Muir Wood combine Mohr–Coulomb yielding with Cam Clay flow and asymptotic hardening. The mobilized strength changes as plastic deformation accumulates.",
    "behaviours": [
      [
        "Evolving strength",
        "Hardening changes the mobilized frictional response."
      ],
      [
        "Separate plastic volume response",
        "The flow rule supplies volume change separately from the yield criterion."
      ]
    ],
    "scope": "This profile describes the 2013 Extended Mohr–Coulomb publication. It has no public laboratory run.",
    "limits": "The model has no postpeak softening or creep. Except for the equal-angle case, it need not reach a true critical state with zero plastic volume rate.",
    "preparation": "The initial mobilized friction and accumulated plastic history matter alongside stress and the material parameters.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Doherty and Muir Wood (2013) — Extended Mohr–Coulomb",
        "url": "https://doi.org/10.1680/geot.12.P.008"
      }
    ],
    "related": [
      "mohr-coulomb",
      "modified-cam-clay"
    ],
    "contentSources": [
      "docs/ingestion/extended-mohr-coulomb-2013/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Extended Mohr–Coulomb (EMC) — Doherty & Muir Wood (2013)"
  },
  "hypoplastic-interface-2016": {
    "summary": "A hypoplastic description of granular soil sliding and volume change at a structure interface.",
    "introduction": "The Stutz–Mašín–Wuttke interface formulation adapts granular hypoplasticity to a thin shear zone next to a structure. Interface slip, normal deformation and shear-zone thickness replace a general bulk loading path.",
    "behaviours": [
      [
        "Interface shear",
        "Traction changes with relative sliding at the contact."
      ],
      [
        "Normal coupling",
        "Normal compression and dilation interact with the shear response."
      ]
    ],
    "scope": "This entry describes the selected 2016 granular interface formulation; there is no public interface laboratory.",
    "limits": "An interface law uses local directions and interface thickness. It is not a general bulk-soil stress update, and different roughness branches require their own definitions.",
    "preparation": "Specify local stress, density, shear-zone thickness, normal deformation and the two slip directions, together with the selected roughness branch.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Stutz, Mašín and Wuttke (2016) — granular soil–structure interface behaviour",
        "url": "https://doi.org/10.1007/s11440-016-0440-1"
      }
    ],
    "related": [
      "hypoplastic-sand-vw96"
    ],
    "contentSources": [
      "docs/ingestion/hypoplastic-interface-2016/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Hypoplastic interface — Stutz, Mašín & Wuttke (2016)"
  },
  "multilaminate-schadlich-schweiger": {
    "summary": "A soil modelling approach that combines responses on many oriented material planes.",
    "introduction": "The Schädlich–Schweiger multilaminate framework describes local plane responses and combines them into a bulk material response. Its stiff-soil formulations include small-strain and overconsolidation effects.",
    "behaviours": [
      [
        "Directional response",
        "Different plane orientations contribute differently to a given loading direction."
      ],
      [
        "Plane histories",
        "History is retained on the individual planes rather than described only by one scalar variable."
      ]
    ],
    "scope": "This profile covers the thesis and related stiff-soil model family. No public full multilaminate laboratory run is supplied.",
    "limits": "The selected base and later extensions differ. A plane criterion or isolated hardening fragment alone does not define the complete model.",
    "preparation": "A complete setup needs the plane set and weights, local histories, initial stress and the chosen anisotropy/overconsolidation variant.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Schädlich and Schweiger — multilaminate model overview",
        "url": "https://soilmodels.com/multilaminate/"
      }
    ],
    "related": [],
    "contentSources": [
      "docs/ingestion/multilaminate-schadlich-schweiger/README.md",
      "docs/ingestion/multilaminate-schadlich-schweiger/base-laws-v1/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Multilaminate model — Schädlich & Schweiger"
  },
  "hypoplastic-thermal-ma-2017": {
    "summary": "A clay hypoplasticity extension for volume change during heating and cooling cycles.",
    "introduction": "Ma, Ng, Mašín and Zhou extend a fine-grained-soil framework with temperature-dependent compression behaviour and thermal-cycle history.",
    "behaviours": [
      [
        "Thermal volume change",
        "Temperature changes affect the compression reference and the volume response."
      ],
      [
        "Cycle history",
        "Successive heating and cooling stages can produce different accumulated deformation."
      ]
    ],
    "scope": "This describes the 2017 thermal-cycle formulation. There is no public thermal laboratory run.",
    "limits": "The thermal extension depends on its particular mechanical host and temperature convention. The 2013 and 2014 clay formulations are not interchangeable hosts.",
    "preparation": "A complete run needs temperature history and its reference convention, thermal memory and a consistently prepared mechanical state.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Ma et al. (2017) — fine-grained soil volume change under thermal cycles",
        "url": "https://doi.org/10.1139/cgj-2016-0459"
      }
    ],
    "related": [
      "hypoplastic-clay-2005",
      "vibe-2026"
    ],
    "contentSources": [
      "docs/ingestion/hypoplastic-thermal-ma-2017/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Thermal-cycle hypoplasticity — Ma et al. (2017)"
  },
  "vibe-2026": {
    "summary": "A time-dependent bentonite model with separate microstructural and macrostructural responses.",
    "introduction": "Mašín’s VIBE formulation describes bentonite with coupled thermal, hydraulic and mechanical effects. Viscous behaviour adds stress relaxation to a double-structure description.",
    "behaviours": [
      [
        "Stress relaxation",
        "The response can evolve over physical time."
      ],
      [
        "Two structural scales",
        "The model distinguishes microstructure from the larger-scale pore structure."
      ],
      [
        "Thermal and hydraulic effects",
        "Temperature and water-retention behaviour enter the bentonite description."
      ]
    ],
    "scope": "This is the 2026 literature entry. No public Atlas VIBE laboratory run is supplied.",
    "limits": "A simple clay or dry creep preset does not reproduce coupled bentonite behaviour. Use the exact formulation and its material calibration.",
    "preparation": "A full setup needs hydraulic and thermal conditions, both structural states and a loading/time history appropriate to the bentonite.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Mašín (2026) — Viscohypoplastic bentonite (VIBE) model",
        "url": "https://doi.org/10.1016/j.enggeo.2026.108827"
      }
    ],
    "related": [
      "hypoplastic-thermal-ma-2017"
    ],
    "contentSources": [
      "catalogue/manifest.json"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Viscohypoplastic bentonite (VIBE) — Mašín (2026)"
  },
  "hypoplastic-clay-2014": {
    "summary": "Clay hypoplasticity with direction-dependent stiffness.",
    "introduction": "The 2014 Mašín model adds stiffness anisotropy to the explicitly asymptotic-state clay framework. Different directions relative to the material plane can have different stiffnesses.",
    "behaviours": [
      [
        "Stiffness anisotropy",
        "Elastic-like response depends on direction relative to the fabric plane."
      ],
      [
        "Hypoplastic clay response",
        "Stress and density still evolve through a direct nonlinear law."
      ]
    ],
    "scope": "This profile describes the 2014 anisotropic formulation. It has no public laboratory run.",
    "limits": "The 2013 isotropic clay law and the 2014 anisotropic extension are separate. A fixed-plane research calculation does not supply automatic rotation of the material fabric.",
    "preparation": "Specify the material-plane orientation, anisotropy ratios, stress and density consistently with the selected formulation.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Mašín (2014) — Clay hypoplasticity model including stiffness anisotropy",
        "url": "https://doi.org/10.1680/geot.13.P.065"
      }
    ],
    "related": [
      "hypoplastic-clay-2013",
      "s-clay1"
    ],
    "contentSources": [
      "docs/models/hypoplastic-clay-2014-original.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Anisotropic clay hypoplasticity — Mašín (2014)"
  },
  "terracotta-2024": {
    "summary": "A rate-dependent clay model using an internal measure of mesoscopic agitation.",
    "introduction": "Wiebicke and Einav’s Terra Cotta model combines elastic and dissipative responses. Its mesoscopic-temperature variable measures internal agitation rather than the specimen’s ordinary thermal temperature.",
    "behaviours": [
      [
        "Rate effects",
        "The response depends on physical loading rate and elapsed time."
      ],
      [
        "Creep and relaxation",
        "Stress holds and strain holds can both produce continuing evolution."
      ]
    ],
    "scope": "This profile concerns the simplified Figure 1 axisymmetric formulation. It has no main-laboratory run; the separate research formulation uses physical time.",
    "limits": "The simplified triaxial formulation, fuller Appendix B law and later tensor generalizations are distinct. Ordinary thermal temperature cannot replace the agitation variable.",
    "preparation": "Initialization requires elastic strain measures, density/solid fraction and mesoscopic temperature, consistent with stress and loading rate.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Wiebicke and Einav (2024) — A simple hydrodynamic model for clay",
        "url": "https://doi.org/10.1016/j.jmps.2024.105789"
      }
    ],
    "related": [],
    "contentSources": [
      "docs/models/terracotta-2024.md",
      "docs/ingestion/terracotta-2024/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Terracotta (Terra Cotta) — Wiebicke & Einav (2024)"
  },
  "hypoplastic-generalized-igs-2024": {
    "summary": "A generalized intergranular-strain framework with additional cyclic-preloading memory.",
    "introduction": "Mugele, Stutz and Mašín generalize intergranular-strain extensions for use with hypoplastic hosts. The chosen host and pairing are part of the model definition.",
    "behaviours": [
      [
        "Small-strain direction memory",
        "An intergranular-strain tensor changes stiffness after turns and reversals."
      ],
      [
        "Cyclic-preloading effects",
        "An additional history variable modifies the stiffness transition as cyclic loading accumulates."
      ]
    ],
    "scope": "This is the 2024 framework entry. A separately listed selected host pairing is available in the laboratory.",
    "limits": "Different host pairings, the 1997 IGS overlay and ISA are distinct models. Framework parameters cannot be transferred without the corresponding host definition.",
    "preparation": "Supply the host state, intergranular-strain tensor and cyclic-preloading history under the selected pairing’s initialization rules.",
    "parameters": [],
    "stateLabels": {},
    "references": [
      {
        "label": "Mugele, Stutz and Mašín (2024) — generalized intergranular strain concept",
        "url": "https://doi.org/10.1016/j.compgeo.2024.106480"
      }
    ],
    "related": [
      "research-hp-extracted-asbs-gis-2024-v03",
      "hypoplastic-sand-igs97",
      "hypoplastic-isa"
    ],
    "contentSources": [
      "docs/ingestion/hypoplastic-generalized-igs-2024/README.md"
    ],
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Generalized intergranular strain — Mugele, Stutz & Mašín (2024)"
  },
  "research-hp-extracted-asbs-gis-2024-v03": {
    "summary": "A selected sand hypoplasticity pairing with generalized small-strain and cyclic-preloading memory.",
    "introduction": "This realization combines the selected hypoplastic host and extracted asymptotic-state description with the 2024 generalized intergranular-strain extension. Its internal variables retain recent strain direction and cyclic-preloading history.",
    "behaviours": [
      [
        "Small-strain direction memory",
        "An intergranular-strain tensor changes stiffness after turns and reversals."
      ],
      [
        "Cyclic-preloading effects",
        "An additional history variable modifies the stiffness transition as cyclic loading accumulates."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Stresses are effective stresses; the surrounding drainage formulation supplies any pore-pressure response. Changing elapsed time alone does not produce creep or relaxation.",
    "limits": "This is one specific host pairing. The intergranular-strain magnitude must remain within its memory radius; the implementation does not project an outside state back onto the boundary. Other GIS pairings and ISA are separate.",
    "preparation": "Supply the initial effective stress and void ratio. A numerically admissible state still needs to represent the material’s actual preparation. Also supply every component of h and the cyclic-preloading variable Ω. A zero-history example is not a reconstructed specimen history.",
    "parameters": [
      {
        "name": "phi",
        "symbol": "φ_c",
        "meaning": "Critical friction angle",
        "help": "Sets the frictional limit at critical state.",
        "unit": "rad"
      },
      {
        "name": "hs",
        "symbol": "h_s",
        "meaning": "Granular hardness",
        "help": "Sets the pressure scale for stiffness and density limits.",
        "unit": "Pa"
      },
      {
        "name": "n",
        "symbol": "n",
        "meaning": "Pressure exponent",
        "help": "Controls how density limits and stiffness change with pressure.",
        "unit": "1"
      },
      {
        "name": "ed0",
        "symbol": "e_d0",
        "meaning": "Dense limiting void ratio",
        "help": "Locates the dense limit at zero pressure.",
        "unit": "1"
      },
      {
        "name": "ec0",
        "symbol": "e_c0",
        "meaning": "Critical void ratio",
        "help": "Locates the critical-state density at zero pressure.",
        "unit": "1"
      },
      {
        "name": "ei0",
        "symbol": "e_i0",
        "meaning": "Loose limiting void ratio",
        "help": "Locates the loose limit at zero pressure.",
        "unit": "1"
      },
      {
        "name": "alpha",
        "symbol": "α",
        "meaning": "Density influence",
        "help": "Controls the influence of density on the nonlinear response.",
        "unit": "1"
      },
      {
        "name": "beta",
        "symbol": "β",
        "meaning": "Density stiffness influence",
        "help": "Controls how relative density changes stiffness.",
        "unit": "1"
      },
      {
        "name": "R",
        "symbol": "R",
        "meaning": "Memory radius",
        "help": "Sets the scale of very small strain over which direction memory changes.",
        "unit": "1"
      },
      {
        "name": "m_R",
        "symbol": "m_R",
        "meaning": "Reversal stiffness",
        "help": "Sets the stiffness increase after reversing the strain direction.",
        "unit": "1"
      },
      {
        "name": "m_T",
        "symbol": "m_T",
        "meaning": "Orthogonal stiffness",
        "help": "Sets the stiffness response when the loading direction turns by a right angle.",
        "unit": "1"
      },
      {
        "name": "beta_R",
        "symbol": "β_r",
        "meaning": "Memory mobilisation",
        "help": "Controls how quickly intergranular strain approaches its limiting magnitude.",
        "unit": "1"
      },
      {
        "name": "chi_R",
        "symbol": "χ",
        "meaning": "Stiffness transition",
        "help": "Controls the transition between small-strain and continuing-loading stiffness.",
        "unit": "1"
      },
      {
        "name": "gamma_chi",
        "symbol": "γ_χ",
        "meaning": "Suppression exponent factor",
        "help": "Controls the history-dependent stiffness-transition exponent.",
        "unit": "1"
      },
      {
        "name": "chi_0",
        "symbol": "χ₀",
        "meaning": "Initial suppression parameter",
        "help": "Sets the initial stiffness-suppression reference.",
        "unit": "1"
      },
      {
        "name": "chi_max",
        "symbol": "χ_max",
        "meaning": "Maximum suppression parameter",
        "help": "Sets the upper stiffness-suppression reference.",
        "unit": "1"
      },
      {
        "name": "C_Omega",
        "symbol": "C_Ω",
        "meaning": "Preloading coefficient",
        "help": "Controls cyclic-preloading history evolution.",
        "unit": "1"
      },
      {
        "name": "gamma_Omega",
        "symbol": "γ_Ω",
        "meaning": "Preloading exponent",
        "help": "Controls the nonlinearity of cyclic-preloading evolution.",
        "unit": "1"
      }
    ],
    "stateLabels": {
      "e": "Void ratio e"
    },
    "references": [
      {
        "label": "Mugele, Stutz and Mašín (2024) — generalized intergranular strain",
        "url": "https://doi.org/10.1016/j.compgeo.2024.106480"
      }
    ],
    "related": [
      "hypoplastic-generalized-igs-2024",
      "hypoplastic-sand-igs97"
    ],
    "contentSources": [
      "models/research-hp-extracted-asbs-gis-2024-v03.json",
      "docs/ingestion/hypoplastic-generalized-igs-2024/README.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Begin with Load model example and a small supported strain path. Inspect the complete h and Ω history when exploring a loading reversal. Keep the initial memory inside its declared radius.",
    "parameterNote": "These host and memory coefficients form one selected pairing. Keep the complete set together, with the specified pressure units and initial histories.",
    "title": "Sand hypoplasticity with generalized intergranular strain · selected pairing"
  },
  "ramberg-osgood-ansys242": {
    "summary": "A reversible nonlinear stress–strain law with a smoothly changing stiffness.",
    "introduction": "This three-dimensional Ramberg–Osgood deformation law relates the current stress to the current strain. Unloading retraces loading, so nonlinearity alone does not imply permanent plastic deformation.",
    "behaviours": [
      [
        "Nonlinear stiffness",
        "The response departs smoothly from the initial elastic slope."
      ],
      [
        "Reversible unloading",
        "There is no plastic-strain memory or hysteresis in this formulation."
      ]
    ],
    "scope": "The Atlas formulation uses three-dimensional small strain, fixed spatial axes and compression-positive stress and strain. Dry total stress.",
    "limits": "This is the constant-parameter ANSYS 2024 R2 deformation-law variant, without a yield surface or permanent plastic strain.",
    "preparation": "Supply consistent full stress and strain tensors.",
    "parameters": [
      {
        "name": "E",
        "symbol": "E",
        "meaning": "Young modulus",
        "help": "Sets the slope of the elastic axial stress–strain response.",
        "unit": "Pa"
      },
      {
        "name": "nu",
        "symbol": "ν",
        "meaning": "Poisson ratio",
        "help": "Controls the balance of lateral and axial elastic deformation.",
        "unit": "1"
      },
      {
        "name": "sigma0",
        "symbol": "σ₀",
        "meaning": "Reference strength",
        "help": "Sets the stress scale for nonlinearity.",
        "unit": "Pa"
      },
      {
        "name": "alpha",
        "symbol": "α",
        "meaning": "Nonlinearity coefficient",
        "help": "Sets the nonlinear strain contribution.",
        "unit": "1"
      },
      {
        "name": "n",
        "symbol": "n",
        "meaning": "Exponent",
        "help": "Controls curvature beyond the initial linear response.",
        "unit": "1"
      }
    ],
    "stateLabels": {},
    "references": [
      {
        "label": "ANSYS 2024 R2 — Ramberg–Osgood material",
        "url": "https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/ans_mat/ramberg-osgood.html"
      }
    ],
    "related": [],
    "contentSources": [
      "models/ramberg-osgood-ansys242.json",
      "docs/models/ramberg-osgood-ansys242.md"
    ],
    "explorationTitle": "Explore the response",
    "exploration": "Use a small monotonic strain path, then reverse it to explore reversible nonlinearity.",
    "parameterNote": "Use consistent units and a material-specific parameter set. Laboratory presets illustrate behaviour.",
    "title": "Ramberg–Osgood · reversible nonlinear elasticity"
  }
};
