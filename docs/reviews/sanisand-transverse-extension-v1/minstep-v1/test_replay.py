import json
from pathlib import Path
import tempfile,unittest
from replay_failure import replay

HERE=Path(__file__).resolve().parent
class SavedReplayTests(unittest.TestCase):
 def corrupt(self,change):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);failure=json.loads((HERE/'saved/failure.json').read_text());change(failure)
   (d/'failure.json').write_text(json.dumps(failure));(d/'partial.json').write_bytes((HERE/'saved/partial.json').read_bytes())
   with self.assertRaises(AssertionError):replay(d)
 def test_changed_trial_output_rejected(self):self.corrupt(lambda f:f['high'].__setitem__(29,'1'))
 def test_changed_error_rejected(self):self.corrupt(lambda f:f.update(error='1'))
if __name__=='__main__':unittest.main()
