"""Portable audit of real retained observations; never executes compiled code."""
import json
import unittest

from tools import clay2014_controlled_study as study


class ControlledEvidence(unittest.TestCase):
    def test_manifest_and_original_negative(self):
        root=study.ROOT;manifest=study.read(root/study.BASE/'manifest.json')
        for name,pin in manifest['files'].items():
            self.assertEqual(study.sha(root/name),pin,name)
        self.assertEqual(manifest['outcome'],'passed')
        self.assertFalse(manifest['scientific_admission'])
        self.assertFalse(manifest['original_failed_study_replaced'])
        self.assertEqual(study.read(root/'catalogue/investigations/clay2014-paths-v1/manifest.json')['outcome'],'failed')

    def test_both_complete_journals_against_frozen_reference(self):
        results=[]
        for backend in ('native','wasm'):
            receipt=study.read(study.ROOT/study.BASE/(backend+'.json'))
            fresh=study.audit(receipt,study.ROOT/study.BASE/(backend+'.transport.jsonl'))
            stored=study.read(study.ROOT/study.BASE/(backend+'-assessment.json'))
            self.assertEqual(fresh,stored)
            self.assertEqual(fresh['outcome'],'passed')
            self.assertEqual(len(fresh['endpoint_comparisons']),18)
            self.assertEqual(sum(len(g['points']) for g in fresh['groups']),315)
            self.assertTrue(all(c['passed'] for c in fresh['endpoint_comparisons']))
            results.append(fresh)
        parity=study.parity(*results)
        self.assertEqual(parity,study.read(study.ROOT/study.BASE/'parity.json'))
        self.assertTrue(parity['passed'])
        self.assertEqual(parity['maximum_state_and_parent_scaled_difference'],0.)


if __name__=='__main__':unittest.main()
