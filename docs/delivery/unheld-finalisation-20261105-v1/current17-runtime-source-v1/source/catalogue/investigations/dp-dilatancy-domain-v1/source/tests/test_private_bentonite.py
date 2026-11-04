import unittest

from tools.map_private_bentonite import bcv_properties, column, convert_vibe, property_unit, vibe_spec


class PrivateBentoniteTests(unittest.TestCase):
    def test_temperature_water_content_is_percent(self):
        kind,spec,_=vibe_spec('WRC1600-60C.txt')
        columns=[column(i,q,u)for i,(q,u)in enumerate(spec)]
        r=convert_vibe(dict(source_line=1,native=[20,25]),columns,kind)
        self.assertEqual(r['values'],{'0':20e6,'1':.25})
        self.assertEqual(r['native'],[20,25])

    def test_segment_endpoints_and_offset_are_preserved(self):
        kind,spec,_=vibe_spec('st040.txt');columns=[column(i,q,u)for i,(q,u)in enumerate(spec)]
        r=convert_vibe(dict(source_line=3,native=[0,1400,40,1420]),columns,kind)
        self.assertEqual(r['source_plot_derived'],dict(start_stress_Pa=5120,end_stress_Pa=45120))
        self.assertEqual(r['native'],[0,1400,40,1420])

    def test_unreferenced_tables_do_not_inherit_units(self):
        for name in ['swellstrain.txt','BCV-ssw.txt','st042.txt']:
            self.assertEqual(vibe_spec(name),('unresolved_source_table',[],None))

    def test_unknown_wrc_column_remains_unresolved(self):
        _,spec,_=vibe_spec('WRC1600.txt')
        self.assertIsNone(spec[2][1])

    def test_duplicate_properties_preserve_columns_and_zero(self):
        rows=[dict(excel_row=1,cells=[None]*4+['swelling',None,'strength']),
              dict(excel_row=2,cells=['id','ref','sample','material','Ps, kPa','Ps, kPa','Rc, kPa']),
              dict(excel_row=3,cells=[1,'REF','a','BCV',0,None,5])]
        p=bcv_properties(rows)
        self.assertEqual([v['column']for v in p],[5,7])
        self.assertEqual([v['value']for v in p],[0,5000])
        self.assertTrue(all(v['reference_code']=='REF'for v in p))

    def test_temperature_uncertainty_does_not_receive_offset(self):
        rows=[dict(excel_row=2,cells=[None]*4+['t, °C','nejistota t, °C']),
              dict(excel_row=3,cells=[1,'REF','a','BCV',20,2])]
        p=bcv_properties(rows)
        self.assertEqual([v['value']for v in p],[293.15,2])
        self.assertFalse(p[0]['is_uncertainty']);self.assertTrue(p[1]['is_uncertainty'])

    def test_unlabelled_unit_is_not_inferred_from_quantity(self):
        self.assertIsNone(property_unit('density'))
        self.assertEqual(property_unit('ρd,\nkg/m3'),'kg/m3')

    def test_swelling_index_and_days_are_scaled_from_explicit_units(self):
        rows=[dict(excel_row=2,cells=[None]*4+['SI_24 h, ml/2 g','doba máčení, dny','doba máčení']),
              dict(excel_row=3,cells=[1,'REF','a','BCV',20,2,3])]
        p=bcv_properties(rows)
        self.assertEqual([v['value']for v in p],[.01,172800,None])
        self.assertEqual(p[0]['unit'],'m³/kg')


if __name__=='__main__':unittest.main()
