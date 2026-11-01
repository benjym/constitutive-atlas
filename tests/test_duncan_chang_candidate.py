"""Source compliance fixtures exercise the complete declarative Duncan law."""
import json
from pathlib import Path
import unittest

from atlas.model import load,interpret

ROOT=Path(__file__).resolve().parents[1]
STUDY=ROOT/'docs/ingestion/duncan-chang-1970/material-v1/execution-v1'

class DuncanChangSourceFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model=load(STUDY/'candidate.json')
        cls.cases=json.loads((STUDY/'requests.json').read_text())['cases']

    def test_complete_source_compliance_endpoints(self):
        self.assertEqual(len(self.cases),72)
        branches=set()
        for case in self.cases:
            with self.subTest(case=case['id']):
                current=case['target'];previous=case['initial']
                residual=interpret(self.model,{'sigma':current[:6],'h':current[6]},
                    {'sigma':previous[:6],'h':previous[6]},case['de'],case['parameters'])
                values=list(residual['sigma'].v)+[residual['h']]
                self.assertLessEqual(max(map(abs,values))/case['parameters']['p_ref'],2e-10)
                branches.add(case['branch'])
        self.assertEqual(branches,{'primary','unload_reload','postfailure'})

    def test_history_is_not_reconstructed_from_current_stress(self):
        case=next(c for c in self.cases if c['id']=='dense-history-1')
        current=case['target'];previous=case['initial']
        residual=interpret(self.model,{'sigma':current[:6],'h':current[6]+100.},
            {'sigma':previous[:6],'h':previous[6]},case['de'],case['parameters'])
        self.assertAlmostEqual(residual['h'],100.,places=7)

if __name__=='__main__':unittest.main()
