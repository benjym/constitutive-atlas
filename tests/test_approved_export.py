"""Exact approved nested definitions survive ordinary export without runtime promotion."""
import json,sqlite3,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from atlas import research
from atlas.dsl import ValidationError
ROOT=Path(__file__).resolve().parents[1]
class ApprovedExport(unittest.TestCase):
 def test_current_database_retains_timed_definition_review_and_source(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'atlas.sqlite';research.export_database(p)
   with sqlite3.connect(p) as c:
    mid='power-creep-itasca900-both-active-ode'
    status,ordinary,raw=c.execute('select status,executable,definition_json from models where id=?',(mid,)).fetchone()
    model=json.loads((ROOT/'models/research/power-creep'/f'{mid}.json').read_text())
    self.assertEqual(json.loads(raw),model);self.assertEqual(status,model['status']);self.assertEqual(ordinary,0)
    self.assertTrue(c.execute('select count(*) from model_approvals where model_id=?',(mid,)).fetchone()[0]>=1)
    review=c.execute('select record_json from agent_reviews where model_id=?',(mid,)).fetchone();self.assertEqual(json.loads(review[0])['status'],'accepted')
    self.assertTrue(c.execute('select count(*) from sources where model_id=?',(mid,)).fetchone()[0])
    self.assertEqual(c.execute('select count(*) from models where executable=1').fetchone()[0],len(research.all_models()))
   research.export_database(p) # repeat export has no duplicate/FK residue
 def test_stale_identity_path_escape_and_conflicting_approval_rejected(self):
  registry=ROOT/'catalogue/approved-models.json';original=json.loads(registry.read_text());base=next(x for x in original['models'] if x['model_id']=='power-creep-itasca900-both-active-ode')
  actual=Path.read_text
  for changed in [{**base,'definition':{**base['definition'],'sha256':'0'*64}},{**base,'model_id':'other'},{**base,'definition':{**base['definition'],'path':'../secret.json'}}]:
   def read(p,*a,**kw):return json.dumps({'models':[changed]}) if p==registry else actual(p,*a,**kw)
   with patch.object(Path,'read_text',read),self.assertRaises((ValidationError,OSError)):research.approved_definitions()
if __name__=='__main__':unittest.main()
