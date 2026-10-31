"""Prospective selection must not silently depend on ambient caches."""
import tempfile,unittest
from pathlib import Path
from atlas.evidence_sources import source_allowed,selected_files
class ProspectiveSources(unittest.TestCase):
 def test_caches_hidden_files_and_bytecode_excluded(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp)
   for name in ('source.py','sub/ref.json','__pycache__/source.py','__pycache__/source.pyc','.cache/ref.json','.git/state.json','source.pyc','.hidden.py'):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
   self.assertEqual([str(p.relative_to(root))for p in selected_files(root,{'.py','.json','.pyc'})],['source.py','sub/ref.json'])
   self.assertEqual([str(p.relative_to(root))for p in selected_files(root,{'.py','.json'})],['source.py','sub/ref.json'])
 def test_explicit_suffix_and_stable_order(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp)
   for name in ('z.hpp','a.py','b.hpp'):(root/name).write_text('fixture')
   self.assertEqual([p.name for p in selected_files(root,{'.hpp'})],['b.hpp','z.hpp'])
 def test_path_escape_rejected(self):
  for path in ('../source.py','/tmp/source.py'):
   with self.assertRaises(ValueError):source_allowed(path,{'.py'})
 def test_selected_symlink_rejected(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);(root/'real.py').write_text('fixture');(root/'alias.py').symlink_to(root/'real.py')
   with self.assertRaises(ValueError):selected_files(root,{'.py'})
if __name__=='__main__':unittest.main()
