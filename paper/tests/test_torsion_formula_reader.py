"""Protect the denominator grouping lost by the general XLS decompiler."""
import importlib.util
from pathlib import Path
import struct
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/extract_torsion_transformations.py'
spec = importlib.util.spec_from_file_location('torsion_formulas', SCRIPT)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def integer(value):
    return b'\x1e' + struct.pack('<H', value)


class FormulaGroupingTests(unittest.TestCase):
    def test_product_in_denominator_remains_grouped(self):
        # RPN: 6 2 3 multiply divide. Ungrouped 6/2*3 would give 9.
        tokens = integer(6) + integer(2) + integer(3) + b'\x05\x06'
        expression = reader.grouped_formula(tokens)
        self.assertEqual(expression, '(6/(2*3))')

    def test_subtraction_operand_remains_grouped(self):
        tokens = integer(6) + integer(2) + integer(1) + b'\x04\x04'
        self.assertEqual(reader.grouped_formula(tokens), '(6-(2-1))')

    def test_unknown_token_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported token'):
            reader.grouped_formula(b'\xff')

    def test_shared_reference_moves_but_absolute_baseline_stays(self):
        tokens = bytes.fromhex('4c0000fbc0441100070004')
        self.assertEqual(reader.grouped_formula(tokens, (21, 7)), '(C22-$H$18)')
        self.assertEqual(reader.grouped_formula(tokens, (21, 8)), '(D22-$H$18)')
        self.assertEqual(reader.grouped_formula(tokens, (85, 10)), '(F86-$H$18)')


if __name__ == '__main__':
    unittest.main()
