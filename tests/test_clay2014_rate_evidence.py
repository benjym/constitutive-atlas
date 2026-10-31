"""Replay retained independent rates and both opaque transports without a binary."""
import unittest
from atlas.evidence import verify_manifest_files
from atlas.model import ROOT
from tools import clay2014_rate_study as s
from tools import clay2014_rate_assessment as a
class RetainedRates(unittest.TestCase):
    def test_retained_source_raw_and_numerical_evidence(self):
        relative='catalogue/investigations/clay2014-rates-v1'
        packet=ROOT/relative
        m=verify_manifest_files(ROOT,relative+'/manifest.json')
        self.assertIs(m['public_admission'],False)
        n=s.read(packet/'native.json');w=s.read(packet/'wasm.json')
        self.assertEqual(s.verify(n)['valid_cases'],37)
        self.assertEqual(s.verify(w)['invalid_recovery_pairs'],16)
        with self.assertRaisesRegex(ValueError,'Wasm raw response binding'):
            s.verify_transport(w,packet/'wasm.transport.json')
        result=a.assess(packet/'wasm.json',packet/'native.json',packet/'wasm.transport.json',packet/'native.transport.json')
        self.assertEqual(result,s.read(packet/'assessment.json'))
        self.assertEqual(result['transport_rows'],{'native':70,'wasm':70})
if __name__=='__main__':unittest.main()
