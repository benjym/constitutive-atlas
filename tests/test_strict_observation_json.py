import struct
import unittest

from tools.strict_observation_json import loads


class StrictObservationJSONTests(unittest.TestCase):
    def test_duplicate_keys_at_every_depth_and_after_unescaping(self):
        for text in ['{"ok":false,"ok":true}', '{"nested":[{"x":0,"x":1}]}',
                     '{"ok":true,"o\\u006b":false}']:
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'duplicate'):
                loads(text)

    def test_nonfinite_values_rejected_even_in_unused_nested_fields(self):
        for token in ['NaN', 'Infinity', '-Infinity', '1e999', '-1e999', '9' * 400]:
            with self.subTest(token=token), self.assertRaises(ValueError):
                loads('{"ok":false,"unused":{"values":[' + token + ']}}')

    def test_signed_zero_subnormals_and_numeric_types(self):
        parsed = loads('[0,-0,0.0,-0.0,-0e100,5e-324,-5e-324,1,1.0,true,false,null]')
        self.assertEqual([type(x) for x in parsed],
                         [int,float,float,float,float,float,float,int,float,bool,bool,type(None)])
        for index in [1, 3, 4]:
            self.assertEqual(struct.pack('>d', parsed[index]).hex(), '8000000000000000')
        self.assertEqual(parsed[5].hex(), '0x0.0000000000001p-1022')
        self.assertEqual(parsed[6].hex(), '-0x0.0000000000001p-1022')
        self.assertEqual(parsed[0], 0)
        self.assertEqual(parsed[2], 0.0)

    def test_largest_finite_value_and_underflow_keep_standard_rounding(self):
        self.assertEqual(loads('1.7976931348623157e308'), float.fromhex('0x1.fffffffffffffp+1023'))
        self.assertEqual(loads('-1e-999').hex(), '-0x0.0p+0')
        self.assertIs(type(loads('9007199254740993')), int)

    def test_standard_json_structure_and_input_encodings(self):
        text = '{"flag":true,"message":"Infinity and NaN are words","a":[1,2.0,null]}'
        for raw in [text, text.encode(), bytearray(text.encode())]:
            self.assertEqual(loads(raw), {'flag':True,'message':'Infinity and NaN are words','a':[1,2.0,None]})
        for invalid in ['{"x":1,}', '[01]', '{}{}', '{"x":nan}']:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                loads(invalid)
