"""Reproduce the complete source-transcribed candidate; no external model dependency."""
import json
from pathlib import Path
CANDIDATE = {'schema_version': '0.3',
 'id': 'kelvin-voigt-comsol63-deviatoric-zero-spin-ode',
 'name': 'COMSOL 6.3 Kelvin–Voigt — deviatoric dry zero-spin ODE',
 'family': 'linear viscoelasticity',
 'description': 'Ordinary isotropic Kelvin–Voigt spring and dashpot in parallel, with deviatoric '
                'viscosity and purely elastic bulk. Small-strain fixed-spatial '
                'compression-positive specialization of COMSOL 6.3 Eq3-36; no initial stress '
                'offset, inelastic, thermal, pore or fractional effects. Persistent eps stores '
                'total infinitesimal strain; viscous stress depends instantaneously on the '
                'prescribed strain rate and has no auxiliary memory. Parameters, numerical bounds '
                'and zero illustrative state are project choices, not calibration.',
 'status': 'draft',
 'sources': [{'url': 'https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_theory.06.029.html#3441080',
              'locator': 'The Kelvin–Voigt Model; Fig3-4; Eq3-36 anchor3441129 image074; eta=tau G '
                         'anchor3441131; dissipation anchor3960090 image075; isotropic elasticity '
                         'anchor3440835 image010; volumetric/deviatoric definitions '
                         'anchors3440792–3440818',
              'role': 'primary vendor mathematical formulation'},
             {'url': 'https://doc.comsol.com/6.3/doc/com.comsol.help.sme/sme_ug_solid.07.016.html#4898977',
              'locator': 'Kelvin–Voigt settings anchors4898977–4898981; select Deviatoric and '
                         'ordinary derivatives; relaxation time s or viscosity Pa s',
              'role': 'primary variant and parameter units'}],
 'formulation': {'time_dependence': 'physical_time',
                 'equation_form': 'ode',
                 'kinematics': 'small_strain_3d',
                 'frame': 'fixed_spatial',
                 'objective_rate': 'none',
                 'tensor_representation': 'mandel',
                 'stress_sign': 'compression_positive',
                 'strain_sign': 'compression_positive',
                 'inputs': {'equation': {'time': {'quantity': 'time',
                                                  'shape': 'scalar',
                                                  'unit': 's',
                                                  'sampling': 'stage',
                                                  'constraint': 'finite'},
                                         'strain_rate': {'quantity': 'strain_rate',
                                                         'measure': 'infinitesimal_strain_rate',
                                                         'shape': 'sym',
                                                         'unit': {'si': [0, 0, -1, 0]},
                                                         'configuration': 'current',
                                                         'sampling': 'stage',
                                                         'constraint': 'finite'}},
                            'advance': {'start_time': {'quantity': 'time',
                                                       'shape': 'scalar',
                                                       'unit': 's',
                                                       'sampling': 'start',
                                                       'constraint': 'finite'},
                                        'duration': {'quantity': 'duration',
                                                     'shape': 'scalar',
                                                     'unit': 's',
                                                     'sampling': 'interval',
                                                     'constraint': 'positive_finite'}}},
                 'stress': {'source': 'observable',
                            'name': 'stress',
                            'measure': 'cauchy',
                            'scope': 'total'}},
 'parameters': {'K': {'default': 20000000.0,
                      'min': 1e-12,
                      'max': 1e+30,
                      'unit': 'Pa',
                      'label': 'Project illustrative K'},
                'G': {'default': 12000000.0,
                      'min': 1e-12,
                      'max': 1e+30,
                      'unit': 'Pa',
                      'label': 'Project illustrative G'},
                'tau': {'default': 2.0,
                        'min': 1e-12,
                        'max': 1e+30,
                        'unit': 's',
                        'label': 'Project illustrative tau'}},
 'state': [{'name': 'eps',
            'shape': 'sym',
            'unit': '1',
            'scale': '1',
            'initial': [0, 0, 0, 0, 0, 0],
            'semantics': {'role': 'persistent',
                          'quantity': 'infinitesimal_strain',
                          'transformation': 'symmetric_spatial_tensor'}}],
 'derived': [],
 'equations': {'eps': 'strain_rate'},
 'domain': ['K > 0 * K', 'G > 0 * G', 'tau > 0 * tau'],
 'initial_checks': [],
 'observables': [{'name': 'stress',
                  'shape': 'sym',
                  'unit': 'Pa',
                  'scale': 'K',
                  'expr': 'K * trace(eps) * I + 2 * G * dev(eps) + 2 * G * tau * '
                          'dev(strain_rate)'}],
 'initialization': {'method': 'explicit_state',
                    'default_policy': 'examples_only',
                    'required_state': ['eps'],
                    'validation': 'domain_and_initial_checks'}}

def candidate_bytes():
    return (json.dumps(CANDIDATE, indent=2, ensure_ascii=False) + "\n").encode()

if __name__ == "__main__":
    target = Path(__file__).with_name("candidate.json")
    payload = candidate_bytes()
    if target.exists():
        assert target.read_bytes() == payload, "retained candidate differs; use a new study identity"
    else:
        target.write_bytes(payload)
    print(target)
