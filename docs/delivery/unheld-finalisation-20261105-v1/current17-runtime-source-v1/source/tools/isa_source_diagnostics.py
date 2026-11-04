"""Independent scalar/source-conflict diagnostics, not an ISA material evaluator."""
import json
import math


def diagnostics():
    # Table1 values; compare literal Appendix38 exponent with cited-host exponent.
    phic = math.radians(32.6)
    a = math.sqrt(3)*(3-math.sin(phic))/(2*math.sqrt(2)*math.sin(phic))
    ratio = (1.212-0.677)/(1.054-0.677)
    bracket = lambda exponent: 3+a*a-math.sqrt(3)*a*ratio**exponent
    R = 1.4e-4
    # Coordinate along one unit symmetric tensor B, no host stress evolution.
    chord = []
    for frac in [0, 0.25, 0.5, 0.75, 1.0]:
        h, c = R*(1-frac), R/2
        chord.append({'reverse_strain_over_R': frac, 'h_over_R': h/R, 'c_over_R': c/R,
                      'FH_over_R': abs(h-c)/R-0.5,
                      'N_defined': frac != 0.5,
                      'strictly_elastic_interior': 0 < frac < 1})
    # Eq29 literally printed: no arrow on strain-rate dot; rho=.5,chi=5,mR=5.
    m = lambda rate: 5+(1-5)*(.5**5)*max(rate,0)
    return {'scope':'source-conflict and elastic-memory algebra only; no coupled material trajectory',
      'barotropy_bracket': {'locator':'Table1 p1516; AppendixC p1529 Eq38',
        'phic_degrees':32.6,'ei0':1.212,'ec0':1.054,'ed0':.677,'alpha':.14,'beta':2.5,
        'a':a,'void_ratio_ratio':ratio,'literal_beta_bracket':bracket(2.5),
        'cited_VW96_alpha_bracket':bracket(.14),'repair_selected':False},
      'literal_eq29_rate_scaling': {'locator':'AppendixC p1528 Eqs28–29',
        'rho':.5,'chi':5,'mR':5,'N_dot_rate':[1.,2.],
        'm_values':[m(1),m(2)],'full_rhs_rate_homogeneity_claimed':False},
      'elastic_reversal_chord': {'locator':'Sec2 p1514 Eqs3–5; AppendixC pp1528–1529 Eqs27,31–32',
        'R':R,'initial_h':'R*B','initial_c':'R*B/2','unit_symmetric_B':True,
        'de_direction':'-B','hypothesis':'remain on source elastic branch until opposite yield boundary; c held fixed',
        'points':chord,'FH_midpoint_N_singularity_exposed':True,
        'complete_stress_Z_epsacc_path':False},
      'figure4_target': {'locator':'Sec3 p1517; Fig4 p1518; Table1 p1516',
        'e0':.8,'p0_kPa':100,'q_amplitude_kPa':60,'mobility_activation':'about fourth cycle (qualitative source statement)',
        'reproduction_ready':False,'missing':['complete initial h,c,Z,eps_acc','exact signed-q loading schedule and preparation','source conflicts resolved','numerical integration details/tolerances','digitized reference values']}}


if __name__ == '__main__':
    print(json.dumps(diagnostics(),indent=2,allow_nan=False))
