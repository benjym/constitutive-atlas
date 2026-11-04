import unittest
from tools.isa_source_diagnostics import diagnostics

class SourceDiagnostics(unittest.TestCase):
 def test_printed_exponent_conflict(self):
  b=diagnostics()['barotropy_bracket']
  self.assertLess(b['literal_beta_bracket'],0)
  self.assertGreater(b['cited_VW96_alpha_bracket'],0)
  self.assertFalse(b['repair_selected'])
 def test_printed_rate_scaling(self):
  v=diagnostics()['literal_eq29_rate_scaling']['m_values']
  self.assertEqual(v,[4.875,4.75])
 def test_elastic_memory_chord_only(self):
  p=diagnostics()['elastic_reversal_chord']['points']
  self.assertAlmostEqual(p[0]['FH_over_R'],0)
  self.assertAlmostEqual(p[-1]['FH_over_R'],0)
  for q in p[1:-1]:self.assertLess(q['FH_over_R'],0)
  self.assertFalse(p[2]['N_defined'])
  self.assertFalse(diagnostics()['figure4_target']['reproduction_ready'])

if __name__=='__main__':unittest.main()
