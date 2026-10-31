import copy,hashlib,json,os,pathlib,tempfile,unittest
from unittest.mock import patch
import capsule

class Replay(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name)
  self.put('atlas/__init__.py','')
  self.put('atlas/model.py',"from pathlib import Path\nROOT=Path(__file__).resolve().parents[1]\nVALUE='old'\n")
  self.put('entry.py',"import atlas.model\nassert atlas.model.VALUE=='old'\nassert str(atlas.model.ROOT)==__import__('os').getcwd()\nprint('old-root-bound')\n")
 def put(self,n,s):p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
 def exported(self,expected_exit=0):
  pins={p.relative_to(self.root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.rglob('*') if p.is_file()}
  return capsule.export(self.root,pins,'entry.py',expected_exit=expected_exit)
 def test_live_evolution_does_not_change_archived_replay(self):
  c=self.exported();self.put('atlas/model.py',"raise RuntimeError('current code changed')\n")
  r=capsule.replay(c);self.assertTrue(r['expected_exit_matched']);self.assertEqual(r['stdout'],'old-root-bound\n')
 def test_missing_import_cannot_fallback_to_ambient_repo(self):
  c=self.exported();del c['files']['atlas/model.py']
  with patch.dict(os.environ,{'PYTHONPATH':str(self.root),'ATLAS_REVIEW_REPO':str(self.root)}):r=capsule.replay(c)
  self.assertNotEqual(r['returncode'],0);self.assertIn('ModuleNotFoundError',r['stderr'])
 def test_negative_exit_is_retained_not_relabelled_pass(self):
  self.put('entry.py',"print('retained-failed-gate')\nraise SystemExit(1)\n");r=capsule.replay(self.exported(1))
  self.assertTrue(r['expected_exit_matched']);self.assertEqual(r['returncode'],1);self.assertEqual(r['stdout'],'retained-failed-gate\n')
 def test_blob_corruption_and_path_escape_rejected(self):
  for mode in ('blob','path','digest','size','collision'):
   c=self.exported()
   if mode=='blob':c['files']['entry.py']['base64']='AA=='
   elif mode=='path':c['files']['../entry.py']=c['files'].pop('entry.py')
   elif mode=='digest':c['files']['entry.py']['sha256']='0'*64
   elif mode=='size':c['files']['entry.py']['bytes']=True
   else:c['files']['atlas']=copy.deepcopy(c['files']['entry.py'])
   with self.subTest(mode=mode),self.assertRaises(ValueError):capsule.validate(c)
 def test_failed_original_pin_never_substitutes_current_hash(self):
  with self.assertRaisesRegex(ValueError,'original source pin'):capsule.export(self.root,{'entry.py':'0'*64},'entry.py')
 def test_input_mutation_during_replay_rejected(self):
  self.put('entry.py',"from pathlib import Path\nPath('atlas/model.py').write_text('changed')\n")
  with self.assertRaisesRegex(ValueError,'input changed'):capsule.replay(self.exported())
 def test_fresh_materialization_required(self):
  c=self.exported()
  with self.assertRaisesRegex(ValueError,'fresh capsule'):capsule.materialize(c,self.root)

if __name__=='__main__':unittest.main()
