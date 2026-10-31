"""Source-supported DP parameter restriction; compiled failure and valid recovery."""
import json,os,subprocess,unittest
from pathlib import Path
from tools.verify_plasticity import csv,dp_reference,compare
ROOT=Path(__file__).resolve().parents[1]
class DPDilatancyDomainTests(unittest.TestCase):
    def test_native_overdilatant_rejection_and_valid_boundary_response(self):
        solver=Path(os.environ.get('ATLAS_SOLVER',ROOT/'build/atlas_solver'))
        initial=[1e5]*3+[0,0,0,.7,0];de=[.01,-.005,-.005,0,0,0]
        def run(M,Md):
            p=[1e5,3e7,.25,M,Md,1e4]
            process=subprocess.run([str(solver),'--model','drucker-prager','--mode','integrate','--parameters',csv(p),'--initial',csv(initial),'--strain',csv(de)],capture_output=True,text=True,timeout=30)
            return process,json.loads(process.stdout),p
        for M,Md in ((1.2,2),(0,.0001)):
            process,result,_=run(M,Md)
            self.assertNotEqual(process.returncode,0);self.assertFalse(result['ok']);self.assertEqual(result['state'],initial)
            # Independent CLI requests; not a persistent-process recovery claim.
            process,result,p=run(1.2,.2);self.assertEqual(process.returncode,0);self.assertTrue(result['ok']);self.assertTrue(compare(result['state'],dp_reference(initial,de,p)[0])[0])
        for M,Md in ((0,0),(1.2,1.2)):
            process,result,p=run(M,Md);self.assertEqual(process.returncode,0);self.assertTrue(result['ok']);self.assertTrue(compare(result['state'],dp_reference(initial,de,p)[0])[0])
if __name__=='__main__':unittest.main()
