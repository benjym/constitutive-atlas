"""Actual source inputs and negative canonical-review guards; never an engine."""
from pathlib import Path
import runpy,unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
prepare=runpy.run_path(str(HERE/'prepare_integration.py'))['prepare']
class Guards(unittest.TestCase):
 def test_noncanonical_review_rejected(self):
  with self.assertRaisesRegex(ValueError,'direct canonical'):prepare(ROOT,ROOT/'docs/ingestion/bingham-comsol63/README.md')
 def test_missing_canonical_review_fails_closed(self):
  path=ROOT/'catalogue/agent-reviews/bingham-comsol63-not-a-real-review.json';self.assertFalse(path.exists())
  with self.assertRaises((ValueError,FileNotFoundError)):prepare(ROOT,path)
if __name__=='__main__':unittest.main()
