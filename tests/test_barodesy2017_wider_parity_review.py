"""Original assertions are preserved and executed inside the finite source archive.

See catalogue/source-replays/finite-tensor-v1/README.md for scope and reproduction.
"""
import unittest
from tests.finite_history_replay import original_families

class OriginalFiniteAssertions(unittest.TestCase):
    def test_archived_original_family(self):
        result=original_families()['barodesy-wider']
        self.assertTrue(result['original_assertions_passed'])
        self.assertEqual(result['original_groups'],20)

if __name__=='__main__':unittest.main()
