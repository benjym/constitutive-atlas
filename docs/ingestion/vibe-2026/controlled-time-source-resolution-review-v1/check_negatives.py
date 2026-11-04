from pathlib import Path
import importlib.util,unittest,io,json,tempfile,hashlib,sys
from unittest.mock import patch
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
with patch('subprocess.run',side_effect=AssertionError('subprocess forbidden')),patch('ctypes.CDLL',side_effect=AssertionError('compiled load forbidden')):
 tests=load('independent_source_resolution_tests',R/'docs/ingestion/vibe-2026/controlled-time-source-resolution-v1/test_source_resolution.py');stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests));(O/'independent-pure-tests.log').write_text(stream.getvalue());assert result.wasSuccessful() and result.testsRun==14
 m=tests.m
 with tempfile.TemporaryDirectory(prefix='runtime-direct-proof-',dir=O) as tmp:
  root=Path(tmp).resolve();name='atlas/controlled_time.py';old=(R/name).read_bytes();h=hashlib.sha256(old).hexdigest();doc='docs/runtime/source.json';archive=f'catalogue/source-snapshots/{h}/{name}'
  def write(path,raw):
   p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
  document=json.dumps({'files':[{'path':name,'sha256':h}]}).encode();write(doc,document);write(archive,old);write(name,b'changed current runtime')
  sidecar={'version':'immutable-source-archive-map-0.1','documents':{doc:hashlib.sha256(document).hexdigest()},'entries':[{'original_path':name,'sha256':h,'archived_path':archive}]};write('docs/runtime/source-archive-map.json',json.dumps(sidecar).encode())
  assert checked_receipt(root,doc,name,h)==root/archive
  with patch.object(m,'ROOT',root):
   try:m.verify_pin(doc,{'path':name,'sha256':h},{})
   except AssertionError:pass
   else:raise AssertionError('Archived runtime incorrectly bypassed direct current pin')
report={'pure_tests':14,'passed':True,'compiled_load_and_subprocess_calls':'explicitly denied','extra_runtime_negative':{'real_valid_document_binding':True,'production_checked_receipt_old_archive_passes':True,'changed_current_runtime_still_rejected':True},'temporary_fixture_removed':True}
(O/'negative-results.json').write_text(json.dumps(report,indent=2)+'\n');print('14 pure tests + valid archive/runtime negative PASS')
