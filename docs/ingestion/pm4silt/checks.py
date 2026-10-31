"""Independent algebraic discrepancy witnesses, not a PM4Silt material kernel."""
import json, math, unittest

def witnesses():
    lam,xi,nd,nb=.06,.03,.3,.8
    cp=[]
    for ratio in (1.,2.,5.,8.):
        cp.append({'p_over_pmin':ratio,'body_eq87':max(0.,min(1.,(ratio-2)/6)),'table2_1':1/(1+(1/ratio)**2)})
    p0,pcs=100000.,80000.
    return {'scope':'independent algebra only; alternatives not selected',
      'surface_exponents':{'inputs':{'lambda':lam,'xi':xi,'nd':nd,'nbwet':nb},'Md_over_M_body12':math.exp(nd*xi),'Md_over_M_table':math.exp(nd*xi/lam),'Mb_over_M_body14':math.exp(-nb*xi),'Mb_over_M_table':math.exp(-nb*xi/lam)},
      'contraction_pressure_factor':cp,
      'default_pmin':{'inputs_Pa':{'consolidation_p':p0,'pcs':pcs},'body_p30_no_greater_than_p0_half':max(500.,min(pcs/8,p0/2)),'table4_2_p67_not_smaller_than_p0_half':max(500.,max(pcs/8,p0/2))},
      'elasticity_pressure_power':{'p_over_pA':4.,'startup_table3_2_power_half':4**.5,'body26_default_nG_075':4**.75},
      'fabric_zero_increment':{'initial_z':[.1,-.1,.2],'table2_1_parent_plus_dz':[.1,-.1,.2],'table3_1_step14_literal_parent_minus_zero_plus_parent':[.2,-.2,.4]},
      'lagged_D':{'inputs':{'G_Pa':100.,'K_Pa':200.,'Kp_Pa':100.,'n_dot_de':.01,'n_dot_r':.2,'dvol':0.,'D_old':0.,'D_candidate':1.},'L_using_old_D':2/300,'L_using_new_D':2/260},
      'contraction_Cwet':{'inputs':{'bounding_distance':1e-6,'xi':.06,'lambda':.06,'Cw1':.02,'Cw2':.1},'literal_equation84_before_printed_cap':1/(1/(1+(.02/1e-6)**4)+1/(1+(.06/.06/.1)**2))}}

class Checks(unittest.TestCase):
    def test_surface_exponents_distinguish(self):
        x=witnesses()['surface_exponents'];self.assertNotEqual(x['Md_over_M_body12'],x['Md_over_M_table']);self.assertNotEqual(x['Mb_over_M_body14'],x['Mb_over_M_table'])
    def test_cpmin_boundary(self):
        x=witnesses()['contraction_pressure_factor'];self.assertEqual(x[1]['body_eq87'],0.);self.assertEqual(x[1]['table2_1'],.8);self.assertEqual(x[-1]['body_eq87'],1.)
    def test_pmin_opposite_bounds(self):
        x=witnesses()['default_pmin'];self.assertEqual(x['body_p30_no_greater_than_p0_half'],10000.);self.assertEqual(x['table4_2_p67_not_smaller_than_p0_half'],50000.)
    def test_startup_power(self):
        x=witnesses()['elasticity_pressure_power'];self.assertEqual(x['startup_table3_2_power_half'],2.);self.assertGreater(x['body26_default_nG_075'],2.)
    def test_literal_fabric_printing(self):
        x=witnesses()['fabric_zero_increment'];self.assertEqual(x['initial_z'],x['table2_1_parent_plus_dz']);self.assertNotEqual(x['initial_z'],x['table3_1_step14_literal_parent_minus_zero_plus_parent'])
    def test_lagged_operands(self):
        x=witnesses()['lagged_D'];self.assertNotEqual(x['L_using_old_D'],x['L_using_new_D'])
    def test_cwet_printed_upper_bound_needs_policy(self):
        self.assertGreater(witnesses()['contraction_Cwet']['literal_equation84_before_printed_cap'],100.)

if __name__=='__main__':
    import sys
    if '--json' in sys.argv:print(json.dumps(witnesses(),indent=2,allow_nan=False))
    else:unittest.main()
