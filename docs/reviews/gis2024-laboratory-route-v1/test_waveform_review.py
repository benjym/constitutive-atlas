"""Synthetic supplement corruption tests, not model evidence."""
import copy,tempfile,unittest
from pathlib import Path
from test_assess import Fixture
from waveform_review import review
class Tests(unittest.TestCase):
 def test_complete_and_poisoned_legacy(self):
  with tempfile.TemporaryDirectory()as d:
   f=Fixture(Path(d));self.assertTrue(review(f.data)['saved_review_pass']);bad=copy.deepcopy(f.data);row=next(r for r in bad['laboratory']if '/cyclic/legacy'in r['id']);row['call']['response']['points'][4]['control']=0.;self.assertRaises(AssertionError,review,bad)
if __name__=='__main__':unittest.main()
